import pytest
from apps.pisadmin.basicinfo.factories import CurrencyFactory
from apps.pisadmin.basicinfo.models import Currency


# API 统一响应格式: { "code": 2000, "data": ..., "msg": ... }
# code=2000 表示成功, code=4000 表示认证/权限/参数错误
CODE_SUCCESS = 2000
CODE_ERROR = 4000


@pytest.mark.django_db
class TestCurrencyViewSet:

    def test_list_currencies(self, authenticate):
        """GET 列表返回成功 + 分页结构"""
        CurrencyFactory.create_batch(3)
        response = authenticate.get("/api/pisadmin/basicinfo/currencies/")
        assert response.data["code"] == CODE_SUCCESS

    def test_create_currency_success(self, authenticate):
        """POST 创建返回成功 + DB 记录"""
        payload = {
            "currencyname": "英镑",
            "currencycode": "GBP",
            "currencysymbol": "£",
            "tax": "20.0",
        }
        response = authenticate.post(
            "/api/pisadmin/basicinfo/currencies/", data=payload, format="json"
        )
        assert response.data["code"] == CODE_SUCCESS
        assert Currency.objects.filter(currencycode="GBP").exists()

    def test_create_currency_unauthenticated(self, api_client):
        """未认证请求返回错误码"""
        payload = {
            "currencyname": "英镑",
            "currencycode": "GBP",
            "currencysymbol": "£",
            "tax": "20.0",
        }
        response = api_client.post(
            "/api/pisadmin/basicinfo/currencies/", data=payload, format="json"
        )
        assert response.data["code"] == CODE_ERROR

    def test_retrieve_currency(self, authenticate):
        """GET 详情返回成功 + 完整字段"""
        currency = CurrencyFactory(currencyname="澳元", currencycode="AUD")
        response = authenticate.get(
            f"/api/pisadmin/basicinfo/currencies/{currency.id}/"
        )
        assert response.data["code"] == CODE_SUCCESS
        assert response.data["data"]["currencyname"] == "澳元"

    def test_update_currency_put(self, authenticate):
        """PUT 全量更新返回成功"""
        currency = CurrencyFactory(currencyname="旧货币")
        payload = {
            "currencyname": "新货币",
            "currencycode": "NEW",
            "currencysymbol": "N",
            "tax": "10.0",
        }
        response = authenticate.put(
            f"/api/pisadmin/basicinfo/currencies/{currency.id}/",
            data=payload,
            format="json",
        )
        assert response.data["code"] == CODE_SUCCESS
        currency.refresh_from_db()
        assert currency.currencyname == "新货币"

    def test_delete_currency(self, authenticate):
        """DELETE 返回成功 + 记录消失"""
        currency = CurrencyFactory()
        response = authenticate.delete(
            f"/api/pisadmin/basicinfo/currencies/{currency.id}/"
        )
        assert response.data["code"] == CODE_SUCCESS
        assert not Currency.objects.filter(id=currency.id).exists()

    def test_delete_currency_unauthenticated_forbidden(self, api_client):
        """未认证删除返回错误码"""
        currency = CurrencyFactory()
        response = api_client.delete(
            f"/api/pisadmin/basicinfo/currencies/{currency.id}/"
        )
        assert response.data["code"] == CODE_ERROR

    def test_create_currency_invalid_data(self, authenticate):
        """非法数据返回错误码 + 错误信息"""
        payload = {"currencyname": ""}  # 缺少必填字段
        response = authenticate.post(
            "/api/pisadmin/basicinfo/currencies/", data=payload, format="json"
        )
        assert response.data["code"] == CODE_ERROR
        assert "货币名称" in response.data["msg"]
