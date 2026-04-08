"""
杂采料号 EIP 同步：适配器、SyncManager、HTTP 接口。

使用 pytest + django_db，客户端与 fixtures 与项目 conftest 一致（api_client / authenticate）。
"""
import pytest
from rest_framework import status

from apps.pisadmin.miscprocurement.models import MiscProcMaterial
from sync.adapters.misc_material import MiscMaterialSyncAdapter
from sync.base import SyncStatus
from sync.factory import SyncFactory
from sync.manager import SyncManager
from sync.models import SyncRecord


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


@pytest.mark.django_db
class TestMiscMaterialSyncAPI:
    """POST /api/sync/material/misc/（DRF force_authenticate 绕过 AK/SK 验签，仅测业务链）。"""

    URL = "/api/sync/material/misc/"

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
        assert response.status_code == status.HTTP_200_OK
        assert response.data["Status"] == "success"
        assert "物料信息已成功抛转至PIS" in response.data["Message"]
        assert MiscProcMaterial.objects.filter(partid="API-001").exists()

    def test_post_validation_error(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            self.URL, data={"companyCode": ""}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["Status"] == "fail"

    def test_post_unauthenticated(self, api_client):
        response = api_client.post(
            self.URL,
            data={
                "companyCode": "VC01",
                "materialCode": "X",
                "materialName": "n",
                "specification": "",
                "unit": "",
            },
            format="json",
        )
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


@pytest.mark.django_db
def test_sync_factory_registers_misc_material():
    assert "misc_material" in SyncFactory.list_adapters()
    adapter = SyncFactory.create("misc_material")
    assert isinstance(adapter, MiscMaterialSyncAdapter)
