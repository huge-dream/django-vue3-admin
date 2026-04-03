# -*- coding: utf-8 -*-
"""邮件正文/主题模板：按业务场景 key 渲染，供询价发布、报价结束、询价截止提醒等流程调用。

扩展方式：
1. 推荐：单文件 ``emails/<name>_template.html``，首行 ``<!-- email-subject: ... -->`` 为主题，
   余下为 HTML 正文；在 ``_CUSTOM_RENDERERS`` 中注册渲染函数（通常调用 ``_split_combined_subject_html``）。
2. 或：在 ``EMAIL_TEMPLATE_FILES`` 登记 (subject.txt, body.html) 路径对，由 ``render_template_pair`` 渲染。
3. 运行时注册：``register_email_template(..., renderer=...)`` 或 ``register_email_template(..., sub, body)``。
"""

from __future__ import annotations

import os
import re
from typing import Any, Callable, Dict, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone

# 杂采询价单发布通知（新询价邀请）
TEMPLATE_RFS_PUBLISH = "RFS_publish"
# 招标方式发布通知（单文件 HTML：首行注释解析主题 + 正文）
TEMPLATE_BIDS_PUBLISH = "Bids_publish"
# 全部供应商已报价 → 询价单进入「报价结束」— 通知采购负责人
TEMPLATE_QUOTE_ENDED = "Quote_ended"
# 报价截止后无待报价/报价中单 → 询价单收口为「报价结束」（典型：sync_expired）— 询价截止提醒
TEMPLATE_QUOTE_TIMEOUT = "Quote_timeout"
# 报价截止时间到期提醒（多个供应商合并一封邮件，按询价单维度）
TEMPLATE_QUOTE_DEADLINE_EXPIRED = "Quote_deadline_expired"


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


def build_context_bids_publish(
    inquiry: Any,
    supplier_group: Dict[str, Any],
    *,
    purchaser_company_name: str = "",
) -> Dict[str, Any]:
    """
    招标邀请邮件（``bids_publish_template.html``）：在 ``build_context_rfs_publish`` 基础上增加
    ``bid_time_range``、``material_short``、``portal_url``、``purchaser_name`` 等变量。
    """
    ctx = build_context_rfs_publish(inquiry, supplier_group, purchaser_company_name=purchaser_company_name)

    bs = getattr(inquiry, "bid_start_time", None)
    be = getattr(inquiry, "bid_end_time", None)
    if bs and be:
        bsl = _for_local_display(bs)
        bel = _for_local_display(be)
        if bsl and bel and bsl.date() == bel.date():
            bid_time_range = f"{bsl.strftime('%Y-%m-%d %H:%M')}~{bel.strftime('%H:%M')}"
        elif bsl and bel:
            bid_time_range = f"{bsl.strftime('%Y-%m-%d %H:%M')} ~ {bel.strftime('%Y-%m-%d %H:%M')}"
        else:
            bid_time_range = "—"
    elif be:
        bel = _for_local_display(be)
        bid_time_range = bel.strftime("%Y-%m-%d %H:%M") if bel else "请登录系统查看"
    elif bs:
        bsl = _for_local_display(bs)
        bid_time_range = (bsl.strftime("%Y-%m-%d %H:%M") + " 起") if bsl else "请登录系统查看"
    else:
        bid_time_range = str(ctx.get("deadline_time") or "请登录系统查看")

    mat_plain = str(ctx.get("material_info") or "")
    material_short = mat_plain[:120] + ("…" if len(mat_plain) > 120 else "")

    purchaser_name = _quote_ended_purchaser_name(inquiry)
    portal_url = str(ctx.get("system_link") or "").strip()

    ctx.update(
        {
            "bid_time_range": bid_time_range,
            "material_short": material_short,
            "portal_url": portal_url,
            "purchaser_name": purchaser_name,
            "purchaser_phone": str(ctx.get("contact_phone") or "").strip(),
        }
    )
    return ctx


