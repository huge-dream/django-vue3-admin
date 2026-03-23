from rest_framework import routers

from .views import (
    MiscMaterialViewSet,
    MiscStationViewSet,
    MiscPartViewSet,
    PriceTemplateViewSet,
    InquiryViewSet,
    InquirySupplierViewSet,
    InquiryAttachmentViewSet,
    InquiryMaterialCostViewSet,
    InquiryProcessCostViewSet,
    InquiryOtherCostViewSet,
    InquiryProfitCostViewSet,
    InquiryRfqItemViewSet,
    CostEstimateTemplateViewSet,
)

router = routers.SimpleRouter()
router.register(r'misc_materials', MiscMaterialViewSet)
router.register(r'misc_stations', MiscStationViewSet)
router.register(r'misc_parts', MiscPartViewSet)
router.register(r'price_template', PriceTemplateViewSet)
router.register(r'inquiry', InquiryViewSet)
router.register(r'inquiry_supplier', InquirySupplierViewSet)
router.register(r'inquiry_attachment', InquiryAttachmentViewSet)
router.register(r'inquiry_material_cost', InquiryMaterialCostViewSet)
router.register(r'inquiry_process_cost', InquiryProcessCostViewSet)
router.register(r'inquiry_other_cost', InquiryOtherCostViewSet)
router.register(r'inquiry_profit_cost', InquiryProfitCostViewSet)
router.register(r'inquiry_rfq_item', InquiryRfqItemViewSet)
router.register(r'cost_template', CostEstimateTemplateViewSet)

urlpatterns = []
urlpatterns += router.urls
