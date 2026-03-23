# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.pisadmin.basicinfo.models import Company
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class CompanySerializer(CustomModelSerializer):
    """公司信息-序列化器"""

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id"]


class CompanyCreateUpdateSerializer(CustomModelSerializer):
    """公司信息 创建/更新"""

    company_code = serializers.CharField(max_length=20)
    company_name = serializers.CharField(max_length=100, allow_blank=True, required=False)
    company_short_name = serializers.CharField(max_length=50, allow_blank=True, required=False)
    company_address = serializers.CharField(max_length=500, allow_blank=True, required=False)
    createuser = serializers.CharField(max_length=20, allow_blank=True, required=False)
    updateuser = serializers.CharField(max_length=20, allow_blank=True, required=False)

    class Meta:
        model = Company
        fields = "__all__"


class CompanyViewSet(CustomModelViewSet):
    """公司信息管理接口"""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    create_serializer_class = CompanyCreateUpdateSerializer
    update_serializer_class = CompanyCreateUpdateSerializer
    search_fields = ["company_code", "company_name", "company_short_name"]
    ordering = ["-create_datetime"]

    def perform_create(self, serializer):
        # 自动记录创建人
        username = getattr(getattr(self.request, "user", None), "username", None)
        serializer.save(createuser=username)

    def perform_update(self, serializer):
        # 自动记录更新人
        username = getattr(getattr(self.request, "user", None), "username", None)
        serializer.save(updateuser=username)
