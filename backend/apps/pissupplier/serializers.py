import json
from decimal import Decimal
from typing import Optional

from django.db import models, transaction
from django.utils import timezone
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from apps.pisadmin.miscprocurement.models import (
    CostEstimateTemplateBody,
    CostEstimateTemplateHead,
    Inquiry,
    InquiryAttachment,
)
from apps.pissupplier.models import (
    QuotationMaster,
    QuotationAttachment,
    QuotationMaterial,
    QuotationProcess,
    QuotationOther,
    QuotationProfit,
    QuotationItem,
)


class BusinessAuditSerializer(CustomModelSerializer):

    audit_create_user_field = None
    audit_create_time_field = None
    audit_update_user_field = None
    audit_update_time_field = None
    audit_datetime_format = "%Y-%m-%d %H:%M:%S"

    def _has_serializer_field(self, field_name):
        return bool(field_name) and field_name in self.fields

    def _get_model_field(self, field_name):
        if not field_name:
            return None
        try:
            return self.Meta.model._meta.get_field(field_name)
        except Exception:
            return None

    def _resolve_time_value(self, field_name, now):
        model_field = self._get_model_field(field_name)
        if isinstance(model_field, models.DateTimeField):
            return now
        return now.strftime(self.audit_datetime_format)

    def _apply_business_audit(self, validated_data, *, is_create):
        username = self.get_request_username()
        if not username:
            return validated_data

        now = timezone.now()
        create_user_field = self.audit_create_user_field
        create_time_field = self.audit_create_time_field
        update_user_field = self.audit_update_user_field
        update_time_field = self.audit_update_time_field

        if is_create:
            if self._has_serializer_field(create_user_field) and not validated_data.get(create_user_field):
                validated_data[create_user_field] = username
            if self._has_serializer_field(create_time_field) and not validated_data.get(create_time_field):
                validated_data[create_time_field] = self._resolve_time_value(create_time_field, now)

        if self._has_serializer_field(update_user_field):
            validated_data[update_user_field] = username
        if self._has_serializer_field(update_time_field):
            validated_data[update_time_field] = self._resolve_time_value(update_time_field, now)

        return validated_data

    def create(self, validated_data):
        validated_data = self._apply_business_audit(validated_data, is_create=True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._apply_business_audit(validated_data, is_create=False)
        return super().update(instance, validated_data)


# 与采购端 rfqmiscellaneous `buildSectionsFromCostTemplate` 一致，供供应商报价页展示列与只读规则
_COST_CATEGORY_TO_TITLE = {
    "1": "材料成本",
    "2": "加工成本",
    "3": "其它成本",
    "4": "管销研费用",
    "5": "利润",
    "6": "税金",
    "7": "产品明细",
}
_COST_SECTION_ORDER = ("产品明细", "材料成本", "加工成本", "其它成本", "管销研费用", "利润", "税金")


def build_cost_template_sections_for_quotation(template_no: str, template_version: Optional[int] = None):
    """
    将 `CostEstimateTemplateBody` 扁平行展开为前端 `sections[]`（含 fields[].is_computed / supplier_required）。
    使用询价单 `Inquiry.template` 作为 template_no，`Inquiry.template_version` 锁定主表 version。

    template_version 为 None 时兼容旧数据：取该编号下已确认主表的最高 version。
    """
    if not template_no:
        return []
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
        return []
    items = list(
        CostEstimateTemplateBody.objects.filter(template_no=head.template_no, version=head.version).order_by(
            "item_order", "id"
        )
    )
    group = {}
    for it in items:
        cat = str(it.cost_category or "")
        title = _COST_CATEGORY_TO_TITLE.get(cat, "其它成本")
        group.setdefault(title, []).append(it)

    def _field_dict(it):
        ic = int(getattr(it, "is_computed", 0) or 0)
        sr = int(getattr(it, "supplier_required", 0) or 0)
        pr = int(getattr(it, "purchaser_required", 0) or 0)
        return {
            "key": it.item_no or "",
            "label": it.item_name_cn or it.item_no or "",
            "is_computed": ic,
            "supplier_required": sr,
            "purchaser_required": pr,
            "autoFill": ic == 1,
            "purchaserRequired": pr == 1,
        }

    sections = []
    for title in _COST_SECTION_ORDER:
        rows = group.get(title)
        if not rows:
            continue
        if title == "材料成本":
            supplier_can_add = int(getattr(head, "is_can_add_materials", 0) or 0) == 1
        elif title == "加工成本":
            supplier_can_add = int(getattr(head, "is_can_add_process", 0) or 0) == 1
        else:
            supplier_can_add = False
        sections.append(
            {
                "id": title,
                "title": title,
                "name": title,
                "enabled": True,
                "supplierCanAddRow": supplier_can_add,
                "fields": [_field_dict(r) for r in rows],
            }
        )
    return sections


def normalize_option_json(payload):
    if payload in (None, ""):
        return None
    if isinstance(payload, str):
        text = payload.strip()
        return text or None
    try:
        return json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


class QuotationAttachmentSerializer(BusinessAuditSerializer):
    uploadtime = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    uploaduser = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)

    audit_create_user_field = "uploaduser"
    audit_create_time_field = "uploadtime"

    class Meta:
        model = QuotationAttachment
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "file_name",
            "file_path",
            "uploadtime",
            "uploaduser",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}


