# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import SipUser
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class SipUserSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = SipUser
        fields = "__all__"
        read_only_fields = ["id"]


class SipUserViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = SipUser.objects.all()
    serializer_class = SipUserSerializer
    # permission_classes = []
