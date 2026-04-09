from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# from dvadmin_ak_sk.libs.authentication import AkSkAuthentication

from sync.manager import SyncManager


class PricingAuditResultSyncView(APIView):
    """
    EIP -> PIS：核价申请单审核完成后抛转审核结果。

    POST ``/api/pricing/applications/result``
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        manager = SyncManager()
        result = manager.process_pricing_audit_webhook(request.data)
        status_code = 200 if result.get("Status") is True else 400
        return Response(result, status=status_code)


class MiscMaterialSyncView(APIView):
    """
    EIP -> PIS: miscellaneous procurement material master (杂采料号).
    Authenticated via dvadmin-ak-sk (X-NSF-* signature headers).

    POST ``/api/sync/materials/misc``
    """

    # authentication_classes = [AkSkAuthentication]
    # permission_classes = [IsAuthenticated]
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        manager = SyncManager()
        result = manager.process_eip_webhook("misc_material", request.data)
        status_code = 200 if result.get("Status") == "success" else 400
        return Response(result, status=status_code)


class VendorQuotePermissionSyncView(APIView):
    """
    EIP -> PIS: 供应商报价权限资料抛转。

    POST ``/api/sync/vendors/quote-permissions``
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        manager = SyncManager()
        result = manager.process_eip_webhook("vendor_quote_permission", request.data)
        status_code = 200 if result.get("Status") == "success" else 400
        return Response(result, status=status_code)


class RawMaterialSyncView(APIView):
    """
    EIP -> PIS: 原料料号资料抛转（策采相关）。

    POST ``/api/sync/materials/raw``
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        manager = SyncManager()
        result = manager.process_eip_webhook("raw_material", request.data)
        status_code = 200 if result.get("Status") == "success" else 400
        return Response(result, status=status_code)
