from typing import Optional

from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import action

from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse
from dvadmin.utils.viewset import CustomModelViewSet

from apps.pisadmin.miscprocurement.models import Inquiry, RFQOperationLogs
from apps.pissupplier.models import (
    QuotationMaster,
    QuotationAttachment,
    QuotationMaterial,
    QuotationProcess,
    QuotationOther,
    QuotationProfit,
    QuotationItem,
)
from apps.pissupplier.serializers import (
    QuotationMasterSerializer,
    QuotationMasterCreateUpdateSerializer,
    QuotationAttachmentSerializer,
    QuotationMaterialSerializer,
    QuotationProcessSerializer,
    QuotationOtherSerializer,
    QuotationProfitSerializer,
    QuotationItemSerializer,
)


class QuotationMasterViewSet(CustomModelViewSet):
    """杂采报价单主表管理接口

    详情 GET 与采购端比价弹窗「供应商报价预览」共用：返回 `QuotationMasterSerializer` 及嵌套材料/加工/其它/利润/上阶物料等。
    """

    queryset = QuotationMaster.objects.prefetch_related(
        "rfq_items",
        "material_costs",
        "process_costs",
        "other_costs",
        "profit_costs",
    )
    serializer_class = QuotationMasterSerializer
    create_serializer_class = QuotationMasterCreateUpdateSerializer
    update_serializer_class = QuotationMasterCreateUpdateSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["view_action"] = getattr(self, "action", None)
        return ctx
    filter_fields = (
        "quotation_no",
        "inquiry_no",
        "supplier_code",
        "supplier_name",
        "status",
        "is_awarded",
    )
    search_fields = (
        "quotation_no",
        "inquiry_no",
        "supplier_code",
        "supplier_name",
        "contact_person",
        "quoteuser",
        "remark",
    )
    ordering = ("-creattime", "-autoid")

    @action(methods=["post"], detail=False, url_path="sync_expired")
    def sync_expired(self, request):
        """
        将当前用户数据权限范围内、状态为待报价(1)或报价中(2)、且已超过报价截止时间的报价单
        更新为已过期(4)。若某询价单下已无任何待报价/报价中的报价单，且询价单仍为「发布」或「报价中」，
        则将该询价单置为「报价结束」(5)。供供应商端列表加载前调用。
        """
        now = timezone.now()
        qs = self.filter_queryset(self.get_queryset()).filter(
            status__in=(1, 2),
            quote_deadline__isnull=False,
            quote_deadline__lt=now,
        )
        inquiry_nos = list(qs.values_list("inquiry_no", flat=True).distinct())
        username = getattr(getattr(request, "user", None), "username", None)
        with transaction.atomic():
            updated = qs.update(status=4)
            inquiries_closed = Inquiry.sync_to_quote_closed_when_no_open_quotations(
                inquiry_nos,
                actor_username=username,
            )
        return SuccessResponse(
            data={"updated": updated, "inquiries_closed": inquiries_closed},
            msg="同步成功",
        )

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.status not in (1, 2):
        #     return ErrorResponse(msg="仅未报价/报价中状态可保存报价内容")
        # 含已报价(3)：采购端比价窗口可回写中标/议价等（仍不可改 status/quotetime，由序列化器剥离）
        if instance.status not in (1, 2, 3):
            return ErrorResponse(msg="当前报价单状态不允许保存")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # if instance.status not in (1, 2):
        #     return ErrorResponse(msg="仅未报价/报价中状态可保存报价内容")
        if instance.status not in (1, 2, 3):
            return ErrorResponse(msg="当前报价单状态不允许保存")
        return super().partial_update(request, *args, **kwargs)

    @staticmethod
    def _sync_inquiry_when_quotation_quoting(
        inquiry_no: str,
        *,
        actor_username: Optional[str] = None,
        quotation_no: Optional[str] = None,
    ):
        """
        任意报价单进入「报价中」(status=2) 时，若询价单仍为「发布」(3)，同步为「报价中」(4)。
        已进入报价中(4) 的询价单无需再改；不回退报价结束及之后状态。
        """
        inq_no = (inquiry_no or "").strip()
        if not inq_no:
            return
        inq = Inquiry.objects.filter(inquiry_no=inq_no, status=3).first()
        if not inq:
            return
        old_status = int(inq.status if inq.status is not None else 0)
        now = timezone.now()
        update_user = (str(actor_username).strip()[:20] if actor_username else None) or None
        inq.status = 4
        inq.update_time = now
        inq.update_datetime = now
        if update_user:
            inq.update_user = update_user
        inq.save(update_fields=["status", "update_time", "update_user", "update_datetime"])
        RFQOperationLogs.try_append(
            inquiry_no=inq.inquiry_no,
            purchase_type=int(inq.purchase_type),
            operation_type=6,
            operation_user=update_user,
            quotation_no=(quotation_no or "-")[:20],
            per_status=old_status,
            cur_status=4,
            operation_desc="供应商进入报价中，询价单同步为报价中",
        )

    @action(methods=["post"], detail=True, url_path="quote")
    def quote(self, request, pk=None):
        """进入报价中：写入当前时间为报价时间，状态为报价中(2)。仅未报价(status=1)可报价。"""
        instance = self.get_object()
        if instance.status not in (1, 2):
            return ErrorResponse(msg="仅未报价状态可进入报价中")
        dl = getattr(instance, "quote_deadline", None)
        if dl is not None and dl < timezone.now():
            return ErrorResponse(msg="已超过报价截止时间")
        instance.status = 2
        instance.quotetime = timezone.now()
        username = getattr(getattr(request, "user", None), "username", None)
        if username:
            instance.quoteuser = username
        with transaction.atomic():
            instance.save(update_fields=["status", "quotetime", "quoteuser"])
            self._sync_inquiry_when_quotation_quoting(
                instance.inquiry_no,
                actor_username=username,
                quotation_no=getattr(instance, "quotation_no", None),
            )
        serializer = self.get_serializer(instance)
        return DetailResponse(data=serializer.data, msg="报价中状态更新成功")

    @action(methods=["post"], detail=True, url_path="submit")
    def submit(self, request, pk=None):
        """正式提交报价：写入当前时间为报价时间，状态为已报价(3)。仅报价中(status=2)可提交。"""
        instance = self.get_object()
        if instance.status != 2:
            return ErrorResponse(msg="仅报价中状态可提交报价")
        dl = getattr(instance, "quote_deadline", None)
        if dl is not None and dl < timezone.now():
            return ErrorResponse(msg="已超过报价截止时间")
        instance.status = 3
        instance.quotetime = timezone.now()
        username = getattr(getattr(request, "user", None), "username", None)
        if username:
            instance.quoteuser = username
        inquiry_quote_closed = False
        with transaction.atomic():
            instance.save(update_fields=["status", "quotetime", "quoteuser"])
            inquiry_quote_closed = Inquiry.sync_to_quote_closed_when_all_suppliers_quoted(
                instance.inquiry_no,
                actor_username=username,
                quotation_no=getattr(instance, "quotation_no", None),
            )
        serializer = self.get_serializer(instance)
        payload = dict(serializer.data)
        payload["inquiry_quote_closed"] = inquiry_quote_closed
        msg = "提交成功" + ("，询价单已进入报价结束" if inquiry_quote_closed else "")
        return DetailResponse(data=payload, msg=msg)


