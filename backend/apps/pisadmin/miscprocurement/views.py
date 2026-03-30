import logging
from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import serializers

from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse
from dvadmin.utils.viewset import CustomModelViewSet
from apps.pisadmin.basicinfo.models import Company, EmailNotice, SystemNoRule
from apps.pisadmin.basicinfo.views.email_template import (
    TEMPLATE_RFS_PUBLISH,
    build_context_rfs_publish,
    render_email,
)
from apps.pisadmin.basicinfo.views.email_utils import send_email_notice

from apps.pissupplier.models import (
    QuotationMaster,
    QuotationMaterial,
    QuotationProcess,
    QuotationOther,
    QuotationProfit,
    QuotationItem,
)

logger = logging.getLogger(__name__)


from .models import (
    MiscProcurementMaterialInfo,
    MiscProcurementStationInfo,
    MiscProcMaterial,
    MiscLowPriceHeader,
    MiscLowPriceDetail,
    MiscNegotiationRecords,
    RFQOperationLogs,
    Inquiry,
    InquirySupplier,
    InquiryAttachment,
    InquiryMaterialCost,
    InquiryProcessCost,
    InquiryOtherCost,
    InquiryProfitCost,
    InquiryRfqItem,
    CostEstimateTemplateHead,
    CostEstimateTemplateBody,
)
from .serializers import (
    MiscMaterialSerializer,
    MiscMaterialCreateUpdateSerializer,
    MiscStationSerializer,
    MiscStationCreateUpdateSerializer,
    MiscPartSerializer,
    MiscPartCreateUpdateSerializer,
    MiscLowPriceHeaderSerializer,
    MiscLowPriceDetailSerializer,
    MiscNegotiationRecordsSerializer,
    MiscNegotiationSaveSerializer,
    RFQOperationLogsSerializer,
    InquirySerializer,
    InquirySupplierSerializer,
    InquiryAttachmentSerializer,
    InquiryMaterialCostSerializer,
    InquiryProcessCostSerializer,
    InquiryOtherCostSerializer,
    InquiryProfitCostSerializer,
    InquiryRfqItemSerializer,
    CostEstimateTemplateHeadSerializer,
    CostEstimateTemplateNewVersionSerializer,
    create_cost_template_new_version,
)


def _negotiation_totals_from_quotation_item(quotation_no: str, part_id: str):
    """从杂采报价单上阶物料明细取议价前含税/不含税总价（与 part_id 匹配行）。"""
    if not quotation_no or not part_id:
        return None, None
    item = (
        QuotationItem.objects.filter(quotation_no=quotation_no, part_id=part_id)
        .order_by("autoid")
        .first()
    )
    if not item:
        return None, None
    return item.total_price_excl_tax, item.total_price_incl_tax


def _safe_decimal(v):
    if v is None:
        return None
    try:
        return Decimal(str(v))
    except Exception:
        return None


def _resolve_inquiry_primary_part_id(inquiry: Inquiry) -> str:
    """与采购端比价弹窗一致：上阶物料首行料号。"""
    first = InquiryRfqItem.objects.filter(inquiry_no=inquiry).order_by("id").first()
    if not first:
        return ""
    return (first.part_id or "").strip()


def _clip_price_str(value, max_len: int = 10) -> str:
    s = str(value).strip() if value is not None else ""
    return s[:max_len]


def _clip_field(value, max_len: int) -> str:
    return str(value or "").strip()[:max_len]


