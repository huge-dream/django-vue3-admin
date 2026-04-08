"""
杂采料号、核价审核结果 EIP 同步：适配器、SyncManager、HTTP 接口。

数据库：项目以 **SQL Server** 为主；单元测试使用 ``application.test_settings``（复用业务库或
``PIS_TEST_USE_SQLITE=1`` 走 SQLite，见该模块说明）。

使用 pytest + django_db，客户端与 fixtures 与项目 conftest 一致（api_client / authenticate）。

查看 **HTTP 入参 / 出参**（接收请求与返回响应）::

    pytest plugins/test/test_sync_misc_material.py -s -q

（``-s`` 关闭输出捕获；否则仅在失败时可能看到部分输出。）
"""
import json
import uuid

import pytest
from rest_framework import status

from apps.pisadmin.basicinfo.models import SupplierUser
from apps.pisadmin.miscprocurement.models import Inquiry, MiscProcMaterial
from sync.adapters.misc_material import MiscMaterialSyncAdapter
from sync.adapters.pricing_result import PricingResultSyncAdapter
from sync.adapters.vnd_quote_perms import VendorQuotePermissionSyncAdapter
from sync.base import SyncStatus
from sync.factory import SyncFactory
from sync.manager import SyncManager
from sync.models import SyncRecord


def _unique_inquiry_no() -> str:
    return f"U{uuid.uuid4().hex[:16].upper()}"


def _inquiry_price_audit_pending(
    *,
    inquiry_no: str,
    company_code: str = "VC01",
    purchase_type: int = 2,
    approval_number: str = "EIP-AUDIT-01",
    status: int = 7,
) -> Inquiry:
    return Inquiry.objects.create(
        inquiry_no=inquiry_no,
        title="单元测",
        purchase_type=purchase_type,
        template="TPL",
        buyer="u1",
        payment_method=1,
        status=status,
        company_code=company_code,
        approval_number=approval_number,
    )


def _pricing_audit_payload(inquiry_no: str, audit_status: str = "APPROVED") -> dict:
    return {
        "Company": "VC01",
        "eipAuditNo": "EIP-AUDIT-01",
        "purchase_category": "2",
        "inquiryNo": inquiry_no,
        "auditStatus": audit_status,
        "auditUser": "aud1",
        "auditTimestamp": "2026-04-08T10:00:00",
    }


def _quote_permission_payload(
    supplier_id: str = "SUP001",
    supplier_name: str = "测试供应商",
    quote_permission: int = 1,
    email: str = "test@vendor.com",
    name: str = "张三",
    companycode: str = "VC01",
) -> dict:
    return {
        "applyNo": f"APP-{uuid.uuid4().hex[:8].upper()}",
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "quote_permission": quote_permission,
        "email": email,
        "name": name,
        "phone": "13800138000",
        "status": "1",
        "companycode": companycode,
    }


