from dvadmin.utils.viewset import CustomModelViewSet

from .models import ProcMaterial
from .serializers import ProcMaterialSerializer, ProcMaterialCreateUpdateSerializer


class ProcMaterialViewSet(CustomModelViewSet):
    """策采料号信息"""

    queryset = ProcMaterial.objects.all()
    serializer_class = ProcMaterialSerializer
    create_serializer_class = ProcMaterialCreateUpdateSerializer
    update_serializer_class = ProcMaterialCreateUpdateSerializer
    filter_fields = ["company_code", "material_code", "partid_category_id", "status"]
    search_fields = ["company_code", "material_code", "material_name_zh", "material_name_en"]
    ordering = ["-create_datetime"]
