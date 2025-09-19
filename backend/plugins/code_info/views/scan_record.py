from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from plugins.code_info.models import ScanData


class ScanRecordSerializer(CustomModelSerializer):
    """
    扫码数据-序列化器
    """

    class Meta:
        model = ScanData
        fields = "__all__"
        read_only_fields = ["id"]


class ScanRecordViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    异常扫码数据记录接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = ScanData.objects.exclude(status=1)
    serializer_class = ScanRecordSerializer
    extra_filter_class = []