def _log_http_roundtrip(title: str, url: str, payload, response) -> None:
    """在终端打印一次「接收到的请求」与「返回的响应」（需 ``pytest -s``）。"""
    try:
        body_in = json.dumps(payload, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        body_in = repr(payload)
    data = getattr(response, "data", None)
    if data is not None:
        try:
            body_out = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        except (TypeError, ValueError):
            body_out = repr(data)
    else:
        raw = getattr(response, "content", b"") or b""
        body_out = raw.decode("utf-8", errors="replace")[:4000]
    print(
        f"\n{'═' * 56}\n"
        f"  {title}\n"
        f"  ── 请求 (EIP → PIS) ─────────────────────────────\n"
        f"  POST {url}\n"
        f"  Content-Type: application/json\n"
        f"  body:\n{body_in}\n"
        f"  ── 响应 (PIS → EIP) ─────────────────────────────\n"
        f"  status: {response.status_code}\n"
        f"  body:\n{body_out}\n"
        f"{'═' * 56}\n",
        flush=True,
    )


@pytest.mark.django_db
class TestMiscMaterialSyncAdapter:
    """MiscMaterialSyncAdapter：校验、转换、落库。"""

    def test_validate_requires_company_and_material(self):
        adapter = MiscMaterialSyncAdapter()
        assert adapter.validate({}) is False
        assert adapter.validate({"companyCode": "A01"}) is False
        assert adapter.validate({"materialCode": "P1"}) is False
        assert adapter.validate({"companyCode": "A01", "materialCode": "P1"}) is True
        assert adapter.validate({"company_code": "A01", "material_code": "P1"}) is True

    def test_transform_maps_eip_fields(self):
        adapter = MiscMaterialSyncAdapter()
        data = {
            "companyCode": "VC01",
            "materialCode": "M-001",
            "materialName": "说明A",
            "specification": "SPEC-1",
            "unit": "PCS",
            "Category": "2",
            "accountCode": "6001",
        }
        t = adapter.transform_to_local(data)
        assert t["company_code"] == "VC01"
        assert t["partid"] == "M-001"
        assert t["partid_name"] == "说明A"
        assert t["specification"] == "SPEC-1"
        assert t["unit"] == "PCS"
        assert t["partid_category_id"] == 2
        assert t["external_id"] == "VC01_M-001"

    def test_transform_non_numeric_category_goes_to_description(self):
        adapter = MiscMaterialSyncAdapter()
        data = {
            "companyCode": "VC01",
            "materialCode": "M-002",
            "Category": "模治具",
            "accountCode": "ACC1",
        }
        t = adapter.transform_to_local(data)
        assert t["partid_category_id"] is None
        assert "模治具" in (t.get("description") or "")
        assert "ACC1" in (t.get("description") or "")

    def test_push_to_local_creates_misc_proc_material(self):
        adapter = MiscMaterialSyncAdapter()
        payload = {
            "companyCode": "VC01",
            "materialCode": "NEW-PART",
            "materialNameZh": "新料号",
            "specification": "S",
            "unit": "EA",
        }
        op = adapter.push_to_local(payload)
        assert op.status == SyncStatus.SUCCESS
        obj = MiscProcMaterial.objects.get(company_code="VC01", partid="NEW-PART")
        assert obj.partid_name == "新料号"
        assert obj.specification == "S"
        assert obj.unit == "EA"

    def test_push_to_local_update_existing(self):
        adapter = MiscMaterialSyncAdapter()
        MiscProcMaterial.objects.create(
            company_code="VC01",
            partid="UP-1",
            partid_name="旧名",
            specification="old",
            unit="U",
        )
        op = adapter.push_to_local(
            {
                "companyCode": "VC01",
                "materialCode": "UP-1",
                "materialName": "新名",
                "specification": "new",
                "unit": "U",
            }
        )
        assert op.status == SyncStatus.SUCCESS
        obj = MiscProcMaterial.objects.get(company_code="VC01", partid="UP-1")
        assert obj.partid_name == "新名"
        assert obj.specification == "new"


@pytest.mark.django_db
class TestSyncManager:
    """SyncManager.process_eip_webhook"""

    def test_unknown_adapter(self):
        mgr = SyncManager()
        out = mgr.process_eip_webhook("no_such_adapter", {})
        assert out["Status"] == "fail"
        assert "未知" in out["Message"]

    def test_success_writes_sync_record(self):
        mgr = SyncManager()
        payload = {
            "companyCode": "VC01",
            "materialCode": "SR-1",
            "materialName": "记录测试",
            "specification": "",
            "unit": "",
        }
        out = mgr.process_eip_webhook("misc_material", payload)
        assert out["Status"] == "success"
        assert out["Message"] == mgr.SUCCESS_MESSAGE_MISC
        assert SyncRecord.objects.filter(adapter_name="misc_material", status="success").exists()

    def test_validation_failure_writes_failed_record(self):
        mgr = SyncManager()
        out = mgr.process_eip_webhook("misc_material", {"companyCode": "X"})
        assert out["Status"] == "fail"
        assert SyncRecord.objects.filter(adapter_name="misc_material", status="failed").exists()

    def test_pricing_audit_success_writes_sync_record(self):
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no)
        mgr = SyncManager()
        out = mgr.process_pricing_audit_webhook(_pricing_audit_payload(inq_no))
        assert out["Status"] is True
        assert out["Message"] == "审核结果已接收并更新本地单据状态"
        assert SyncRecord.objects.filter(adapter_name="pricing_result", status="success").exists()
        assert Inquiry.objects.get(inquiry_no=inq_no).status == 8

    def test_pricing_audit_validation_failure_writes_failed_record(self):
        mgr = SyncManager()
        out = mgr.process_pricing_audit_webhook({"Company": "VC01"})
        assert out["Status"] is False
        assert SyncRecord.objects.filter(adapter_name="pricing_result", status="failed").exists()

    def test_vendor_quote_permission_success_writes_sync_record(self):
        mgr = SyncManager()
        payload = _quote_permission_payload(supplier_id="VQP-SUP", email="vqp@test.com")
        out = mgr.process_eip_webhook("vendor_quote_permission", payload)
        assert out["Status"] == "success"
        assert SyncRecord.objects.filter(adapter_name="vendor_quote_permission", status="success").exists()
        assert SupplierUser.objects.filter(supplier_id="VQP-SUP", user_email="vqp@test.com").exists()

    def test_vendor_quote_permission_validation_failure_writes_failed_record(self):
        mgr = SyncManager()
        out = mgr.process_eip_webhook("vendor_quote_permission", {"applyNo": "X"})
        assert out["Status"] == "fail"
        assert SyncRecord.objects.filter(adapter_name="vendor_quote_permission", status="failed").exists()


