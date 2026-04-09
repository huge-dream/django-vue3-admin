from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from sync.base import BaseSyncAdapter, SyncDirection
from sync.factory import SyncFactory

logger = logging.getLogger(__name__)


def _first_str(data: Dict[str, Any], *keys: str) -> str:
    for k in keys:
        v = data.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return ""


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
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            from django.utils import timezone as tz

            dt = tz.make_aware(dt, tz.get_current_timezone())
        return dt
    except Exception:
        return None


class RawMaterialSyncAdapter(BaseSyncAdapter):
    """EIP 原料料号资料抛转：同步原料料号主数据（策采相关）。"""

    adapter_name = "raw_material"
    direction = SyncDirection.EIP_TO_PIS

    def validate(self, data: Dict[str, Any]) -> bool:
        company = _first_str(data, "companyCode", "company_code")
        material_code = _first_str(data, "materialCode", "material_code")
        return bool(company and material_code)

    def transform_to_local(self, data: Dict[str, Any]) -> Dict[str, Any]:
        company_code = _first_str(data, "companyCode", "company_code")
        material_code = _first_str(data, "materialCode", "material_code")
        material_name_zh = _first_str(
            data, "materialNameZh", "material_name_zh", "materialName", "material_name"
        )
        material_name_en = _first_str(data, "materialNameEn", "material_name_en")
        material_name_vi = _first_str(data, "materialNameVi", "material_name_vi")
        specification = _first_str(data, "specification")
        unit = _first_str(data, "unit")
        source_code = _first_str(data, "sourceCode", "source_code")
        model_type = _first_str(data, "modelType", "model_type")
        product_category = _first_str(data, "productCategory", "product_category")
        group_code = _first_str(data, "groupCode", "group_code")
        material_group = _first_str(data, "materialGroup", "material_group")
        market_class = _first_str(data, "marketClass", "market_class")
        approval_status = _first_str(data, "approvalStatus", "approval_status")
        createtime = _parse_datetime(data.get("createtime"))
        updatetime = _parse_datetime(data.get("updatetime"))

        external_id = f"{company_code}_{material_code}"
        return {
            "company_code": company_code,
            "material_code": material_code,
            "material_name_zh": material_name_zh,
            "material_name_en": material_name_en,
            "material_name_vi": material_name_vi,
            "specification": specification,
            "unit": unit,
            "source_code": source_code,
            "model_type": model_type,
            "product_category": product_category,
            "group_code": group_code,
            "material_group": material_group,
            "market_class": market_class,
            "approval_status": approval_status,
            "createtime": createtime,
            "updatetime": updatetime,
            "external_id": external_id,
        }

    def save_to_local(self, transformed_data: Dict[str, Any]) -> bool:
        from apps.pisadmin.procurement.models import ProcMaterial

        company_code = transformed_data.get("company_code")
        material_code = transformed_data.get("material_code")
        createtime = transformed_data.pop("createtime", None)
        updatetime = transformed_data.pop("updatetime", None)
        transformed_data.pop("external_id", "")

        defaults = {
            "material_name_zh": transformed_data.get("material_name_zh") or "",
            "material_name_en": transformed_data.get("material_name_en") or "",
            "material_name_vi": transformed_data.get("material_name_vi") or "",
            "specification": transformed_data.get("specification") or "",
            "unit": transformed_data.get("unit") or "",
            "source_code": transformed_data.get("source_code") or "",
            "model_type": transformed_data.get("model_type") or "",
            "product_category": transformed_data.get("product_category") or "",
            "group_code": transformed_data.get("group_code") or "",
            "material_group": transformed_data.get("material_group") or "",
            "market_class": transformed_data.get("market_class") or "",
            "approval_status": transformed_data.get("approval_status") or "",
        }

        obj, created = ProcMaterial.objects.update_or_create(
            company_code=company_code,
            material_code=material_code,
            defaults=defaults,
        )

        logger.info(
            f"[RawMaterialSyncAdapter] {'创建' if created else '更新'} ProcMaterial: "
            f"company_code={company_code}, material_code={material_code}"
        )
        return True

    def transform_to_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}


SyncFactory.register("raw_material", RawMaterialSyncAdapter)
