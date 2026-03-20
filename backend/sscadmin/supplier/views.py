from dvadmin.utils.viewset import CustomModelViewSet

from sscadmin.supplier.models import (
    QuotationMaster,
    QuotationAttachment,
    QuotationMaterial,
    QuotationProcess,
    QuotationOther,
    QuotationProfit,
    QuotationItem,
)
from sscadmin.supplier.serializers import (
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
    """杂采报价单主表管理接口"""

    queryset = QuotationMaster.objects.all()
    serializer_class = QuotationMasterSerializer
    create_serializer_class = QuotationMasterCreateUpdateSerializer
    update_serializer_class = QuotationMasterCreateUpdateSerializer
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

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


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