@pytest.mark.django_db
class TestPricingResultSyncAdapter:
    """PricingResultSyncAdapter：校验、转换、落库。"""

    def test_validate_requires_all_fields(self):
        adapter = PricingResultSyncAdapter()
        assert adapter.validate({}) is False
        base = _pricing_audit_payload("X1")
        assert adapter.validate(base) is True
        assert adapter.validate({**base, "Company": ""}) is False

    def test_transform_maps_eip_fields(self):
        adapter = PricingResultSyncAdapter()
        data = {
            "Company": "VC01",
            "eipAuditNo": "EIP-1",
            "purchase_category": "2",
            "inquiryNo": "RFQ99",
            "auditStatus": "APPROVED",
            "auditUser": "u1",
            "auditTimestamp": "2026-01-02T08:30:00",
        }
        t = adapter.transform_to_local(data)
        assert t["company"] == "VC01"
        assert t["eip_audit_no"] == "EIP-1"
        assert t["purchase_category"] == 2
        assert t["inquiry_no"] == "RFQ99"
        assert t["audit_status"] == "APPROVED"
        assert t["external_id"] == "RFQ99_EIP-1"

    def test_push_to_local_approved_updates_inquiry(self):
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no)
        adapter = PricingResultSyncAdapter()
        op = adapter.push_to_local(_pricing_audit_payload(inq_no, "APPROVED"))
        assert op.status == SyncStatus.SUCCESS
        obj = Inquiry.objects.get(inquiry_no=inq_no)
        assert obj.status == 8
        assert obj.approval_status == 1

    def test_push_to_local_rejected_sets_lost(self):
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no)
        adapter = PricingResultSyncAdapter()
        op = adapter.push_to_local(_pricing_audit_payload(inq_no, "REJECTED"))
        assert op.status == SyncStatus.SUCCESS
        obj = Inquiry.objects.get(inquiry_no=inq_no)
        assert obj.status == 9
        assert obj.approval_status == 2

    def test_push_to_local_fails_when_not_price_audit_status(self):
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no, status=5)
        adapter = PricingResultSyncAdapter()
        op = adapter.push_to_local(_pricing_audit_payload(inq_no))
        assert op.status == SyncStatus.FAILED


@pytest.mark.django_db
class TestMiscMaterialSyncAPI:
    """POST /api/sync/material/misc（DRF force_authenticate 绕过 AK/SK 验签，仅测业务链）。"""

    URL = "/api/sync/material/misc"

    def test_post_success(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        payload = {
            "companyCode": "VC01",
            "materialCode": "API-001",
            "materialName": "接口测",
            "specification": "SP",
            "unit": "KG",
        }
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "杂采料号抛转 · 成功", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] == "success"
        assert "物料信息已成功抛转至PIS" in response.data["Message"]
        assert MiscProcMaterial.objects.filter(partid="API-001").exists()

    def test_post_validation_error(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        bad = {"companyCode": ""}
        response = api_client.post(self.URL, data=bad, format="json")
        _log_http_roundtrip("杂采料号抛转 · 校验失败", self.URL, bad, response)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["Status"] == "fail"

    def test_post_allow_any_without_login(self, api_client):
        """EIP 抛转接口当前为 AllowAny：未携带 JWT 也应能调通（与生产验签策略无关时）。"""
        payload = {
            "companyCode": "VC01",
            "materialCode": "NOAUTH-001",
            "materialName": "n",
            "specification": "",
            "unit": "",
        }
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "杂采料号抛转 · 未登录可访问 (AllowAny)", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] == "success"
        assert MiscProcMaterial.objects.filter(partid="NOAUTH-001").exists()


