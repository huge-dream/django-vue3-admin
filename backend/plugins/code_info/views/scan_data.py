from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.validator import CustomValidationError
from dvadmin.utils.viewset import CustomModelViewSet
from plugins.code_info.models import ScanData


class ScanDataSerializer(CustomModelSerializer):
    """
    扫码数据-序列化器
    """

    class Meta:
        model = ScanData
        fields = "__all__"
        read_only_fields = ["id"]

class CreateScanDataSerializer(CustomModelSerializer):
    """
    扫码数据-序列化器
    """

    def create(self, validated_data):
        code = validated_data.get("code")
        print(code)
        code_list = code.split("/")
        if len(code_list) == 5:
            validated_data["product_code"] = code_list[0]
            validated_data["supplier_code"] = code_list[1]
            validated_data["production_batch"] = code_list[2]
            validated_data["product_serial_number"] = code_list[3]
            validated_data["version_number"] = code_list[4]
            validated_data["shift"] = self.request.user.description
        instance = super().create(validated_data)
        # 1.格式错误
        if len(code_list) != 5:
            instance.status = 2
            instance.save()
            raise CustomValidationError("数据格式错误")
        # 2.查询数据是否已存在数据库
        print("ScanData.objects.filter(code=code, status=1)",ScanData.objects.filter(code=code, status=1))
        if ScanData.objects.filter(code=code, status=1).exclude(id=instance.id).exists():
            instance.status = 0
            instance.save()
            raise CustomValidationError("重复扫码")
        return instance


    class Meta:
        model = ScanData
        fields = "__all__"
        read_only_fields = ["id"]


class ScanDataViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    扫码数据接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = ScanData.objects.filter(status=1)
    serializer_class = ScanDataSerializer
    create_serializer_class = CreateScanDataSerializer
    extra_filter_class = []
