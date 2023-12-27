# -*- coding: utf-8 -*-
import os

from rest_framework import serializers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
import django

django.setup()
from dvadmin.system.models import (
    Role, Dept, Users, Menu, MenuButton,
    ApiWhiteList, Dictionary, SystemConfig,
    RoleMenuPermission, RoleMenuButtonPermission, MenuField
)
from dvadmin.utils.serializers import CustomModelSerializer


class UsersInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        role_key = self.initial_data.get('role_key', [])
        role_ids = Role.objects.filter(key__in=role_key).values_list('id', flat=True)
        instance.role.set(role_ids)
        dept_key = self.initial_data.get('dept_key', None)
        dept_id = Dept.objects.filter(key=dept_key).first()
        instance.dept = dept_id
        instance.save()
        return instance

    class Meta:
        model = Users
        fields = ["username", "email", 'mobile', 'avatar', "name", 'gender', 'user_type', "dept", 'user_type',
                  'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'creator', 'dept_belong_id',
                  'password', 'last_login', 'is_superuser']
        read_only_fields = ['id']
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class MenuButtonInitSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = MenuButton
        fields = ['id', 'name', 'value', 'api', 'method', 'menu']
        read_only_fields = ["id"]


class MenuFieldInitSerializer(CustomModelSerializer):
    """
    初始化列权限-序列化器
    """

    class Meta:
        model = MenuField
        fields = ['id', 'menu', 'field_name', 'title', 'model']
        read_only_fields = ["id"]


