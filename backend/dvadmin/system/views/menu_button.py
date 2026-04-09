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
        批量创建菜单"增删改查查"权限
        创建的数据来源于菜单，需要规范创建菜单参数
        value：菜单的component_name:method
        api:菜单的web_path增加'/api'前缀，并根据method增加{id}
        """
        menu_obj = Menu.objects.filter(id=request.data['menu']).first()
        if not menu_obj:
            return DetailResponse(data={}, msg="菜单不存在", code=4000)
        if not menu_obj.component_name:
            return DetailResponse(data={}, msg="该菜单未设置组件名称(component_name)，无法自动生成权限", code=4000)

        # 获取已存在的 value，避免唯一约束冲突
        existing_values = set(
            MenuButton.objects.filter(menu=menu_obj.id).values_list('value', flat=True)
        )

        result_list = [
            {'menu': menu_obj.id, 'name': '新增', 'name_en': 'Add', 'name_zh_tw': '新增', 'value': f'{menu_obj.component_name}:Create', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '删除', 'name_en': 'Delete', 'name_zh_tw': '刪除', 'value': f'{menu_obj.component_name}:Delete', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 3},
            {'menu': menu_obj.id, 'name': '编辑', 'name_en': 'Edit', 'name_zh_tw': '編輯', 'value': f'{menu_obj.component_name}:Update', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 2},
            {'menu': menu_obj.id, 'name': '查询', 'name_en': 'Search', 'name_zh_tw': '查詢', 'value': f'{menu_obj.component_name}:Search', 'api': f'/api/{menu_obj.component_name}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '详情', 'name_en': 'Detail', 'name_zh_tw': '詳情', 'value': f'{menu_obj.component_name}:Retrieve', 'api': f'/api/{menu_obj.component_name}/{{id}}/', 'method': 0},
            {'menu': menu_obj.id, 'name': '复制', 'name_en': 'Copy', 'name_zh_tw': '複製', 'value': f'{menu_obj.component_name}:Copy', 'api': f'/api/{menu_obj.component_name}/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导入', 'name_en': 'Import', 'name_zh_tw': '導入', 'value': f'{menu_obj.component_name}:Import', 'api': f'/api/{menu_obj.component_name}/import_data/', 'method': 1},
            {'menu': menu_obj.id, 'name': '导出', 'name_en': 'Export', 'name_zh_tw': '導出', 'value': f'{menu_obj.component_name}:Export', 'api': f'/api/{menu_obj.component_name}/export_data/', 'method': 1},
        ]

        # 只保留不存在的新记录
        to_create = [r for r in result_list if r['value'] not in existing_values]
        skipped = len(result_list) - len(to_create)

        if to_create:
            serializer = self.get_serializer(data=to_create, many=True)
            serializer.is_valid(raise_exception=True)
            MenuButton.objects.bulk_create(
                [MenuButton(**item) for item in to_create],
                ignore_conflicts=True
            )

        return SuccessResponse(data={'created': len(to_create), 'skipped': skipped}, msg=f"批量创建成功 {len(to_create)} 项，跳过 {skipped} 项（已存在）")

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def scan_get_apps(self, request):
        """
        获取可扫描的 Django App 列表
        基于 Django app registry，返回 dvadmin.* 和 apps.* 下有 views 子模块的 app
        """
        import importlib
        from django.apps import apps

        custom_apps = []
        seen = set()
        for app_config in apps.get_app_configs():
            name = app_config.name  # e.g. 'dvadmin.system' or 'apps.pisadmin.basicinfo'
            # 支持 dvadmin.* 和 apps.* 两个命名空间
            if not (name.startswith('dvadmin.') or name.startswith('apps.')):
                continue
            if name in seen:
                continue
            seen.add(name)

            # 取 short name: 'dvadmin.system' -> 'system', 'apps.pisadmin.basicinfo' -> 'pisadmin.basicinfo'
            short_name = name.split('.', 1)[1]
            if short_name in ('utils',):
                continue

            # 验证是否有 views 子模块
            try:
                importlib.import_module(f'{name}.views')
            except ModuleNotFoundError:
                continue

            custom_apps.append(short_name)

        return DetailResponse(data=sorted(custom_apps))

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def scan_viewset(self, request):
        """
        扫描指定 app 下所有 ViewSet，返回接口预览数据
        请求体: {"app": "system"}
        """
        import importlib
        import pkgutil
        from pathlib import Path
        from rest_framework.viewsets import GenericViewSet
        from rest_framework.decorators import action
        from dvadmin.system.models import MenuButton

        app_name = request.data.get('app')
        if not app_name:
            return DetailResponse(data=[], msg="app 参数必填")

        # 根据 app_name 格式确定正确的命名空间前缀
        # app_name 为 'system' -> dvadmin.system
        # app_name 为 'pisadmin.basicinfo' -> apps.pisadmin.basicinfo
        if '.' in app_name:
            full_app_name = f'apps.{app_name}'
        else:
            full_app_name = f'dvadmin.{app_name}'
        result = []

        try:
            views_pkg = importlib.import_module(f'{full_app_name}.views')
        except ModuleNotFoundError:
            return DetailResponse(data=[], msg=f"App '{app_name}' 下未找到 views 模块")

        views_pkg_path = Path(views_pkg.__file__).parent
        view_modules = []
        for importer, modname, ispkg in pkgutil.iter_modules([str(views_pkg_path)]):
            if modname not in ('__init__',):
                view_modules.append(f'{full_app_name}.views.{modname}')

        existing_values = set(MenuButton.objects.values_list('value', flat=True))
        seen_viewset_ids = set()  # 去重：同一 ViewSet 类可能被多个子模块引用

        # 标准 CRUD action 映射
        standard_actions = {
            'list': ('GET', 0, '列表查询'),
            'create': ('POST', 1, '新增'),
            'retrieve': ('GET', 0, '详情查询'),
            'update': ('PUT', 2, '更新'),
            'partial_update': ('PATCH', 2, '部分更新'),
            'destroy': ('DELETE', 3, '删除'),
        }

        import inspect
        for module_name in view_modules:
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue

            for attr_name in dir(module):
                cls = getattr(module, attr_name)
                if not isinstance(cls, type):
                    continue
                if not issubclass(cls, GenericViewSet):
                    continue
                if cls is GenericViewSet:
                    continue
                # 去重
                if id(cls) in seen_viewset_ids:
                    continue
                seen_viewset_ids.add(id(cls))

                viewset_name = cls.__name__
                model_name = viewset_name.removesuffix('ViewSet') if viewset_name.endswith('ViewSet') else viewset_name

                viewset_verbose_name = viewset_name
                if cls.__doc__:
                    lines = cls.__doc__.strip().split('\n')
                    viewset_verbose_name = lines[0].strip()

                found_actions = {}

                # 先加入标准 CRUD action
                found_actions.update(standard_actions)

                # 再找自定义 @action
                import inspect
                for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                    if hasattr(method, 'mapping'):
                        # 这是 @action 装饰的方法
                        http_method = list(method.mapping.keys())[0].upper()
                        method_map = {'GET': 0, 'POST': 1, 'PUT': 2, 'PATCH': 2, 'DELETE': 3}
                        method_int = method_map.get(http_method, 0)
                        action_doc = (method.__doc__ or '').strip().split('\n')[0] if method.__doc__ else name
                        found_actions[name] = (http_method, method_int, action_doc)

                # 获取该 ViewSet 对应的 URL 前缀
                prefix = viewset_name.lower().replace('viewset', '')
                lookup = 'id'
                if hasattr(cls, 'lookup_field'):
                    lookup = getattr(cls, 'lookup_field') or 'id'

                buttons = []
                for action_name, (http_method, method_int, name) in found_actions.items():
                    action_title = action_name.replace('_', ' ').title().replace(' ', '')
                    value = f"{app_name}:{model_name}:{action_title}"

                    # 将 app_name 中的点转为斜杠，生成正确的 URL 路径
                    # pisadmin.basicinfo -> /api/pisadmin/basicinfo/
                    api_path = app_name.replace('.', '/')

                    if action_name in ('list', 'create'):
                        path = f"/api/{api_path}/{prefix}/"
                    elif action_name in ('retrieve', 'update', 'partial_update', 'destroy'):
                        path = f"/api/{api_path}/{prefix}/{{{lookup}}}/"
                    else:
                        path = f"/api/{api_path}/{prefix}/{action_name}/"

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