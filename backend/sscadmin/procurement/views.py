from dvadmin.utils.viewset import CustomModelViewSet

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
)
from .serializers import (
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

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


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
