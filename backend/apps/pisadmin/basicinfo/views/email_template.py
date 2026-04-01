# -*- coding: utf-8 -*-
"""邮件正文/主题模板：按业务场景 key 渲染，供询价发布、报价结束等流程调用。

扩展方式：
1. 在下方注册 ``EMAIL_TEMPLATE_FILES``（主题模板路径 + HTML 正文路径），
   再实现 ``build_context_<场景>(...)``，通过 ``render_email(TEMPLATE_xxx, ctx)`` 调用。
2. 若需完全自定义渲染逻辑（非一对 .txt/.html），将 ``TEMPLATE_xxx`` 登记到 ``_CUSTOM_RENDERERS``。
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

# 杂采询价单发布通知（新询价邀请）
TEMPLATE_RFS_PUBLISH = "RFS_publish"
# 全部供应商已报价 → 询价单进入「报价结束」— 通知采购负责人
TEMPLATE_QUOTE_ENDED = "Quote_ended"


def _for_local_display(dt: Any):
    """
    转为用于邮件展示的「本地」时间。

    - USE_TZ=False 时 ORM 常返回 naive（即便库中是 timestamptz），应直接按业务时区墙钟时间格式化，
      不可调用 timezone.localtime(naive)，否则会触发 ValueError。
    - aware 时再用 localtime 转到当前激活时区展示。
    """
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return dt
    return timezone.localtime(dt)


def supplier_portal_base_url() -> str:
    """供应商端入口基址；优先 Django settings，其次环境变量 PIS_SUPPLIER_PORTAL_URL。"""
    base = getattr(settings, "PIS_SUPPLIER_PORTAL_URL", None) or os.getenv("PIS_SUPPLIER_PORTAL_URL", "") or ""
    return str(base).strip().rstrip("/")


def admin_portal_base_url() -> str:
    """采购/管理端前端基址；优先 settings.PIS_ADMIN_PORTAL_URL，其次环境变量。"""
    base = getattr(settings, "PIS_ADMIN_PORTAL_URL", None) or os.getenv("PIS_ADMIN_PORTAL_URL", "") or ""
    return str(base).strip().rstrip("/")


def system_brand_name() -> str:
    """邮件落款系统名称。"""
    return str(getattr(settings, "PIS_EMAIL_SYSTEM_NAME", None) or "AVC PIS").strip() or "AVC PIS"


def build_context_rfs_publish(
    inquiry: Any,
    supplier_group: Dict[str, Any],
    *,
    purchaser_company_name: str = "",
) -> Dict[str, Any]:
    """
    组装 RFS_publish 模板变量（均为未转义纯文本，由 Django 模板引擎在渲染 HTML 时自动转义）。
    supplier_group：与 `_group_inquiry_suppliers` 一致的结构。
    """
    vendor_name = (supplier_group.get("supplier_name") or "").strip() or "贵司"
    rfq_number = (getattr(inquiry, "inquiry_no", None) or "").strip()
    title = (getattr(inquiry, "title", None) or "").strip()

    raw_part_ids = supplier_group.get("part_ids") or set()
    part_ids = {str(x) for x in raw_part_ids}
    lines: list[str] = []
    rfq_mgr = getattr(inquiry, "rfq_items", None)
    if rfq_mgr is not None:
        for row in rfq_mgr.all():
            if str(row.part_id) not in part_ids:
                continue
            seg = " ".join(x for x in (row.part_id, (row.product_name or "").strip()) if x).strip()
            if seg:
                lines.append(seg)
    if not lines and part_ids:
        lines = sorted(part_ids)
    material_info = "；".join(lines) if lines else (title or "—")

    qd = getattr(inquiry, "quote_deadline", None)
    # 招标：主表不存报价截止时，发布邮件展示投标截止时间
    if qd is None and int(getattr(inquiry, "buying_method", 1) or 1) == 2:
        qd = getattr(inquiry, "bid_end_time", None)
    if qd:
        local_qd = _for_local_display(qd)
        deadline_time = local_qd.strftime("%Y-%m-%d %H:%M")
        deadline_date_subject = local_qd.strftime("%Y-%m-%d")
    else:
        deadline_time = "请登录系统查看"
        deadline_date_subject = "待定"

    now = _for_local_display(timezone.now())
    current_date = now.strftime("%Y-%m-%d") if now else ""

    base = supplier_portal_base_url()
    system_link = base if base else ""

    buyer = (getattr(inquiry, "buyer", None) or "").strip()
    contact_person = buyer or "采购部"
    contact_phone = ""  # 询价单主表暂无采购电话字段，预留

    pcn = (purchaser_company_name or "").strip()
    if not pcn:
        pcn = (getattr(inquiry, "company_code", None) or "").strip() or "我司"

    return {
        "vendor_name": vendor_name,
        "purchaser_company_name": pcn,
        "rfq_number": rfq_number,
        "material_info": material_info,
        "inquiry_title": title,
        "deadline_time": deadline_time,
        "deadline_date_subject": deadline_date_subject,
        "system_link": system_link,
        "contact_person": contact_person,
        "contact_phone": contact_phone,
        "current_date": current_date,
    }


def build_context_quote_ended(
    inquiry: Any,
    *,
    last_quotation_no: str = "",
) -> Dict[str, Any]:
    """
    报价结束通知（采购端）：全部供应商已提交报价，询价单进入「报价结束」。
    """
    rfq_number = (getattr(inquiry, "inquiry_no", None) or "").strip()
    title = (getattr(inquiry, "title", None) or "").strip()
    buyer = (getattr(inquiry, "buyer", None) or "").strip()
    purchaser_name = buyer or "采购同事"

    now = _for_local_display(timezone.now())
    current_date = now.strftime("%Y-%m-%d") if now else ""
    closed_time = now.strftime("%Y-%m-%d %H:%M:%S") if now else "—"

    base = admin_portal_base_url()
    admin_link = base if base else ""

    t_short = title[:40] + ("…" if len(title) > 40 else "") if title else "—"

    return {
        "purchaser_name": purchaser_name,
        "rfq_number": rfq_number,
        "inquiry_title": title or "—",
        "inquiry_title_short": t_short,
        "last_quotation_no": (last_quotation_no or "").strip(),
        "closed_time": closed_time,
        "current_date": current_date,
        "admin_link": admin_link,
        "system_name": system_brand_name(),
    }


# ---------------------------------------------------------------------------
# 模板文件注册：template_key -> (subject 相对 templates/, body 相对 templates/)
# 新增一类邮件时：在此增加一行，并放置对应 templates/emails/*.txt / *.html
# ---------------------------------------------------------------------------
EMAIL_TEMPLATE_FILES: Dict[str, Tuple[str, str]] = {
    TEMPLATE_QUOTE_ENDED: ("emails/quote_ended_subject.txt", "emails/quote_ended_body.html"),
}


def render_template_pair(
    subject_template: str,
    body_template: str,
    context: Dict[str, Any],
) -> Tuple[str, str]:
    """
    通用：按一对 Django 模板路径渲染 (subject, html_body)。
    subject 一般为纯文本；HTML 正文由引擎对变量自动转义（HTML 安全）。
    """
    subject = render_to_string(subject_template, context).strip()
    body = render_to_string(body_template, context)
    return subject, body


def _render_rfs_publish_body(ctx: Dict[str, Any]) -> Tuple[str, str]:
    """RFS_publish：主题需 material_short，在渲染前注入。"""
    mat_plain = str(ctx.get("material_info") or "")
    material_short = mat_plain[:120] + ("…" if len(mat_plain) > 120 else "")

    render_ctx: Dict[str, Any] = {
        **ctx,
        "material_short": material_short,
    }
    return render_template_pair(
        "emails/rfs_publish_subject.txt",
        "emails/rfs_publish_body.html",
        render_ctx,
    )


_CUSTOM_RENDERERS: Dict[str, Callable[[Dict[str, Any]], Tuple[str, str]]] = {
    TEMPLATE_RFS_PUBLISH: _render_rfs_publish_body,
}


def render_email(template_key: str, context: Dict[str, Any]) -> Tuple[str, str]:
    """
    按模板类型渲染邮件。

    解析顺序：
    1. ``_CUSTOM_RENDERERS`` 中注册的完全自定义渲染器；
    2. ``EMAIL_TEMPLATE_FILES`` 中的 (subject, body) 路径对；
    否则抛出 ``ValueError``。

    :return: (subject, body)；body 为 HTML 时由调用方在 EmailNotice.payload 中标记 is_html。
    """
    custom = _CUSTOM_RENDERERS.get(template_key)
    if custom:
        return custom(context)

    paths = EMAIL_TEMPLATE_FILES.get(template_key)
    if paths:
        sub_path, body_path = paths
        return render_template_pair(sub_path, body_path, context)

    raise ValueError(f"Unknown email template: {template_key!r}")


def register_email_template(
    template_key: str,
    subject_template: str,
    body_template: str,
    *,
    renderer: Optional[Callable[[Dict[str, Any]], Tuple[str, str]]] = None,
) -> None:
    """
    运行时注册（可选）：用于插件或测试注入额外模板。

    - 若提供 ``renderer``，则走自定义渲染，不再使用路径对。
    - 否则将 ``subject_template`` / ``body_template`` 登记到 ``EMAIL_TEMPLATE_FILES``。
    """
    if renderer is not None:
        _CUSTOM_RENDERERS[template_key] = renderer
        EMAIL_TEMPLATE_FILES.pop(template_key, None)
        return
    EMAIL_TEMPLATE_FILES[template_key] = (subject_template, body_template)
    _CUSTOM_RENDERERS.pop(template_key, None)