class NestedQuotationAttachmentSerializer(QuotationAttachmentSerializer):
    class Meta(QuotationAttachmentSerializer.Meta):
        validators = []


class QuotationMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationMaterial
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "material_spec",
            "length",
            "width",
            "height",
            "unit_price",
            "qty",
            "specific_gravity",
            "material_cost",
            "weight",
            "remark",
            "option_json",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}

    def validate_option_json(self, value):
        return normalize_option_json(value)


class NestedQuotationMaterialSerializer(QuotationMaterialSerializer):
    class Meta(QuotationMaterialSerializer.Meta):
        validators = []


class QuotationProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationProcess
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "process_station",
            "unit",
            "unit_rate",
            "process_qty",
            "process_price",
            "remark",
            "option_json",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}

    def validate_option_json(self, value):
        return normalize_option_json(value)


class NestedQuotationProcessSerializer(QuotationProcessSerializer):
    class Meta(QuotationProcessSerializer.Meta):
        validators = []


class QuotationOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationOther
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "packaging_cost",
            "transportation_cost",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}


class NestedQuotationOtherSerializer(QuotationOtherSerializer):
    class Meta(QuotationOtherSerializer.Meta):
        validators = []


class QuotationProfitSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationProfit
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "tax_rate",
            "profit_rate",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}


class NestedQuotationProfitSerializer(QuotationProfitSerializer):
    class Meta(QuotationProfitSerializer.Meta):
        validators = []


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = [
            "autoid",
            "quotation_no",
            "part_id",
            "product_name",
            "unit",
            "qty",
            "is_bom",
            "unit_price",
            "product_cost",
            "total_material_cost",
            "total_processing_cost",
            "total_other_expense",
            "total_opex_amt",
            "profit_rate",
            "total_price_excl_tax",
            "tax_rate",
            "total_price_incl_tax",
            "is_awarded",
            "winning_bid_price",
        ]
        read_only_fields = ["autoid"]
        extra_kwargs = {"quotation_no": {"required": False, "allow_null": True}}


class NestedQuotationItemSerializer(QuotationItemSerializer):
    class Meta(QuotationItemSerializer.Meta):
        validators = []


_INQUIRY_ATTACHMENT_TYPE_LABELS = {1: "产品图纸", 2: "招标文件", 3: "其它文件"}


class SupplierInquiryAttachmentSerializer(serializers.ModelSerializer):
    """供应商报价详情：询价单附件（`pis_proc_inquiry_attachment`），只读。"""

    file_type_label = serializers.SerializerMethodField()

    def get_file_type_label(self, obj):
        ft = getattr(obj, "file_type", None)
        try:
            ft = int(ft)
        except (TypeError, ValueError):
            ft = 3
        return _INQUIRY_ATTACHMENT_TYPE_LABELS.get(ft, "其它文件")

    class Meta:
        model = InquiryAttachment
        fields = [
            "id",
            "part_id",
            "file_type",
            "file_type_label",
            "file_name",
            "file_path",
            "upload_time",
            "upload_user",
        ]
        read_only_fields = [
            "id",
            "part_id",
            "file_type",
            "file_name",
            "file_path",
            "upload_time",
            "upload_user",
        ]


