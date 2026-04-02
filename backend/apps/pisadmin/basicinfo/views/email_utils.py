import logging
import os
import tempfile
import urllib.parse
import urllib.request
from datetime import timedelta
from typing import Any, Dict, List, Tuple
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from django.contrib.auth import get_user_model

from apps.pisadmin.basicinfo.models import EmailNotice

logger = logging.getLogger(__name__)


def _collect_attachment_paths(raw_list: List[Any]) -> List[str]:
    paths: List[str] = []
    if not isinstance(raw_list, list):
        return paths
    for item in raw_list:
        if isinstance(item, str):
            if item:
                paths.append(item)
            continue
        if isinstance(item, dict):
            candidate = item.get("file_path") or item.get("path") or item.get("filepath")
            url = item.get("url")
            if candidate:
                paths.append(candidate)
            elif url and isinstance(url, str) and url.startswith("http"):
                # download remote file to temp location
                try:
                    parsed = urllib.parse.urlparse(url)
                    filename = os.path.basename(parsed.path) or "attachment"
                    fd, temp_path = tempfile.mkstemp(prefix="mail_att_", suffix=os.path.splitext(filename)[1])
                    os.close(fd)
                    urllib.request.urlretrieve(url, temp_path)
                    paths.append(temp_path)
                except Exception:
                    # skip silently; caller can still send email without this attachment
                    continue
    return paths


def resolve_inquiry_purchaser_emails(inquiry) -> list:
    """
    根据询价单解析采购端收件人邮箱：优先「采购负责人」对应系统用户邮箱；
    若无则依次尝试创建人（creator / creator_id）、创建人账号（create_user）。
    """
    User = get_user_model()

    buyer = (getattr(inquiry, "buyer", None) or "").strip()
    if buyer:
        u = User.objects.filter(username=buyer).exclude(email__isnull=True).exclude(email="").first()
        if not u:
            u = User.objects.filter(name=buyer).exclude(email__isnull=True).exclude(email="").first()
        if u and getattr(u, "email", None):
            return [str(u.email).strip()]

    cr = getattr(inquiry, "creator", None)
    if cr is not None and getattr(cr, "email", None):
        return [str(cr.email).strip()]
    cid = getattr(inquiry, "creator_id", None)
    if cid:
        u = User.objects.filter(id=cid).exclude(email__isnull=True).exclude(email="").first()
        if u and getattr(u, "email", None):
            return [str(u.email).strip()]

    cu = (getattr(inquiry, "create_user", None) or "").strip()
    if cu:
        u = User.objects.filter(username=cu).exclude(email__isnull=True).exclude(email="").first()
        if u and getattr(u, "email", None):
            return [str(u.email).strip()]

    return []


