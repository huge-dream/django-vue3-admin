# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.pisadmin.basicinfo.models import Supplier, SupplierUser
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class SupplierUserSerializer(CustomModelSerializer):
    """供应商用户信息"""

    class Meta:
        model = SupplierUser
        fields = [f.name for f in SupplierUser._meta.concrete_fields]
        read_only_fields = ["id"]


class SupplierUserCreateUpdateSerializer(CustomModelSerializer):
    """供应商用户信息 创建/更新"""

    class Meta:
        model = SupplierUser
        fields = "__all__"


class SupplierSerializer(CustomModelSerializer):
    """供应商信息"""

    class Meta:
        model = Supplier
        fields = [f.name for f in Supplier._meta.concrete_fields]
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


class SupplierUserViewSet(CustomModelViewSet):
    """供应商用户信息（独立表；按 supplier_id 筛选可得到某供应商下全部联系人）"""

    queryset = SupplierUser.objects.all()
    serializer_class = SupplierUserSerializer
    create_serializer_class = SupplierUserCreateUpdateSerializer
    update_serializer_class = SupplierUserCreateUpdateSerializer
    filter_fields = ["supplier_id", "supplier_role", "status", "user_email"]
    search_fields = ["supplier_id", "supplier_name", "user_email", "user_name", "user_phone"]
    ordering = ["-create_datetime", "id"]