def _sync_misc_low_price_records(inquiry: Inquiry, part_id: str) -> None:
    """
    制程最低价落库（与比价展开明细一致）：
    - 询价单下**每个上阶物料料号**单独一套主/次表数据（多料号互不合并）。
    - **材料**：按「材料规格」各一行，取各供应商该规格 material_cost 的 min；次表为同规格下重量、单价 min。
    - **加工**：按「工站」各一行，取各供应商该工站 process_price 的 min（多工站互不合并）。
    - **其它**：包装费、运输费分列取 min（优先 sup_quotation_other；无则用上阶物料 total_other_expense 回退，两列同 min）。
    - **利润率**：cost_type=6，各报价单该料号利润率取 min。杂采不落库管销研（cost_type=5）。
    不写「整单材料成本/加工成本」汇总行，避免多规格/多工站被合并成一条。
    """
    inquiry_no = (inquiry.inquiry_no or "").strip()
    if not inquiry_no:
        return

    qm_qs = QuotationMaster.objects.filter(inquiry_no=inquiry_no).exclude(status=4)
    qn_list = list(qm_qs.values_list("quotation_no", flat=True))
    if not qn_list:
        return

    souce_ref = inquiry_no[:20]

    raw_parts = [
        str(x).strip()
        for x in InquiryRfqItem.objects.filter(inquiry_no=inquiry)
        .values_list("part_id", flat=True)
        .distinct()
        if x is not None and str(x).strip() != ""
    ]
    fallback = (part_id or "").strip()
    part_ids = raw_parts if raw_parts else ([fallback] if fallback else [])
    if not part_ids:
        return

    for pid in part_ids:
        MiscLowPriceHeader.objects.filter(inquiry_no=inquiry_no, part_id=pid).delete()
        MiscLowPriceDetail.objects.filter(inquiry_no=inquiry_no, part_id=pid).delete()

        # —— 材料：按材料规格一行；次表重量/单价 ——
        materials = QuotationMaterial.objects.filter(quotation_no__in=qm_qs, part_id=pid)
        by_spec: dict[str, list] = defaultdict(list)
        for m in materials:
            spec = (m.material_spec or "").strip() or "材料"
            by_spec[spec].append(m)

        for spec, rows in by_spec.items():
            costs = []
            for r in rows:
                if r.material_cost is not None:
                    try:
                        costs.append(Decimal(str(r.material_cost)))
                    except Exception:
                        continue
            if costs:
                MiscLowPriceHeader.objects.create(
                    inquiry_no=inquiry_no,
                    part_id=pid,
                    souce_no=souce_ref or None,
                    cost_type="1",
                    item_no=_clip_field(spec, 100),
                    min_price=_clip_price_str(min(costs)),
                )

            weights = []
            unit_prices = []
            for r in rows:
                if r.weight is not None:
                    try:
                        weights.append(Decimal(str(r.weight)))
                    except Exception:
                        pass
                if r.unit_price is not None:
                    try:
                        unit_prices.append(Decimal(str(r.unit_price)))
                    except Exception:
                        pass
            spec_key = _clip_field(spec, 50)
            if weights:
                MiscLowPriceDetail.objects.create(
                    inquiry_no=inquiry_no,
                    part_id=pid,
                    cost_type="1",
                    material_spec=spec_key,
                    item_no="1",
                    value=_clip_price_str(min(weights)),
                    souce_no=souce_ref,
                )
            if unit_prices:
                MiscLowPriceDetail.objects.create(
                    inquiry_no=inquiry_no,
                    part_id=pid,
                    cost_type="1",
                    material_spec=spec_key,
                    item_no="2",
                    value=_clip_price_str(min(unit_prices)),
                    souce_no=souce_ref,
                )

        # —— 加工：按工站一行（多工站互不合并）——
        processes = QuotationProcess.objects.filter(quotation_no__in=qm_qs, part_id=pid)
        by_station: dict[str, list] = defaultdict(list)
        for p in processes:
            st = (p.process_station or "").strip() or "工站"
            by_station[st].append(p)

        for station, rows in by_station.items():
            prices = []
            for r in rows:
                if r.process_price is not None:
                    try:
                        prices.append(Decimal(str(r.process_price)))
                    except Exception:
                        continue
            if prices:
                MiscLowPriceHeader.objects.create(
                    inquiry_no=inquiry_no,
                    part_id=pid,
                    souce_no=souce_ref or None,
                    cost_type="2",
                    item_no=_clip_field(station, 100),
                    min_price=_clip_price_str(min(prices)),
                )

        # —— 包装费 / 运输费（FK 用报价主表 QuerySet；兼容 part_id 大小写；无子表时回退上阶物料 total_other_expense）——
        others = QuotationOther.objects.filter(quotation_no__in=qm_qs).filter(
            Q(part_id=pid) | Q(part_id__iexact=(pid or "").strip())
        )
        pkg_vals = []
        tr_vals = []
        for o in others:
            if o.packaging_cost is not None:
                try:
                    pkg_vals.append(Decimal(str(o.packaging_cost)))
                except Exception:
                    pass
            if o.transportation_cost is not None:
                try:
                    tr_vals.append(Decimal(str(o.transportation_cost)))
                except Exception:
                    pass
        if not pkg_vals and not tr_vals:
            for qn in qn_list:
                it = (
                    QuotationItem.objects.filter(quotation_no=qn, part_id=pid).order_by("autoid").first()
                    or QuotationItem.objects.filter(quotation_no=qn).order_by("autoid").first()
                )
                if it is None or it.total_other_expense is None:
                    continue
                try:
                    v = Decimal(str(it.total_other_expense))
                except Exception:
                    continue
                pkg_vals.append(v)
                tr_vals.append(v)

        if pkg_vals:
            MiscLowPriceHeader.objects.create(
                inquiry_no=inquiry_no,
                part_id=pid,
                souce_no=souce_ref or None,
                cost_type="3",
                item_no="包装费",
                min_price=_clip_price_str(min(pkg_vals)),
            )
        if tr_vals:
            MiscLowPriceHeader.objects.create(
                inquiry_no=inquiry_no,
                part_id=pid,
                souce_no=souce_ref or None,
                cost_type="4",
                item_no="运输费",
                min_price=_clip_price_str(min(tr_vals)),
            )

        # —— 利润率 cost_type=6（杂采无管销研 cost_type=5，不落库）——
        pr_vals = []
        for qn in qn_list:
            it = QuotationItem.objects.filter(quotation_no=qn, part_id=pid).order_by("autoid").first()
            if it is None:
                it = QuotationItem.objects.filter(quotation_no=qn).order_by("autoid").first()
            if it is not None and it.profit_rate is not None and str(it.profit_rate).strip() != "":
                v = _safe_decimal(it.profit_rate)
                if v is not None:
                    pr_vals.append(v)
                    continue
            pf = QuotationProfit.objects.filter(quotation_no=qn, part_id=pid).order_by("autoid").first()
            if pf is not None and pf.profit_rate is not None:
                v = _safe_decimal(pf.profit_rate)
                if v is not None:
                    pr_vals.append(v)
        if pr_vals:
            MiscLowPriceHeader.objects.create(
                inquiry_no=inquiry_no,
                part_id=pid,
                souce_no=souce_ref or None,
                cost_type="6",
                item_no="利润率",
                min_price=_clip_price_str(min(pr_vals)),
            )


class MiscMaterialViewSet(CustomModelViewSet):
    queryset = MiscProcurementMaterialInfo.objects.all()
    serializer_class = MiscMaterialSerializer
    create_serializer_class = MiscMaterialCreateUpdateSerializer
    update_serializer_class = MiscMaterialCreateUpdateSerializer
    search_fields = ["materialtype", "factory"]
    ordering = ["-create_datetime"]


class MiscStationViewSet(CustomModelViewSet):
    queryset = MiscProcurementStationInfo.objects.all()
    serializer_class = MiscStationSerializer
    create_serializer_class = MiscStationCreateUpdateSerializer
    update_serializer_class = MiscStationCreateUpdateSerializer
    search_fields = ["stationname", "stationcode", "company_code"]
    ordering = ["-create_datetime"]


class MiscPartViewSet(CustomModelViewSet):
    queryset = MiscProcMaterial.objects.all()
    serializer_class = MiscPartSerializer
    create_serializer_class = MiscPartCreateUpdateSerializer
    update_serializer_class = MiscPartCreateUpdateSerializer
    search_fields = ["partid", "partid_name", "company_code"]
    ordering = ["-create_datetime"]


