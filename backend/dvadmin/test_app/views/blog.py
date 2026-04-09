# -*- coding: utf-8 -*-
"""
@Remark: 博客管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.test_app.models import Blog
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class BlogSerializer(CustomModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class BlogViewSet(CustomModelViewSet):
    """
    博客管理
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    @action(methods=['get'], detail=False)
    def published_list(self, request):
        """获取已发布的博客列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(methods=['post'], detail=False)
    def batch_publish(self, request):
        """批量发布博客"""
        ids = request.data.get('ids', [])
        Blog.objects.filter(id__in=ids).update(status=1)
        return SuccessResponse(msg="批量发布成功")
