import json

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import serializers

from .models import (
    MiscProcurementMaterialInfo,
    MiscProcurementStationInfo,
    MiscProcMaterial,
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
from apps.pisadmin.basicinfo.models import Unit
from apps.pisadmin.basicinfo.models import SystemNoRule
from dvadmin.utils.serializers import CustomModelSerializer


def get_request_username(serializer) -> str:
    request = serializer.context.get("request")
    user = getattr(request, "user", None) if request else None
    if not user:
        return ""
    return (
        getattr(user, "username", "")
        or getattr(user, "name", "")
        or getattr(user, "nick_name", "")
        or getattr(user, "nickname", "")
        or ""
    )


def get_request_username_from_request(request) -> str:
    if not request:
        return ""
    user = getattr(request, "user", None)
    if not user:
        return ""
    return (
        getattr(user, "username", "")
        or getattr(user, "name", "")
        or getattr(user, "nick_name", "")
        or getattr(user, "nickname", "")
        or ""
    )


def normalize_unit_code(value):
    text = str(value or "").strip()
    if not text:
        return None

    text = text[:20]
    matched = Unit.objects.filter(unitcode=text).only("unitcode").first()
    if matched and matched.unitcode:
        return str(matched.unitcode).strip()[:20]

    matched = Unit.objects.filter(unitname=text).only("unitcode", "unitname").first()
    if matched:
        resolved = str(matched.unitcode or matched.unitname or text).strip()
        return resolved[:20] if resolved else None

    return text


SUPPLIER_BEHAVIOR_TO_CODE = {
    "prefill_locked": 1,
    "prefill_editable": 2,
    "hidden_required": 3,
    "hidden_optional": 4,
    "required": 5,
    "optional": 6,
}

SUPPLIER_CODE_TO_BEHAVIOR = {value: key for key, value in SUPPLIER_BEHAVIOR_TO_CODE.items()}

ATTACHMENT_TYPE_TO_CODE = {
    "drawing": 1,
    "产品图纸": 1,
    "1": 1,
    1: 1,
    "tender": 2,
    "招标文件": 2,
    "2": 2,
    2: 2,
    "other": 3,
    "其它文件": 3,
    "其他文件": 3,
    "3": 3,
    3: 3,
}


def normalize_purchaser_required(value, is_computed=0):
    if is_computed:
        return 0
    if value in (None, ""):
        return 0
    if isinstance(value, bool):
        return 1 if value else 0
    try:
        return 1 if int(value) else 0
    except (TypeError, ValueError):
        if isinstance(value, str):
            return 1 if value.strip().lower() in ("true", "yes", "y", "on") else 0
        return 0


def normalize_supplier_required(value, purchaser_required=0, supplier_editable=None, is_computed=0):
    if is_computed:
        return 0
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        if text in SUPPLIER_BEHAVIOR_TO_CODE:
            return SUPPLIER_BEHAVIOR_TO_CODE[text]
        try:
            code = int(text)
            if 0 <= code <= 6:
                return code
        except ValueError:
            pass
    elif isinstance(value, bool):
        if purchaser_required:
            if value:
                return 2 if supplier_editable else 1
            return 4 if supplier_editable else 3
        return 5 if value else 6
    elif value is not None:
        try:
            code = int(value)
            if 0 <= code <= 6:
                return code
        except (TypeError, ValueError):
            pass

    if purchaser_required:
        if supplier_editable is True:
            return 4
        if supplier_editable is False:
            return 3
    return 0


def get_supplier_behavior(value, purchaser_required=0, supplier_editable=None):
    code = normalize_supplier_required(value, purchaser_required=purchaser_required, supplier_editable=supplier_editable)
    return SUPPLIER_CODE_TO_BEHAVIOR.get(code, "")


def normalize_attachment_file_type(value):
    if value in (None, ""):
        return 3
    if value in ATTACHMENT_TYPE_TO_CODE:
        return ATTACHMENT_TYPE_TO_CODE[value]
    text = str(value).strip()
    if text in ATTACHMENT_TYPE_TO_CODE:
        return ATTACHMENT_TYPE_TO_CODE[text]
    try:
        code = int(text)
        if code in (1, 2, 3):
            return code
    except (TypeError, ValueError):
        pass
    return 3


class MiscMaterialSerializer(CustomModelSerializer):
    """杂采材料信息-序列化器"""

    class Meta:
        model = MiscProcurementMaterialInfo
        fields = "__all__"
        read_only_fields = ["id"]


class MiscMaterialCreateUpdateSerializer(CustomModelSerializer):
    """杂采材料信息 创建/更新"""

    materialtype = serializers.CharField(max_length=50, required=False, allow_blank=True)
    factory = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = MiscProcurementMaterialInfo
        fields = "__all__"


class MiscStationSerializer(CustomModelSerializer):
    """杂采加工工站信息-序列化器"""

    class Meta:
        model = MiscProcurementStationInfo
        fields = "__all__"
        read_only_fields = ["id"]


class MiscStationCreateUpdateSerializer(CustomModelSerializer):
    """杂采加工工站信息 创建/更新"""

    stationname = serializers.CharField(max_length=50)
    stationcode = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_code = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = MiscProcurementStationInfo
        fields = "__all__"


class MiscPartSerializer(CustomModelSerializer):
    """杂采料号信息-序列化器"""

    class Meta:
        model = MiscProcMaterial
        fields = "__all__"
        read_only_fields = ["id"]


class MiscPartCreateUpdateSerializer(CustomModelSerializer):
    """杂采料号信息 创建/更新"""

    partid_name = serializers.CharField(max_length=50)
    specification = serializers.CharField(max_length=50)
    unit = serializers.CharField(max_length=50)

    class Meta:
        model = MiscProcMaterial
        fields = "__all__"


class CostEstimateTemplateBodySerializer(serializers.ModelSerializer):
    supplier_behavior = serializers.SerializerMethodField()
    item_name_en = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    item_name_vn = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        if isinstance(data, dict) and "is_fixed" not in data and "item_category" in data:
            data["is_fixed"] = data.get("item_category")
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        is_computed = int(getattr(instance, "is_computed", 0) or 0)
        if is_computed == 1:
            data["purchaser_required"] = 0
            data["supplier_required"] = 0
            data["supplier_behavior"] = ""
        return data

    def get_supplier_behavior(self, obj):
        if int(getattr(obj, "is_computed", 0) or 0) == 1:
            return ""
        return get_supplier_behavior(getattr(obj, "supplier_required", 0), getattr(obj, "purchaser_required", 0))

    class Meta:
        model = CostEstimateTemplateBody
        fields = [
            "id",
            "cost_category",
            "item_order",
            "item_no",
            "item_name_cn",
            "item_name_en",
            "item_name_vn",
            "is_fixed",
            "is_computed",
            "purchaser_required",
            "supplier_required",
            "supplier_behavior",
            "remark",
            "version",
        ]


class CostEstimateTemplateHeadSerializer(CustomModelSerializer):
    # 模型上 template_no 无 blank=True，ModelSerializer 自动字段会 required=True；
    # 创建时由 create()/_generate_template_no() 写入，故对入参只读，避免「模板编号必填」校验错误。
    template_no = serializers.CharField(read_only=True)
    template_desc = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    items = CostEstimateTemplateBodySerializer(many=True, required=False)

    class Meta:
        model = CostEstimateTemplateHead
        fields = [
            "id",
            "template_no",
            "template_name",
            "procurement_category",
            "is_bom",
            "acti",
            "template_desc",
            "is_can_add_materials",
            "is_can_add_process",
            "version",
            "status",
            "create_user",
            "create_time",
            "update_user",
            "update_time",
            "items",
        ]
        read_only_fields = ["id", "create_time", "update_time"]

    def validate_status(self, value):
        if value is None:
            return value
        allowed = {c[0] for c in CostEstimateTemplateHead.STATUS_CHOICES}
        try:
            v = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("状态必须为整数")
        if v not in allowed:
            choices_txt = "；".join(f"{code}（{label}）" for code, label in CostEstimateTemplateHead.STATUS_CHOICES)
            raise serializers.ValidationError(f"状态无效，允许：{choices_txt}")
        return v

    def _generate_template_no(self) -> str:
        date_part = timezone.now().strftime("%Y%m%d")
        base = f"CT{date_part}"
        with transaction.atomic():
            last = (
                CostEstimateTemplateHead.objects.select_for_update()
                .filter(template_no__startswith=base)
                .order_by("-template_no")
                .first()
            )
            if last and last.template_no and len(last.template_no) >= len(base) + 3:
                try:
                    seq = int(last.template_no[-3:]) + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            if seq > 999:
                raise serializers.ValidationError("当日编号已达上限，请联系管理员")
            return f"{base}{seq:03d}"

    def _upsert_items(self, head: CostEstimateTemplateHead, items, current_user: str = "", current_time=None):
        # 同一模板编号下可多版本；只删除当前主表行对应版本号的明细，避免误删其它版本
        head_ver = getattr(head, "version", None)
        if head_ver is None:
            head_ver = 1
        CostEstimateTemplateBody.objects.filter(template_no=head.template_no, version=head_ver).delete()
        bulk = []
        if current_time is None:
            current_time = timezone.now()

        def to_int(v, default=0):
            if v is None or v == "":
                return default
            if isinstance(v, bool):
                return 1 if v else 0
            try:
                return int(v)
            except Exception:
                # 兼容 'true'/'false'
                if isinstance(v, str):
                    lv = v.strip().lower()
                    if lv in ("true", "yes", "y", "on"):
                        return 1
                    if lv in ("false", "no", "n", "off"):
                        return 0
                return default

        for idx, item in enumerate(items or [], start=1):
            is_computed_raw = (
                item.get("is_computed", None)
                if isinstance(item, dict)
                else None
            )
            if is_computed_raw is None and isinstance(item, dict):
                is_computed_raw = item.get("isComputed", item.get("autoFill", 0))
            is_computed = to_int(is_computed_raw, 0)
            purchaser_required = normalize_purchaser_required(item.get("purchaser_required", 0), is_computed=is_computed)
            # 兼容 item_name_en/vn 多种键名，确保编辑时用户修改的国际化名称能正确写入
            item_name_cn = (item.get("item_name_cn") or item.get("itemNameCn") or "").strip() or ""
            item_name_en = (item.get("item_name_en") or item.get("itemNameEn") or "").strip() or None
            item_name_vn = (item.get("item_name_vn") or item.get("itemNameVn") or "").strip() or None
            body_version = item.get("version")
            if body_version is None or body_version == "":
                body_version = getattr(head, "version", 1) or 1
            else:
                body_version = to_int(body_version, getattr(head, "version", 1) or 1)
            bulk.append(
                CostEstimateTemplateBody(
                    template_no=head.template_no,
                    cost_category=item.get("cost_category", ""),
                    item_order=item.get("item_order", idx),
                    item_no=item.get("item_no", str(idx)),
                    item_name_cn=item_name_cn,
                    item_name_en=item_name_en,
                    item_name_vn=item_name_vn,
                    is_fixed=int(item.get("is_fixed", item.get("item_category", 0)) or 0),
                    is_computed=is_computed,
                    purchaser_required=purchaser_required,
                    supplier_required=normalize_supplier_required(
                        item.get("supplier_required", item.get("supplier_behavior")),
                        purchaser_required=purchaser_required,
                        supplier_editable=item.get("supplier_editable"),
                        is_computed=is_computed,
                    ),
                    remark=item.get("remark"),
                    version=body_version,
                    create_user=current_user or None,
                    create_time=current_time,
                    update_user=current_user or None,
                    update_time=current_time,
                )
            )
        if bulk:
            CostEstimateTemplateBody.objects.bulk_create(bulk)

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        current_user = get_request_username(self)
        current_time = timezone.now()
        if not validated_data.get("template_no"):
            validated_data["template_no"] = self._generate_template_no()
        if "version" not in validated_data or validated_data.get("version") is None:
            validated_data["version"] = 1
        validated_data["create_user"] = current_user or validated_data.get("create_user")
        validated_data["create_time"] = current_time
        validated_data["update_user"] = current_user or validated_data.get("update_user")
        validated_data["update_time"] = current_time
        head = CostEstimateTemplateHead.objects.create(**validated_data)
        self._upsert_items(head, items, current_user=current_user, current_time=current_time)
        return head

    def update(self, instance, validated_data):
        # 重要：若未传 items，不要清空明细
        items = validated_data.pop("items", None)
        current_user = get_request_username(self)
        current_time = timezone.now()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update_user = current_user or instance.update_user
        instance.update_time = current_time
        instance.save()
        if items is not None:
            self._upsert_items(instance, items, current_user=current_user, current_time=current_time)
        return instance


class CostEstimateTemplateNewVersionSerializer(serializers.Serializer):
    """
    已确认模板派生新版本：沿用同一 template_no，版本号由服务端在同编号下取 max(version)+1；
    与「添加」初始模板（自动生成新编号）的业务入口分离。
    """

    template_name = serializers.CharField(max_length=50)
    procurement_category = serializers.CharField(max_length=4)
    is_bom = serializers.CharField(max_length=4, required=False, default="Y")
    acti = serializers.CharField(max_length=4, required=False, allow_blank=True, default="Y")
    template_desc = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")
    is_can_add_materials = serializers.IntegerField(required=False, default=0)
    is_can_add_process = serializers.IntegerField(required=False, default=0)
    items = CostEstimateTemplateBodySerializer(many=True, required=False)


def _cost_item_to_int(v, default=0):
    """与 CostEstimateTemplateHeadSerializer._upsert_items 内 to_int 一致，用于明细比对。"""
    if v is None or v == "":
        return default
    if isinstance(v, bool):
        return 1 if v else 0
    try:
        return int(v)
    except Exception:
        if isinstance(v, str):
            lv = v.strip().lower()
            if lv in ("true", "yes", "y", "on"):
                return 1
            if lv in ("false", "no", "n", "off"):
                return 0
        return default


def _cost_template_item_row_tuple_from_dict(item: dict, idx: int) -> tuple:
    """将请求体中的单条明细规范为与落库语义一致的比对元组（不含 template_no/version/id）。"""
    is_computed_raw = item.get("is_computed", None)
    if is_computed_raw is None:
        is_computed_raw = item.get("isComputed", item.get("autoFill", 0))
    is_computed = _cost_item_to_int(is_computed_raw, 0)
    purchaser_required = normalize_purchaser_required(item.get("purchaser_required", 0), is_computed=is_computed)
    supplier_required = normalize_supplier_required(
        item.get("supplier_required", item.get("supplier_behavior")),
        purchaser_required=purchaser_required,
        supplier_editable=item.get("supplier_editable"),
        is_computed=is_computed,
    )
    item_order = _cost_item_to_int(item.get("item_order", idx), idx)
    return (
        str(item.get("cost_category", "") or ""),
        item_order,
        str(item.get("item_no", str(idx)) or ""),
        (item.get("item_name_cn") or item.get("itemNameCn") or "").strip(),
        (item.get("item_name_en") or item.get("itemNameEn") or "").strip(),
        (item.get("item_name_vn") or item.get("itemNameVn") or "").strip(),
        _cost_item_to_int(item.get("is_fixed", item.get("item_category", 0)), 0),
        is_computed,
        purchaser_required,
        supplier_required,
        (item.get("remark") or "").strip(),
    )


def _cost_template_item_row_tuple_from_body(obj: CostEstimateTemplateBody) -> tuple:
    is_computed = _cost_item_to_int(getattr(obj, "is_computed", 0), 0)
    purchaser_required = normalize_purchaser_required(getattr(obj, "purchaser_required", 0), is_computed=is_computed)
    supplier_required = normalize_supplier_required(
        getattr(obj, "supplier_required", 0),
        purchaser_required=purchaser_required,
        supplier_editable=None,
        is_computed=is_computed,
    )
    return (
        str(getattr(obj, "cost_category", "") or ""),
        _cost_item_to_int(getattr(obj, "item_order", 0), 0),
        str(getattr(obj, "item_no", "") or ""),
        (getattr(obj, "item_name_cn", None) or "").strip(),
        (getattr(obj, "item_name_en", None) or "").strip(),
        (getattr(obj, "item_name_vn", None) or "").strip(),
        _cost_item_to_int(getattr(obj, "is_fixed", 0), 0),
        is_computed,
        purchaser_required,
        supplier_required,
        (getattr(obj, "remark", None) or "").strip(),
    )


def _cost_template_items_compare_signature_from_payload(items_clean: list) -> tuple:
    rows = []
    for idx, row in enumerate(items_clean or [], start=1):
        if isinstance(row, dict):
            rows.append(_cost_template_item_row_tuple_from_dict(row, idx))
    rows.sort(key=lambda t: (t[1], t[2]))
    return tuple(rows)


def _cost_template_items_compare_signature_from_db(template_no: str, version: int) -> tuple:
    qs = CostEstimateTemplateBody.objects.filter(template_no=template_no, version=version).order_by("item_order", "id")
    rows = [_cost_template_item_row_tuple_from_body(r) for r in qs]
    rows.sort(key=lambda t: (t[1], t[2]))
    return tuple(rows)


@transaction.atomic
def create_cost_template_new_version(
    source_head: CostEstimateTemplateHead,
    validated: dict,
    request,
) -> CostEstimateTemplateHead:
    """
    从已确认主表行创建新版本主表行并写入明细；不调用 HeadSerializer.create，不复用「初始模板」编号生成逻辑。
    """
    template_no = source_head.template_no
    # 锁定同编号行，避免并发下 version 冲突
    list(CostEstimateTemplateHead.objects.select_for_update().filter(template_no=template_no))

    items_in = validated.get("items") or []
    items_clean = []
    for row in items_in:
        if isinstance(row, dict):
            # 忽略客户端带的明细 version，一律与新建主表 version 对齐（避免与 max+1 不一致）
            row = {k: v for k, v in row.items() if k not in ("id", "version")}
        items_clean.append(row)

    prev_ver = int(getattr(source_head, "version", 1) or 1)
    sig_new = _cost_template_items_compare_signature_from_payload(items_clean)
    sig_old = _cost_template_items_compare_signature_from_db(template_no, prev_ver)
    if sig_new == sig_old:
        raise serializers.ValidationError(
            {"items": ["新版本明细与上一版本相同，无需创建新版本"]}
        )

    agg = CostEstimateTemplateHead.objects.filter(template_no=template_no).aggregate(mx=Max("version"))
    max_v = agg["mx"]
    next_v = int(max_v if max_v is not None else 0) + 1

    current_user = get_request_username_from_request(request)
    current_time = timezone.now()
    acti = validated.get("acti")
    if acti in (None, ""):
        acti = "Y"
    is_bom = validated.get("is_bom") or "Y"

    head = CostEstimateTemplateHead.objects.create(
        template_no=template_no,
        template_name=validated["template_name"],
        procurement_category=validated["procurement_category"],
        is_bom=is_bom,
        acti=acti,
        template_desc=validated.get("template_desc") or "",
        is_can_add_materials=int(validated.get("is_can_add_materials") or 0),
        is_can_add_process=int(validated.get("is_can_add_process") or 0),
        version=next_v,
        status=0,
        create_user=current_user or None,
        create_time=current_time,
        update_user=current_user or None,
        update_time=current_time,
    )

    helper = CostEstimateTemplateHeadSerializer()
    helper._upsert_items(head, items_clean, current_user=current_user, current_time=current_time)
    return head


class InquirySupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquirySupplier
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "supplier_code",
            "supplier_name",
            "contact_person",
            "contact_phone",
            "contact_email",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class NestedInquirySupplierSerializer(InquirySupplierSerializer):
    class Meta(InquirySupplierSerializer.Meta):
        validators = []


class InquiryAttachmentSerializer(serializers.ModelSerializer):
    """采购端询价单附件读写；供应商端只读见 `apps.pissupplier.serializers.QuotationMasterSerializer.inquiry_attachments`。"""

    file_type = serializers.CharField()

    def validate_file_type(self, value):
        return normalize_attachment_file_type(value)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["file_type"] = normalize_attachment_file_type(data.get("file_type"))
        return data

    class Meta:
        model = InquiryAttachment
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "file_type",
            "file_name",
            "file_path",
            "upload_time",
            "upload_user",
        ]
        read_only_fields = ["id", "upload_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class NestedInquiryAttachmentSerializer(InquiryAttachmentSerializer):
    class Meta(InquiryAttachmentSerializer.Meta):
        validators = []


class InquiryMaterialCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryMaterialCost
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "material_spec",
            "length",
            "width",
            "height",
            "unit_price",
            "qty",
            "specific_gravity",
            "material_cost",
            "remark",
            "option_json",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class InquiryProcessCostSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["unit"] = normalize_unit_code(data.get("unit"))
        return data

    class Meta:
        model = InquiryProcessCost
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "process_station",
            "unit",
            "unit_rate",
            "process_qty",
            "process_price",
            "remark",
            "option_json",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class InquiryOtherCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryOtherCost
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "packaging_cost",
            "transportation_cost",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class InquiryProfitCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryProfitCost
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "tax_rate",
            "profit_rate",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class InquiryRfqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryRfqItem
        fields = [
            "id",
            "inquiry_no",
            "part_id",
            "product_name",
            "unit",
            "qty",
            "is_bom",
            "unit_price",
            "total_material_cost",
            "total_processing_cost",
            "total_other_expense",
            "total_opex_amt",
            "profit_rate",
            "total_price_excl_tax",
            "tax_rate",
            "total_price_incl_tax",
            "option_json",
            "create_time",
            "create_user",
        ]
        read_only_fields = ["id", "create_time"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_null": True}}


class InquirySerializer(CustomModelSerializer):
    MATERIAL_COST_OPTION_EXCLUDE_KEYS = {
        "partNo",
        "part_no",
        "partId",
        "part_id",
        "material",
        "material_spec",
        "length",
        "width",
        "height",
        "specificgravity",
        "specific_gravity",
        "qty",
        "weight",
        "unitPrice",
        "unitprice",
        "unit_price",
        "price",
        "material_cost",
        "materialCost",
        "material_fee",
        "materialFee",
        "remark",
    }
    PROCESS_COST_OPTION_EXCLUDE_KEYS = {
        "partNo",
        "part_no",
        "partId",
        "part_id",
        "process_station",
        "unit",
        "unitrate",
        "unit_rate",
        "rate",
        "processqty",
        "process_qty",
        "qty",
        "quantity",
        "processprice",
        "process_price",
        "process_cost",
        "remark",
    }
    RFQ_ITEM_OPTION_EXCLUDE_KEYS = {
        "partNo",
        "part_no",
        "partId",
        "part_id",
        "desc",
        "product_name",
        "productName",
        "unit",
        "qty",
        "quantity",
        "price",
        "unitPrice",
        "unitprice",
        "unit_price",
        "amount",
        "total_material_cost",
        "total_processing_cost",
        "total_other_expense",
        "total_opex_amt",
        "profit_rate",
        "tax_rate",
        "total_price_excl_tax",
        "total_price_incl_tax",
    }

    suppliers = NestedInquirySupplierSerializer(many=True, required=False)
    attachments = NestedInquiryAttachmentSerializer(many=True, required=False)
    material_costs = InquiryMaterialCostSerializer(many=True, required=False)
    process_costs = InquiryProcessCostSerializer(many=True, required=False)
    other_costs = InquiryOtherCostSerializer(many=True, required=False)
    profit_costs = InquiryProfitCostSerializer(many=True, required=False)
    rfq_items = InquiryRfqItemSerializer(many=True, required=False)

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        if isinstance(data, dict) and "target_price" not in data and "inquiry_price" in data:
            data["target_price"] = data.get("inquiry_price")
        return super().to_internal_value(data)

    class Meta:
        model = Inquiry
        fields = "__all__"
        # CoreModel 审计 + 主表业务审计：禁止客户端写入篡改；create/update 中仍可向 validated_data 注入业务字段
        read_only_fields = [
            "id",
            "create_datetime",
            "update_datetime",
            "creator",
            "modifier",
            "create_time",
            "create_user",
            "update_time",
            "update_user",
        ]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_blank": True, "allow_null": True}}

    def _generate_code(self, validated_data: dict) -> str:
        """
        按 `SystemNoRule` 取号：rule_code=miscRFS，company_code 取表单或默认「通用」厂区。
        组装见 `SystemNoRule.allocate_system_number`（prefix + factory_code + sequence_date + 流水）。
        """
        company_code = (validated_data.get("company_code") or "").strip() or SystemNoRule.DEFAULT_SYSTEM_NO_COMPANY_CODE
        username = get_request_username(self) or None
        return SystemNoRule.allocate_system_number(company_code, "miscRFS", username=username)

    def _upsert_suppliers(self, inquiry: Inquiry, suppliers):
        """更新或创建供应商信息"""
        InquirySupplier.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for supplier in suppliers or []:
            bulk.append(
                InquirySupplier(
                    inquiry_no=inquiry,
                    part_id=supplier.get("part_id", ""),
                    supplier_code=supplier.get("supplier_code", ""),
                    supplier_name=supplier.get("supplier_name", ""),
                    contact_person=supplier.get("contact_person"),
                    contact_phone=supplier.get("contact_phone"),
                    contact_email=supplier.get("contact_email"),
                    create_user=supplier.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquirySupplier.objects.bulk_create(bulk)

    def _upsert_attachments(self, inquiry: Inquiry, attachments):
        """更新或创建附件信息"""
        InquiryAttachment.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for attachment in attachments or []:
            bulk.append(
                InquiryAttachment(
                    inquiry_no=inquiry,
                    part_id=attachment.get("part_id", ""),
                    file_type=normalize_attachment_file_type(attachment.get("file_type")),
                    file_name=attachment.get("file_name", ""),
                    file_path=attachment.get("file_path", ""),
                    upload_user=attachment.get("upload_user") or current_user or None,
                )
            )
        if bulk:
            InquiryAttachment.objects.bulk_create(bulk)

    def _normalize_option_json(self, payload, excluded_keys):
        if payload in (None, ""):
            return None

        parsed = payload
        if isinstance(payload, str):
            payload = payload.strip()
            if not payload:
                return None
            try:
                parsed = json.loads(payload)
            except (TypeError, ValueError):
                return payload

        if not isinstance(parsed, dict):
            try:
                return json.dumps(parsed, ensure_ascii=False)
            except (TypeError, ValueError):
                return None

        filtered = {key: value for key, value in parsed.items() if key not in excluded_keys}
        if not filtered:
            return None
        return json.dumps(filtered, ensure_ascii=False)

    def _normalize_material_option_json(self, row):
        return self._normalize_option_json(row.get("option_json"), self.MATERIAL_COST_OPTION_EXCLUDE_KEYS)

    def _normalize_process_option_json(self, row):
        return self._normalize_option_json(row.get("option_json"), self.PROCESS_COST_OPTION_EXCLUDE_KEYS)

    def _normalize_rfq_item_option_json(self, row):
        return self._normalize_option_json(row.get("option_json"), self.RFQ_ITEM_OPTION_EXCLUDE_KEYS)

    def _upsert_material_costs(self, inquiry: Inquiry, material_costs):
        """更新或创建材料成本明细"""
        InquiryMaterialCost.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for row in material_costs or []:
            bulk.append(
                InquiryMaterialCost(
                    inquiry_no=inquiry,
                    part_id=row.get("part_id", ""),
                    material_spec=row.get("material_spec"),
                    length=row.get("length"),
                    width=row.get("width"),
                    height=row.get("height"),
                    unit_price=row.get("unit_price"),
                    qty=row.get("qty"),
                    specific_gravity=row.get("specific_gravity"),
                    material_cost=row.get("material_cost"),
                    remark=row.get("remark"),
                    option_json=self._normalize_material_option_json(row),
                    create_user=row.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquiryMaterialCost.objects.bulk_create(bulk)

    def _upsert_process_costs(self, inquiry: Inquiry, process_costs):
        """更新或创建加工成本明细"""
        InquiryProcessCost.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for row in process_costs or []:
            bulk.append(
                InquiryProcessCost(
                    inquiry_no=inquiry,
                    part_id=row.get("part_id", ""),
                    process_station=row.get("process_station"),
                    unit=normalize_unit_code(row.get("unit")),
                    unit_rate=row.get("unit_rate"),
                    process_qty=row.get("process_qty"),
                    process_price=row.get("process_price"),
                    remark=row.get("remark"),
                    option_json=self._normalize_process_option_json(row),
                    create_user=row.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquiryProcessCost.objects.bulk_create(bulk)

    def _upsert_other_costs(self, inquiry: Inquiry, other_costs):
        """更新或创建其它成本明细"""
        InquiryOtherCost.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for row in other_costs or []:
            bulk.append(
                InquiryOtherCost(
                    inquiry_no=inquiry,
                    part_id=row.get("part_id", ""),
                    packaging_cost=row.get("packaging_cost"),
                    transportation_cost=row.get("transportation_cost"),
                    create_user=row.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquiryOtherCost.objects.bulk_create(bulk)

    def _upsert_profit_costs(self, inquiry: Inquiry, profit_costs):
        """更新或创建税费利润明细"""
        InquiryProfitCost.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)
        for row in profit_costs or []:
            bulk.append(
                InquiryProfitCost(
                    inquiry_no=inquiry,
                    part_id=row.get("part_id", ""),
                    tax_rate=row.get("tax_rate"),
                    profit_rate=row.get("profit_rate"),
                    create_user=row.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquiryProfitCost.objects.bulk_create(bulk)

    def _upsert_rfq_items(self, inquiry: Inquiry, rfq_items):
        """更新或创建采购产品明细"""
        InquiryRfqItem.objects.filter(inquiry_no=inquiry).delete()
        bulk = []
        current_user = get_request_username(self)

        def resolve_part_unit(part_id, unit):
            unit_text = str(unit or "").strip()
            if unit_text:
                return unit_text[:10]

            if not part_id:
                return None

            queryset = MiscProcMaterial.objects.filter(partid=part_id)
            if inquiry.company_code:
                matched = queryset.filter(company_code=inquiry.company_code).first()
                if matched and matched.unit:
                    return str(matched.unit).strip()[:10]

            matched = queryset.first()
            if matched and matched.unit:
                return str(matched.unit).strip()[:10]
            return None

        for row in rfq_items or []:
            bulk.append(
                InquiryRfqItem(
                    inquiry_no=inquiry,
                    part_id=row.get("part_id", ""),
                    product_name=row.get("product_name"),
                    unit=resolve_part_unit(row.get("part_id", ""), row.get("unit")),
                    qty=row.get("qty"),
                    is_bom=row.get("is_bom"),
                    unit_price=row.get("unit_price"),
                    total_material_cost=row.get("total_material_cost"),
                    total_processing_cost=row.get("total_processing_cost"),
                    total_other_expense=row.get("total_other_expense"),
                    total_opex_amt=row.get("total_opex_amt"),
                    profit_rate=row.get("profit_rate"),
                    total_price_excl_tax=row.get("total_price_excl_tax"),
                    tax_rate=row.get("tax_rate"),
                    total_price_incl_tax=row.get("total_price_incl_tax"),
                    option_json=self._normalize_rfq_item_option_json(row),
                    create_user=row.get("create_user") or current_user or None,
                )
            )
        if bulk:
            InquiryRfqItem.objects.bulk_create(bulk)

    def create(self, validated_data):
        """
        创建新的询价单记录，自动生成inquiry_no（询价单号）
        """
        suppliers = validated_data.pop("suppliers", [])
        attachments = validated_data.pop("attachments", [])
        material_costs = validated_data.pop("material_costs", [])
        process_costs = validated_data.pop("process_costs", [])
        other_costs = validated_data.pop("other_costs", [])
        profit_costs = validated_data.pop("profit_costs", [])
        rfq_items = validated_data.pop("rfq_items", [])
        current_user = get_request_username(self)
        current_time = timezone.now()
        
        if not validated_data.get("inquiry_no"):
            validated_data["inquiry_no"] = self._generate_code(validated_data)
        # 询价单创建后默认进入“开立”，状态流转仅允许通过专用动作接口处理
        validated_data["status"] = 1
        validated_data.pop("confirm_user", None)
        validated_data.pop("confirm_time", None)
        validated_data.pop("release_user", None)
        validated_data.pop("release_time", None)
        validated_data["create_user"] = current_user or validated_data.get("create_user")
        validated_data["update_user"] = current_user or validated_data.get("update_user")
        validated_data["update_time"] = current_time

        inquiry = super().create(validated_data)
        
        # 创建相关的供应商和附件记录
        self._upsert_suppliers(inquiry, suppliers)
        self._upsert_attachments(inquiry, attachments)
        self._upsert_material_costs(inquiry, material_costs)
        self._upsert_process_costs(inquiry, process_costs)
        self._upsert_other_costs(inquiry, other_costs)
        self._upsert_profit_costs(inquiry, profit_costs)
        self._upsert_rfq_items(inquiry, rfq_items)
        
        return inquiry

    def update(self, instance, validated_data):
        """
        更新询价单记录
        """
        suppliers = validated_data.pop("suppliers", None)
        attachments = validated_data.pop("attachments", None)
        material_costs = validated_data.pop("material_costs", None)
        process_costs = validated_data.pop("process_costs", None)
        other_costs = validated_data.pop("other_costs", None)
        profit_costs = validated_data.pop("profit_costs", None)
        rfq_items = validated_data.pop("rfq_items", None)
        current_user = get_request_username(self)
        current_time = timezone.now()
        
        # 更新时不修改inquiry_no
        validated_data.pop("inquiry_no", None)
        # 状态流转和对应审计字段仅允许通过专用动作接口处理
        validated_data.pop("status", None)
        validated_data.pop("confirm_user", None)
        validated_data.pop("confirm_time", None)
        validated_data.pop("release_user", None)
        validated_data.pop("release_time", None)
        validated_data["update_user"] = current_user or validated_data.get("update_user")
        validated_data["update_time"] = current_time
        inquiry = super().update(instance, validated_data)
        
        # 更新供应商和附件信息
        if suppliers is not None:
            self._upsert_suppliers(inquiry, suppliers)
        if attachments is not None:
            self._upsert_attachments(inquiry, attachments)
        if material_costs is not None:
            self._upsert_material_costs(inquiry, material_costs)
        if process_costs is not None:
            self._upsert_process_costs(inquiry, process_costs)
        if other_costs is not None:
            self._upsert_other_costs(inquiry, other_costs)
        if profit_costs is not None:
            self._upsert_profit_costs(inquiry, profit_costs)
        if rfq_items is not None:
            self._upsert_rfq_items(inquiry, rfq_items)
        
        return inquiry