def send_quote_ended_notice_to_purchaser(inquiry, *, last_quotation_no: str = "") -> bool:
    """
    询价单进入「报价结束」时通知采购负责人（HTML 邮件 + EmailNotice 记录）。
    正文与主题由 ``emails/quote_ended_template.html`` 首行 ``<!-- email-subject: ... -->`` 解析。
    无有效收件人时跳过发送，返回 False。
    """
    from apps.pisadmin.basicinfo.views.email_template import (
        TEMPLATE_QUOTE_ENDED,
        build_context_quote_ended,
        render_email,
    )

    to_list = resolve_inquiry_purchaser_emails(inquiry)
    if not to_list:
        return False

    ctx = build_context_quote_ended(inquiry, last_quotation_no=last_quotation_no or "")
    subject, body = render_email(TEMPLATE_QUOTE_ENDED, ctx)

    notice = EmailNotice.objects.create(
        subject=subject,
        body=body,
        to_emails=to_list,
        cc_emails=[],
        bcc_emails=[],
        attachments=[],
        biz_type="inquiry_quote_ended",
        biz_id=getattr(inquiry, "inquiry_no", None) or "",
        status="pending",
        payload={
            "template_key": TEMPLATE_QUOTE_ENDED,
            "is_html": True,
            "inquiry_no": ctx.get("inquiry_no"),
            "supplier_count": ctx.get("supplier_count"),
            "completion_time": ctx.get("completion_time"),
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


def should_send_quote_timeout_reminder(inquiry_no: str, *, cooldown_hours: int = 24) -> bool:
    """
    同一询价单「询价截止提醒」在冷却期内不重复发送，避免供应商端多次刷新列表/详情导致采购重复收信。
    """
    key = (inquiry_no or "").strip()
    if not key:
        return False
    cutoff = timezone.now() - timedelta(hours=cooldown_hours)
    return not EmailNotice.objects.filter(
        biz_type="inquiry_quote_timeout",
        biz_id=key,
        status="success",
        sent_at__gte=cutoff,
    ).exists()


def send_quote_timeout_notice_to_purchaser(inquiry) -> bool:
    """
    询价截止提醒（HTML + EmailNotice）：由 ``notify_purchasers_quote_timeout_for_inquiries`` 在
    供应商端 ``POST .../quotation_master/sync_expired/`` 将超期未报价单置为已过期之后按需调用。
    正文与主题由 ``emails/quote_timeout_template.html`` 首行 ``<!-- email-subject: ... -->`` 解析。
    无有效收件人时跳过发送，返回 False。
    """
    from apps.pisadmin.basicinfo.views.email_template import (
        TEMPLATE_QUOTE_TIMEOUT,
        build_context_quote_timeout,
        render_email,
    )

    to_list = resolve_inquiry_purchaser_emails(inquiry)
    if not to_list:
        return False

    ctx = build_context_quote_timeout(inquiry)
    subject, body = render_email(TEMPLATE_QUOTE_TIMEOUT, ctx)

    notice = EmailNotice.objects.create(
        subject=subject,
        body=body,
        to_emails=to_list,
        cc_emails=[],
        bcc_emails=[],
        attachments=[],
        biz_type="inquiry_quote_timeout",
        biz_id=getattr(inquiry, "inquiry_no", None) or "",
        status="pending",
        payload={
            "template_key": TEMPLATE_QUOTE_TIMEOUT,
            "is_html": True,
            "inquiry_no": ctx.get("inquiry_no"),
            "quoted_count": ctx.get("quoted_count"),
            "invited_count": ctx.get("invited_count"),
            "deadline": ctx.get("deadline"),
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


def notify_purchasers_quote_timeout_for_inquiries(inquiry_nos: List[str]) -> int:
    """
    在供应商端 ``sync_expired`` 将超期未报价单置为已过期之后调用：对涉及询价单向采购负责人发送截止提醒邮件。
    返回成功发送的询价单数量（去重后、且受冷却期限制）。
    """
    from apps.pisadmin.miscprocurement.models import Inquiry

    unique = sorted({(x or "").strip() for x in inquiry_nos if x and str(x).strip()})
    sent = 0
    for inq_no in unique:
        if not should_send_quote_timeout_reminder(inq_no):
            continue
        inq = Inquiry.objects.filter(inquiry_no=inq_no).first()
        if not inq:
            continue
        try:
            if send_quote_timeout_notice_to_purchaser(inq):
                sent += 1
        except Exception:
            logger.exception("询价截止提醒邮件发送失败 inquiry_no=%s", inq_no)
    return sent


def send_bids_publish_notice_to_supplier(
    inquiry,
    supplier_group: Dict[str, Any],
    *,
    purchaser_company_name: str = "",
) -> Tuple[bool, EmailNotice]:
    """
    招标邀请邮件（单文件 ``bids_publish_template.html``）：向单个供应商分组发送 HTML 邮件并写入 EmailNotice。

    无有效收件人时仍创建 notice 并标记失败，返回 (False, notice)；成功发送返回 (True, notice)。
    """
    from apps.pisadmin.basicinfo.views.email_template import (
        TEMPLATE_BIDS_PUBLISH,
        build_context_bids_publish,
        render_email,
    )

    email = (supplier_group.get("contact_email") or "").strip()
    to_list = [email] if email else []

    ctx = build_context_bids_publish(
        inquiry,
        supplier_group,
        purchaser_company_name=purchaser_company_name or "",
    )
    subject, body = render_email(TEMPLATE_BIDS_PUBLISH, ctx)

    notice = EmailNotice.objects.create(
        subject=subject,
        body=body,
        to_emails=to_list,
        cc_emails=[],
        bcc_emails=[],
        attachments=[],
        biz_type="inquiry_bids_publish",
        biz_id=getattr(inquiry, "inquiry_no", None) or "",
        status="pending",
        payload={
            "template_key": TEMPLATE_BIDS_PUBLISH,
            "is_html": True,
            "inquiry_no": ctx.get("rfq_number"),
            "inquiry_title": ctx.get("inquiry_title"),
            "bid_time_range": ctx.get("bid_time_range"),
            "supplier_name": (supplier_group.get("supplier_name") or "").strip(),
        },
    )

    if not to_list:
        notice.status = "failed"
        notice.last_error = "缺少供应商邮箱"
        notice.save(update_fields=["status", "last_error", "update_datetime"])
        return False, notice

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
    return success, notice


def send_email_notice(notice) -> Tuple[bool, Dict[str, Any]]:
    """Send an email based on EmailNotice instance.

    Returns (success, details)
    """

    # 无认证中继（如内网 25 端口）允许 EMAIL_HOST_USER / EMAIL_HOST_PASSWORD 为空；Django SMTP 仅在两者均有值时 login
    host = (getattr(settings, "EMAIL_HOST", None) or "").strip()
    port_raw = getattr(settings, "EMAIL_PORT", None)
    if not host:
        return False, {"error": "邮件配置不完整：未配置 SMTP 主机 EMAIL_HOST"}
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        return False, {"error": "邮件配置不完整：EMAIL_PORT 无效"}
    if not (1 <= port <= 65535):
        return False, {"error": "邮件配置不完整：EMAIL_PORT 无效"}

    to_list = notice.to_emails or []
    cc_list = notice.cc_emails or []
    bcc_list = notice.bcc_emails or []
    if not to_list:
        return False, {"error": "收件人为空"}

    use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
    use_tls = getattr(settings, "EMAIL_USE_TLS", False)
    from_email = (getattr(settings, "EMAIL_FROM", None) or "").strip() or (
        (getattr(settings, "EMAIL_HOST_USER", None) or "").strip()
    )
    if not from_email:
        return False, {"error": "邮件配置不完整：请配置 EMAIL_FROM 或 EMAIL_HOST_USER 作为发件人"}

    try:
        connection = get_connection(
            fail_silently=False,
            host=host,
            port=port,
            use_ssl=use_ssl,
            use_tls=use_tls,
            timeout=20,
        )

        msg = EmailMessage(
            subject=notice.subject or "",
            body=notice.body or "",
            from_email=from_email,
            to=to_list,
            cc=cc_list,
            bcc=bcc_list,
            connection=connection,
        )

        payload = notice.payload or {}
        is_html = bool(payload.get("is_html") or payload.get("is_body_html"))
        if is_html:
            msg.content_subtype = "html"

        temp_files: List[str] = []
        try:
            paths = _collect_attachment_paths(notice.attachments)
            for path in paths:
                if not path:
                    continue
                try:
                    msg.attach_file(path)
                except Exception:
                    # 如果文件不可用，忽略该附件继续
                    continue
                if path.startswith(tempfile.gettempdir()):
                    temp_files.append(path)
            msg.send(fail_silently=False)
        finally:
            for f in temp_files:
                try:
                    os.remove(f)
                except Exception:
                    pass

        return True, {"message": "sent"}
    except Exception as exc:
        return False, {"error": str(exc)}


class EmailNoticeSerializer(CustomModelSerializer):
    to_emails = serializers.JSONField(required=False)
    cc_emails = serializers.JSONField(required=False)
    bcc_emails = serializers.JSONField(required=False)
    attachments = serializers.JSONField(required=False)
    payload = serializers.JSONField(required=False)
    response = serializers.JSONField(required=False)

    class Meta:
        model = EmailNotice
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime", "creator", "modifier"]

    def _ensure_list(self, value, field_name):
        if value is None:
            return []
        if isinstance(value, str):
            try:
                import json

                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            raise serializers.ValidationError(f"{field_name} must be a list")
        if not isinstance(value, list):
            raise serializers.ValidationError(f"{field_name} must be a list")
        return value

    def _ensure_dict(self, value, field_name):
        if value is None:
            return {}
        if isinstance(value, str):
            try:
                import json

                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            raise serializers.ValidationError(f"{field_name} must be a dict")
        if not isinstance(value, dict):
            raise serializers.ValidationError(f"{field_name} must be a dict")
        return value

    def validate_to_emails(self, value):
        return self._ensure_list(value, "to_emails")

    def validate_cc_emails(self, value):
        return self._ensure_list(value, "cc_emails")

    def validate_bcc_emails(self, value):
        return self._ensure_list(value, "bcc_emails")

    def validate_attachments(self, value):
        return self._ensure_list(value, "attachments")

    def validate_payload(self, value):
        return self._ensure_dict(value, "payload")

    def validate_response(self, value):
        return self._ensure_dict(value, "response")


class EmailNoticeViewSet(CustomModelViewSet):
    queryset = EmailNotice.objects.all()
    serializer_class = EmailNoticeSerializer
    filter_fields = ("subject", "status", "biz_type", "biz_id")
    search_fields = ("subject", "biz_type", "biz_id", "last_error", "message_id")
    ordering_fields = ("sent_at", "update_datetime", "create_datetime")
    ordering = ("-sent_at", "-update_datetime")

    def get_queryset(self):
        qs = super().get_queryset()
        params = getattr(self, "request", None)
        if not params:
            return qs

        raw_range = self.request.query_params.getlist("sent_at") or []
        if not raw_range:
            raw_value = self.request.query_params.get("sent_at")
            if raw_value:
                raw_range = raw_value.split(",") if "," in raw_value else raw_value.split("|")

        if len(raw_range) >= 2:
            start = parse_datetime(raw_range[0].strip())
            end = parse_datetime(raw_range[1].strip())
            if start and end:
                qs = qs.filter(sent_at__range=(start, end))

        return qs

    @action(detail=True, methods=["post"], url_path="resend")
    def resend(self, request, pk=None):
        notice = self.get_object()

        # update retry count and mark sending
        notice.retry_count = (notice.retry_count or 0) + 1
        notice.status = "sending"
        notice.save(update_fields=["retry_count", "status", "update_datetime"])

        success, detail = send_email_notice(notice)

        notice.response = detail
        if success:
            notice.status = "success"
            notice.sent_at = timezone.now()
            notice.last_error = None
        else:
            notice.status = "failed"
            notice.last_error = detail.get("error") if isinstance(detail, dict) else str(detail)

        notice.save(update_fields=["status", "sent_at", "response", "last_error", "update_datetime"])

        return Response({"success": success, "detail": detail})