class QuotationMasterSerializer(BusinessAuditSerializer):
    """杂采报价单主表序列化器"""

    creattime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        required=False,
        allow_null=True,
    )
    # 列表/详情展示：上阶物料明细 total_price_incl_tax 之和（主表无报价金额列）
    quote_amount = serializers.SerializerMethodField(read_only=True)
    template_sections = serializers.SerializerMethodField(read_only=True)
    inquiry_attachments = serializers.SerializerMethodField(read_only=True)
    attachments = QuotationAttachmentSerializer(many=True, required=False)
    material_costs = QuotationMaterialSerializer(many=True, required=False)
    process_costs = NestedQuotationProcessSerializer(many=True, required=False)
    other_costs = QuotationOtherSerializer(many=True, required=False)
    profit_costs = QuotationProfitSerializer(many=True, required=False)
    rfq_items = QuotationItemSerializer(many=True, required=False)

    audit_create_user_field = "createuser"
    audit_create_time_field = "creattime"
    audit_update_user_field = "quoteuser"
    audit_update_time_field = "quotetime"

    def get_quote_amount(self, obj):
        total = Decimal("0")
        has_value = False
        for row in obj.rfq_items.all():
            v = getattr(row, "total_price_incl_tax", None)
            if v is not None:
                total += v
                has_value = True
        return total if has_value else None

    def get_template_sections(self, obj):
        """列表接口不展开，避免 N+1；详情(retrieve)返回与询价成本模板一致的 sections。"""
        if self.context.get("quotation_skip_template_sections"):
            return []
        if self.context.get("view_action") != "retrieve":
            return []
        inquiry_no = getattr(obj, "inquiry_no", None)
        if not inquiry_no:
            return []
        inq = Inquiry.objects.filter(inquiry_no=inquiry_no).only("template", "template_version").first()
        if not inq or not inq.template:
            return []
        return build_cost_template_sections_for_quotation(
            inq.template,
            getattr(inq, "template_version", None),
        )

    def get_inquiry_attachments(self, obj):
        """详情接口返回询价单附件；列表不查，避免 N+1。"""
        if self.context.get("view_action") != "retrieve":
            return []
        inquiry_no = getattr(obj, "inquiry_no", None)
        if not inquiry_no:
            return []
        qs = (
            InquiryAttachment.objects.filter(inquiry_no=inquiry_no)
            .order_by("file_type", "-upload_time", "id")
        )
        return SupplierInquiryAttachmentSerializer(qs, many=True).data

    class Meta:
        model = QuotationMaster
        fields = "__all__"
        read_only_fields = ["autoid"]


