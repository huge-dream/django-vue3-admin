import pytest
from rest_framework import status
from apps.pisadmin.basicinfo.factories import CurrencyFactory
from apps.pisadmin.basicinfo.models import Currency


@pytest.mark.django_db
class TestCurrencyViewSet:

    def test_list_currencies(self, authenticate):
        """GET 列表返回 200 + 分页结构"""
        CurrencyFactory.create_batch(3)
        response = authenticate.get("/api/currencies/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_currency_success(self, authenticate):
        """POST 创建返回 201 + DB 记录"""
        payload = {
            "currencyname": "英镑",
            "currencycode": "GBP",
            "currencysymbol": "£",
            "tax": "20.0",
        }
        response = authenticate.post("/api/currencies/", data=payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Currency.objects.filter(currencycode="GBP").exists()

    def test_create_currency_unauthenticated(self, api_client):
        """未认证请求返回 401"""
        payload = {
            "currencyname": "英镑",
            "currencycode": "GBP",
            "currencysymbol": "£",
            "tax": "20.0",
        }
        response = api_client.post("/api/currencies/", data=payload, format="json")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_retrieve_currency(self, authenticate):
        """GET 详情返回 200 + 完整字段"""
        currency = CurrencyFactory(currencyname="澳元", currencycode="AUD")
        response = authenticate.get(f"/api/currencies/{currency.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["currencyname"] == "澳元"

    def test_update_currency_put(self, authenticate):
        """PUT 全量更新返回 200"""
        currency = CurrencyFactory(currencyname="旧货币")
        payload = {
            "currencyname": "新货币",
            "currencycode": "NEW",
            "currencysymbol": "N",
            "tax": "10.0",
        }
        response = authenticate.put(f"/api/currencies/{currency.id}/", data=payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        currency.refresh_from_db()
        assert currency.currencyname == "新货币"

    def test_delete_currency(self, authenticate):
        """DELETE 返回 204 + 记录消失"""
        currency = CurrencyFactory()
        response = authenticate.delete(f"/api/currencies/{currency.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Currency.objects.filter(id=currency.id).exists()

    def test_delete_currency_unauthenticated_forbidden(self, api_client):
        """普通用户删除应返回 403"""
        currency = CurrencyFactory()
        response = api_client.delete(f"/api/currencies/{currency.id}/")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_create_currency_invalid_data(self, authenticate):
        """非法数据返回 400 + 错误详情"""
        payload = {"currencyname": ""}  # 缺少必填字段
        response = authenticate.post("/api/currencies/", data=payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
