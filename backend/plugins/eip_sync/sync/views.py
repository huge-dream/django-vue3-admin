from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dvadmin_ak_sk.libs.authentication import AkSkAuthentication

from sync.manager import SyncManager


class MiscMaterialSyncView(APIView):
    """
    EIP -> PIS: miscellaneous procurement material master (杂采料号).
    Authenticated via dvadmin-ak-sk (X-NSF-* signature headers).
    """

    authentication_classes = [AkSkAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        manager = SyncManager()
        result = manager.process_eip_webhook("misc_material", request.data)
        status_code = 200 if result.get("Status") == "success" else 400
        return Response(result, status=status_code)
