# -*- coding: utf-8 -*-
import pypinyin
from django.db.models import Q
from rest_framework import serializers

from dvadmin.system.models import Area
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class AreaSerializer(CustomModelSerializer):
    """
    地区-序列化器
    """
    pcode_count = serializers.SerializerMethodField(read_only=True)
    hasChild = serializers.SerializerMethodField()
    pcode_info = serializers.SerializerMethodField()

    def get_pcode_info(self, instance):
        pcode = Area.objects.filter(code=instance.pcode_id).values("name", "code")
        return pcode

    def get_pcode_count(self, instance: Area):
        return Area.objects.filter(pcode=instance).count()

    def get_hasChild(self, instance):
        hasChild = Area.objects.filter(pcode=instance.code)
        if hasChild:
            return True
        return False

    class Meta:
        model = Area
        fields = "__all__"
        read_only_fields = ["id"]


class AreaCreateUpdateSerializer(CustomModelSerializer):
    """
    地区管理 创建/更新时的列化器
    """

    def to_internal_value(self, data):
        pinyin = ''.join([''.join(i) for i in pypinyin.pinyin(data["name"], style=pypinyin.NORMAL)])
        data["level"] = 1
        data["pinyin"] = pinyin
        data["initials"] = pinyin[0].upper() if pinyin else "#"
        pcode = data["pcode"] if 'pcode' in data else None
        if pcode:
            pcode = Area.objects.get(pk=pcode)
            data["pcode"] = pcode.code
            data["level"] = pcode.level + 1
        return super().to_internal_value(data)

    class Meta:
        model = Area
        fields = '__all__'


class AreaViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    地区管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    create_serializer_class = AreaCreateUpdateSerializer
    update_serializer_class = AreaCreateUpdateSerializer
    extra_filter_class = []

    def list(self, request, *args, **kwargs):
        self.request.query_params._mutable = True
        params = self.request.query_params
        known_params = {'page', 'limit', 'pcode'}
        # 使用集合操作检查是否有未知参数
        other_params_exist = any(param not in known_params for param in params)
        if other_params_exist:
            queryset = self.queryset.filter(enable=True)
        else:
            pcode = params.get('pcode', None)
            params['limit'] = 999
            if params and pcode:
                queryset = self.queryset.filter(enable=True, pcode=pcode)
            else:
                queryset = self.queryset.filter(enable=True, level=1)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")