class MenuInitSerializer(CustomModelSerializer):
    """
    递归深度获取数信息(用于生成初始化json文件)
    """
    name = serializers.CharField(required=False)
    children = serializers.SerializerMethodField()
    menu_button = serializers.SerializerMethodField()
    menu_field = serializers.SerializerMethodField()

    def get_children(self, obj: Menu):
        data = []
        instance = Menu.objects.filter(parent_id=obj.id)
        if instance:
            serializer = MenuInitSerializer(instance=instance, many=True)
            data = serializer.data
        return data

    def get_menu_button(self, obj: Menu):
        data = []
        instance = obj.menuPermission.order_by('method')
        if instance:
            data = list(instance.values('name', 'value', 'api', 'method'))
        return data

    def get_menu_field(self, obj: Menu):
        data = []
        instance = obj.menufield_set.order_by('field_name')
        if instance:
            data = list(instance.values('field_name', 'title', 'model'))
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        children = self.initial_data.get('children')
        menu_button = self.initial_data.get('menu_button')
        menu_field = self.initial_data.get('menu_field')
        # 菜单表
        if children:
            for menu_data in children:
                menu_data['parent'] = instance.id
                filter_data = {
                    "name": menu_data['name'],
                    "web_path": menu_data['web_path'],
                    "component": menu_data['component'],
                    "component_name": menu_data['component_name'],
                }
                instance_obj = Menu.objects.filter(**filter_data).first()
                if instance_obj and not self.initial_data.get('reset'):
                    continue
                serializer = MenuInitSerializer(instance_obj, data=menu_data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        # 菜单按钮
        if menu_button:
            for menu_button_data in menu_button:
                menu_button_data['menu'] = instance.id
                filter_data = {
                    "menu": menu_button_data['menu'],
                    "value": menu_button_data['value']
                }
                instance_obj = MenuButton.objects.filter(**filter_data).first()
                serializer = MenuButtonInitSerializer(instance_obj, data=menu_button_data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        # 列权限
        if menu_field:
            for field_data in menu_field:
                field_data['menu'] = instance.id
                filter_data = {
                    'menu': field_data['menu'],
                    'field_name': field_data['field_name'],
                    'model': field_data['model']
                }
                instance_obj = MenuField.objects.filter(**filter_data).first()
                serializer = MenuFieldInitSerializer(instance_obj, data=field_data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return instance

    class Meta:
        model = Menu
        fields = ['name', 'icon', 'sort', 'is_link', 'is_catalog', 'web_path', 'component', 'component_name', 'status',
                  'cache', 'visible', 'parent', 'children', 'menu_button', 'menu_field', 'creator', 'dept_belong_id']
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }
        read_only_fields = ['id', 'children']


class RoleInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """

    class Meta:
        model = Role
        fields = ['name', 'key', 'sort', 'status',
                  'creator', 'dept_belong_id']
        read_only_fields = ["id"]
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class RoleMenuInitSerializer(CustomModelSerializer):
    """
    初始化角色菜单(用于生成初始化json文件)
    """
    role_key = serializers.CharField(max_length=100, required=True)
    menu_component_name = serializers.CharField(max_length=100, required=True)

    def create(self, validated_data):
        init_data = self.initial_data
        validated_data.pop('menu_component_name')
        validated_data.pop('role_key')
        role_id = Role.objects.filter(key=init_data['role_key']).first()
        menu_id = Menu.objects.filter(component_name=init_data['menu_component_name']).first()
        validated_data['role'] = role_id
        validated_data['menu'] = menu_id
        return super().create(validated_data)

    class Meta:
        model = RoleMenuPermission
        fields = ['role_key', 'menu_component_name', 'creator', 'dept_belong_id']
        read_only_fields = ["id"]
        extra_kwargs = {
            'role': {'required': False},
            'menu': {'required': False},
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class RoleMenuButtonInitSerializer(CustomModelSerializer):
    """
    初始化角色菜单按钮(用于生成初始化json文件)
    """
    role_key = serializers.CharField(max_length=100, required=True)
    menu_button_value = serializers.CharField(max_length=100, required=True)
    data_range = serializers.CharField(max_length=100, required=False)

    def create(self, validated_data):
        init_data = self.initial_data
        validated_data.pop('menu_button_value')
        validated_data.pop('role_key')
        role_id = Role.objects.filter(key=init_data['role_key']).first()
        menu_button_id = MenuButton.objects.filter(value=init_data['menu_button_value']).first()
        validated_data['role'] = role_id
        validated_data['menu_button'] = menu_button_id
        instance = super().create(validated_data)
        instance.dept.set([])
        return instance

    class Meta:
        model = RoleMenuButtonPermission
        fields = ['role_key', 'menu_button_value', 'data_range', 'dept', 'creator', 'dept_belong_id']
        read_only_fields = ["id"]
        extra_kwargs = {
            'role': {'required': False},
            'menu': {'required': False},
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class ApiWhiteListInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """

    class Meta:
        model = ApiWhiteList
        fields = ['url', 'method', 'enable_datasource', 'creator', 'dept_belong_id']
        read_only_fields = ["id"]
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class DeptInitSerializer(CustomModelSerializer):
    """
    递归深度获取数信息(用于生成初始化json文件)
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj: Dept):
        data = []
        instance = Dept.objects.filter(parent_id=obj.id)
        if instance:
            serializer = DeptInitSerializer(instance=instance, many=True)
            data = serializer.data
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        children = self.initial_data.get('children')
        if children:
            for menu_data in children:
                menu_data['parent'] = instance.id
                filter_data = {
                    "name": menu_data['name'],
                    "parent": menu_data['parent'],
                    "key": menu_data['key']
                }
                instance_obj = Dept.objects.filter(**filter_data).first()
                if instance_obj and not self.initial_data.get('reset'):
                    continue
                serializer = DeptInitSerializer(instance_obj, data=menu_data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance

    class Meta:
        model = Dept
        fields = ['name', 'sort', 'owner', 'phone', 'email', 'status', 'parent', 'creator', 'dept_belong_id',
                  'children', 'key']
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }
        read_only_fields = ['id', 'children']


class DictionaryInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj: Dictionary):
        data = []
        instance = Dictionary.objects.filter(parent_id=obj.id)
        if instance:
            serializer = DictionaryInitSerializer(instance=instance, many=True)
            data = serializer.data
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        children = self.initial_data.get('children')
        # 菜单表
        if children:
            for data in children:
                data['parent'] = instance.id
                filter_data = {
                    "value": data['value'],
                    "parent": data['parent']
                }
                instance_obj = Dictionary.objects.filter(**filter_data).first()
                if instance_obj and not self.initial_data.get('reset'):
                    continue
                serializer = DictionaryInitSerializer(instance_obj, data=data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return instance

    class Meta:
        model = Dictionary
        fields = ['label', 'value', 'parent', 'type', 'color', 'is_value', 'status', 'sort', 'remark', 'creator',
                  'dept_belong_id', 'children']
        read_only_fields = ["id"]
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }


class SystemConfigInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj: SystemConfig):
        data = []
        instance = SystemConfig.objects.filter(parent_id=obj.id)
        if instance:
            serializer = SystemConfigInitSerializer(instance=instance, many=True)
            data = serializer.data
        return data

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        children = self.initial_data.get('children')
        # 菜单表
        if children:
            for data in children:
                data['parent'] = instance.id
                filter_data = {
                    "key": data['key'],
                    "parent": data['parent']
                }
                instance_obj = SystemConfig.objects.filter(**filter_data).first()
                if instance_obj and not self.initial_data.get('reset'):
                    continue
                serializer = SystemConfigInitSerializer(instance_obj, data=data, request=self.request)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return instance

    class Meta:
        model = SystemConfig
        fields = ['parent', 'title', 'key', 'value', 'sort', 'status', 'data_options', 'form_item_type', 'rule',
                  'placeholder', 'setting', 'creator', 'dept_belong_id', 'children']
        read_only_fields = ["id"]
        extra_kwargs = {
            'creator': {'write_only': True},
            'dept_belong_id': {'write_only': True}
        }
