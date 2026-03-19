# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import Unit
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class UnitSerializer(CustomModelSerializer):
    """计量单位-序列化器"""

    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ["id"]


class UnitCreateUpdateSerializer(CustomModelSerializer):
    """计量单位 创建/更新"""

    unitname = serializers.CharField(max_length=50)
    unitcode = serializers.CharField(max_length=20, allow_blank=True, required=False)

    class Meta:
        model = Unit
        fields = "__all__"


class UnitViewSet(CustomModelViewSet):
    """计量单位管理接口"""

    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    create_serializer_class = UnitCreateUpdateSerializer
    update_serializer_class = UnitCreateUpdateSerializer
    search_fields = ["unitname", "unitcode"]
    ordering = ["-create_datetime"]
