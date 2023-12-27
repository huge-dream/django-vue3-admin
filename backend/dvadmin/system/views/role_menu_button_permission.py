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

from dvadmin.system.models import RoleMenuButtonPermission, Menu, MenuButton, Dept, RoleMenuPermission, FieldPermission, \
    MenuField
from dvadmin.system.views.menu import MenuSerializer
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class RoleMenuButtonPermissionSerializer(CustomModelSerializer):
    """
    菜单按钮-序列化器
    """
    class Meta:
        model = RoleMenuButtonPermission
        fields = "__all__"
        read_only_fields = ["id"]



class RoleMenuButtonPermissionCreateUpdateSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """
    menu_button__name = serializers.CharField(source='menu_button.name', read_only=True)
    menu_button__value = serializers.CharField(source='menu_button.value', read_only=True)

    class Meta:
        model = RoleMenuButtonPermission
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
        return RoleMenuButtonPermission.objects.filter(
            menu_button__id=instance['id'],
            role__id=params.get('role'),
        ).exists()

    def get_data_range(self, instance):
        params = self.request.query_params
        obj = RoleMenuButtonPermission.objects.filter(
            menu_button__id=instance['id'],
            role__id=params.get('role'),
        ).first()
        if obj is None:
            return None
        return obj.data_range


    class Meta:
        model = MenuButton
        fields = ['id','name','value','isCheck','data_range']

class RoleFieldPermissionSerializer(CustomModelSerializer):

    class Meta:
        model = FieldPermission
        fields = "__all__"

class RoleMenuFieldSerializer(CustomModelSerializer):
    is_query = serializers.SerializerMethodField()
    is_create = serializers.SerializerMethodField()
    is_update = serializers.SerializerMethodField()

    def get_is_query(self, instance):
        params = self.request.query_params
        queryset = instance.menu_field.filter(role=params.get('role')).first()
        if queryset:
            return queryset.is_query
        return False

    def get_is_create(self, instance):
        params = self.request.query_params
        queryset = instance.menu_field.filter(role=params.get('role')).first()
        if queryset:
            return queryset.is_create
        return False

    def get_is_update(self, instance):
        params = self.request.query_params
        queryset = instance.menu_field.filter(role=params.get('role')).first()
        if queryset:
            return queryset.is_update
        return False
    class Meta:
        model = MenuField
        fields = ['id','field_name','title','is_query','is_create','is_update']


class RoleMenuPermissionSerializer(CustomModelSerializer):
    """
    菜单和按钮权限
    """
    name = serializers.SerializerMethodField()
    isCheck = serializers.SerializerMethodField()
    btns = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()

    def get_name(self, instance):
        parent_list = Menu.get_all_parent(instance['id'])
        names = [d["name"] for d in parent_list]
        return "/".join(names)
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
        col_list = MenuField.objects.filter(menu=instance['id'])
        serializer = RoleMenuFieldSerializer(col_list,many=True,request=self.request)
        return serializer.data



    class Meta:
        model = Menu
        fields = ['id','name','isCheck','btns','columns']

class RoleMenuButtonPermissionViewSet(CustomModelViewSet):
    """
    菜单按钮接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = RoleMenuButtonPermission.objects.all()
    serializer_class = RoleMenuButtonPermissionSerializer
    create_serializer_class = RoleMenuButtonPermissionCreateUpdateSerializer
    update_serializer_class = RoleMenuButtonPermissionCreateUpdateSerializer
    extra_filter_class = []

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_role_premission(self, request):
        """
        角色授权获取:
        :param request: role
        :return: menu,btns,columns
        """
        params = request.query_params
        role = params.get('role',None)
        if  role is None:
            return ErrorResponse(msg="未获取到角色信息")
        is_superuser = request.user.is_superuser
        if is_superuser:
            queryset = Menu.objects.filter(status=1,is_catalog=False).values('name', 'id').all()
        else:
            role_id = request.user.role.values_list('id', flat=True)
            menu_list = RoleMenuPermission.objects.filter(role__in=role_id).values_list('id',flat=True)
            queryset = Menu.objects.filter(status=1, is_catalog=False,id__in=menu_list).values('name', 'id').all()
        serializer = RoleMenuPermissionSerializer(queryset,many=True,request=request)
        data = serializer.data
        return DetailResponse(data=data)

    @action(methods=['PUT'], detail=True, permission_classes=[IsAuthenticated])
    def set_role_premission(self,request,pk):
        """
        对角色的菜单和按钮及按钮范围授权:
        :param request:
        :param pk: role
        :return:
        """
        body = request.data
        RoleMenuPermission.objects.filter(role=pk).delete()
        RoleMenuButtonPermission.objects.filter(role=pk).delete()
        for menu in body:
            if menu.get('isCheck'):
                menu_parent = Menu.get_all_parent(menu.get('id'))
                role_menu_permission_list = []
                for d in menu_parent:
                    role_menu_permission_list.append(RoleMenuPermission(role_id=pk, menu_id=d["id"]))
                RoleMenuPermission.objects.bulk_create(role_menu_permission_list)
                # RoleMenuPermission.objects.create(role_id=pk, menu_id=menu.get('id'))
            for btn in menu.get('btns'):
                if btn.get('isCheck'):
                    data_range = btn.get('data_range',0) or 0
                    instance = RoleMenuButtonPermission.objects.create(role_id=pk, menu_button_id=btn.get('id'),data_range=data_range)
                    instance.dept.set(btn.get('dept',[]))
            for col in menu.get('columns'):
                FieldPermission.objects.update_or_create(role_id=pk,field_id=col.get('id'),is_query=col.get('is_query'),is_create=col.get('is_create'),is_update=col.get('is_update'))
        return DetailResponse(msg="授权成功")



    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def role_menu_get_button(self, request):
        """
        当前用户角色和菜单获取可下拉选项的按钮:角色授权页面使用
        :param request:
        :return:
        """
        if params := request.query_params:
            if menu_id := params.get('menu', None):
                is_superuser = request.user.is_superuser
                if is_superuser:
                    queryset = MenuButton.objects.filter(menu=menu_id).values('id', 'name')
                else:
                    role_list = request.user.role.values_list('id', flat=True)
                    queryset = RoleMenuButtonPermission.objects.filter(
                        role__in=role_list, menu_button__menu=menu_id
                    ).values(btn_id=F('menu_button__id'), name=F('menu_button__name'))
                return DetailResponse(data=queryset)
        return ErrorResponse(msg="参数错误")

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
                    role_queryset = RoleMenuButtonPermission.objects.filter(
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
        if is_superuser:
            queryset = Dept.objects.values('id', 'name', 'parent')
        else:
            if not params:
                return ErrorResponse(msg="参数错误")
            menu_button = params.get('menu_button')
            if menu_button is None:
                return ErrorResponse(msg="参数错误")
            role_list = request.user.role.values_list('id', flat=True)
            queryset = RoleMenuButtonPermission.objects.filter(role__in=role_list, menu_button=None).values(
                dept_id=F('dept__id'),
                name=F('dept__name'),
                parent=F('dept__parent')
            )
        return DetailResponse(data=queryset)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def menu_to_button(self, request):
        """
        根据所选择菜单获取已配置的按钮/接口权限:角色授权页面使用
        :param request:
        :return:
        """
        params = request.query_params
        menu_id = params.get('menu', None)
        if menu_id is None:
            return ErrorResponse(msg="未获取到参数")
        is_superuser = request.user.is_superuser
        if is_superuser:
            queryset = RoleMenuButtonPermission.objects.filter(menu_button__menu=menu_id).values(
                'id',
                'data_range',
                'menu_button',
                'menu_button__name',
                'menu_button__value'
            )
            return DetailResponse(data=queryset)
        else:
            if params:

                role_id = params.get('role', None)
                if role_id is None:
                    return ErrorResponse(msg="未获取到参数")
                queryset = RoleMenuButtonPermission.objects.filter(role=role_id, menu_button__menu=menu_id).values(
                    'id',
                    'data_range',
                    'menu_button',
                    'menu_button__name',
                    'menu_button__value'
                )
                return DetailResponse(data=queryset)
        return ErrorResponse(msg="未获取到参数")

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def role_to_menu(self, request):
        """
        获取角色对应的按钮权限
        :param request:
        :return:
        """
        params = request.query_params
        role_id = params.get('role', None)
        if role_id is None:
            return ErrorResponse(msg="未获取到参数")
        queryset = RoleMenuPermission.objects.filter(role_id=role_id).values_list('menu_id', flat=True).distinct()

        return DetailResponse(data=queryset)