class QuotationAttachmentViewSet(CustomModelViewSet):
    """杂采报价单附件管理接口"""

    queryset = QuotationAttachment.objects.all()
    serializer_class = QuotationAttachmentSerializer
    create_serializer_class = QuotationAttachmentSerializer
    update_serializer_class = QuotationAttachmentSerializer
    filter_fields = ("quotation_no", "part_id", "file_name")
    search_fields = ("quotation_no", "part_id", "file_name", "uploaduser")
    ordering = ("-autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class QuotationMaterialViewSet(CustomModelViewSet):
    """杂采报价单材料成本明细管理接口"""

    queryset = QuotationMaterial.objects.all()
    serializer_class = QuotationMaterialSerializer
    create_serializer_class = QuotationMaterialSerializer
    update_serializer_class = QuotationMaterialSerializer
    filter_fields = ("quotation_no", "part_id", "material_spec")
    search_fields = ("quotation_no", "part_id", "material_spec", "remark")
    ordering = ("autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class QuotationProcessViewSet(CustomModelViewSet):
    """杂采报价单加工成本明细管理接口"""

    queryset = QuotationProcess.objects.all()
    serializer_class = QuotationProcessSerializer
    create_serializer_class = QuotationProcessSerializer
    update_serializer_class = QuotationProcessSerializer
    filter_fields = ("quotation_no", "part_id", "process_station")
    search_fields = ("quotation_no", "part_id", "process_station", "remark")
    ordering = ("autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class QuotationOtherViewSet(CustomModelViewSet):
    """杂采报价单其他费用明细管理接口"""

    queryset = QuotationOther.objects.all()
    serializer_class = QuotationOtherSerializer
    create_serializer_class = QuotationOtherSerializer
    update_serializer_class = QuotationOtherSerializer
    filter_fields = ("quotation_no", "part_id")
    search_fields = ("quotation_no", "part_id")
    ordering = ("autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class QuotationProfitViewSet(CustomModelViewSet):
    """杂采报价单税率利润明细管理接口"""

    queryset = QuotationProfit.objects.all()
    serializer_class = QuotationProfitSerializer
    create_serializer_class = QuotationProfitSerializer
    update_serializer_class = QuotationProfitSerializer
    filter_fields = ("quotation_no", "part_id")
    search_fields = ("quotation_no", "part_id")
    ordering = ("autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class QuotationItemViewSet(CustomModelViewSet):
    """杂采报价单上阶物料明细管理接口"""

    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer
    create_serializer_class = QuotationItemSerializer
    update_serializer_class = QuotationItemSerializer
    filter_fields = ("quotation_no", "part_id", "product_name")
    search_fields = ("quotation_no", "part_id", "product_name")
    ordering = ("autoid",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
