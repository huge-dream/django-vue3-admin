from rest_framework import routers

from apps.pissupplier.views import (
    QuotationMasterViewSet,
    QuotationAttachmentViewSet,
    QuotationMaterialViewSet,
    QuotationProcessViewSet,
    QuotationOtherViewSet,
    QuotationProfitViewSet,
    QuotationItemViewSet,
)

router = routers.SimpleRouter()
router.register(r"quotation_master", QuotationMasterViewSet)
router.register(r"quotation_attachment", QuotationAttachmentViewSet)
router.register(r"quotation_material", QuotationMaterialViewSet)
router.register(r"quotation_process", QuotationProcessViewSet)
router.register(r"quotation_other", QuotationOtherViewSet)
router.register(r"quotation_profit", QuotationProfitViewSet)
router.register(r"quotation_item", QuotationItemViewSet)

urlpatterns = []
urlpatterns += router.urls
