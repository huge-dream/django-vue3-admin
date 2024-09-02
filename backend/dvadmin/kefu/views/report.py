# -*- coding: utf-8 -*-
"""
"""
from dvadmin.kefu.models import Report
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class ReportSerializer(CustomModelSerializer):
    """
    接口白名单-序列化器
    """

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["id"]


class ReportViewSet(CustomModelViewSet):
    """
    接口白名单
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    # permission_classes = []
