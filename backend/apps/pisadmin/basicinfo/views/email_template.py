# -*- coding: utf-8 -*-
"""邮件正文/主题模板：按业务场景 key 渲染，供询价发布等流程调用。"""

from __future__ import annotations

import html
import os
from typing import Any, Callable, Dict, Tuple

from django.conf import settings
from django.utils import timezone

# 杂采询价单发布通知（新询价邀请）
TEMPLATE_RFS_PUBLISH = "RFS_publish"


def _h(text: Any) -> str:
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


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


def build_context_rfs_publish(
    inquiry: Any,
    supplier_group: Dict[str, Any],
    *,
    purchaser_company_name: str = "",
) -> Dict[str, Any]:
    """
    组装 RFS_publish 模板变量（均为未转义纯文本，由渲染函数做 HTML 转义）。
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


def _render_rfs_publish_body(ctx: Dict[str, Any]) -> Tuple[str, str]:
    """返回 (subject, html_body)。"""
    rfq = _h(ctx.get("rfq_number"))
    mat = ctx.get("material_info") or ""
    mat_plain = str(mat)
    mid = mat_plain[:120] + ("…" if len(mat_plain) > 120 else "")
    subject = f"【新询价邀请】{ctx.get('rfq_number') or '—'} - {mid} - 截止：{ctx.get('deadline_date_subject') or '—'}"

    vendor = _h(ctx.get("vendor_name"))
    purchaser = _h(ctx.get("purchaser_company_name"))
    material_html = _h(ctx.get("material_info"))
    deadline_line = _h(ctx.get("deadline_time"))
    link = ctx.get("system_link") or ""
    link_h = _h(link)
    contact_name = _h(ctx.get("contact_person"))
    phone_raw = (ctx.get("contact_phone") or "").strip()
    phone = _h(phone_raw) if phone_raw else "—"
    closing_date = _h(ctx.get("current_date"))

    if link:
        button_block = f"""
    <p style="margin:16px 0;">
      <a href="{link_h}" style="display:inline-block;padding:10px 20px;background:#2563eb;color:#ffffff;
        text-decoration:none;border-radius:6px;font-weight:600;">立即前往报价</a>
    </p>
    <p style="margin:8px 0 0;font-size:13px;color:#64748b;">若按钮无法点击，请复制以下链接到浏览器打开：</p>
    <p style="margin:4px 0 16px;word-break:break-all;font-size:13px;"><a href="{link_h}">{link_h}</a></p>"""
    else:
        button_block = """
    <p style="margin:16px 0;color:#b45309;">系统未配置供应商门户地址（PIS_SUPPLIER_PORTAL_URL），请联系管理员获取登录方式。</p>"""

    body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8" /></head>
<body style="font-family:'Microsoft YaHei',SimHei,sans-serif;font-size:14px;color:#1e293b;line-height:1.6;">
  <p>尊敬的 {vendor} 合作伙伴：</p>
  <p>您好！</p>
  <p>我司（{purchaser}）现正式发布新的采购询价单，诚邀贵司参与报价，我们非常期待与您的合作。</p>

  <h3 style="margin:20px 0 8px;font-size:15px;">📋 询价单概要</h3>
  <ul style="margin:0;padding-left:20px;">
    <li><strong>询价单号：</strong>{rfq}</li>
    <li><strong>采购物料：</strong>{material_html}</li>
    <li><strong>报价截止时间：</strong>{deadline_line}（请务必在此时间前提交）</li>
  </ul>

  <h3 style="margin:20px 0 8px;font-size:15px;">💡 如何参与报价？</h3>
  <p style="margin:8px 0;">请点击下方按钮登录系统查看详情并填写报价：</p>
  {button_block}

  <h3 style="margin:20px 0 8px;font-size:15px;">⚠️ 注意事项</h3>
  <ul style="margin:0;padding-left:20px;">
    <li>逾期系统将自动关闭报价通道，无法补报。</li>
    <li>如有疑问，请联系采购专员 {contact_name}（电话: {phone}）。</li>
  </ul>

  <p style="margin:24px 0 8px;">祝商祺！</p>
  <p style="margin:0;">{purchaser} 采购部</p>
  <p style="margin:4px 0 16px;">{closing_date}</p>
  <p style="font-size:12px;color:#94a3b8;">此邮件由系统自动发送，请勿直接回复。</p>
</body></html>"""
    return subject, body


_RENDERERS: Dict[str, Callable[[Dict[str, Any]], Tuple[str, str]]] = {
    TEMPLATE_RFS_PUBLISH: _render_rfs_publish_body,
}


def render_email(template_key: str, context: Dict[str, Any]) -> Tuple[str, str]:
    """
    按模板类型渲染邮件。
    :return: (subject, body)；body 为 HTML 时由调用方在 EmailNotice.payload 中标记 is_html。
    """
    renderer = _RENDERERS.get(template_key)
    if not renderer:
        raise ValueError(f"Unknown email template: {template_key!r}")
    return renderer(context)
