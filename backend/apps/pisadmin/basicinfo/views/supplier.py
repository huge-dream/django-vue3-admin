# -*- coding: utf-8 -*-
import hashlib

from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from application import dispatch
from apps.pisadmin.basicinfo.models import Supplier, SupplierUser
from dvadmin.system.models import Dept, Role, Users
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet

SUPPLIER_DEPT_KEY = "supplier"


def _default_system_password_plain() -> str:
    v = dispatch.get_system_config_values("base.default_password")
    if v is None or str(v).strip() == "":
        return "admin123456"
    return str(v).strip()


def _system_role_key_from_supplier_role(supplier_role: int) -> str:
    role_map = dict(SupplierUser.ROLE_CHOICES)
    key = role_map.get(supplier_role)
    if not key:
        raise ValidationError(
            detail={"supplier_role": [f"不支持的供应商角色（{supplier_role}），无法映射系统角色"]}
        )
    return key


def _sync_create_system_user_for_supplier(supplier_user: SupplierUser, request) -> None:
    """在系统用户表创建账号：账号=联络人邮箱，部门 key=supplier，角色按 supplier_role 映射，性别=0，密码=系统默认密码。"""
    email = (supplier_user.user_email or "").strip()
    if not email:
        raise ValidationError(detail={"user_email": ["联络人邮箱不能为空（系统登录账号将使用该邮箱）"]})

    if Users.objects.filter(username=email).exists():
        raise ValidationError(
            detail={
                "user_email": ["该邮箱已作为系统用户账号存在，请更换联络人邮箱或联系管理员处理已有账号"]
            }
        )

    dept = Dept.objects.filter(key=SUPPLIER_DEPT_KEY, status=True).first() or Dept.objects.filter(
        key=SUPPLIER_DEPT_KEY
    ).first()
    if not dept:
        raise ValidationError(
            detail={
                "_dept": [f'未找到部门 key="{SUPPLIER_DEPT_KEY}"（供应商），请先在「部门管理」中维护']
            }
        )

    role_key = _system_role_key_from_supplier_role(supplier_user.supplier_role)
    role = Role.objects.filter(key=role_key, status=True).first() or Role.objects.filter(key=role_key).first()
    if not role:
        raise ValidationError(
            detail={"supplier_role": [f'未找到系统角色 key="{role_key}"，请先在「角色管理」中维护']}
        )

    plain = _default_system_password_plain()
    md5_password = hashlib.md5(plain.encode("utf-8")).hexdigest()
    hashed = make_password(md5_password)

    is_active = bool(supplier_user.status)

    user = Users(
        username=email,
        email=email,
        name=(supplier_user.user_name or "").strip() or email,
        mobile=(supplier_user.user_phone or "").strip() or "",
        gender=0,
        dept=dept,
        dept_belong_id=str(dept.id) if dept.id is not None else None,
        is_active=is_active,
    )
    user.password = hashed
    if request and getattr(request, "user", None) and str(request.user) != "AnonymousUser":
        user.creator = request.user

    try:
        user.save()
    except IntegrityError as e:
        raise ValidationError(
            detail={"user_email": ["该邮箱已作为系统用户账号存在（并发冲突），请重试或更换邮箱"]}
        ) from e

    user.role.add(role)
    if dept.id is not None and not user.manage_dept.filter(pk=dept.pk).exists():
        user.manage_dept.add(dept.id)


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
    """供应商用户信息（独立表；按 supplier_id 筛选可得到某供应商下全部联系人）。新建时在系统用户表同步创建账号。"""

    queryset = SupplierUser.objects.all()
    serializer_class = SupplierUserSerializer
    create_serializer_class = SupplierUserCreateUpdateSerializer
    update_serializer_class = SupplierUserCreateUpdateSerializer
    filter_fields = ["supplier_id", "supplier_role", "status", "user_email"]
    search_fields = ["supplier_id", "supplier_name", "user_email", "user_name", "user_phone"]
    ordering = ["-create_datetime", "id"]

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            _sync_create_system_user_for_supplier(instance, self.request)
