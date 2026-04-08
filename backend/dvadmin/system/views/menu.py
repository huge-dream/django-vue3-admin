# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/1 001 22:38
@Remark: 菜单模块
"""
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.system.models import Menu, RoleMenuPermission
from dvadmin.system.views.menu_button import MenuButtonSerializer
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class MenuSerializer(CustomModelSerializer):
    """
    菜单表的简单序列化器
    """
    menuPermission = serializers.SerializerMethodField(read_only=True)
    hasChild = serializers.SerializerMethodField()

    def get_menuPermission(self, instance):
        queryset = instance.menuPermission.order_by('-name').values('id', 'name', 'value')
        # MenuButtonSerializer(instance.menuPermission.all(), many=True)
        if queryset:
            return queryset
        else:
            return None

    def get_hasChild(self, instance):
        hasChild = Menu.objects.filter(parent=instance.id)
        if hasChild:
            return True
        return False

    class Meta:
        model = Menu
        fields = "__all__"
        read_only_fields = ["id"]


class MenuCreateSerializer(CustomModelSerializer):
    """
    菜单表的创建序列化器
    """
    name = serializers.CharField(required=False)

    def create(self, validated_data):
        menu_obj = Menu.objects.filter(parent_id=validated_data.get('parent', None)).order_by('-sort').first()
        last_sort = menu_obj.sort if menu_obj else 0
        validated_data['sort'] = last_sort + 1
        return super().create(validated_data)

    class Meta:
        model = Menu
        fields = "__all__"
        read_only_fields = ["id"]


class WebRouterSerializer(CustomModelSerializer):
    """
    前端菜单路由的简单序列化器
    """
    path = serializers.CharField(source="web_path")
    title = serializers.CharField(source="name")

    class Meta:
        model = Menu
        fields = (
            'id', 'parent', 'icon', 'sort', 'path', 'name', 'title', 'is_link','link_url', 'is_catalog', 'web_path', 'component',
            'component_name', 'cache', 'visible','is_iframe','is_affix', 'status')
        read_only_fields = ["id"]


class MenuViewSet(CustomModelViewSet):
    """
    菜单管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    create_serializer_class = MenuCreateSerializer
    update_serializer_class = MenuCreateSerializer
    search_fields = ['name', 'status']
    filter_fields = ['parent', 'name', 'status', 'is_link', 'visible', 'cache', 'is_catalog']

    def list(self, request):
        """懒加载"""
        request.query_params._mutable = True
        params = request.query_params
        parent = params.get('parent', None)
        page = params.get('page', None)
        limit = params.get('limit', None)
        if page:
            del params['page']
        if limit:
            del params['limit']
        if params:
            if parent:
                queryset = self.queryset.filter(parent=parent)
            else:
                queryset = self.queryset.filter()
        else:
            queryset = self.queryset.filter(parent__isnull=True)
        queryset = self.filter_queryset(queryset)
        serializer = MenuSerializer(queryset, many=True, request=request)
        data = serializer.data
        return SuccessResponse(data=data)

    @action(methods=['GET'], detail=False, permission_classes=[])
    def web_router(self, request):
        """用于前端获取当前角色的路由"""
        user = request.user
        if user.is_superuser:
            queryset = self.queryset.filter(status=1).order_by("sort")
        else:
            role_list = user.role.values_list('id', flat=True)
            menu_list = RoleMenuPermission.objects.filter(role__in=role_list).values_list('menu_id', flat=True)
            queryset = Menu.objects.filter(id__in=menu_list).order_by("sort")
        serializer = WebRouterSerializer(queryset, many=True, request=request)
        data = serializer.data
        return SuccessResponse(data=data, total=len(data), msg="获取成功")

    @action(methods=['GET'], detail=False, permission_classes=[])
    def get_all_menu(self, request):
        """用于菜单管理获取所有的菜单"""
        user = request.user
        queryset = self.queryset.all()
        if not user.is_superuser:
            role_list = user.role.values_list('id', flat=True)
            menu_list = RoleMenuPermission.objects.filter(role__in=role_list).values_list('menu_id')
            queryset = Menu.objects.filter(id__in=menu_list)
        serializer = WebRouterSerializer(queryset, many=True, request=request)
        data = serializer.data
        return SuccessResponse(data=data, total=len(data), msg="获取成功")

    @action(methods=['POST'], detail=False, permission_classes=[])
    def move_up(self, request):
        """菜单上移"""
        menu_id = request.data.get('menu_id')
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return ErrorResponse(msg="菜单不存在")
        previous_menu = Menu.objects.filter(sort__lt=menu.sort, parent=menu.parent).order_by('-sort').first()
        if previous_menu:
            previous_menu.sort, menu.sort = menu.sort, previous_menu.sort
            previous_menu.save()
            menu.save()
        return SuccessResponse(data=[], msg="上移成功")

    @action(methods=['POST'], detail=False, permission_classes=[])
    def move_down(self, request):
        """菜单下移"""
        menu_id = request.data['menu_id']
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return ErrorResponse(msg="菜单不存在")
        next_menu = Menu.objects.filter(sort__gt=menu.sort, parent=menu.parent).order_by('sort').first()
        if next_menu:
            next_menu.sort, menu.sort = menu.sort, next_menu.sort
            next_menu.save()
            menu.save()
        return SuccessResponse(data=[], msg="下移成功")
