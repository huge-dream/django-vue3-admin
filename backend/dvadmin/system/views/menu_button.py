# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/3 003 0:30
@Remark: 菜单按钮管理
"""
from django.db.models import F
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import MenuButton, RoleMenuButtonPermission, Menu
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet




class MenuButtonSerializer(CustomModelSerializer):
    """
    菜单按钮-序列化器
    """

    class Meta:
        model = MenuButton
        fields = ['id', 'name', 'value', 'api', 'method','menu']
        read_only_fields = ["id"]




class MenuButtonCreateUpdateSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = MenuButton
        fields = "__all__"
        read_only_fields = ["id"]


class MenuButtonViewSet(CustomModelViewSet):
    """
    菜单按钮接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = MenuButton.objects.order_by('create_datetime')
    serializer_class = MenuButtonSerializer
    create_serializer_class = MenuButtonCreateUpdateSerializer
    update_serializer_class = MenuButtonCreateUpdateSerializer
    extra_filter_class = []

    def list(self, request, *args, **kwargs):
        """
        重写list方法
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset()).order_by('name')
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(serializer.data,msg="获取成功")

    @action(methods=['get'],detail=False,permission_classes=[IsAuthenticated])
    def menu_button_all_permission(self,request):
        """
        获取所有的按钮权限
        :param request:
        :return:
        """
        is_superuser = request.user.is_superuser
        if is_superuser:
            queryset = MenuButton.objects.values_list('value',flat=True)
        else:
            role_id = request.user.role.values_list('id', flat=True)
            queryset = RoleMenuButtonPermission.objects.filter(role__in=role_id).values_list('menu_button__value',flat=True).distinct()
        return DetailResponse(data=queryset)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def batch_create(self, request, *args, **kwargs):
        """
        批量创建菜单“增删改查查”权限
        创建的数据来源于菜单，需要规范创建菜单参数
        value：菜单的component_name:method
        api:菜单的web_path增加'/api'前缀，并根据method增加{id}
        """
        menu_obj = Menu.objects.filter(id=request.data['menu']).first()
        result_list = [
            {'menu': menu_obj.id, 'name': '新增', 'value': f'{menu_obj.component_name}:Create', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '删除', 'value': f'{menu_obj.component_name}:Delete', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 3},
            {'menu': menu_obj.id, 'name': '编辑', 'value': f'{menu_obj.component_name}:Update', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 2},
            {'menu': menu_obj.id, 'name': '查询', 'value': f'{menu_obj.component_name}:Search', 'api': f'/api/{menu_obj.component_name}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '详情', 'value': f'{menu_obj.component_name}:Retrieve', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '复制', 'value': f'{menu_obj.component_name}:Copy', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导入', 'value': f'{menu_obj.component_name}:Import', 'api': f'/api/{menu_obj.component_name}/import_data/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导出', 'value': f'{menu_obj.component_name}:Export', 'api': f'/api{menu_obj.component_name}/export_data/', 'method': 1},]
        serializer = self.get_serializer(data=result_list, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, msg="批量创建成功")