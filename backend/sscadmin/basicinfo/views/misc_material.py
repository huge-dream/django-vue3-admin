# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import MiscProcurementMaterialInfo
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class MiscMaterialSerializer(CustomModelSerializer):
    """杂采材料信息-序列化器"""

    class Meta:
        model = MiscProcurementMaterialInfo
        fields = "__all__"
        read_only_fields = ["id"]


class MiscMaterialCreateUpdateSerializer(CustomModelSerializer):
    """杂采材料信息 创建/更新"""

    materialtype = serializers.CharField(max_length=50, required=False, allow_blank=True)
    factory = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = MiscProcurementMaterialInfo
        fields = "__all__"


class MiscMaterialViewSet(CustomModelViewSet):
    """杂采材料信息管理接口"""

    queryset = MiscProcurementMaterialInfo.objects.all()
    serializer_class = MiscMaterialSerializer
    create_serializer_class = MiscMaterialCreateUpdateSerializer
    update_serializer_class = MiscMaterialCreateUpdateSerializer
    search_fields = ["materialtype", "factory"]
    ordering = ["-create_datetime"]
