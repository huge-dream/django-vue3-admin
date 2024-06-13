# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import SipTrunk
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class SipTrunkSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = SipTrunk
        fields = "__all__"
        read_only_fields = ["id"]


class SipTrunkViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = SipTrunk.objects.all()
    serializer_class = SipTrunkSerializer
    # permission_classes = []