class CostEstimateTemplateViewSet(CustomModelViewSet):
    """成本估算模板主表；status：0 未确认 / 1 已确认 / 2 作废（列表默认不含作废）。"""

    queryset = CostEstimateTemplateHead.objects.all()
    serializer_class = CostEstimateTemplateHeadSerializer
    filter_fields = ("template_no", "template_name", "procurement_category", "is_bom", "acti", "version", "status")
    search_fields = ("template_no", "template_name", "template_desc")
    ordering = ("-update_time", "-id")

    # 与 models.CostEstimateTemplateHead.STATUS_CHOICES 中「作废」取值一致
    TEMPLATE_STATUS_VOID = 2
    TEMPLATE_STATUS_DRAFT = 0
    TEMPLATE_STATUS_CONFIRMED = 1

    @staticmethod
    def _head_status_value(instance) -> int:
        # status 为 0（未确认）时不能使用 (value or -1)，否则 0 会被当成 falsy 变成 -1
        v = getattr(instance, "status", None)
        if v is None:
            return -1
        try:
            return int(v)
        except (TypeError, ValueError):
            return -1

    def get_queryset(self):
        qs = super().get_queryset()
        # 仅列表默认隐藏作废；retrieve/update 等需能按 id 加载作废行（否则筛选作废后无法查看详情）
        if getattr(self, "action", None) != "list":
            return qs
        params = getattr(self.request, "query_params", getattr(self.request, "GET", {}))
        status_raw = params.get("status")
        # 列表默认不展示作废；查询区显式选「状态=作废」时传 status=2，不过滤以便列出作废行
        if status_raw is not None and str(status_raw).strip() != "":
            try:
                st = int(status_raw)
            except (TypeError, ValueError):
                return qs.exclude(status=self.TEMPLATE_STATUS_VOID)
            if st == self.TEMPLATE_STATUS_VOID:
                return qs
        return qs.exclude(status=self.TEMPLATE_STATUS_VOID)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        st = self._head_status_value(instance)
        if st == self.TEMPLATE_STATUS_VOID:
            return ErrorResponse(msg="模板已作废，不可修改")
        if st == self.TEMPLATE_STATUS_CONFIRMED:
            return ErrorResponse(msg="已确认模板不可修改")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        st = self._head_status_value(instance)
        if st == self.TEMPLATE_STATUS_VOID:
            return ErrorResponse(msg="模板已作废，不可修改")
        if st == self.TEMPLATE_STATUS_CONFIRMED:
            return ErrorResponse(msg="已确认模板不可修改")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return ErrorResponse(msg="成本模板不允许删除")

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        return ErrorResponse(msg="成本模板不允许删除")

    @action(methods=['post'], detail=True)
    def confirm(self, request, *args, **kwargs):
        """未确认(0) → 已确认(1)。同模板编号下 version 低于当前行的非作废主表行一律改为作废(2)。"""
        instance = self.get_object()
        cur = self._head_status_value(instance)
        if cur == self.TEMPLATE_STATUS_VOID:
            return ErrorResponse(msg="作废模板不可确认")
        if cur != self.TEMPLATE_STATUS_DRAFT:
            return ErrorResponse(msg="仅未确认状态的模板可确认")
        now = timezone.now()
        username = getattr(getattr(request, "user", None), "username", None) or ""
        uname = str(username)[:20] if username else ""

        with transaction.atomic():
            qs_old = CostEstimateTemplateHead.objects.filter(
                template_no=instance.template_no,
                version__lt=instance.version,
            ).exclude(status=self.TEMPLATE_STATUS_VOID)
            voided_count = qs_old.count()
            upd = {"status": self.TEMPLATE_STATUS_VOID, "update_time": now}
            if uname:
                upd["update_user"] = uname
            qs_old.update(**upd)

            instance.status = self.TEMPLATE_STATUS_CONFIRMED
            instance.update_time = now
            if uname:
                instance.update_user = uname
            instance.save(update_fields=["status", "update_time", "update_user"])

        serializer = self.get_serializer(instance)
        msg = "确认成功，已作废旧版本" if voided_count else "确认成功"
        return DetailResponse(data=serializer.data, msg=msg)

    @action(methods=["post"], detail=True, url_path="new_version")
    def new_version(self, request, *args, **kwargs):
        """已确认模板派生新版本：同 template_no，version=max+1，status=0；请求体校验见 CostEstimateTemplateNewVersionSerializer。"""
        source = self.get_object()
        if self._head_status_value(source) != self.TEMPLATE_STATUS_CONFIRMED:
            return ErrorResponse(msg="仅已确认模板可创建新版本")
        sz = CostEstimateTemplateNewVersionSerializer(data=request.data, context={"request": request})
        if not sz.is_valid():
            return ErrorResponse(msg="参数校验失败", data=sz.errors)
        try:
            head = create_cost_template_new_version(source, sz.validated_data, request)
        except serializers.ValidationError as e:
            detail = getattr(e, "detail", None)
            if isinstance(detail, dict):
                first_msg = None
                for v in detail.values():
                    if isinstance(v, list) and v:
                        first_msg = str(v[0])
                        break
                    if isinstance(v, str) and v.strip():
                        first_msg = v.strip()
                        break
                return ErrorResponse(msg=first_msg or "创建新版本失败", data=detail)
            return ErrorResponse(msg=str(detail or e))
        out = CostEstimateTemplateHeadSerializer(head, context={"request": request})
        return DetailResponse(data=out.data, msg="新版本创建成功")


