# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import MiscProcMaterial
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class MiscPartSerializer(CustomModelSerializer):
    """杂采料号信息-序列化器"""

    class Meta:
        model = MiscProcMaterial
        fields = "__all__"
        read_only_fields = ["id"]


class MiscPartCreateUpdateSerializer(CustomModelSerializer):
    """杂采料号信息 创建/更新"""

    partid_name = serializers.CharField(max_length=50)
    specification = serializers.CharField(max_length=50)
    unit = serializers.CharField(max_length=50)

    class Meta:
        model = MiscProcMaterial
        fields = "__all__"


class MiscPartViewSet(CustomModelViewSet):
    """杂采料号信息管理接口"""

    queryset = MiscProcMaterial.objects.all()
    serializer_class = MiscPartSerializer
    create_serializer_class = MiscPartCreateUpdateSerializer
    update_serializer_class = MiscPartCreateUpdateSerializer
    search_fields = ["partid", "partid_name", "company_code"]
    ordering = ["-create_datetime"]
