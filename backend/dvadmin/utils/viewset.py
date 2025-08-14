# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/1 001 22:57
@Remark: 自定义视图集
"""
import copy

from django.db import transaction
from django_filters import DateTimeFromToRangeFilter
from django_filters.rest_framework import FilterSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from dvadmin.utils.filters import CoreModelFilterBankend, DataLevelPermissionMargeFilter
from dvadmin.utils.import_export_mixin import ExportSerializerMixin, ImportSerializerMixin
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from dvadmin.utils.permission import CustomPermission
from dvadmin.utils.models import get_custom_app_models, CoreModel
from dvadmin.system.models import FieldPermission, MenuField
from django_restql.mixins import QueryArgumentsMixin


class CustomModelViewSet(ModelViewSet, ImportSerializerMixin, ExportSerializerMixin, QueryArgumentsMixin):
    """
    自定义的ModelViewSet:
    统一标准的返回格式;新增,查询,修改可使用不同序列化器
    (1)ORM性能优化, 尽可能使用values_queryset形式
    (2)xxx_serializer_class 某个方法下使用的序列化器(xxx=create|update|list|retrieve|destroy)
    (3)filter_fields = '__all__' 默认支持全部model中的字段查询(除json字段外)
    (4)import_field_dict={} 导入时的字段字典 {model值: model的label}
    (5)export_field_label = [] 导出时的字段
    """
    values_queryset = None
    ordering_fields = '__all__'
    create_serializer_class = None
    update_serializer_class = None
    filter_fields = '__all__'
    search_fields = ()
    extra_filter_class = [CoreModelFilterBankend,DataLevelPermissionMargeFilter]
    permission_classes = [CustomPermission]
    import_field_dict = {}
    export_field_label = {}

    def filter_queryset(self, queryset):
        for backend in set(set(self.filter_backends) | set(self.extra_filter_class or [])):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        if getattr(self, 'values_queryset', None):
            return self.values_queryset
        return super().get_queryset()

    def get_serializer_class(self):
        action_serializer_name = f"{self.action}_serializer_class"
        action_serializer_class = getattr(self, action_serializer_name, None)
        if action_serializer_class:
            return action_serializer_class
        return super().get_serializer_class()

    # 通过many=True直接改造原有的API，使其可以批量创建
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        # 全部以可见字段为准
        can_see = self.get_menu_field(serializer_class)
        # 排除掉序列化器级的字段(排除字段权限中未授权的字段)
        # if not self.request.user.is_superuser:
        #     exclude_set = set(serializer_class._declared_fields.keys()) - set(can_see)
        #     for field in exclude_set:
        #         serializer_class._declared_fields.pop(field)
        #     meta = copy.deepcopy(serializer_class.Meta)
        #     meta.fields = list(can_see)
        #     serializer_class.Meta = meta
        # 在分页器中使用
        self.request.permission_fields = can_see
        if isinstance(self.request.data, list):
            with transaction.atomic():
                return serializer_class(many=True, *args, **kwargs)
        else:
            return serializer_class(*args, **kwargs)

    def get_menu_field(self, serializer_class):
        """获取字段权限"""

        if not any(model['object'] is serializer_class.Meta.model for model in get_custom_app_models()):
            return []

        # 匿名用户没有角色
        ret = FieldPermission.objects.filter(field__model=serializer_class.Meta.model.__name__)
        if hasattr(self.request.user, 'role'):
            roles = self.request.user.role.values_list('id', flat=True)
            ret = ret.filter(is_query=True, role__in=roles)

        return ret.values_list('field__field_name', flat=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return DetailResponse(data=serializer.data, msg="新增成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return DetailResponse(data=serializer.data, msg="获取成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, request=request, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return DetailResponse(data=serializer.data, msg="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return DetailResponse(data=[], msg="删除成功")

    keys = openapi.Schema(description='主键列表', type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['keys'],
        properties={'keys': keys}
    ), operation_summary='批量删除')
    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        request_data = request.data
        keys = request_data.get('keys', None)
        if keys:
            self.get_queryset().filter(id__in=keys).delete()
            return SuccessResponse(data=[], msg="删除成功")
        else:
            return ErrorResponse(msg="未获取到keys字段")

    @action(methods=['post'], detail=False)
    def get_by_ids(self, request):
        """通过IDS列表获取数据"""
        ids = request.data.get('ids', [])
        if ids and ids != ['']:
            queryset = self.get_queryset().filter(id__in=ids)
            serializer = self.get_serializer(queryset, many=True)
            return DetailResponse(data=serializer.data)
        return DetailResponse(data=None)
