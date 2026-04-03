import pytest
from apps.pisadmin.basicinfo.factories import CurrencyFactory
from apps.pisadmin.basicinfo.views.currency import CurrencySerializer, CurrencyCreateUpdateSerializer


# DRF 的 django_restql DynamicFieldsMixin 使用 model verbose_name 作为 error key
# 例如 currencyname 字段的 error key 是 "货币名称"（模型的 verbose_name）
# 以下是字段名到 error key 的映射
FIELD_ERROR_KEYS = {
    "currencyname": "货币名称",
    "currencycode": "货币代码",
    "currencysymbol": "货币符号",
    "tax": "税率",
}


@pytest.mark.django_db
class TestCurrencyCreateUpdateSerializer:

    def test_create_currency_success(self):
        """合法数据应创建成功"""
        data = {
            "currencyname": "人民币",
            "currencycode": "CNY",
            "currencysymbol": "¥",
            "tax": "6.5",
        }
        serializer = CurrencyCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.currencyname == "人民币"
        assert instance.currencycode == "CNY"

    def test_currencyname_required(self):
        """currencyname 必填"""
        data = {
            "currencycode": "CNY",
            "currencysymbol": "¥",
            "tax": "6.5",
        }
        serializer = CurrencyCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert FIELD_ERROR_KEYS["currencyname"] in serializer.errors

    def test_currencysymbol_required(self):
        """currencysymbol 必填"""
        data = {
            "currencyname": "美元",
            "currencycode": "USD",
            "tax": "6.5",
        }
        serializer = CurrencyCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert FIELD_ERROR_KEYS["currencysymbol"] in serializer.errors

    def test_tax_required(self):
        """tax 必填"""
        data = {
            "currencyname": "日元",
            "currencycode": "JPY",
            "currencysymbol": "¥",
        }
        serializer = CurrencyCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert FIELD_ERROR_KEYS["tax"] in serializer.errors

    @pytest.mark.parametrize(
        "field,invalid_value",
        [
            ("currencyname", ""),  # 空字符串
            ("currencyname", "A" * 100),  # 超过 max_length=50
            ("currencycode", "A" * 100),  # 超过 max_length=20
            ("currencysymbol", "A" * 100),  # 超过 max_length=10
        ],
    )
    def test_field_max_length_validation(self, field, invalid_value):
        """字段长度超限应返回 ValidationError"""
        data = {
            "currencyname": "测试",
            "currencycode": "CNY",
            "currencysymbol": "¥",
            "tax": "6.5",
        }
        data[field] = invalid_value
        serializer = CurrencyCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert FIELD_ERROR_KEYS[field] in serializer.errors

    def test_update_currency_success(self, db):
        """更新已有记录"""
        existing = CurrencyFactory(currencyname="旧名称")
        data = {
            "currencyname": "新名称",
            "currencycode": "USD",
            "currencysymbol": "$",
            "tax": "5.0",
        }
        serializer = CurrencyCreateUpdateSerializer(instance=existing, data=data)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.currencyname == "新名称"


@pytest.mark.django_db
class TestCurrencySerializer:

    def test_serialize_currency(self):
        """序列化输出包含所有字段"""
        currency = CurrencyFactory(
            currencyname="欧元",
            currencycode="EUR",
            currencysymbol="€",
        )
        serializer = CurrencySerializer(currency)
        data = serializer.data
        assert data["currencyname"] == "欧元"
        assert data["currencycode"] == "EUR"
        assert data["currencysymbol"] == "€"
