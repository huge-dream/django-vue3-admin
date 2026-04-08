from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.pisadmin.miscprocurement.models import Inquiry, RFQOperationLogs

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


def _parse_audit_timestamp(raw: Any) -> datetime:
    if raw is None:
        raise ValueError("审核完成时间不能为空")
    if isinstance(raw, datetime):
        dt = raw
    else:
        s = str(raw).strip()
        if not s:
            raise ValueError("审核完成时间不能为空")
        dt = parse_datetime(s)
        if dt is None:
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("审核完成时间格式无效") from exc
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _norm_purchase_category(raw: Any) -> int:
    if raw is None:
        raise ValueError("采购类别无效")
    s = str(raw).strip()
    if s in ("1", "2"):
        return int(s)
    raise ValueError("采购类别无效")


def _norm_audit_status(raw: Any) -> str:
    if raw is None:
        raise ValueError("审核结果无效")
    s = str(raw).strip().upper()
    if s in ("APPROVED", "REJECTED"):
        return s
    raise ValueError("审核结果无效")


class PricingResultSyncAdapter(BaseSyncAdapter):
    """EIP 核价审核结果抛转：更新询价单状态及 EIP 审核字段。"""

    adapter_name = "pricing_result"
    direction = SyncDirection.EIP_TO_PIS

    STATUS_PRICE_AUDIT = 7
    STATUS_APPROVED = 8
    STATUS_LOST = 9
    EIP_APPROVAL_OK = 1
    EIP_APPROVAL_REJECT = 2

    def validate(self, data: Dict[str, Any]) -> bool:
        company = _first_str(data, "Company", "company")
        eip_audit = _first_str(data, "eipAuditNo", "eip_audit_no")
        cat = _first_str(data, "purchase_category", "purchaseCategory")
        inq = _first_str(data, "inquiryNo", "inquiry_no")
        status = _first_str(data, "auditStatus", "audit_status")
        user = _first_str(data, "auditUser", "audit_user")
        ts = data.get("auditTimestamp") if "auditTimestamp" in data else data.get("audit_timestamp")
        ts_ok = ts is not None and str(ts).strip() != ""
        return bool(company and eip_audit and cat and inq and status and user and ts_ok)

    def transform_to_local(self, data: Dict[str, Any]) -> Dict[str, Any]:
        company = _first_str(data, "Company", "company")
        eip_audit_no = _first_str(data, "eipAuditNo", "eip_audit_no")
        cat_raw = data.get("purchase_category")
        if cat_raw is None:
            cat_raw = data.get("purchaseCategory")
        purchase_category = _norm_purchase_category(cat_raw)
        inquiry_no = _first_str(data, "inquiryNo", "inquiry_no")
        audit_status = _norm_audit_status(_first_str(data, "auditStatus", "audit_status"))
        audit_user = _first_str(data, "auditUser", "audit_user")[:20]
        raw_ts = data.get("auditTimestamp") if "auditTimestamp" in data else data.get("audit_timestamp")
        audit_ts = _parse_audit_timestamp(raw_ts)

        external_id = f"{inquiry_no}_{eip_audit_no}"
        return {
            "company": company,
            "eip_audit_no": eip_audit_no[:20],
            "purchase_category": purchase_category,
            "inquiry_no": inquiry_no[:20],
            "audit_status": audit_status,
            "audit_user": audit_user,
            "audit_timestamp": audit_ts,
            "external_id": external_id,
        }

    def save_to_local(self, transformed_data: Dict[str, Any]) -> bool:
        inquiry_no = transformed_data["inquiry_no"]
        company = transformed_data["company"]
        eip_audit_no = transformed_data["eip_audit_no"]
        purchase_category = int(transformed_data["purchase_category"])
        audit_status = transformed_data["audit_status"]
        audit_user = transformed_data["audit_user"]
        audit_ts = transformed_data["audit_timestamp"]

        with transaction.atomic():
            obj = (
                Inquiry.objects.select_for_update()
                .filter(inquiry_no=inquiry_no)
                .first()
            )
            if not obj:
                raise ValueError("询价单不存在")

            if int(obj.purchase_type or 0) != purchase_category:
                raise ValueError("单号不匹配")

            cc_db = (obj.company_code or "").strip()
            cc_in = (company or "").strip()
            if cc_db and cc_in and cc_db != cc_in:
                raise ValueError("单号不匹配")

            appr = (obj.approval_number or "").strip()
            if appr and appr != eip_audit_no:
                raise ValueError("单号不匹配")
            if not appr:
                obj.approval_number = eip_audit_no

            if int(obj.status or 0) != self.STATUS_PRICE_AUDIT:
                raise ValueError("当前询价单非价格审核状态，无法更新审核结果")

            old_status = int(obj.status if obj.status is not None else 0)
            obj.approval_status = (
                self.EIP_APPROVAL_OK if audit_status == "APPROVED" else self.EIP_APPROVAL_REJECT
            )
            obj.update_user = audit_user
            obj.update_time = audit_ts

            if audit_status == "APPROVED":
                new_status = self.STATUS_APPROVED
                op_type = 9
                op_desc = f"EIP核价审核通过（审核人：{audit_user}）"
            else:
                new_status = self.STATUS_LOST
                op_type = 10
                op_desc = f"EIP核价审核驳回（审核人：{audit_user}）"

            obj.status = new_status
            obj.update_datetime = audit_ts
            obj.save(
                update_fields=[
                    "status",
                    "approval_number",
                    "approval_status",
                    "update_user",
                    "update_time",
                    "update_datetime",
                ]
            )

            if old_status != new_status:
                RFQOperationLogs.try_append(
                    inquiry_no=obj.inquiry_no,
                    purchase_type=int(obj.purchase_type),
                    operation_type=op_type,
                    operation_user=audit_user,
                    quotation_no="-",
                    per_status=old_status,
                    cur_status=new_status,
                    operation_desc=op_desc[:200],
                )

        return True

    def transform_to_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}


SyncFactory.register("pricing_result", PricingResultSyncAdapter)
