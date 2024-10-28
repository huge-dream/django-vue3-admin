# -*- coding: utf-8 -*-

from itertools import groupby

from django.db.models import F
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import FieldPermission, MenuField
from dvadmin.utils.json_response import DetailResponse
from dvadmin.utils.models import get_custom_app_models


class FieldPermissionMixin:
    @action(methods=['get'], detail=False,permission_classes=[IsAuthenticated])
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
        if user.is_superuser==1:
            data = MenuField.objects.filter( model=model['model']).values('field_name')
            for item in data:
                item['is_create'] = True
                item['is_query'] = True
                item['is_update'] = True
        else:
            roles = request.user.role.values_list('id', flat=True)
            data= FieldPermission.objects.filter(
                 field__model=model['model'],role__in=roles
            ).values( 'is_create', 'is_query', 'is_update',field_name=F('field__field_name'))
            
            """
            合并权限

            这段代码首先根据 field_name 对列表进行排序，
            然后使用 groupby 按 field_name 进行分组。
            对于每个组，它创建一个新的字典 merged，
            并遍历组中的每个字典，将布尔值字段使用逻辑或（or）操作符进行合并（如果 merged 中还没有该字段，则默认为 False），
            其他字段（如 field_name）则直接取组的关键字（即 key）
            """

            # 使用field_name对列表进行分组, # groupby 需要先对列表进行排序，因为它只能对连续相同的元素进行分组。
            grouped = groupby(sorted(list(data), key=lambda x: x['field_name']), key=lambda x: x['field_name'])

            data = []

            # 遍历分组，合并权限
            for key, group in grouped:

                # 初始化一个空字典来存储合并后的结果
                merged = {}
                for item in group:
                    # 合并权限， True值优先
                    merged['is_create'] = merged.get('is_create', False) or item['is_create']
                    merged['is_query'] = merged.get('is_query', False) or item['is_query']
                    merged['is_update'] = merged.get('is_update', False) or item['is_update']
                    merged['field_name'] = key

                data.append(merged)

        return DetailResponse(data=data)