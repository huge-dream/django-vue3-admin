# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import DisNumber
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class DisNumberSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = DisNumber
        fields = "__all__"
        read_only_fields = ["id"]


class DisNumberViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = DisNumber.objects.all()
    serializer_class = DisNumberSerializer
    # permission_classes = []