class QuotationMasterCreateUpdateSerializer(BusinessAuditSerializer):
    """杂采报价单主表写入序列化器"""

    attachments = NestedQuotationAttachmentSerializer(many=True, required=False)
    material_costs = NestedQuotationMaterialSerializer(many=True, required=False)
    process_costs = NestedQuotationProcessSerializer(many=True, required=False)
    other_costs = NestedQuotationOtherSerializer(many=True, required=False)
    profit_costs = NestedQuotationProfitSerializer(many=True, required=False)
    rfq_items = NestedQuotationItemSerializer(many=True, required=False)
    quotation_no = serializers.CharField(max_length=20)
    inquiry_no = serializers.CharField(max_length=20)
    supplier_code = serializers.CharField(max_length=20)
    supplier_name = serializers.CharField(max_length=20)
    contact_person = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    contact_phone = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    contact_email = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    quote_deadline = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    validity_days = serializers.IntegerField(required=False, allow_null=True)
    delivery_days = serializers.IntegerField(required=False, allow_null=True)
    payment_method = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    is_awarded = serializers.IntegerField(required=False, allow_null=True)
    createuser = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    creattime = serializers.DateTimeField(required=False, allow_null=True)
    quoteuser = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    quotetime = serializers.DateTimeField(required=False, allow_null=True)
    remark = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    audit_create_user_field = "createuser"
    audit_create_time_field = "creattime"
    audit_update_user_field = "quoteuser"
    audit_update_time_field = "quotetime"

    class Meta:
        model = QuotationMaster
        fields = "__all__"
        # 创建人/创建时间仅发布生成或首次创建时由服务端写入；禁止 PUT 用详情回传覆盖
        read_only_fields = ["autoid", "createuser", "creattime"]

    def _apply_business_audit(self, validated_data, *, is_create):
        validated_data = super()._apply_business_audit(validated_data, is_create=is_create)
        # 报价时间仅通过视图 `submit` 写入；保存/新建接口不自动写入 quotetime
        tf = self.audit_update_time_field
        if tf and tf in validated_data:
            validated_data.pop(tf, None)
        return validated_data

    def validate_payment_method(self, value):
        if value is None:
            return value
        valid_values = {choice[0] for choice in QuotationMaster.PAYMENT_METHOD_CHOICES}
        if value not in valid_values:
            raise serializers.ValidationError("付款方式不合法")
        return value

    def validate_status(self, value):
        if value is None:
            return value
        valid_values = {choice[0] for choice in QuotationMaster.STATUS_CHOICES}
        if value not in valid_values:
            raise serializers.ValidationError("状态值不合法")
        return value

    def validate_is_awarded(self, value):
        if value is None:
            return value
        valid_values = {choice[0] for choice in QuotationMaster.AWARD_STATUS_CHOICES}
        if value not in valid_values:
            raise serializers.ValidationError("中标状态值不合法")
        return value

    def _upsert_attachments(self, quotation, attachments):
        QuotationAttachment.objects.filter(quotation_no=quotation).delete()
        if not attachments:
            return
        bulk = []
        username = self.get_request_username()
        now_text = timezone.now().strftime(self.audit_datetime_format)
        fn_max = QuotationAttachment._meta.get_field("file_name").max_length
        fp_max = QuotationAttachment._meta.get_field("file_path").max_length
        part_max = QuotationAttachment._meta.get_field("part_id").max_length
        for row in attachments:
            fn = (row.get("file_name") or "").strip()
            fp = row.get("file_path")
            fp = (fp or "").strip() if fp is not None else ""
            pid = (row.get("part_id") or "").strip()
            if not fn and not fp:
                continue
            bulk.append(
                QuotationAttachment(
                    quotation_no=quotation,
                    part_id=pid[:part_max],
                    file_name=fn[:fn_max],
                    file_path=(fp[:fp_max] if fp else None) or None,
                    uploadtime=row.get("uploadtime") or now_text,
                    uploaduser=row.get("uploaduser") or username or None,
                )
            )
        if bulk:
            QuotationAttachment.objects.bulk_create(bulk)

    def _upsert_material_costs(self, quotation, material_costs):
        QuotationMaterial.objects.filter(quotation_no=quotation).delete()
        if not material_costs:
            return
        bulk = []
        for row in material_costs:
            bulk.append(
                QuotationMaterial(
                    quotation_no=quotation,
                    part_id=row.get("part_id", ""),
                    material_spec=row.get("material_spec", ""),
                    length=row.get("length"),
                    width=row.get("width"),
                    height=row.get("height"),
                    unit_price=row.get("unit_price"),
                    qty=row.get("qty"),
                    specific_gravity=row.get("specific_gravity"),
                    material_cost=row.get("material_cost"),
                    weight=row.get("weight"),
                    remark=row.get("remark"),
                    option_json=normalize_option_json(row.get("option_json")),
                )
            )
        QuotationMaterial.objects.bulk_create(bulk)

    def _upsert_process_costs(self, quotation, process_costs):
        QuotationProcess.objects.filter(quotation_no=quotation).delete()
        if not process_costs:
            return
        bulk = []
        for row in process_costs:
            bulk.append(
                QuotationProcess(
                    quotation_no=quotation,
                    part_id=row.get("part_id", ""),
                    process_station=row.get("process_station"),
                    unit=row.get("unit"),
                    unit_rate=row.get("unit_rate"),
                    process_qty=row.get("process_qty"),
                    process_price=row.get("process_price"),
                    remark=row.get("remark"),
                    option_json=normalize_option_json(row.get("option_json")),
                )
            )
        QuotationProcess.objects.bulk_create(bulk)

    def _upsert_other_costs(self, quotation, other_costs):
        QuotationOther.objects.filter(quotation_no=quotation).delete()
        if not other_costs:
            return
        bulk = []
        for row in other_costs:
            bulk.append(
                QuotationOther(
                    quotation_no=quotation,
                    part_id=row.get("part_id", ""),
                    packaging_cost=row.get("packaging_cost"),
                    transportation_cost=row.get("transportation_cost"),
                )
            )
        QuotationOther.objects.bulk_create(bulk)

    def _upsert_profit_costs(self, quotation, profit_costs):
        QuotationProfit.objects.filter(quotation_no=quotation).delete()
        if not profit_costs:
            return
        bulk = []
        for row in profit_costs:
            bulk.append(
                QuotationProfit(
                    quotation_no=quotation,
                    part_id=row.get("part_id", ""),
                    tax_rate=row.get("tax_rate"),
                    profit_rate=row.get("profit_rate"),
                )
            )
        QuotationProfit.objects.bulk_create(bulk)

    def _upsert_rfq_items(self, quotation, rfq_items):
        QuotationItem.objects.filter(quotation_no=quotation).delete()
        if not rfq_items:
            return
        bulk = []
        for row in rfq_items:
            bulk.append(
                QuotationItem(
                    quotation_no=quotation,
                    part_id=row.get("part_id", ""),
                    product_name=row.get("product_name", ""),
                    unit=row.get("unit", ""),
                    qty=row.get("qty"),
                    is_bom=row.get("is_bom"),
                    unit_price=row.get("unit_price"),
                    product_cost=row.get("product_cost"),
                    total_material_cost=row.get("total_material_cost"),
                    total_processing_cost=row.get("total_processing_cost"),
                    total_other_expense=row.get("total_other_expense"),
                    total_opex_amt=row.get("total_opex_amt"),
                    profit_rate=row.get("profit_rate"),
                    total_price_excl_tax=row.get("total_price_excl_tax"),
                    tax_rate=row.get("tax_rate"),
                    total_price_incl_tax=row.get("total_price_incl_tax"),
                    is_awarded=row.get("is_awarded"),
                    winning_bid_price=row.get("winning_bid_price"),
                )
            )
        QuotationItem.objects.bulk_create(bulk)

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("status", None)
        validated_data.pop("quotetime", None)
        attachments = validated_data.pop("attachments", [])
        material_costs = validated_data.pop("material_costs", [])
        process_costs = validated_data.pop("process_costs", [])
        other_costs = validated_data.pop("other_costs", [])
        profit_costs = validated_data.pop("profit_costs", [])
        rfq_items = validated_data.pop("rfq_items", [])
        quotation = super().create(validated_data)
        self._upsert_attachments(quotation, attachments)
        self._upsert_material_costs(quotation, material_costs)
        self._upsert_process_costs(quotation, process_costs)
        self._upsert_other_costs(quotation, other_costs)
        self._upsert_profit_costs(quotation, profit_costs)
        self._upsert_rfq_items(quotation, rfq_items)
        return quotation

    @transaction.atomic
    def update(self, instance, validated_data):
        # 状态与报价时间仅能通过 `QuotationMasterViewSet.submit` 变更
        validated_data.pop("status", None)
        validated_data.pop("quotetime", None)
        attachments = validated_data.pop("attachments", None)
        material_costs = validated_data.pop("material_costs", None)
        process_costs = validated_data.pop("process_costs", None)
        other_costs = validated_data.pop("other_costs", None)
        profit_costs = validated_data.pop("profit_costs", None)
        rfq_items = validated_data.pop("rfq_items", None)
        quotation = super().update(instance, validated_data)
        if attachments is not None:
            self._upsert_attachments(quotation, attachments)
        if material_costs is not None:
            self._upsert_material_costs(quotation, material_costs)
        if process_costs is not None:
            self._upsert_process_costs(quotation, process_costs)
        if other_costs is not None:
            self._upsert_other_costs(quotation, other_costs)
        if profit_costs is not None:
            self._upsert_profit_costs(quotation, profit_costs)
        if rfq_items is not None:
            self._upsert_rfq_items(quotation, rfq_items)
        return quotation