def _quote_ended_purchaser_name(inquiry: Any) -> str:
    """采购负责人展示名：优先系统用户姓名，否则采购负责人字段原文。"""
    buyer = (getattr(inquiry, "buyer", None) or "").strip()
    if not buyer:
        return "采购同事"
    User = get_user_model()
    u = User.objects.filter(username=buyer).exclude(name__isnull=True).exclude(name="").first()
    if not u:
        u = User.objects.filter(name=buyer).first()
    if u and (getattr(u, "name", None) or "").strip():
        return str(u.name).strip()
    return buyer


def _quote_ended_material_or_project_name(inquiry: Any) -> str:
    """物料/项目名称：优先 RFQ 行料号+品名汇总，否则询价单名称/材料类型。"""
    lines: list[str] = []
    rfq_mgr = getattr(inquiry, "rfq_items", None)
    if rfq_mgr is not None:
        for row in rfq_mgr.all():
            seg = " ".join(x for x in (row.part_id, (getattr(row, "product_name", None) or "").strip()) if x).strip()
            if seg:
                lines.append(seg)
    if lines:
        return "；".join(lines)
    title = (getattr(inquiry, "title", None) or "").strip()
    if title:
        return title
    mt = (getattr(inquiry, "material_type", None) or "").strip()
    return mt or "—"


def _quote_ended_completion_time(inquiry: Any) -> Any:
    """全部已报价单中，取最晚的报价时间（quotetime 优先，否则 creattime）。"""
    from apps.pissupplier.models import QuotationMaster

    inq_no = (getattr(inquiry, "inquiry_no", None) or "").strip()
    if not inq_no:
        return None
    latest: Any = None
    qs = QuotationMaster.objects.filter(inquiry_no=inq_no, status=3).only("quotetime", "creattime")
    for row in qs:
        t = row.quotetime or row.creattime
        if t is None:
            continue
        if latest is None or t > latest:
            latest = t
    return latest


def build_context_quote_ended(
    inquiry: Any,
    *,
    last_quotation_no: str = "",
) -> Dict[str, Any]:
    """
    报价完成通知（采购端）：受邀供应商均已提交报价，与模板「报价完成通知」文案一致。
    """
    from apps.pisadmin.miscprocurement.models import InquirySupplier

    inquiry_no = (getattr(inquiry, "inquiry_no", None) or "").strip()
    title = (getattr(inquiry, "title", None) or "").strip()
    inquiry_name = title or "—"

    purchaser_name = _quote_ended_purchaser_name(inquiry)
    material_or_project_name = _quote_ended_material_or_project_name(inquiry)
    plain = material_or_project_name
    material_or_project_short = plain[:40] + ("…" if len(plain) > 40 else "") if plain and plain != "—" else "—"

    supplier_count = (
        InquirySupplier.objects.filter(inquiry_no=inquiry)
        .values_list("supplier_code", flat=True)
        .distinct()
        .count()
    )

    raw_done = _quote_ended_completion_time(inquiry)
    if raw_done is None:
        raw_done = _for_local_display(timezone.now())
    done_local = _for_local_display(raw_done)
    completion_time = done_local.strftime("%Y-%m-%d %H:%M") if done_local else "—"

    base = admin_portal_base_url()
    pk = getattr(inquiry, "pk", None) or getattr(inquiry, "id", None)
    comparison_page_url = ""
    if base and pk is not None:
        comparison_page_url = f"{base}/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice/{pk}"

    now = _for_local_display(timezone.now())
    current_date = now.strftime("%Y-%m-%d") if now else ""

    return {
        "purchaser_name": purchaser_name,
        "inquiry_no": inquiry_no,
        "inquiry_name": inquiry_name,
        "material_or_project_name": material_or_project_name,
        "material_or_project_short": material_or_project_short,
        "supplier_count": supplier_count,
        "completion_time": completion_time,
        "comparison_page_url": comparison_page_url,
        # 兼容旧模板变量（若外部仍有引用）
        "rfq_number": inquiry_no,
        "inquiry_title": inquiry_name,
        "inquiry_title_short": material_or_project_short,
        "last_quotation_no": (last_quotation_no or "").strip(),
        "closed_time": completion_time,
        "current_date": current_date,
        "admin_link": comparison_page_url or base,
        "system_name": system_brand_name(),
    }


