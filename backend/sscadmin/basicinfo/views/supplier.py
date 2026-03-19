# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import Supplier
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class SupplierSerializer(CustomModelSerializer):
    """供应商信息-序列化器"""

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ["id"]


class SupplierCreateUpdateSerializer(CustomModelSerializer):
    """供应商信息 创建/更新"""

    supplier_id = serializers.CharField(max_length=20)
    supplier_name = serializers.CharField(max_length=100)
    supplier_short_name = serializers.CharField(max_length=50)
    contact_person = serializers.CharField(max_length=20)
    contact_phone = serializers.CharField(max_length=20)
    contact_email = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=20)
    province = serializers.CharField(max_length=20)

    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierViewSet(CustomModelViewSet):
    """供应商信息管理接口"""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    create_serializer_class = SupplierCreateUpdateSerializer
    update_serializer_class = SupplierCreateUpdateSerializer
    search_fields = ["supplier_name", "supplier_short_name", "supplier_id", "company_code"]
    ordering = ["-create_datetime"]
