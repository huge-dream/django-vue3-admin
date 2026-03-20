import json

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from sscadmin.basicinfo.models import MiscProcMaterial, Unit
from .models import (
    PriceTemplate,
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
from dvadmin.utils.serializers import CustomModelSerializer
from .cost_template_builder import CostTemplateBuilder


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


class PriceTemplateSerializer(CustomModelSerializer):
    """
    将前端传入的成本结构写入独立的成本模板主/明细表（`CostEstimateTemplateHead` / `CostEstimateTemplateBody`）。
    `sections` 字段已弃用，调用方仍可传 `sections` 或 `templateLines` 兼容旧前端。
    """

    def _generate_code(self) -> str:
        date_part = timezone.now().strftime("%Y%m%d")
        base = f"CT{date_part}"
        with transaction.atomic():
            last = (
                PriceTemplate.objects.select_for_update()
                .filter(code__startswith=base)
                .order_by("-code")
                .first()
            )
            if last and last.code and len(last.code) >= len(base) + 3:
                try:
                    seq = int(last.code[-3:]) + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            if seq > 999:
                raise serializers.ValidationError("当日编号已达上限，请联系管理员")
            return f"{base}{seq:03d}"

    class Meta:
        model = PriceTemplate
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime", "creator", "modifier"]
        extra_kwargs = {"code": {"required": False, "allow_blank": True, "allow_null": True}}

    def _map_procurement_category(self, val: str) -> str:
        # 将本项目的采购类别映射到成本模板的取值（1/2）。根据需要调整映射规则。
        if val == "strategic":
            return "1"
        if val == "misc":
            return "2"
        return "1"

    def _create_cost_template(self, price_obj: PriceTemplate, sections):
        """
        根据前端发送的 sections 数据创建成本模板
        
        使用 CostTemplateBuilder 工具类将分层结构的 sections 数据展开，
        逐条创建 CostEstimateTemplateBody 明细记录。
        
        数据流：
          前端 sections (分层结构)
          ↓ (展开)
          CostEstimateTemplateHead (主表，一条)
          ↓
          CostEstimateTemplateBody (明细表，多条，逐行插入)
        """
        if not sections:
            return None
        
        # 获取当前请求用户信息
        request = self.context.get("request")
        current_user = getattr(request.user, "username", "") if request and request.user else ""
        current_time = timezone.now()
        
        # 生成唯一的 template_no
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
                seq = 1
            template_no = f"{base}{seq:03d}"

            # 创建成本模板主表记录，并设置审计字段
            head = CostEstimateTemplateHead.objects.create(
                template_no=template_no,
                template_name=price_obj.name,
                procurement_category=self._map_procurement_category(price_obj.procurement_category),
                is_bom="N",
                acti="Y",
                template_desc=(getattr(price_obj, "remark", None) or ""),
                is_can_add_materials=0,
                is_can_add_process=0,
                create_user=current_user,
                create_time=current_time,
                update_user=current_user,
                update_time=current_time,
            )

            # 使用 CostTemplateBuilder 将 sections 数据展开，逐条创建明细
            # 传递 create_user 和 create_time 以填充审计字段
            created_count = CostTemplateBuilder.create_cost_template_body_records(
                head, 
                sections,
                create_user=current_user,
                create_time=current_time
            )
            
            # 可选：调试输出（取消注释以启用）
            # CostTemplateBuilder.debug_print_sections_expansion(sections)

            return head

    def create(self, validated_data):
        # 兼容旧前端：从 request 中读取 sections/templateLines
        request = self.context.get("request")
        sections = None
        if request is not None:
            sections = request.data.get("sections") or request.data.get("templateLines")

        if not validated_data.get("code"):
            validated_data["code"] = self._generate_code()

        price = super().create(validated_data)

        # 将成本结构写入独立表（以 PriceTemplate.code 为唯一关联键）
        if sections:
            try:
                self._create_cost_template(price, sections)
            except Exception as e:
                # 不吞异常，避免“前端显示成功但数据库未写入”
                raise serializers.ValidationError(f"成本结构模板写入失败：{e}")

        return price

    def update(self, instance, validated_data):
        request = self.context.get("request")
        sections = None
        if request is not None:
            sections = request.data.get("sections") or request.data.get("templateLines")

        price = super().update(instance, validated_data)

        # 更新时：对同一 template_no(=PriceTemplate.code) 做 upsert，并重建明细
        if sections:
            try:
                self._create_cost_template(price, sections)
            except Exception as e:
                raise serializers.ValidationError(f"成本结构模板更新失败：{e}")

        return price


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
        ]


class CostEstimateTemplateHeadSerializer(CustomModelSerializer):
    template_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
            "create_user",
            "create_time",
            "update_user",
            "update_time",
            "items",
        ]
        read_only_fields = ["id", "create_time", "update_time"]

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
        CostEstimateTemplateBody.objects.filter(template_no=head).delete()
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
            bulk.append(
                CostEstimateTemplateBody(
                    template_no=head,
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
        read_only_fields = ["id", "create_datetime", "update_datetime", "creator", "modifier"]
        extra_kwargs = {"inquiry_no": {"required": False, "allow_blank": True, "allow_null": True}}

    def _generate_code(self) -> str:
        """
        自动生成唯一的询价单号
        格式: RFS + YYMMDD + 5位序号 (e.g., RFS26031700001)
        """
        date_part = timezone.now().strftime("%y%m%d")
        base = f"RFS{date_part}"
        with transaction.atomic():
            last = (
                Inquiry.objects.select_for_update()
                .filter(inquiry_no__startswith=base)
                .order_by("-inquiry_no")
                .first()
            )
            if last and last.inquiry_no and len(last.inquiry_no) >= len(base) + 5:
                try:
                    seq = int(last.inquiry_no[-5:]) + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            if seq > 99999:
                raise serializers.ValidationError("当日编号已达上限，请联系管理员")
            return f"{base}{seq:05d}"

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
            validated_data["inquiry_no"] = self._generate_code()
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
