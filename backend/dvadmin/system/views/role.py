# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/3 003 0:30
@Remark: 角色管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import Role, Menu, MenuButton, Dept, Users
from dvadmin.system.views.dept import DeptSerializer
from dvadmin.system.views.menu import MenuSerializer
from dvadmin.system.views.menu_button import MenuButtonSerializer
from dvadmin.utils.crud_mixin import FastCrudMixin
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.json_response import SuccessResponse, DetailResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomUniqueValidator
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.permission import CustomPermission


class RoleSerializer(CustomModelSerializer):
    """
    角色-序列化器
    """
    users = serializers.SerializerMethodField()

    @staticmethod
    def get_users(instance):
        users = instance.users_set.exclude(id=1).values('id', 'name', 'dept__name')
        return users

    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ["id"]


class RoleCreateUpdateSerializer(CustomModelSerializer):
    """
    角色管理 创建/更新时的列化器
    """
    menu = MenuSerializer(many=True, read_only=True)
    dept = DeptSerializer(many=True, read_only=True)
    permission = MenuButtonSerializer(many=True, read_only=True)
    key = serializers.CharField(max_length=50,
                                validators=[CustomUniqueValidator(queryset=Role.objects.all(), message="权限字符必须唯一")])
    name = serializers.CharField(max_length=50, validators=[CustomUniqueValidator(queryset=Role.objects.all())])

    def validate(self, attrs: dict):
        return super().validate(attrs)

    # def save(self, **kwargs):
    #     is_superuser = self.request.user.is_superuser
    #     if not is_superuser:
    #         self.validated_data.pop('admin')
    #     data = super().save(**kwargs)
    #     return data

    class Meta:
        model = Role
        fields = '__all__'


class MenuPermissionSerializer(CustomModelSerializer):
    """
    菜单的按钮权限
    """
    menuPermission = serializers.SerializerMethodField()

    def get_menuPermission(self, instance):
        is_superuser = self.request.user.is_superuser
        if is_superuser:
            queryset = MenuButton.objects.filter(menu__id=instance.id)
        else:
            menu_permission_id_list = self.request.user.role.values_list('permission', flat=True)
            queryset = MenuButton.objects.filter(id__in=menu_permission_id_list, menu__id=instance.id)
        serializer = MenuButtonSerializer(queryset, many=True, read_only=True)
        return serializer.data

    class Meta:
        model = Menu
        fields = ['id', 'parent', 'name', 'menuPermission']


class MenuButtonPermissionSerializer(CustomModelSerializer):
    """
    菜单和按钮权限
    """
    isCheck = serializers.SerializerMethodField()

    def get_isCheck(self, instance):
        is_superuser = self.request.user.is_superuser
        if is_superuser:
            return True
        else:
            return MenuButton.objects.filter(
                menu__id=instance.id,
                role__id__in=self.request.user.role.values_list('id', flat=True),
            ).exists()

    class Meta:
        model = Menu
        fields = '__all__'


class RoleViewSet(CustomModelViewSet, FastCrudMixin,FieldPermissionMixin):
    """
    角色管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    create_serializer_class = RoleCreateUpdateSerializer
    update_serializer_class = RoleCreateUpdateSerializer
    search_fields = ['name', 'key']

    @action(methods=['PUT'], detail=True, permission_classes=[IsAuthenticated])
    def set_role_users(self, request, pk):
        """
        设置 角色-用户
        :param request:
        :return:
        """
        data = request.data
        direction = data.get('direction')
        movedKeys = data.get('movedKeys')
        role = Role.objects.get(pk=pk)
        if direction == "left":
            # left : 移除用户权限
            role.users_set.remove(*movedKeys)
        else:
            # right : 添加用户权限
            role.users_set.add(*movedKeys)
        serializer = RoleSerializer(role)
        return DetailResponse(data=serializer.data, msg="更新成功")

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated, CustomPermission])
    def get_role_users(self, request):
        """
        获取角色已授权、未授权的用户
        已授权的用户:1
        未授权的用户:0
        """
        role_id = request.query_params.get('role_id', None)

        if not role_id:
            return ErrorResponse(msg="请选择角色")

        if request.query_params.get('authorized', 0) == "1":
            queryset = Users.objects.filter(role__id=role_id).exclude(is_superuser=True)
        else:
            queryset = Users.objects.exclude(role__id=role_id).exclude(is_superuser=True)

        if name := request.query_params.get('name', None):
            queryset = queryset.filter(name__icontains=name)

        if dept := request.query_params.get('dept', None):
            queryset = queryset.filter(dept=dept)

        page = self.paginate_queryset(queryset.values('id', 'name', 'dept__name'))
        if page is not None:
            return self.get_paginated_response(page)

        return SuccessResponse(data=page)

    @action(methods=['DELETE'], detail=True, permission_classes=[IsAuthenticated, CustomPermission])
    def remove_role_user(self, request, pk):
        """
        角色-删除用户
        """
        user_id = request.data.get('user_id', None)

        if not user_id:
            return ErrorResponse(msg="请选择用户")

        role = self.get_object()
        role.users_set.remove(*user_id)

        return SuccessResponse(msg="删除成功")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated, CustomPermission])
    def add_role_users(self, request, pk):
        """
        角色-添加用户
        """
        users_id = request.data.get('users_id', None)

        if not users_id:
            return ErrorResponse(msg="请选择用户")

        role = self.get_object()
        role.users_set.add(*users_id)

        return DetailResponse(msg="添加成功")