def _inquiry_effective_deadline_for_display(inquiry: Any) -> Tuple[Any, str]:
    """询价/招标下用于邮件展示的截止时间：询价用 quote_deadline，招标用 bid_end_time。"""
    qd = getattr(inquiry, "quote_deadline", None)
    if qd is None and int(getattr(inquiry, "buying_method", 1) or 1) == 2:
        qd = getattr(inquiry, "bid_end_time", None)
    if not qd:
        return None, "—"
    loc = _for_local_display(qd)
    return qd, loc.strftime("%Y-%m-%d %H:%M") if loc else "—"


def build_context_quote_timeout(inquiry: Any) -> Dict[str, Any]:
    """
    询价截止提醒（采购端）：已到截止时间、需查看报价并完成比价；与模板「询价截止提醒」文案一致。
    """
    from apps.pisadmin.miscprocurement.models import InquirySupplier
    from apps.pissupplier.models import QuotationMaster

    inquiry_no = (getattr(inquiry, "inquiry_no", None) or "").strip()
    title = (getattr(inquiry, "title", None) or "").strip()
    inquiry_name = title or "—"

    purchaser_name = _quote_ended_purchaser_name(inquiry)
    material_or_project_name = _quote_ended_material_or_project_name(inquiry)
    plain = material_or_project_name
    material_or_project_short = plain[:40] + ("…" if len(plain) > 40 else "") if plain and plain != "—" else "—"

    _, deadline_display = _inquiry_effective_deadline_for_display(inquiry)

    invited_count = (
        InquirySupplier.objects.filter(inquiry_no=inquiry)
        .values_list("supplier_code", flat=True)
        .distinct()
        .count()
    )

    quoted_count = (
        QuotationMaster.objects.filter(inquiry_no=inquiry_no, status=3)
        .values_list("supplier_code", flat=True)
        .distinct()
        .count()
    )

    base = admin_portal_base_url()
    pk = getattr(inquiry, "pk", None) or getattr(inquiry, "id", None)
    comparison_page_url = ""
    if base and pk is not None:
        comparison_page_url = f"{base}/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice/{pk}"

    now = _for_local_display(timezone.now())
    current_date = now.strftime("%Y-%m-%d") if now else ""

    return {
        "purchaser_name": purchaser_name,
        "inquiry_no": inquiry_no,
        "inquiry_name": inquiry_name,
        "material_or_project_name": material_or_project_name,
        "material_or_project_short": material_or_project_short,
        "deadline": deadline_display,
        "quoted_count": quoted_count,
        "invited_count": invited_count,
        "comparison_page_url": comparison_page_url,
        "rfq_number": inquiry_no,
        "inquiry_title": inquiry_name,
        "current_date": current_date,
        "admin_link": comparison_page_url or base,
        "system_name": system_brand_name(),
    }


def build_context_quote_deadline_expired(
    inquiry: Any,
    expired_suppliers: list,
) -> Dict[str, Any]:
    """
    报价截止到期提醒（采购端）：按询价单合并多个已到期未报价供应商，发送一封邮件。
    expired_suppliers: list[{"supplier_name", "contact_person", "quote_deadline", "status"}, ...]
    """
    from apps.pisadmin.miscprocurement.models import InquirySupplier

    inquiry_no = (getattr(inquiry, "inquiry_no", None) or "").strip()
    title = (getattr(inquiry, "title", None) or "").strip()
    inquiry_name = title or "—"

    purchaser_name = _quote_ended_purchaser_name(inquiry)
    material_or_project_name = _quote_ended_material_or_project_name(inquiry)

    invited_count = (
        InquirySupplier.objects.filter(inquiry_no=inquiry)
        .values_list("supplier_code", flat=True)
        .distinct()
        .count()
    )

    base = admin_portal_base_url()
    pk = getattr(inquiry, "pk", None) or getattr(inquiry, "id", None)
    comparison_page_url = ""
    if base and pk is not None:
        comparison_page_url = f"{base}/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice/{pk}"

    return {
        "purchaser_name": purchaser_name,
        "inquiry_no": inquiry_no,
        "inquiry_name": inquiry_name,
        "material_or_project_name": material_or_project_name,
        "supplier_count": len(expired_suppliers),
        "expired_suppliers": expired_suppliers,
        "invited_count": invited_count,
        "comparison_page_url": comparison_page_url,
        "current_date": _for_local_display(timezone.now()).strftime("%Y-%m-%d"),
        "admin_link": comparison_page_url or base,
        "system_name": system_brand_name(),
    }


