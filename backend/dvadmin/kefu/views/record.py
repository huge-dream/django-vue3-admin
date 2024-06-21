# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import Record
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class RecordSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = Record
        fields = "__all__"
        read_only_fields = ["id"]


class RecordViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    # permission_classes = []