class InquiryViewSet(CustomModelViewSet):
    """
    杂采询价单 CRUD/发布等。

    与供应商报价单联动：当 `pissupplier.QuotationMasterViewSet.sync_expired` 将超时报价置为已过期后，
    若该询价下已无待报价/报价中的报价单，且主表状态仍为「发布」(3) 或「报价中」(4)，
    会由 `Inquiry.sync_to_quote_closed_when_no_open_quotations` 将询价单置为「报价结束」(5)。
    """

    queryset = Inquiry.objects.all().prefetch_related(
        "suppliers",
        "attachments",
        "material_costs",
        "process_costs",
        "other_costs",
        "profit_costs",
        "rfq_items",
    )
    serializer_class = InquirySerializer
    filter_fields = (
        "inquiry_no",
        "title",
        "purchase_type",
        "template",
        "template_version",
        "status",
        "buyer",
        "buying_method",
    )
    search_fields = ("inquiry_no", "title", "material_type", "buyer", "remark")
    ordering = ("-update_datetime",)

    STATUS_OPEN = 1
    STATUS_CONFIRMED = 2
    STATUS_PUBLISHED = 3
    STATUS_QUOTING = 4
    STATUS_QUOTE_ENDED = 5
    STATUS_BARGaining = 6
    STATUS_NEGOTIATED = 7
    STATUS_PRICE_REVIEW = 7
    STATUS_APPROVED = 8
    STATUS_AWARDED = 9
    STATUS_VOID = 0
    TEMPLATE_PREFILL_FIELD_MAP = {
        "1": {
            "material": "material_spec",
            "materialspec": "material_spec",
            "length": "length",
            "width": "width",
            "height": "height",
            "specificgravity": "specific_gravity",
            "qty": "qty",
            "unitprice": "unit_price",
            "materialcost": "material_cost",
            "weight": "weight",
            "remark": "remark",
        },
        "2": {
            "processstation": "process_station",
            "unit": "unit",
            "unitrate": "unit_rate",
            "processqty": "process_qty",
            "processprice": "process_price",
            "remark": "remark",
        },
        "3": {
            "packagingcost": "packaging_cost",
            "transportationcost": "transportation_cost",
        },
        "5": {
            "profitrate": "profit_rate",
        },
        "6": {
            "taxrate": "tax_rate",
        },
        "7": {
            "partno": "part_id",
            "desc": "product_name",
            "productname": "product_name",
            "unit": "unit",
            "qty": "qty",
            "price": "unit_price",
            "unitprice": "unit_price",
            "amount": "product_cost",
            "totalmaterialcost": "total_material_cost",
            "totalprocessingcost": "total_processing_cost",
            "totalotherexpense": "total_other_expense",
            "totalopexamt": "total_opex_amt",
            "profitrate": "profit_rate",
            "taxrate": "tax_rate",
            "totalpriceexcltax": "total_price_excl_tax",
            "totalpriceincltax": "total_price_incl_tax",
        },
    }

    @staticmethod
    def _clip(value, max_length):
        text = str(value or "").strip()
        return text[:max_length]

    @staticmethod
    def _normalize_template_key(value):
        text = str(value or "").strip().lower()
        return "".join(ch for ch in text if ch.isalnum())

    def _get_request_username(self) -> str:
        user = getattr(self.request, "user", None)
        if not user:
            return ""
        return (
            getattr(user, "username", "")
            or getattr(user, "name", "")
            or getattr(user, "nick_name", "")
            or getattr(user, "nickname", "")
            or ""
        )

    def _ensure_editable(self, instance):
        if int(getattr(instance, "status", self.STATUS_OPEN) or self.STATUS_OPEN) != self.STATUS_OPEN:
            return ErrorResponse(msg="当前询价单状态仅允许查看，不允许编辑或删除；如需修改请先还原为“开立”")
        return None

    def _save_status(
        self,
        instance,
        *,
        status,
        confirm_user=None,
        confirm_time=None,
        release_user=None,
        release_time=None,
        comparison_user=None,
        comparison_time=None,
        operation_type=None,
        operation_desc=None,
    ):
        old_status = int(instance.status if instance.status is not None else 0)
        current_time = timezone.now()
        current_user = self._get_request_username() or getattr(instance, "update_user", None)
        instance.status = status
        instance.confirm_user = confirm_user
        instance.confirm_time = confirm_time
        instance.release_user = release_user
        instance.release_time = release_time
        if comparison_user is not None:
            instance.comparison_user = comparison_user
        if comparison_time is not None:
            instance.comparison_time = comparison_time
        instance.update_user = current_user
        instance.update_time = current_time
        instance.save(
            update_fields=[
                "status",
                "confirm_user",
                "confirm_time",
                "release_user",
                "release_time",
                "comparison_user",
                "comparison_time",
                "update_user",
                "update_time",
            ]
        )
        new_status = int(status)
        if operation_type is not None and old_status != new_status:
            RFQOperationLogs.try_append(
                inquiry_no=instance.inquiry_no,
                purchase_type=int(instance.purchase_type),
                operation_type=operation_type,
                operation_user=current_user or None,
                quotation_no="-",
                per_status=old_status,
                cur_status=new_status,
                operation_desc=operation_desc,
            )
        serializer = self.get_serializer(instance)
        return DetailResponse(data=serializer.data, msg="状态更新成功")

    def _generate_quotation_numbers(self, count: int, inquiry: Inquiry):
        """
        杂采报价单号：复用 `SystemNoRule`（rule_code=miscQTS），与询价单 miscRFS 同源取号逻辑。
        company_code 优先询价单字段，否则「通用」厂区。
        """
        if count <= 0:
            return []
        company_code = (getattr(inquiry, "company_code", None) or "").strip() or SystemNoRule.DEFAULT_SYSTEM_NO_COMPANY_CODE
        username = self._get_request_username() or None
        return SystemNoRule.allocate_system_numbers(
            company_code,
            "miscQTS",
            count,
            username=username,
            now=timezone.now(),
        )

    def _get_template_prefill_fields(self, template_no, template_version=None):
        """
        根据询价单关联的成本模板（Inquiry.template = template_no，Inquiry.template_version = 主表 version），
        找出「发布生成报价单时」允许从询价单带入到报价子表的字段名集合。

        满足以下任一条件时，对应映射字段进入集合（从询价单带入报价子表），否则为空值（见 _pick_prefill_value）：
        - is_computed == 1（系统自动计算/带出）
        - supplier_required == 1（带出不可修改）或 2（带出可修改）

        template_version 为空时兼容旧数据：取该编号下「已确认」主表的最高 version。
        """
        if not template_no:
            return {}

        tn = str(template_no).strip()
        base_qs = CostEstimateTemplateHead.objects.filter(template_no=tn, status=1)
        head = None
        if template_version is not None and template_version != "":
            try:
                ver = int(template_version)
            except (TypeError, ValueError):
                ver = None
            if ver is not None:
                head = base_qs.filter(version=ver).first()
        if head is None:
            head = base_qs.order_by("-version", "-id").first()
        if not head:
            return {}

        prefill_fields = {}
        queryset = CostEstimateTemplateBody.objects.filter(
            template_no=head.template_no,
            version=head.version,
        ).filter(Q(is_computed=1) | Q(supplier_required__in=(1, 2))).values(
            "cost_category", "item_no", "item_name_cn"
        )

        for row in queryset:
            cost_category = str(row.get("cost_category") or "").strip()
            mapping = self.TEMPLATE_PREFILL_FIELD_MAP.get(cost_category, {})
            raw_keys = [row.get("item_no"), row.get("item_name_cn")]
            for raw_key in raw_keys:
                normalized = self._normalize_template_key(raw_key)
                target_field = mapping.get(normalized)
                if target_field:
                    prefill_fields.setdefault(cost_category, set()).add(target_field)
        return prefill_fields

    @staticmethod
    def _pick_prefill_value(prefill_fields, cost_category, field_name, source_value, empty_default=None):
        category_fields = prefill_fields.get(str(cost_category), set())
        if field_name in category_fields:
            return source_value
        return empty_default

    @staticmethod
    def _resolve_purchaser_company_name(inquiry: Inquiry) -> str:
        code = (getattr(inquiry, "company_code", None) or "").strip()
        if code:
            row = Company.objects.filter(company_code=code).only("company_name", "company_short_name").first()
            if row:
                return (row.company_name or row.company_short_name or code).strip()
            return code
        return ""

    def _group_inquiry_suppliers(self, inquiry: Inquiry):
        """
        按询价单供应商子表 `InquirySupplier` 汇总：同一 `supplier_code`（空代码时用行级占位）合并多料号 `part_id`，
        供 `_create_supplier_quotations` 为每个供应商生成一份 `QuotationMaster`。
        返回条目的 supplier_code / supplier_name / 联系人字段均来自子表行数据（截断至报价主表字段长度）。
        """
        supplier_map = {}
        for row in inquiry.suppliers.all():
            clipped_code = self._clip(row.supplier_code, 20)
            # 与 key 一致：无代码时用行级占位，保证写入 QuotationMaster.supplier_code 非空（序列化必填）
            key = clipped_code or f"SUP-{row.id}"
            current = supplier_map.setdefault(
                key,
                {
                    "supplier_code": clipped_code or key,
                    "supplier_name": self._clip(row.supplier_name, 20),
                    "contact_person": self._clip(row.contact_person, 20),
                    "contact_phone": self._clip(row.contact_phone, 20),
                    "contact_email": self._clip(row.contact_email, 20),
                    "part_ids": set(),
                },
            )
            current["part_ids"].add(row.part_id)
            # 合并多行时：若后续行补全了真实供应商代码，覆盖 SUP-* 占位
            if clipped_code and (
                not current.get("supplier_code")
                or str(current["supplier_code"]).startswith("SUP-")
            ):
                current["supplier_code"] = clipped_code
            if not current["supplier_name"] and row.supplier_name:
                current["supplier_name"] = self._clip(row.supplier_name, 20)
            if not current["contact_person"] and row.contact_person:
                current["contact_person"] = self._clip(row.contact_person, 20)
            if not current["contact_phone"] and row.contact_phone:
                current["contact_phone"] = self._clip(row.contact_phone, 20)
            if not current["contact_email"] and row.contact_email:
                current["contact_email"] = self._clip(row.contact_email, 20)
        groups = list(supplier_map.values())
        for g in groups:
            # 子表未填名称时，用已确定的代码占位，避免报价主表 supplier_name 为空串
            if not (g.get("supplier_name") or "").strip():
                g["supplier_name"] = self._clip(g.get("supplier_code") or "", 20)
        return groups

    def _ensure_inquiry_has_supplier_groups(self, inquiry: Inquiry, *, empty_message: str):
        """
        仅在「确认」时调用：供应商子表经 `_group_inquiry_suppliers` 汇总后须非空。
        「发布」仅允许在已确认后进行，不再重复校验名单（与业务约定一致）。
        """
        groups = self._group_inquiry_suppliers(inquiry)
        if not groups:
            raise serializers.ValidationError(empty_message)
        return groups

    def _create_supplier_quotations(self, inquiry: Inquiry):
        """
        询价单发布：按供应商子表汇总结果，为每个供应商创建一张 `QuotationMaster`（及子表明细），
        主表 `supplier_code`、`supplier_name` 与联系人信息与 `InquirySupplier` 对应数据一致（见 `_group_inquiry_suppliers`）。
        名单是否在空已在确认环节校验，此处不再校验。
        """
        supplier_groups = self._group_inquiry_suppliers(inquiry)

        QuotationMaster.objects.filter(inquiry_no=inquiry.inquiry_no).delete()

        quotation_numbers = self._generate_quotation_numbers(len(supplier_groups), inquiry)
        prefill_fields = self._get_template_prefill_fields(
            getattr(inquiry, "template", None),
            getattr(inquiry, "template_version", None),
        )
        current_user = self._clip(
            self._get_request_username() or getattr(inquiry, "release_user", None),
            20,
        ) or None
        current_time = timezone.now()
        # 招标(2)：供应商端报价单沿用「投标截止时间」作为有效报价截止；询价(1)用主表 quote_deadline。
        quote_deadline = inquiry.quote_deadline
        if int(getattr(inquiry, "buying_method", 1) or 1) == 2:
            quote_deadline = getattr(inquiry, "bid_end_time", None) or quote_deadline

        inquiry_materials = list(inquiry.material_costs.all())
        inquiry_processes = list(inquiry.process_costs.all())
        inquiry_others = list(inquiry.other_costs.all())
        inquiry_profits = list(inquiry.profit_costs.all())
        inquiry_items = list(inquiry.rfq_items.all())

        material_bulk = []
        process_bulk = []
        other_bulk = []
        profit_bulk = []
        item_bulk = []

        for quotation_no, supplier in zip(quotation_numbers, supplier_groups):
            # 主表供应商字段与 InquirySupplier 子表一致（已由 _group_inquiry_suppliers 从子表汇总）
            quotation = QuotationMaster.objects.create(
                quotation_no=quotation_no,
                inquiry_no=inquiry.inquiry_no,
                supplier_code=supplier["supplier_code"],
                supplier_name=supplier["supplier_name"],
                contact_person=supplier["contact_person"] or None,
                contact_phone=supplier["contact_phone"] or None,
                contact_email=supplier["contact_email"] or None,
                quote_deadline=quote_deadline,
                buying_method=getattr(inquiry, "buying_method", None),
                bid_start_time=getattr(inquiry, "bid_start_time", None),
                bid_end_time=getattr(inquiry, "bid_end_time", None),
                delivery_days=getattr(inquiry, "lead_time_days", None),
                payment_method=getattr(inquiry, "payment_method", None),
                status=1,
                is_awarded=0,
                createuser=current_user,
                creattime=current_time,
                remark=None,
            )
            part_ids = supplier["part_ids"]

            for row in inquiry_materials:
                if row.part_id in part_ids:
                    material_spec_src = self._pick_prefill_value(
                        prefill_fields, "1", "material_spec", row.material_spec, empty_default=""
                    )
                    material_bulk.append(
                        QuotationMaterial(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            material_spec=self._clip(material_spec_src or "", 20),
                            length=self._pick_prefill_value(prefill_fields, "1", "length", row.length),
                            width=self._pick_prefill_value(prefill_fields, "1", "width", row.width),
                            height=self._pick_prefill_value(prefill_fields, "1", "height", row.height),
                            unit_price=self._pick_prefill_value(prefill_fields, "1", "unit_price", row.unit_price),
                            qty=self._pick_prefill_value(prefill_fields, "1", "qty", row.qty),
                            specific_gravity=self._pick_prefill_value(
                                prefill_fields, "1", "specific_gravity", row.specific_gravity
                            ),
                            material_cost=self._pick_prefill_value(prefill_fields, "1", "material_cost", row.material_cost),
                            weight=self._pick_prefill_value(prefill_fields, "1", "weight", row.weight),
                            remark=self._pick_prefill_value(prefill_fields, "1", "remark", row.remark),
                            option_json=row.option_json if prefill_fields.get("1") else None,
                        )
                    )

            for row in inquiry_processes:
                if row.part_id in part_ids:
                    process_station_src = self._pick_prefill_value(
                        prefill_fields, "2", "process_station", row.process_station
                    )
                    process_bulk.append(
                        QuotationProcess(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            process_station=self._clip(process_station_src, 20) if process_station_src else None,
                            unit=self._pick_prefill_value(prefill_fields, "2", "unit", row.unit),
                            unit_rate=self._pick_prefill_value(prefill_fields, "2", "unit_rate", row.unit_rate),
                            process_qty=self._pick_prefill_value(prefill_fields, "2", "process_qty", row.process_qty),
                            process_price=self._pick_prefill_value(prefill_fields, "2", "process_price", row.process_price),
                            remark=self._pick_prefill_value(prefill_fields, "2", "remark", row.remark),
                            option_json=row.option_json if prefill_fields.get("2") else None,
                        )
                    )

            for row in inquiry_others:
                if row.part_id in part_ids:
                    other_bulk.append(
                        QuotationOther(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            packaging_cost=self._pick_prefill_value(prefill_fields, "3", "packaging_cost", row.packaging_cost),
                            transportation_cost=self._pick_prefill_value(prefill_fields, "3", "transportation_cost", row.transportation_cost),
                        )
                    )

            for row in inquiry_profits:
                if row.part_id in part_ids:
                    profit_bulk.append(
                        QuotationProfit(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            tax_rate=self._pick_prefill_value(prefill_fields, "6", "tax_rate", row.tax_rate),
                            profit_rate=self._pick_prefill_value(prefill_fields, "5", "profit_rate", row.profit_rate),
                        )
                    )

            for row in inquiry_items:
                if row.part_id in part_ids:
                    # 上阶物料核心字段与询价 `InquiryRfqItem` 一致，发布时始终带入报价单（不依赖模板 prefill 是否勾选「产品明细」列）
                    product_name_src = row.product_name
                    unit_src = row.unit
                    qty_src = row.qty
                    unit_price_src = row.unit_price
                    item_bulk.append(
                        QuotationItem(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            product_name=self._clip(product_name_src or "", 20),
                            unit=self._clip(unit_src or "", 10),
                            qty=int(qty_src) if qty_src is not None else 0,
                            is_bom=row.is_bom or 0,
                            unit_price=unit_price_src,
                            product_cost=self._pick_prefill_value(prefill_fields, "7", "product_cost", None),
                            total_material_cost=self._pick_prefill_value(prefill_fields, "7", "total_material_cost", row.total_material_cost),
                            total_processing_cost=self._pick_prefill_value(prefill_fields, "7", "total_processing_cost", row.total_processing_cost),
                            total_other_expense=self._pick_prefill_value(prefill_fields, "7", "total_other_expense", row.total_other_expense),
                            total_opex_amt=self._pick_prefill_value(prefill_fields, "7", "total_opex_amt", row.total_opex_amt),
                            profit_rate=self._pick_prefill_value(prefill_fields, "7", "profit_rate", row.profit_rate),
                            total_price_excl_tax=self._pick_prefill_value(prefill_fields, "7", "total_price_excl_tax", row.total_price_excl_tax),
                            tax_rate=self._pick_prefill_value(prefill_fields, "7", "tax_rate", row.tax_rate),
                            total_price_incl_tax=self._pick_prefill_value(prefill_fields, "7", "total_price_incl_tax", row.total_price_incl_tax),
                            is_awarded=0,
                            winning_bid_price=None,
                        )
                    )

        if material_bulk:
            QuotationMaterial.objects.bulk_create(material_bulk)
        if process_bulk:
            QuotationProcess.objects.bulk_create(process_bulk)
        if other_bulk:
            QuotationOther.objects.bulk_create(other_bulk)
        if profit_bulk:
            QuotationProfit.objects.bulk_create(profit_bulk)
        if item_bulk:
            QuotationItem.objects.bulk_create(item_bulk)

    def perform_create(self, serializer):
        inquiry = serializer.save()
        RFQOperationLogs.try_append(
            inquiry_no=inquiry.inquiry_no,
            purchase_type=int(inquiry.purchase_type),
            operation_type=1,
            operation_user=self._get_request_username() or None,
            quotation_no="-",
            per_status=None,
            cur_status=int(inquiry.status) if inquiry.status is not None else 1,
            operation_desc="询价单创建",
        )

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        blocked = self._ensure_editable(instance)
        if blocked:
            return blocked
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        blocked = self._ensure_editable(instance)
        if blocked:
            return blocked
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        blocked = self._ensure_editable(instance)
        if blocked:
            return blocked
        return super().destroy(request, *args, **kwargs)

    @action(methods=["delete"], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        keys = request.data.get("keys", None)
        if not keys:
            return ErrorResponse(msg="未获取到keys字段")
        locked = self.get_queryset().filter(id__in=keys).exclude(status=self.STATUS_OPEN)
        if locked.exists():
            return ErrorResponse(msg="仅“开立”状态的询价单允许删除")
        self.get_queryset().filter(id__in=keys).delete()
        return SuccessResponse(data=[], msg="删除成功")

    @action(methods=["put"], detail=True)
    def confirm(self, request, pk=None):
        instance = self.get_object()
        if int(instance.status or self.STATUS_OPEN) != self.STATUS_OPEN:
            return ErrorResponse(msg="只有“开立”状态的询价单才能确认")
        try:
            self._ensure_inquiry_has_supplier_groups(
                instance, empty_message="请先维护询价单供应商名单后再确认"
            )
        except serializers.ValidationError as exc:
            detail = getattr(exc, "detail", None)
            if isinstance(detail, (list, tuple)) and detail:
                msg = str(detail[0])
            else:
                msg = str(detail or exc)
            return ErrorResponse(msg=msg)
        current_user = self._get_request_username() or None
        current_time = timezone.now()
        return self._save_status(
            instance,
            status=self.STATUS_CONFIRMED,
            confirm_user=current_user,
            confirm_time=current_time,
            release_user=getattr(instance, "release_user", None),
            release_time=getattr(instance, "release_time", None),
            operation_type=2,
            operation_desc="询价单确认",
        )

    @action(methods=["put"], detail=True)
    def restore(self, request, pk=None):
        instance = self.get_object()
        if int(instance.status or self.STATUS_OPEN) != self.STATUS_CONFIRMED:
            return ErrorResponse(msg='只有“确认”状态的询价单才能还原为“开立”')
        return self._save_status(
            instance,
            status=self.STATUS_OPEN,
            confirm_user=None,
            confirm_time=None,
            release_user=None,
            release_time=None,
            operation_type=4,
            operation_desc="询价单还原为开立",
        )

    @action(methods=["put"], detail=True)
    def publish(self, request, pk=None):
        instance = self.get_object()
        if int(instance.status or self.STATUS_OPEN) != self.STATUS_CONFIRMED:
            return ErrorResponse(msg='只有“确认”状态的询价单才能发布')
        current_user = self._get_request_username() or None
        current_time = timezone.now()
        try:
            with transaction.atomic():
                self._create_supplier_quotations(instance)  # 发布询价单时按供应商关联表，逐个创建对应的报价单
                self._notify_vendors_on_publish(instance)  # 与子表汇总结果一致，逐供应商发送发布邮件
                return self._save_status(
                    instance,
                    status=self.STATUS_PUBLISHED,
                    confirm_user=getattr(instance, "confirm_user", None),
                    confirm_time=getattr(instance, "confirm_time", None),
                    release_user=current_user,
                    release_time=current_time,
                    operation_type=3,
                    operation_desc="询价单发布",
                )
        except serializers.ValidationError as exc:
            detail = getattr(exc, "detail", None)
            if isinstance(detail, (list, tuple)) and detail:
                msg = str(detail[0])
            else:
                msg = str(detail or exc)
            return ErrorResponse(msg=msg)

    @action(methods=["put"], detail=True)
    def start_bargaining(self, request, pk=None):
        """开启比价议价：从报价结束状态进入比议价中；并写入比价-制程最低价主/次表。"""
        instance = self.get_object()
        if int(instance.status or self.STATUS_PUBLISHED) not in (self.STATUS_PUBLISHED, self.STATUS_QUOTING, self.STATUS_QUOTE_ENDED):
            return ErrorResponse(msg='只有“发布”或“报价结束”状态的询价单才能开启比价')
        current_user = self._get_request_username() or None
        current_time = timezone.now()
        part_id = _resolve_inquiry_primary_part_id(instance)
        try:
            with transaction.atomic():
                if part_id:
                    _sync_misc_low_price_records(instance, part_id)
                else:
                    logger.warning(
                        "start_bargaining: 询价单无上阶物料料号，跳过制程最低价落库 inquiry_no=%s",
                        instance.inquiry_no,
                    )
                return self._save_status(
                    instance,
                    status=self.STATUS_BARGaining,
                    confirm_user=getattr(instance, "confirm_user", None),
                    confirm_time=getattr(instance, "confirm_time", None),
                    release_user=getattr(instance, "release_user", None),
                    release_time=getattr(instance, "release_time", None),
                    comparison_user=current_user,
                    comparison_time=current_time,
                    operation_type=7,
                    operation_desc="开启比议价",
                )
        except Exception as exc:
            logger.exception("start_bargaining 写入制程最低价失败")
            return ErrorResponse(msg=f"开启比价失败：{exc}")

    @action(methods=["put"], detail=True)
    def confirm_negotiation(self, request, pk=None):
        """确认议价：从比议价中进入议价确认/价格审核"""
        instance = self.get_object()
        if int(instance.status or self.STATUS_BARGaining) != self.STATUS_BARGaining:
            return ErrorResponse(msg='只有“比议价中”状态的询价单才能确认议价')
        part_id = _resolve_inquiry_primary_part_id(instance)
        if not part_id:
            return ErrorResponse(msg="询价单无上阶物料料号，无法确认比价")
        try:
            with transaction.atomic():
                _sync_misc_low_price_records(instance, part_id)
                return self._save_status(
                    instance,
                    status=self.STATUS_NEGOTIATED,
                    confirm_user=getattr(instance, "confirm_user", None),
                    confirm_time=getattr(instance, "confirm_time", None),
                    release_user=getattr(instance, "release_user", None),
                    release_time=getattr(instance, "release_time", None),
                    comparison_user=getattr(instance, "comparison_user", None),
                    comparison_time=getattr(instance, "comparison_time", None),
                    operation_type=8,
                    operation_desc="议价审核提交（进入价格审核）",
                )
        except Exception as exc:
            return ErrorResponse(msg=f"确认比价失败：{exc}")

    @action(methods=["put"], detail=True)
    def submit_price_audit(self, request, pk=None):
        """价格审核提交：由「价格审核」(7) 进入「核价通过」(8)。"""
        instance = self.get_object()
        if int(instance.status or 0) != self.STATUS_NEGOTIATED:
            return ErrorResponse(msg='只有「价格审核」状态的询价单才能提交核价')
        return self._save_status(
            instance,
            status=self.STATUS_APPROVED,
            confirm_user=getattr(instance, "confirm_user", None),
            confirm_time=getattr(instance, "confirm_time", None),
            release_user=getattr(instance, "release_user", None),
            release_time=getattr(instance, "release_time", None),
            comparison_user=getattr(instance, "comparison_user", None),
            comparison_time=getattr(instance, "comparison_time", None),
            operation_type=9,
            operation_desc="议价审核完成（核价通过）",
        )

    @action(methods=["get"], detail=True, url_path="negotiation_records")
    def negotiation_records(self, request, pk=None):
        """按询价单号查询杂采议价记录（可选 part_id）。"""
        instance = self.get_object()
        part_id = (request.query_params.get("part_id") or "").strip()
        if not part_id:
            part_id = _resolve_inquiry_primary_part_id(instance)
        qs = MiscNegotiationRecords.objects.filter(inquiry_no=instance.inquiry_no)
        if part_id:
            qs = qs.filter(part_id=part_id)
        data = MiscNegotiationRecordsSerializer(qs.order_by("id"), many=True).data
        return DetailResponse(data=data, msg="success")

    @action(methods=["put"], detail=True, url_path="save_negotiation_records")
    def save_negotiation_records(self, request, pk=None):
        """按报价单写入杂采议价记录：议价结果 + 该报价单议价前含税/不含税总价快照（来自上阶物料明细）。"""
        instance = self.get_object()
        serializer = MiscNegotiationSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        part_id = (serializer.validated_data.get("part_id") or "").strip()
        if not part_id:
            part_id = _resolve_inquiry_primary_part_id(instance)
        if not part_id:
            return ErrorResponse(msg="询价单无上阶物料料号，无法保存议价记录")
        records = serializer.validated_data.get("records") or []
        username = self._get_request_username() or None
        now = timezone.now()
        with transaction.atomic():
            for row in records:
                qn = (row.get("quotation_no") or "").strip()
                if not qn:
                    return ErrorResponse(msg="records 中每条须包含 quotation_no（报价单号）")
                code = (row.get("supplier_code") or "").strip()
                if not code:
                    qm = QuotationMaster.objects.filter(quotation_no=qn).only("supplier_code").first()
                    if qm:
                        code = (qm.supplier_code or "").strip()
                is_awarded = int(row.get("is_awarded") or 0)
                # 议价价格独立于是否中标：用户填写即落库（清空时前端传 null）
                bp = row.get("bargaining_price")
                snap_ex, snap_in = _negotiation_totals_from_quotation_item(qn, part_id)
                tex = row.get("total_price_excl_tax")
                tin = row.get("total_price_incl_tax")
                if tex is None:
                    tex = snap_ex
                if tin is None:
                    tin = snap_in
                if tex is None:
                    tex = Decimal("0")
                if tin is None:
                    tin = Decimal("0")
                defaults = {
                    "supplier_code": code or None,
                    "is_awarded": is_awarded,
                    "bargaining_user": username,
                    "bargaining_time": now,
                    "bargaining_price": bp,
                    "quotation_no": qn,
                    "total_price_excl_tax": tex,
                    "total_price_incl_tax": tin,
                }
                qs = MiscNegotiationRecords.objects.filter(
                    inquiry_no=instance.inquiry_no,
                    part_id=part_id,
                    quotation_no=qn,
                )
                if qs.count() > 1:
                    keep_id = qs.order_by("id").first().id
                    qs.exclude(id=keep_id).delete()
                obj = (
                    MiscNegotiationRecords.objects.filter(
                        inquiry_no=instance.inquiry_no,
                        part_id=part_id,
                        quotation_no=qn,
                    )
                    .order_by("id")
                    .first()
                )
                if obj:
                    for k, v in defaults.items():
                        setattr(obj, k, v)
                    obj.save()
                else:
                    MiscNegotiationRecords.objects.create(
                        inquiry_no=instance.inquiry_no,
                        part_id=part_id,
                        **defaults,
                    )
        out_qs = MiscNegotiationRecords.objects.filter(
            inquiry_no=instance.inquiry_no,
            part_id=part_id,
        ).order_by("id")
        return DetailResponse(
            data=MiscNegotiationRecordsSerializer(out_qs, many=True).data,
            msg="议价记录已保存",
        )

    def _notify_vendors_on_publish(self, inquiry: Inquiry):
        """
        按询价单供应商子表汇总（与 `_create_supplier_quotations` 相同的 `_group_inquiry_suppliers`），
        每个供应商分组一封邮件，避免同一供应商多行子表重复发送。
        """
        supplier_groups = self._group_inquiry_suppliers(inquiry)
        if not supplier_groups:
            return

        purchaser_company_name = self._resolve_purchaser_company_name(inquiry)

        for vendor in supplier_groups:
            if not isinstance(vendor, dict):
                continue

            supplier_name = (vendor.get("supplier_name") or "").strip()
            email = (vendor.get("contact_email") or "").strip()
            to_list = [email] if email else []

            ctx = build_context_rfs_publish(
                inquiry,
                vendor,
                purchaser_company_name=purchaser_company_name,
            )
            subject, body = render_email(TEMPLATE_RFS_PUBLISH, ctx)

            notice = EmailNotice.objects.create(
                subject=subject,
                body=body,
                to_emails=to_list,
                cc_emails=[],
                bcc_emails=[],
                attachments=[],
                biz_type="inquiry",
                biz_id=inquiry.inquiry_no,
                status="pending",
                payload={
                    "template_key": TEMPLATE_RFS_PUBLISH,
                    "is_html": True,
                    "inquiry_no": inquiry.inquiry_no,
                    "inquiry_title": inquiry.title,
                    "quote_deadline": ctx.get("deadline_time"),
                    "supplier_name": supplier_name,
                },
            )

            if not to_list:
                notice.status = "failed"
                notice.last_error = "缺少供应商邮箱"
                notice.save(update_fields=["status", "last_error", "update_datetime"])
                continue

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


class InquirySupplierViewSet(CustomModelViewSet):
    queryset = InquirySupplier.objects.all()
    serializer_class = InquirySupplierSerializer
    filter_fields = ("inquiry_no", "supplier_code", "supplier_name")
    search_fields = ("inquiry_no", "supplier_code", "supplier_name", "contact_person")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryAttachmentViewSet(CustomModelViewSet):
    queryset = InquiryAttachment.objects.all()
    serializer_class = InquiryAttachmentSerializer
    filter_fields = ("inquiry_no", "file_type", "file_name")
    search_fields = ("inquiry_no", "file_name", "file_type")
    ordering = ("-upload_time",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryMaterialCostViewSet(CustomModelViewSet):
    queryset = InquiryMaterialCost.objects.all()
    serializer_class = InquiryMaterialCostSerializer
    filter_fields = ("inquiry_no", "part_id", "material_spec")
    search_fields = ("inquiry_no", "part_id", "material_spec", "remark")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryProcessCostViewSet(CustomModelViewSet):
    queryset = InquiryProcessCost.objects.all()
    serializer_class = InquiryProcessCostSerializer
    filter_fields = ("inquiry_no", "part_id", "process_station")
    search_fields = ("inquiry_no", "part_id", "process_station", "remark")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryOtherCostViewSet(CustomModelViewSet):
    queryset = InquiryOtherCost.objects.all()
    serializer_class = InquiryOtherCostSerializer
    filter_fields = ("inquiry_no", "part_id")
    search_fields = ("inquiry_no", "part_id")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryProfitCostViewSet(CustomModelViewSet):
    queryset = InquiryProfitCost.objects.all()
    serializer_class = InquiryProfitCostSerializer
    filter_fields = ("inquiry_no", "part_id")
    search_fields = ("inquiry_no", "part_id")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryRfqItemViewSet(CustomModelViewSet):
    queryset = InquiryRfqItem.objects.all()
    serializer_class = InquiryRfqItemSerializer
    filter_fields = ("inquiry_no", "part_id", "product_name")
    search_fields = ("inquiry_no", "part_id", "product_name")
    ordering = ("id",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class MiscLowPriceHeaderViewSet(CustomModelViewSet):
    """比价-制程最低价记录主表"""

    queryset = MiscLowPriceHeader.objects.all()
    serializer_class = MiscLowPriceHeaderSerializer
    filter_fields = ("inquiry_no", "part_id", "souce_no", "cost_type", "item_no")
    search_fields = ("inquiry_no", "part_id", "souce_no", "item_no")
    ordering = ("-create_datetime", "id")


class MiscLowPriceDetailViewSet(CustomModelViewSet):
    """比价-制程最低价记录次表"""

    queryset = MiscLowPriceDetail.objects.all()
    serializer_class = MiscLowPriceDetailSerializer
    filter_fields = ("inquiry_no", "part_id", "cost_type", "material_spec", "item_no", "souce_no")
    search_fields = ("inquiry_no", "part_id", "material_spec", "item_no", "souce_no")
    ordering = ("-create_datetime", "id")


class MiscNegotiationRecordsViewSet(CustomModelViewSet):
    """杂采议价记录表"""

    queryset = MiscNegotiationRecords.objects.all()
    serializer_class = MiscNegotiationRecordsSerializer
    filter_fields = ("inquiry_no", "part_id", "supplier_code")
    search_fields = ("inquiry_no", "part_id", "supplier_code")
    ordering = ("-create_datetime", "id")


class RFQOperationLogsViewSet(CustomModelViewSet):
    """询价单操作日志（rfq_operation_logs）"""

    queryset = RFQOperationLogs.objects.all()
    serializer_class = RFQOperationLogsSerializer
    create_serializer_class = RFQOperationLogsSerializer
    update_serializer_class = RFQOperationLogsSerializer
    filter_fields = (
        "inquiry_no",
        "quotation_no",
        "operation_type",
        "operation_user",
        "purchase_type",
    )
    search_fields = ("inquiry_no", "quotation_no", "operation_user", "operation_desc")
    ordering = ("-create_datetime", "-id")