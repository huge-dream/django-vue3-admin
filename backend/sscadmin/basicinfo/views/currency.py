# -*- coding: utf-8 -*-
from rest_framework import serializers

from sscadmin.basicinfo.models import Currency
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class CurrencySerializer(CustomModelSerializer):
    """币别税率-序列化器"""

    class Meta:
        model = Currency
        fields = "__all__"
        read_only_fields = ["id"]


class CurrencyCreateUpdateSerializer(CustomModelSerializer):
    """币别税率 创建/更新"""

    currencyname = serializers.CharField(max_length=50)
    currencycode = serializers.CharField(max_length=20, allow_blank=True, required=False)
    currencysymbol = serializers.CharField(max_length=10)
    factory = serializers.CharField(max_length=10, allow_blank=True, required=False)

    class Meta:
        model = Currency
        fields = "__all__"


class CurrencyViewSet(CustomModelViewSet):
    """币别税率管理接口"""

    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    create_serializer_class = CurrencyCreateUpdateSerializer
    update_serializer_class = CurrencyCreateUpdateSerializer
    search_fields = ["currencyname", "currencycode", "currencysymbol", "factory"]
    ordering = ["-create_datetime"]
