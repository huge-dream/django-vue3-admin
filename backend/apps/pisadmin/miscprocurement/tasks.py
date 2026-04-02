# -*- coding: utf-8 -*-
"""
Celery 定时任务：报价截止时间到期邮件通知采购。
"""
import logging
from typing import Dict, Any, List

from django.utils import timezone

from application.celery import app
from apps.pissupplier.models import QuotationMaster
from apps.pisadmin.miscprocurement.models import Inquiry

logger = logging.getLogger(__name__)


def _is_in_cooldown(inquiry_no: str, cooldown_hours: int = 24) -> bool:
    """
    检查该询价单是否在冷却期内（24h内已成功发送过）。
    复用 email_utils 的冷却判断逻辑。
    """
    from apps.pisadmin.basicinfo.views.email_utils import should_send_quote_timeout_reminder
    return not should_send_quote_timeout_reminder(inquiry_no, cooldown_hours=cooldown_hours)


def _get_purchaser_emails(inquiry_no: str) -> List[str]:
    """根据询价单号获取采购负责人邮箱列表。"""
    from apps.pisadmin.basicinfo.views.email_utils import resolve_inquiry_purchaser_emails
    inquiry = Inquiry.objects.filter(inquiry_no=inquiry_no).first()
    if not inquiry:
        return []
    return resolve_inquiry_purchaser_emails(inquiry)


def _build_expired_supplier_list(inquiry_no: str) -> List[Dict[str, Any]]:
    """
    构建某询价单下所有已到期未报价供应商列表。
    """
    now = timezone.now()
    rows = QuotationMaster.objects.filter(
        inquiry_no=inquiry_no,
        status__in=(1, 2),  # 1=待报价, 2=报价中
        quote_deadline__lt=now,
    ).values("supplier_name", "contact_person", "contact_phone", "quote_deadline", "status")

    result = []
    for row in rows:
        deadline_local = row["quote_deadline"]
        if deadline_local and timezone.is_aware(deadline_local):
            from django.utils.timezone import localtime
            deadline_display = localtime(deadline_local).strftime("%Y-%m-%d %H:%M")
        else:
            deadline_display = str(deadline_local or "—")

        result.append({
            "supplier_name": row["supplier_name"] or "—",
            "contact_person": row["contact_person"] or None,
            "quote_deadline": deadline_display,
            "status": row["status"],
        })
    return result


def _send_deadline_expired_email(inquiry: Inquiry, expired_suppliers: List[Dict[str, Any]]) -> bool:
    """
    渲染并发送单封报价截止到期邮件（一个询价单合并所有供应商）。
    复用 email_utils 的 send_email_notice 底层。
    """
    from apps.pisadmin.basicinfo.views.email_template import (
        TEMPLATE_QUOTE_DEADLINE_EXPIRED,
        build_context_quote_deadline_expired,
        render_email,
    )
    from apps.pisadmin.basicinfo.views.email_utils import send_email_notice
    from apps.pisadmin.basicinfo.models import EmailNotice

    to_list = _get_purchaser_emails(inquiry.inquiry_no)
    if not to_list:
        logger.warning("报价截止提醒无法找到采购负责人邮箱，inquiry_no=%s", inquiry.inquiry_no)
        return False

    ctx = build_context_quote_deadline_expired(inquiry, expired_suppliers)
    subject, body = render_email(TEMPLATE_QUOTE_DEADLINE_EXPIRED, ctx)

    notice = EmailNotice.objects.create(
        subject=subject,
        body=body,
        to_emails=to_list,
        cc_emails=[],
        bcc_emails=[],
        attachments=[],
        biz_type="inquiry_quote_timeout",  # 复用现有 biz_type 用于冷却期判断
        biz_id=inquiry.inquiry_no,
        status="pending",
        payload={
            "template_key": TEMPLATE_QUOTE_DEADLINE_EXPIRED,
            "is_html": True,
            "inquiry_no": ctx.get("inquiry_no"),
            "supplier_count": ctx.get("supplier_count"),
        },
    )
    notice.status = "sending"
    notice.save(update_fields=["status", "update_datetime"])

    success, detail = send_email_notice(notice)
    notice.response = detail or {}
    if success:
        notice.status = "success"
        notice.sent_at = timezone.now()
        notice.last_error = None
    else:
        notice.status = "failed"
        notice.last_error = detail.get("error") if isinstance(detail, dict) else str(detail)

    notice.save(update_fields=["status", "sent_at", "response", "last_error", "update_datetime"])
    return success


@app.task(bind=True, max_retries=3, default_retry_delay=180)
def check_quote_deadline_expired(self) -> Dict[str, int]:
    """
    Celery Beat 定时任务：轮询报价截止时间已到期的报价单，
    按询价单合并发送邮件通知采购负责人，每天最多一次。

    查询条件：status ∈ {1, 2}（待报价/报价中）且 quote_deadline < now

    Returns: {"checked": N, "sent": M, "skipped": K, "errors": E}
    """
    now = timezone.now()

    # 1. 找出所有已到期但未报价的报价单
    expired_qs = QuotationMaster.objects.filter(
        status__in=(1, 2),
        quote_deadline__isnull=False,
        quote_deadline__lt=now,
    ).values_list("inquiry_no", flat=True).distinct()

    # 2. 按 inquiry_no 分组
    inquiry_nos = list(expired_qs)

    checked = len(inquiry_nos)
    sent = 0
    skipped = 0
    errors = 0

    for inq_no in inquiry_nos:
        # 3. 检查24h冷却期
        if _is_in_cooldown(inq_no, cooldown_hours=24):
            skipped += 1
            continue

        # 4. 获取 Inquiry 对象
        inquiry = Inquiry.objects.filter(inquiry_no=inq_no).first()
        if not inquiry:
            logger.warning("报价截止提醒未找到询价单，inquiry_no=%s", inq_no)
            skipped += 1
            continue

        # 5. 构建到期供应商列表
        expired_suppliers = _build_expired_supplier_list(inq_no)
        if not expired_suppliers:
            skipped += 1
            continue

        # 6. 发送邮件
        try:
            if _send_deadline_expired_email(inquiry, expired_suppliers):
                sent += 1
            else:
                errors += 1
        except Exception:
            logger.exception("报价截止提醒邮件发送异常，inquiry_no=%s", inq_no)
            errors += 1

    logger.info(
        "报价截止提醒任务完成: checked=%d, sent=%d, skipped=%d, errors=%d",
        checked, sent, skipped, errors,
    )
    return {"checked": checked, "sent": sent, "skipped": skipped, "errors": errors}
