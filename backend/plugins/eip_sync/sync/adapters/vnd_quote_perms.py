from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from django.db import transaction

from apps.pisadmin.basicinfo.models import SupplierUser

from sync.base import BaseSyncAdapter, SyncDirection
from sync.factory import SyncFactory


def _first_str(data: Dict[str, Any], *keys: str) -> str:
    for k in keys:
        v = data.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return ""


def _norm_quote_permission(raw: Any) -> int:
    if raw is None:
        raise ValueError("报价权限无效")
    try:
        val = int(raw)
    except (TypeError, ValueError):
        raise ValueError("报价权限无效")
    if val not in (1, 2, 3):
        raise ValueError("报价权限无效")
    return val


def _norm_status(raw: Any) -> int:
    if raw is None:
        return 1
    try:
        val = int(raw)
    except (TypeError, ValueError):
        return 1
    return 1 if val else 0


def _parse_datetime(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    try:
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(s)
        if dt is not None:
            return dt
        from datetime import timezone
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            from django.utils import timezone as tz
            dt = tz.make_aware(dt, tz.get_current_timezone())
        return dt
    except Exception:
        return None


class VendorQuotePermissionSyncAdapter(BaseSyncAdapter):
    """EIP 供应商报价权限资料抛转：更新供应商用户主数据的报价权限及厂区开通状态。"""

    adapter_name = "vendor_quote_permission"
    direction = SyncDirection.EIP_TO_PIS

    PERMISSION_ROLE_MAP = {
        1: 3,
        2: 2,
        3: 1,
    }

    def validate(self, data: Dict[str, Any]) -> bool:
        apply_no = _first_str(data, "applyNo", "apply_no")
        supplier_id = _first_str(data, "supplier_id")
        supplier_name = _first_str(data, "supplier_name")
        quote_perm = _first_str(data, "quote_permission", "quotePermission")
        email = _first_str(data, "email")
        name = _first_str(data, "name")
        companycode = _first_str(data, "companycode", "companyCode")
        return bool(apply_no and supplier_id and supplier_name and quote_perm and email and name and companycode)

    def transform_to_local(self, data: Dict[str, Any]) -> Dict[str, Any]:
        supplier_id = _first_str(data, "supplier_id")
        supplier_name = _first_str(data, "supplier_name")
        quote_permission = _norm_quote_permission(
            data.get("quote_permission") if "quote_permission" in data else data.get("quotePermission")
        )
        email = _first_str(data, "email")
        name = _first_str(data, "name")
        phone = _first_str(data, "phone")
        status = _norm_status(data.get("status"))
        companycode = _first_str(data, "companycode", "companyCode")
        createtime = _parse_datetime(data.get("createtime"))
        updatetime = _parse_datetime(data.get("updatetime"))

        company_list = [c.strip() for c in companycode.split(",") if c.strip()]

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "quote_permission": quote_permission,
            "user_email": email,
            "user_name": name,
            "user_phone": phone or "",
            "status": status,
            "company_list": company_list,
            "createtime": createtime,
            "updatetime": updatetime,
        }

    def save_to_local(self, transformed_data: Dict[str, Any]) -> bool:
        supplier_id = transformed_data["supplier_id"]
        supplier_name = transformed_data["supplier_name"]
        quote_permission = transformed_data["quote_permission"]
        user_email = transformed_data["user_email"]
        user_name = transformed_data["user_name"]
        user_phone = transformed_data["user_phone"]
        status = transformed_data["status"]
        company_list = transformed_data["company_list"]

        if not company_list:
            raise ValueError("报价开通权限厂区不能为空")

        supplier_role = self.PERMISSION_ROLE_MAP.get(quote_permission, 1)

        with transaction.atomic():
            for company_code in company_list:
                defaults = {
                    "supplier_name": supplier_name,
                    "supplier_role": supplier_role,
                    "user_name": user_name,
                    "user_phone": user_phone,
                    "status": status,
                }
                SupplierUser.objects.update_or_create(
                    supplier_id=supplier_id,
                    user_email=user_email,
                    defaults=defaults,
                )

        return True

    def transform_to_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}


SyncFactory.register("vendor_quote_permission", VendorQuotePermissionSyncAdapter)
