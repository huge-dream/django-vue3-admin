# -*- coding: utf-8 -*-
"""
@Remark: 产品管理
"""
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.test_app.models import Product
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class ProductSerializer(CustomModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductViewSet(CustomModelViewSet):
    """
    产品管理
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(methods=['get'], detail=False)
    def low_stock_alert(self, request):
        """库存预警列表"""
        threshold = int(request.query_params.get('threshold', 10))
        queryset = self.filter_queryset(self.get_queryset().filter(stock__lt=threshold))
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(methods=['post'], detail=False)
    def batch_adjust_price(self, request):
        """批量调整价格"""
        ids = request.data.get('ids', [])
        rate = request.data.get('rate', 1.0)
        for product in Product.objects.filter(id__in=ids):
            product.price = product.price * rate
            product.save()
        return SuccessResponse(msg="价格调整成功")
