# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import MiscProcurementStationInfo
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class MiscStationSerializer(CustomModelSerializer):
    """杂采加工工站信息-序列化器"""

    class Meta:
        model = MiscProcurementStationInfo
        fields = "__all__"
        read_only_fields = ["id"]


class MiscStationCreateUpdateSerializer(CustomModelSerializer):
    """杂采加工工站信息 创建/更新"""

    stationname = serializers.CharField(max_length=50)
    stationcode = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_code = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = MiscProcurementStationInfo
        fields = "__all__"


class MiscStationViewSet(CustomModelViewSet):
    """杂采加工工站信息管理接口"""

    queryset = MiscProcurementStationInfo.objects.all()
    serializer_class = MiscStationSerializer
    create_serializer_class = MiscStationCreateUpdateSerializer
    update_serializer_class = MiscStationCreateUpdateSerializer
    search_fields = ["stationname", "stationcode", "company_code"]
    ordering = ["-create_datetime"]
