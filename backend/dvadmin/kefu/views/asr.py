# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import Asr
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class AsrSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = Asr
        fields = "__all__"
        read_only_fields = ["id"]


class AsrViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Asr.objects.all()
    serializer_class = AsrSerializer
    # permission_classes = []
