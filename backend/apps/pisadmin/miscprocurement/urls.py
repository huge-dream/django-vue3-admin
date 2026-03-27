from rest_framework import routers

from .views import (
    MiscMaterialViewSet,
    MiscStationViewSet,
    MiscPartViewSet,
    MiscLowPriceHeaderViewSet,
    MiscLowPriceDetailViewSet,
    InquiryViewSet,
    InquirySupplierViewSet,
    InquiryAttachmentViewSet,
    InquiryMaterialCostViewSet,
    InquiryProcessCostViewSet,
    InquiryOtherCostViewSet,
    InquiryProfitCostViewSet,
    InquiryRfqItemViewSet,
    CostEstimateTemplateViewSet,
    RFQOperationLogsViewSet,
)

router = routers.SimpleRouter()
router.register(r'misc_materials', MiscMaterialViewSet)
router.register(r'misc_stations', MiscStationViewSet)
router.register(r'misc_parts', MiscPartViewSet)
router.register(r'inquiry', InquiryViewSet)
router.register(r'inquiry_supplier', InquirySupplierViewSet)
router.register(r'inquiry_attachment', InquiryAttachmentViewSet)
router.register(r'inquiry_material_cost', InquiryMaterialCostViewSet)
router.register(r'inquiry_process_cost', InquiryProcessCostViewSet)
router.register(r'inquiry_other_cost', InquiryOtherCostViewSet)
router.register(r'inquiry_profit_cost', InquiryProfitCostViewSet)
router.register(r'inquiry_rfq_item', InquiryRfqItemViewSet)
router.register(r'proc_low_price_header', MiscLowPriceHeaderViewSet)
router.register(r'proc_low_price_detail', MiscLowPriceDetailViewSet)
router.register(r'cost_template', CostEstimateTemplateViewSet)
router.register(r'rfq_operation_logs', RFQOperationLogsViewSet)

urlpatterns = []
urlpatterns += router.urls
