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
        fields = ['id', 'name', 'name_en', 'name_zh_tw', 'value', 'api', 'method', 'menu']
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
            {'menu': menu_obj.id, 'name': '新增', 'name_en': 'Add', 'name_zh_tw': '新增', 'value': f'{menu_obj.component_name}:Create', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '删除', 'name_en': 'Delete', 'name_zh_tw': '刪除', 'value': f'{menu_obj.component_name}:Delete', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 3},
            {'menu': menu_obj.id, 'name': '编辑', 'name_en': 'Edit', 'name_zh_tw': '編輯', 'value': f'{menu_obj.component_name}:Update', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 2},
            {'menu': menu_obj.id, 'name': '查询', 'name_en': 'Search', 'name_zh_tw': '查詢', 'value': f'{menu_obj.component_name}:Search', 'api': f'/api/{menu_obj.component_name}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '详情', 'name_en': 'Detail', 'name_zh_tw': '詳情', 'value': f'{menu_obj.component_name}:Retrieve', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '复制', 'name_en': 'Copy', 'name_zh_tw': '複製', 'value': f'{menu_obj.component_name}:Copy', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导入', 'name_en': 'Import', 'name_zh_tw': '導入', 'value': f'{menu_obj.component_name}:Import', 'api': f'/api/{menu_obj.component_name}/import_data/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导出', 'name_en': 'Export', 'name_zh_tw': '導出', 'value': f'{menu_obj.component_name}:Export', 'api': f'/api/{menu_obj.component_name}/export_data/', 'method': 1},]
        serializer = self.get_serializer(data=result_list, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, msg=_("Batch creation successful"))

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def scan_get_apps(self, request):
        """
        获取可扫描的 Django App 列表
        仅返回 dvadmin 下的自定义 app（排除框架内置 app）
        """
        from django.apps import apps

        # 获取 dvadmin 下所有已注册的自定义 app
        custom_apps = []
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('dvadmin.') and app_config.name != 'dvadmin':
                # 排除 system app 本身（避免循环）
                if app_config.name != 'dvadmin.system':
                    custom_apps.append(app_config.name.split('.')[-1])

        return DetailResponse(data=sorted(custom_apps))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def scan_viewset(self, request):
        """
        扫描指定 app 下所有 ViewSet，返回接口预览数据
        请求体: {"app": "system"}
        """
        import importlib
        from rest_framework.routers import SimpleRouter
        from rest_framework.viewsets import GenericViewSet
        from dvadmin.system.models import MenuButton

        app_name = request.data.get('app')
        if not app_name:
            return DetailResponse(data=[], msg="app 参数必填")

        full_app_name = f'dvadmin.{app_name}'
        result = []

        try:
            # 动态导入 app 下的 views 模块
            views_module = importlib.import_module(f'{full_app_name}.views')
        except ModuleNotFoundError:
            return DetailResponse(data=[], msg=f"App '{app_name}' 下未找到 views 模块")

        # 获取已存在的 value 集合
        existing_values = set(MenuButton.objects.values_list('value', flat=True))

        # 遍历 app 下所有 ViewSet 类
        for attr_name in dir(views_module):
            cls = getattr(views_module, attr_name)
            if not isinstance(cls, type):
                continue
            if not issubclass(cls, GenericViewSet):
                continue
            if cls is GenericViewSet:
                continue

            # 提取 ViewSet 名称
            viewset_name = cls.__name__  # 如 "MenuViewSet"
            if viewset_name.endswith('ViewSet'):
                model_name = viewset_name[:-8]  # "Menu"
            else:
                model_name = viewset_name

            # 尝试从 docstring 获取中文名称
            viewset_verbose_name = viewset_name
            if cls.__doc__:
                lines = cls.__doc__.strip().split('\n')
                viewset_verbose_name = lines[0].strip()

            # 构建该 ViewSet 的 router 来获取所有 action
            router_prefix = viewset_name.lower().replace('viewset', '')
            router = SimpleRouter()
            try:
                router.register(router_prefix, cls, basename=router_prefix)
            except Exception:
                continue

            buttons = []
            for prefix, viewset_instance, actions in router.registry:
                for action_name, method in actions.items():
                    # 获取 HTTP 方法
                    http_method = method.upper()  # 如 "GET", "POST"

                # 排除基类（名字含 Custom/Base/Generic）
                viewset_name = cls.__name__
                if any(viewset_name.startswith(prefix) for prefix in ('Custom', 'Base', 'Generic', 'Abstract')):
                    continue
                model_name = viewset_name.removesuffix('ViewSet') if viewset_name.endswith('ViewSet') else viewset_name

                    # 获取 action 名称（驼峰转首字母大写）
                    action_title = action_name.replace('_', ' ').title().replace(' ', '')
                    value = f"{app_name}:{model_name}:{action_title}"

                    # 获取 docstring 作为 name
                    action_method = getattr(viewset_instance, action_name, None)
                    if action_method and hasattr(action_method, '__doc__') and action_method.__doc__:
                        name_lines = action_method.__doc__.strip().split('\n')
                        name = name_lines[0].strip()
                    else:
                        # 固定规则
                        name_map = {
                            'List': '列表查询', 'Retrieve': '详情查询', 'Create': '新增',
                            'Update': '更新', 'Destroy': '删除', 'Partialupdate': '部分更新',
                        }
                        name = name_map.get(action_title, action_title)

                    # 生成接口路径
                    lookup = 'id'
                    if hasattr(viewset_instance, 'lookup_field'):
                        lookup = getattr(viewset_instance, 'lookup_field') or 'id'
                    if action_name in ('list', 'create'):
                        path = f"/api/{app_name}/{prefix}/"
                    elif action_name in ('retrieve', 'update', 'partial_update', 'destroy'):
                        path = f"/api/{app_name}/{prefix}/{{{lookup}}}/"
                    else:
                        # custom action
                        path = f"/api/{app_name}/{prefix}/{action_name}/"

                    buttons.append({
                        'path': path,
                        'method': http_method,
                        'action': action_name,
                        'name': name,
                        'value': value,
                        'is_existing': value in existing_values,
                        'method_int': method_int,
                    })

            if buttons:
                result.append({
                    'viewset': viewset_name,
                    'viewset_verbose_name': viewset_verbose_name,
                    'buttons': buttons,
                })

        return DetailResponse(data=result)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def scan_batch_create(self, request):
        """
        批量创建 MenuButton
        请求体: {"menu_id": 12, "buttons": [...]}
        """
        from dvadmin.system.models import MenuButton

        menu_id = request.data.get('menu_id')
        buttons = request.data.get('buttons', [])

        if not menu_id:
            return DetailResponse(data={}, msg="menu_id 参数必填", code=4000)
        if not buttons:
            return DetailResponse(data={}, msg="buttons 不能为空", code=4000)

        created_count = 0
        skipped_count = 0

        # 获取已存在的 value
        existing_values = set(MenuButton.objects.filter(menu_id=menu_id).values_list('value', flat=True))

        objects_to_create = []
        for btn in buttons:
            value = btn.get('value')
            if value in existing_values:
                skipped_count += 1
                continue

            method_int = btn.get('method_int', 0)
            if isinstance(btn.get('method'), str):
                method_map = {'GET': 0, 'POST': 1, 'PUT': 2, 'PATCH': 2, 'DELETE': 3}
                method_int = method_map.get(btn['method'].upper(), 0)

            objects_to_create.append(MenuButton(
                menu_id=menu_id,
                name=btn.get('name', ''),
                value=value,
                api=btn.get('path', ''),
                method=method_int,
            ))
            existing_values.add(value)

        if objects_to_create:
            MenuButton.objects.bulk_create(objects_to_create)
            created_count = len(objects_to_create)

        return DetailResponse(data={'count': created_count, 'skipped': skipped_count}, msg=f"已创建 {created_count} 项，跳过 {skipped_count} 项（已存在）")