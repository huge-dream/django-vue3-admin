# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/3 003 0:30
@Remark: 菜单按钮管理
"""
from django.db.models import F, Subquery, OuterRef, Exists
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import RoleApiPermission, Menu, MenuButton, Dept, RoleMenuPermission, Columns
from dvadmin.system.views.menu import MenuSerializer
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class RoleApiPermissionSerializer(CustomModelSerializer):
    """
    菜单按钮-序列化器
    """
    class Meta:
        model = RoleApiPermission
        fields = "__all__"
        read_only_fields = ["id"]



class RoleApiPermissionCreateUpdateSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """
    menu_button__name = serializers.CharField(source='menu_button.name', read_only=True)
    menu_button__value = serializers.CharField(source='menu_button.value', read_only=True)

    class Meta:
        model = RoleApiPermission
        fields = "__all__"
        read_only_fields = ["id"]


class RoleButtonPermissionSerializer(CustomModelSerializer):
    """
    角色按钮权限
    """
    isCheck = serializers.SerializerMethodField()
    data_range = serializers.SerializerMethodField()

    def get_isCheck(self, instance):
        params = self.request.query_params
        return RoleApiPermission.objects.filter(
            menu_button__id=instance['id'],
            role__id=params.get('role'),
        ).exists()

    def get_data_range(self, instance):
        params = self.request.query_params
        obj = RoleApiPermission.objects.filter(
            menu_button__id=instance['id'],
            role__id=params.get('role'),
        ).first()
        if obj is None:
            return None
        return obj.data_range


    class Meta:
        model = MenuButton
        fields = ['id','name','value','isCheck','data_range']

class RoleColumnsSerializer(CustomModelSerializer):

    class Meta:
        model = Columns
        fields = "__all__"


class RoleMenuPermissionSerializer(CustomModelSerializer):
    """
    菜单和按钮权限
    """
    isCheck = serializers.SerializerMethodField()
    btns = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()

    def get_isCheck(self, instance):
        params = self.request.query_params
        return RoleMenuPermission.objects.filter(
            menu__id=instance['id'],
            role__id=params.get('role'),
        ).exists()

    def get_btns(self, instance):
        btn_list = MenuButton.objects.filter(menu__id=instance['id']).values('id', 'name', 'value')
        serializer = RoleButtonPermissionSerializer(btn_list,many=True,request=self.request)
        return  serializer.data

    def get_columns(self, instance):
        params = self.request.query_params
        col_list = Columns.objects.filter(role__id=params.get('role'))
        serializer = RoleColumnsSerializer(col_list,many=True,request=self.request)
        return serializer.data



    class Meta:
        model = Menu
        fields = ['id','name','isCheck','btns','columns']

class RoleApiPermissionViewSet(CustomModelViewSet):
    """
    菜单按钮接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = RoleApiPermission.objects.all()
    serializer_class = RoleApiPermissionSerializer
    create_serializer_class = RoleApiPermissionCreateUpdateSerializer
    update_serializer_class = RoleApiPermissionCreateUpdateSerializer
    extra_filter_class = []

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def data_scope(self, request):
        """
        获取数据权限范围:角色授权页面使用
        :param request:
        :return:
        """
        is_superuser = request.user.is_superuser
        if is_superuser:
            data = [
                {
                    "value": 0,
                    "label": '仅本人数据权限'
                },
                {
                    "value": 1,
                    "label": '本部门及以下数据权限'
                },
                {
                    "value": 2,
                    "label": '本部门数据权限'
                },
                {
                    "value": 3,
                    "label": '全部数据权限'
                },
                {
                    "value": 4,
                    "label": '自定义数据权限'
                }
            ]
            return DetailResponse(data=data)
        else:
            data = []
            role_list = request.user.role.values_list('id', flat=True)
            if params := request.query_params:
                if menu_button_id := params.get('menu_button', None):
                    role_queryset = RoleApiPermission.objects.filter(
                        role__in=role_list, menu_button__id=menu_button_id
                    ).values_list('data_range', flat=True)
                    data_range_list = list(set(role_queryset))
                    for item in data_range_list:
                        if item == 0:
                            data = [{
                                "value": 0,
                                "label": '仅本人数据权限'
                            }]
                        elif item == 1:
                            data = [{
                                "value": 0,
                                "label": '仅本人数据权限'
                            }, {
                                "value": 1,
                                "label": '本部门及以下数据权限'
                            },
                                {
                                    "value": 2,
                                    "label": '本部门数据权限'
                                }]
                        elif item == 2:
                            data = [{
                                "value": 0,
                                "label": '仅本人数据权限'
                            },
                                {
                                    "value": 2,
                                    "label": '本部门数据权限'
                                }]
                        elif item == 3:
                            data = [{
                                "value": 0,
                                "label": '仅本人数据权限'
                            },
                                {
                                    "value": 3,
                                    "label": '全部数据权限'
                                }, ]
                        elif item == 4:
                            data = [{
                                "value": 0,
                                "label": '仅本人数据权限'
                            },
                                {
                                    "value": 4,
                                    "label": '自定义数据权限'
                                }]
                        else:
                            data = []
                    return DetailResponse(data=data)
        return ErrorResponse(msg="参数错误")

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def role_to_dept_all(self, request):
        """
        当前用户角色下所能授权的部门:角色授权页面使用
        :param request:
        :return:
        """
        params = request.query_params
        is_superuser = request.user.is_superuser
        is_admin = request.user.role.values_list('admin', flat=True)
        if is_superuser or True in is_admin:
            queryset = Dept.objects.values('id', 'name', 'parent')
        else:
            if not params:
                return ErrorResponse(msg="参数错误")
            menu_button = params.get('menu_button')
            if menu_button is None:
                return ErrorResponse(msg="参数错误")
            role_list = request.user.role.values_list('id', flat=True)
            dept_ids = RoleApiPermission.objects.filter(role__in=role_list).values_list('dept__id',flat=True)
            queryset = Dept.objects.filter(id__in=dept_ids).values('id', 'name', 'parent')
        return DetailResponse(data=queryset)