@pytest.mark.django_db
class TestPricingAuditResultSyncAPI:
    """POST /api/pricing/applications/result"""

    URL = "/api/pricing/applications/result"

    def test_post_success_approved(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no)
        payload = _pricing_audit_payload(inq_no)
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "核价审核结果抛转 · 审核通过 APPROVED", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] is True
        assert "审核结果已接收" in response.data["Message"]
        assert Inquiry.objects.get(inquiry_no=inq_no).status == 8

    def test_post_validation_error(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        bad = {"Company": ""}
        response = api_client.post(self.URL, data=bad, format="json")
        _log_http_roundtrip("核价审核结果抛转 · 校验失败", self.URL, bad, response)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["Status"] is False

    def test_post_business_error_wrong_status(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        inq_no = _unique_inquiry_no()
        _inquiry_price_audit_pending(inquiry_no=inq_no, status=5)
        payload = _pricing_audit_payload(inq_no)
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "核价审核结果抛转 · 业务失败(询价单非价格审核)", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["Status"] is False


@pytest.mark.django_db
def test_sync_factory_registers_eip_adapters():
    names = SyncFactory.list_adapters()
    assert "misc_material" in names
    assert "pricing_result" in names
    assert "vendor_quote_permission" in names
    assert isinstance(SyncFactory.create("misc_material"), MiscMaterialSyncAdapter)
    assert isinstance(SyncFactory.create("pricing_result"), PricingResultSyncAdapter)
    assert isinstance(SyncFactory.create("vendor_quote_permission"), VendorQuotePermissionSyncAdapter)


@pytest.mark.django_db
class TestVendorQuotePermissionSyncAdapter:
    """VendorQuotePermissionSyncAdapter：校验、转换、落库。"""

    def test_validate_requires_all_required_fields(self):
        adapter = VendorQuotePermissionSyncAdapter()
        assert adapter.validate({}) is False
        assert adapter.validate({"applyNo": "A1"}) is False
        assert adapter.validate({"supplier_id": "S1"}) is False
        base = _quote_permission_payload()
        assert adapter.validate(base) is True
        assert adapter.validate({**base, "supplier_id": ""}) is False
        assert adapter.validate({**base, "companycode": ""}) is False

    def test_validate_accepts_camel_case_fields(self):
        adapter = VendorQuotePermissionSyncAdapter()
        data = {
            "applyNo": "APP-001",
            "supplier_id": "SUP001",
            "supplier_name": "供应商A",
            "quotePermission": 2,
            "email": "a@b.com",
            "name": "李四",
            "companyCode": "VC02",
        }
        assert adapter.validate(data) is True

    def test_transform_maps_eip_fields(self):
        adapter = VendorQuotePermissionSyncAdapter()
        data = {
            "applyNo": "APP-001",
            "supplier_id": "SUP001",
            "supplier_name": "测试供应商",
            "quote_permission": 2,
            "email": "test@vendor.com",
            "name": "张三",
            "phone": "13800138000",
            "status": "1",
            "companycode": "VC01,VC02",
            "createtime": "2026-04-01T09:00:00",
            "updatetime": "2026-04-08T10:00:00",
        }
        t = adapter.transform_to_local(data)
        assert t["supplier_id"] == "SUP001"
        assert t["supplier_name"] == "测试供应商"
        assert t["quote_permission"] == 2
        assert t["user_email"] == "test@vendor.com"
        assert t["user_name"] == "张三"
        assert t["user_phone"] == "13800138000"
        assert t["status"] == 1
        assert t["company_list"] == ["VC01", "VC02"]

    def test_transform_quote_permission_3_maps_correctly(self):
        adapter = VendorQuotePermissionSyncAdapter()
        data = _quote_permission_payload(quote_permission=3)
        t = adapter.transform_to_local(data)
        assert t["quote_permission"] == 3
        assert t["user_email"] == "test@vendor.com"

    def test_transform_quote_permission_role_mapping(self):
        adapter = VendorQuotePermissionSyncAdapter()
        data1 = _quote_permission_payload(quote_permission=1)
        assert adapter.transform_to_local(data1)["quote_permission"] == 1
        data2 = _quote_permission_payload(quote_permission=2)
        assert adapter.transform_to_local(data2)["quote_permission"] == 2

    def test_push_to_local_creates_supplier_user(self):
        adapter = VendorQuotePermissionSyncAdapter()
        payload = _quote_permission_payload(supplier_id="NEW-SUP", email="new@vendor.com")
        op = adapter.push_to_local(payload)
        assert op.status == SyncStatus.SUCCESS
        obj = SupplierUser.objects.get(supplier_id="NEW-SUP", user_email="new@vendor.com")
        assert obj.supplier_name == "测试供应商"
        assert obj.user_name == "张三"
        assert obj.status == 1
        assert obj.supplier_role == 3

    def test_push_to_local_role_mapping_misc_quote(self):
        adapter = VendorQuotePermissionSyncAdapter()
        payload = _quote_permission_payload(
            supplier_id="MISC-SUP",
            email="misc@vendor.com",
            quote_permission=2,
        )
        op = adapter.push_to_local(payload)
        assert op.status == SyncStatus.SUCCESS
        obj = SupplierUser.objects.get(supplier_id="MISC-SUP", user_email="misc@vendor.com")
        assert obj.supplier_role == 2

    def test_push_to_local_role_mapping_raw_quote(self):
        adapter = VendorQuotePermissionSyncAdapter()
        payload = _quote_permission_payload(
            supplier_id="RAW-SUP",
            email="raw@vendor.com",
            quote_permission=3,
        )
        op = adapter.push_to_local(payload)
        assert op.status == SyncStatus.SUCCESS
        obj = SupplierUser.objects.get(supplier_id="RAW-SUP", user_email="raw@vendor.com")
        assert obj.supplier_role == 1

    def test_push_to_local_update_existing(self):
        SupplierUser.objects.create(
            supplier_id="EXIST-SUP",
            supplier_name="旧名称",
            supplier_role=1,
            user_email="existing@vendor.com",
            user_name="旧用户",
            user_phone="111",
            status=0,
        )
        adapter = VendorQuotePermissionSyncAdapter()
        op = adapter.push_to_local(
            _quote_permission_payload(
                supplier_id="EXIST-SUP",
                supplier_name="新名称",
                email="existing@vendor.com",
                name="新用户",
            )
        )
        assert op.status == SyncStatus.SUCCESS
        obj = SupplierUser.objects.get(supplier_id="EXIST-SUP", user_email="existing@vendor.com")
        assert obj.supplier_name == "新名称"
        assert obj.user_name == "新用户"
        assert obj.status == 1

    def test_push_to_local_multi_company_validation(self):
        """多厂区逗号分隔时会逐个创建，但 SupplierUser.supplier_id + user_email 为唯一键，
        故同一 supplier_id 不同 email 会创建多条记录。"""
        adapter = VendorQuotePermissionSyncAdapter()
        op1 = adapter.push_to_local(
            _quote_permission_payload(
                supplier_id="MULTI-SUP",
                email="user1@vendor.com",
                companycode="VC01,VC02,VC03",
            )
        )
        assert op1.status == SyncStatus.SUCCESS
        op2 = adapter.push_to_local(
            _quote_permission_payload(
                supplier_id="MULTI-SUP",
                email="user2@vendor.com",
                companycode="VC01,VC02",
            )
        )
        assert op2.status == SyncStatus.SUCCESS
        assert SupplierUser.objects.filter(supplier_id="MULTI-SUP").count() == 2


@pytest.mark.django_db
class TestVendorQuotePermissionSyncAPI:
    """POST /api/sync/vendors/quote-permissions"""

    URL = "/api/sync/vendors/quote-permissions"

    def test_post_success(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        payload = _quote_permission_payload(supplier_id="API-SUP", email="api@vendor.com")
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "供应商报价权限抛转 · 成功", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] == "success"
        assert "权限信息已成功跳转至PIS" in response.data["Message"]
        assert SupplierUser.objects.filter(supplier_id="API-SUP", user_email="api@vendor.com").exists()

    def test_post_validation_error(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        bad = {"applyNo": "X"}
        response = api_client.post(self.URL, data=bad, format="json")
        _log_http_roundtrip("供应商报价权限抛转 · 校验失败", self.URL, bad, response)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["Status"] == "fail"

    def test_post_allow_any_without_login(self, api_client):
        """EIP 抛转接口当前为 AllowAny：未携带 JWT 也应能调通。"""
        payload = _quote_permission_payload(supplier_id="NOAUTH-SUP", email="noauth@vendor.com")
        response = api_client.post(self.URL, data=payload, format="json")
        _log_http_roundtrip(
            "供应商报价权限抛转 · 未登录可访问 (AllowAny)", self.URL, payload, response
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] == "success"
        assert SupplierUser.objects.filter(supplier_id="NOAUTH-SUP", user_email="noauth@vendor.com").exists()
