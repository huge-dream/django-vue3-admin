# -*- coding: utf-8 -*-

from django.db.models import F
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import FieldPermission, MenuField
from dvadmin.utils.json_response import DetailResponse
from dvadmin.utils.models import get_custom_app_models


class FieldPermissionMixin:
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def field_permission(self, request):
        """
        获取字段权限
        """
        finded = False
        for model in get_custom_app_models():
            if model['object'] is self.serializer_class.Meta.model:
                finded = True
                break
            if finded:
                break
        if finded is False:
            return []
        user = request.user
        # 创建一个默认字典来存储最终的结果
        result = {}
        if user.is_superuser == 1:
            data = MenuField.objects.filter(model=model['model']).values('field_name')
            for item in data:
                field_name = item.pop('field_name')
                result[field_name] = {}
                result[field_name]['is_create'] = True
                result[field_name]['is_query'] = True
                result[field_name]['is_update'] = True
            else:
                roles = request.user.role.values_list('id', flat=True)
                data = FieldPermission.objects.filter(
                    field__model=model['model'], role__in=roles
                ).values('is_create', 'is_query', 'is_update', field_name=F('field__field_name'))
            """
            合并权限
            """
            # 遍历原始数据并填充结果字典
            for item in data:
                field_name = item.pop('field_name')
                for key, value in item.items():
                    if field_name in result:
                        if value:
                            result[field_name][key] = True
                    else:
                        result[field_name] = {}
                        result[field_name][key] = value
        return DetailResponse(data=result)
