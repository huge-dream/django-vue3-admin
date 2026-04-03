# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.decorators import action

from apps.pisadmin.basicinfo.models import Supplier, SupplierUser
from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class SupplierUserSerializer(CustomModelSerializer):
    """供应商用户信息（子表 pis_supplier_users）"""

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
    """供应商信息-序列化器（含关联 supplier_user）"""

    supplier_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Supplier
        fields = [f.name for f in Supplier._meta.concrete_fields] + ["supplier_user"]
        read_only_fields = ["id"]

    def get_supplier_user(self, obj):
        cache = self.context.get("supplier_user_by_sid")
        if cache is not None:
            su = cache.get(obj.supplier_id)
        else:
            su = SupplierUser.objects.filter(supplier_id=obj.supplier_id).first()
        if su is None:
            return None
        return SupplierUserSerializer(su, context=self.context).data


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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        m = getattr(self, "_supplier_user_map", None)
        if m is not None:
            ctx["supplier_user_by_sid"] = m
        return ctx

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            rows = page
        else:
            rows = list(queryset)
        sids = [row.supplier_id for row in rows]
        self._supplier_user_map = {
            u.supplier_id: u for u in SupplierUser.objects.filter(supplier_id__in=sids)
        }
        try:
            serializer = self.get_serializer(rows, many=True, request=request)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        finally:
            self._supplier_user_map = None

    @action(methods=["get", "put", "patch"], detail=True, url_path="supplier_user")
    def supplier_user_nested(self, request, pk=None):
        """按供应商主键维护关联的供应商用户信息（与 Supplier.supplier_id 对应，唯一）。"""
        supplier = self.get_object()
        sid = (supplier.supplier_id or "").strip()
        if not sid:
            return ErrorResponse(msg="供应商缺少 supplier_id")

        if request.method == "GET":
            su = SupplierUser.objects.filter(supplier_id=sid).first()
            if su is None:
                return DetailResponse(data=None, msg="暂无供应商用户信息")
            return DetailResponse(data=SupplierUserSerializer(su, context={"request": request}).data)

        su = SupplierUser.objects.filter(supplier_id=sid).first()
        ser = SupplierUserCreateUpdateSerializer(
            instance=su,
            data=request.data,
            partial=request.method == "PATCH",
            context={"request": request},
        )
        ser.is_valid(raise_exception=True)
        name = ser.validated_data.get("supplier_name")
        if name is None or str(name).strip() == "":
            name = supplier.supplier_name
        obj = ser.save(supplier_id=sid, supplier_name=name)
        return DetailResponse(
            data=SupplierUserSerializer(obj, context={"request": request}).data,
            msg="保存成功",
        )


class SupplierUserViewSet(CustomModelViewSet):
    """供应商用户信息接口（子表；与 Supplier.supplier_id 关联）"""

    queryset = SupplierUser.objects.all()
    serializer_class = SupplierUserSerializer
    create_serializer_class = SupplierUserCreateUpdateSerializer
    update_serializer_class = SupplierUserCreateUpdateSerializer
    filter_fields = ["company_code", "supplier_id", "supplier_role", "status", "user_email"]
    search_fields = ["supplier_id", "supplier_name", "user_email", "user_name", "user_phone"]
    ordering = ["-create_datetime", "id"]
