from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer

from .models import ProcMaterial


class ProcMaterialSerializer(CustomModelSerializer):
    """策采料号信息-序列化器"""

    class Meta:
        model = ProcMaterial
        fields = "__all__"
        read_only_fields = ["id"]


class ProcMaterialCreateUpdateSerializer(CustomModelSerializer):
    """策采料号信息 创建/更新"""

    material_name_zh = serializers.CharField(max_length=50)
    specification = serializers.CharField(max_length=50)
    unit = serializers.CharField(max_length=50)

    class Meta:
        model = ProcMaterial
        fields = "__all__"
