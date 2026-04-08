from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from apps.pisadmin.miscprocurement.models import MiscProcMaterial

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


def _parse_category_id(raw: Any) -> Optional[int]:
    if raw is None or raw == "":
        return None
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return None


def _build_extra_description(data: Dict[str, Any], category_used_as_id: bool) -> str:
    extra: Dict[str, Any] = {}
    ac = data.get("accountCode") or data.get("account_code")
    if ac is not None and str(ac).strip() != "":
        extra["accountCode"] = str(ac).strip()
    cat = data.get("Category") or data.get("category")
    if cat is not None and str(cat).strip() != "" and not category_used_as_id:
        extra["category"] = str(cat).strip()
    for label, keys in (
        ("materialNameEn", ("materialNameEn", "material_name_en")),
        ("materialNameVi", ("materialNameVi", "material_name_vi")),
    ):
        v = _first_str(data, *keys)
        if v:
            extra[label] = v
    if not extra:
        return ""
    try:
        blob = json.dumps(extra, ensure_ascii=False)
    except (TypeError, ValueError):
        return ""
    if len(blob) <= 255:
        return blob
    return blob[:252] + "..."


class MiscMaterialSyncAdapter(BaseSyncAdapter):
    adapter_name = "misc_material"
    direction = SyncDirection.EIP_TO_PIS

    def validate(self, data: Dict[str, Any]) -> bool:
        company = _first_str(data, "companyCode", "company_code")
        code = _first_str(data, "materialCode", "material_code")
        return bool(company and code)

    def transform_to_local(self, data: Dict[str, Any]) -> Dict[str, Any]:
        company_code = _first_str(data, "companyCode", "company_code")
        partid = _first_str(data, "materialCode", "material_code")
        partid_name = _first_str(
            data,
            "materialName",
            "materialNameZh",
            "material_name",
            "material_name_zh",
        )
        specification = _first_str(data, "specification")
        unit = _first_str(data, "unit")

        cat_raw = data.get("Category") if "Category" in data else data.get("category")
        partid_category_id = _parse_category_id(cat_raw)
        category_used_as_id = partid_category_id is not None

        description = _build_extra_description(data, category_used_as_id)
        if not description:
            desc_existing = _first_str(data, "description")
            if desc_existing:
                description = desc_existing[:255]

        external_id = f"{company_code}_{partid}"
        return {
            "company_code": company_code,
            "partid": partid,
            "partid_name": partid_name,
            "specification": specification,
            "unit": unit,
            "partid_category_id": partid_category_id,
            "description": description,
            "external_id": external_id,
            "status": 1,
        }

    def save_to_local(self, transformed_data: Dict[str, Any]) -> bool:
        external_id = transformed_data.pop("external_id", "")
        _ = external_id
        company_code = transformed_data.get("company_code")
        partid = transformed_data.get("partid")
        defaults = {
            "partid_name": transformed_data.get("partid_name") or "",
            "specification": transformed_data.get("specification") or "",
            "unit": transformed_data.get("unit") or "",
            "partid_category_id": transformed_data.get("partid_category_id"),
            "status": transformed_data.get("status", 1),
        }
        desc = transformed_data.get("description")
        if desc:
            defaults["description"] = desc[:255]

        MiscProcMaterial.objects.update_or_create(
            company_code=company_code,
            partid=partid,
            defaults=defaults,
        )
        return True

    def transform_to_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}


SyncFactory.register("misc_material", MiscMaterialSyncAdapter)