# ---------------------------------------------------------------------------
# 可选：template_key -> (subject 相对 templates/, body 相对 templates/)，由 render_template_pair 渲染。
# 内置场景均已改为单文件 *_template.html，见 _CUSTOM_RENDERERS。
# ---------------------------------------------------------------------------
EMAIL_TEMPLATE_FILES: Dict[str, Tuple[str, str]] = {}


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
    """RFS_publish：单文件 ``rfs_publish_template.html``；主题需 material_short，在渲染前注入。"""
    mat_plain = str(ctx.get("material_info") or "")
    material_short = mat_plain[:120] + ("…" if len(mat_plain) > 120 else "")

    render_ctx: Dict[str, Any] = {
        **ctx,
        "material_short": material_short,
    }
    html = render_to_string("emails/rfs_publish_template.html", render_ctx)
    return _split_combined_subject_html(html)


def _render_quote_ended_combined(ctx: Dict[str, Any]) -> Tuple[str, str]:
    """Quote_ended：单文件 ``quote_ended_template.html``。"""
    html = render_to_string("emails/quote_ended_template.html", ctx)
    return _split_combined_subject_html(html)


def _render_quote_timeout_combined(ctx: Dict[str, Any]) -> Tuple[str, str]:
    """Quote_timeout：单文件 ``quote_timeout_template.html``。"""
    html = render_to_string("emails/quote_timeout_template.html", ctx)
    return _split_combined_subject_html(html)


# 首行必须为：<!-- email-subject: 纯文本主题 -->（主题内勿含连续两个减号 ``--``，以免破坏 HTML 注释）
_COMBINED_EMAIL_SUBJECT_RE = re.compile(
    r"^\s*<!--\s*email-subject:\s*(.+?)\s*-->\s*",
    re.IGNORECASE | re.DOTALL,
)


def _split_combined_subject_html(html: str) -> Tuple[str, str]:
    """从合并模板中解析 (subject, body_html)。"""
    m = _COMBINED_EMAIL_SUBJECT_RE.match(html)
    if not m:
        raise ValueError(
            "合并邮件模板必须以 <!-- email-subject: ... --> 开头（首行），参见 emails/*_template.html"
        )
    subject = m.group(1).replace("\r", " ").replace("\n", " ").strip()
    body = html[m.end() :].lstrip()
    return subject, body


def _render_bids_publish_combined(ctx: Dict[str, Any]) -> Tuple[str, str]:
    """Bids_publish：单文件 HTML，首行注释为主题。"""
    html = render_to_string("emails/bids_publish_template.html", ctx)
    return _split_combined_subject_html(html)


_CUSTOM_RENDERERS: Dict[str, Callable[[Dict[str, Any]], Tuple[str, str]]] = {
    TEMPLATE_RFS_PUBLISH: _render_rfs_publish_body,
    TEMPLATE_BIDS_PUBLISH: _render_bids_publish_combined,
    TEMPLATE_QUOTE_ENDED: _render_quote_ended_combined,
    TEMPLATE_QUOTE_TIMEOUT: _render_quote_timeout_combined,
}


def render_email(template_key: str, context: Dict[str, Any]) -> Tuple[str, str]:
    """
    按模板类型渲染邮件。

    解析顺序：
    1. ``_CUSTOM_RENDERERS``（单文件 ``*_template.html`` 等）；
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
