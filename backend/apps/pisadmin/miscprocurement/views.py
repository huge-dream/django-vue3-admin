from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import serializers

from dvadmin.utils.json_response import DetailResponse, ErrorResponse, SuccessResponse
from dvadmin.utils.viewset import CustomModelViewSet
from apps.pissupplier.models import (
    QuotationMaster,
    QuotationAttachment,
    QuotationMaterial,
    QuotationProcess,
    QuotationOther,
    QuotationProfit,
    QuotationItem,
)

from .models import (
    MiscProcurementMaterialInfo,
    MiscProcurementStationInfo,
    MiscProcMaterial,
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
from .serializers import (
    MiscMaterialSerializer,
    MiscMaterialCreateUpdateSerializer,
    MiscStationSerializer,
    MiscStationCreateUpdateSerializer,
    MiscPartSerializer,
    MiscPartCreateUpdateSerializer,
    PriceTemplateSerializer,
    InquirySerializer,
    InquirySupplierSerializer,
    InquiryAttachmentSerializer,
    InquiryMaterialCostSerializer,
    InquiryProcessCostSerializer,
    InquiryOtherCostSerializer,
    InquiryProfitCostSerializer,
    InquiryRfqItemSerializer,
    CostEstimateTemplateHeadSerializer,
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


class PriceTemplateViewSet(CustomModelViewSet):
    queryset = PriceTemplate.objects.all()
    serializer_class = PriceTemplateSerializer
    filter_fields = ("code", "name", "procurement_category", "category", "active", "enable_cost_structure")
    search_fields = ("code", "name", "remark")
    ordering = ("-update_datetime",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        """
        删除价格模板时，同步删除对应的成本结构模板主/明细表数据。
        关联键：CostEstimateTemplateHead.template_no == PriceTemplate.code
        """
        template_no = getattr(instance, "code", None)
        if template_no:
            CostEstimateTemplateHead.objects.filter(template_no=template_no).delete()
        instance.delete()


class CostEstimateTemplateViewSet(CustomModelViewSet):
    queryset = CostEstimateTemplateHead.objects.all()
    serializer_class = CostEstimateTemplateHeadSerializer
    filter_fields = ("template_no", "template_name", "procurement_category", "is_bom", "acti")
    search_fields = ("template_no", "template_name", "template_desc")
    ordering = ("-update_time", "-id")

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class InquiryViewSet(CustomModelViewSet):
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
    filter_fields = ("inquiry_no", "title", "purchase_type", "template", "status", "buyer")
    search_fields = ("inquiry_no", "title", "material_type", "buyer", "remark")
    ordering = ("-update_datetime",)

    STATUS_OPEN = 1
    STATUS_CONFIRMED = 2
    STATUS_PUBLISHED = 3
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

    def _save_status(self, instance, *, status, confirm_user=None, confirm_time=None, release_user=None, release_time=None):
        current_time = timezone.now()
        current_user = self._get_request_username() or getattr(instance, "update_user", None)
        instance.status = status
        instance.confirm_user = confirm_user
        instance.confirm_time = confirm_time
        instance.release_user = release_user
        instance.release_time = release_time
        instance.update_user = current_user
        instance.update_time = current_time
        instance.save(
            update_fields=[
                "status",
                "confirm_user",
                "confirm_time",
                "release_user",
                "release_time",
                "update_user",
                "update_time",
            ]
        )
        serializer = self.get_serializer(instance)
        return DetailResponse(data=serializer.data, msg="状态更新成功")

    def _generate_quotation_numbers(self, count: int):
        if count <= 0:
            return []

        date_part = timezone.now().strftime("%y%m%d")
        base = f"QFS{date_part}"
        last = (
            QuotationMaster.objects.select_for_update()
            .filter(quotation_no__startswith=base)
            .order_by("-quotation_no")
            .first()
        )
        if last and last.quotation_no and len(last.quotation_no) >= len(base) + 5:
            try:
                start_seq = int(last.quotation_no[-5:]) + 1
            except ValueError:
                start_seq = 1
        else:
            start_seq = 1

        end_seq = start_seq + count - 1
        if end_seq > 99999:
            raise serializers.ValidationError("当日报价单编号已达上限，请联系管理员")

        return [f"{base}{seq:05d}" for seq in range(start_seq, end_seq + 1)]

    def _get_template_prefill_fields(self, template_no):
        """
        根据询价单关联的成本模板（Inquiry.template = CostEstimateTemplateHead.template_no），
        找出「发布生成报价单时」允许从询价单带入到报价子表的字段名集合。

        满足以下任一条件时，对应映射字段进入集合（从询价单带入报价子表），否则为空值（见 _pick_prefill_value）：
        - is_computed == 1（系统自动计算/带出）
        - supplier_required == 1（带出不可修改）或 2（带出可修改）
        """
        if not template_no:
            return {}

        prefill_fields = {}
        queryset = CostEstimateTemplateBody.objects.filter(
            template_no_id=template_no,
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

    def _create_supplier_quotations(self, inquiry: Inquiry):
        """
        询价单发布：按供应商子表汇总结果，为每个供应商创建一张 `QuotationMaster`（及子表明细），
        主表 `supplier_code`、`supplier_name` 与联系人信息与 `InquirySupplier` 对应数据一致（见 `_group_inquiry_suppliers`）。
        """
        supplier_groups = self._group_inquiry_suppliers(inquiry)
        if not supplier_groups:
            raise serializers.ValidationError("请先维护询价单供应商名单，再执行发布")

        QuotationMaster.objects.filter(inquiry_no=inquiry.inquiry_no).delete()

        quotation_numbers = self._generate_quotation_numbers(len(supplier_groups))
        prefill_fields = self._get_template_prefill_fields(getattr(inquiry, "template", None))
        current_user = self._clip(
            self._get_request_username() or getattr(inquiry, "release_user", None),
            20,
        ) or None
        current_time = timezone.now()
        quote_deadline = inquiry.quote_deadline.strftime("%Y-%m-%d %H:%M:%S") if inquiry.quote_deadline else None

        inquiry_attachments = list(inquiry.attachments.all())
        inquiry_materials = list(inquiry.material_costs.all())
        inquiry_processes = list(inquiry.process_costs.all())
        inquiry_others = list(inquiry.other_costs.all())
        inquiry_profits = list(inquiry.profit_costs.all())
        inquiry_items = list(inquiry.rfq_items.all())

        attachment_bulk = []
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
                delivery_days=getattr(inquiry, "lead_time_days", None),
                payment_method=getattr(inquiry, "payment_method", None),
                status=1,
                is_awarded=0,
                createuser=current_user,
                creattime=current_time,
                remark=None,
            )
            part_ids = supplier["part_ids"]

            for row in inquiry_attachments:
                if row.part_id in part_ids:
                    attachment_bulk.append(
                        QuotationAttachment(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            file_name=self._clip(row.file_name, 20),
                            file_path=self._clip(row.file_path, 20) or None,
                            uploadtime=None,
                            uploaduser=None,
                        )
                    )

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
                    product_name_src = self._pick_prefill_value(
                        prefill_fields, "7", "product_name", row.product_name, empty_default=""
                    )
                    unit_src = self._pick_prefill_value(prefill_fields, "7", "unit", row.unit, empty_default="")
                    qty_src = self._pick_prefill_value(prefill_fields, "7", "qty", row.qty, empty_default=0)
                    item_bulk.append(
                        QuotationItem(
                            quotation_no=quotation,
                            part_id=row.part_id,
                            product_name=self._clip(product_name_src or "", 20),
                            unit=self._clip(unit_src or "", 10),
                            qty=int(qty_src) if qty_src is not None else 0,
                            is_bom=row.is_bom or 0,
                            unit_price=self._pick_prefill_value(prefill_fields, "7", "unit_price", row.unit_price),
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

        if attachment_bulk:
            QuotationAttachment.objects.bulk_create(attachment_bulk)
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
        serializer.save()

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
        current_user = self._get_request_username() or None
        current_time = timezone.now()
        return self._save_status(
            instance,
            status=self.STATUS_CONFIRMED,
            confirm_user=current_user,
            confirm_time=current_time,
            release_user=getattr(instance, "release_user", None),
            release_time=getattr(instance, "release_time", None),
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
                self._create_supplier_quotations(instance)
                return self._save_status(
                    instance,
                    status=self.STATUS_PUBLISHED,
                    confirm_user=getattr(instance, "confirm_user", None),
                    confirm_time=getattr(instance, "confirm_time", None),
                    release_user=current_user,
                    release_time=current_time,
                )
        except serializers.ValidationError as exc:
            detail = getattr(exc, "detail", None)
            if isinstance(detail, (list, tuple)) and detail:
                msg = str(detail[0])
            else:
                msg = str(detail or exc)
            return ErrorResponse(msg=msg)


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
