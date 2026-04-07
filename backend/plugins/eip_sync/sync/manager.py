from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.utils import timezone

from sync.base import SyncOperationResult, SyncStatus
from sync.factory import SyncFactory
from sync.logger import SyncLogger
from sync.models import SyncRecord


class SyncManager:
    """Routes inbound EIP webhooks to registered adapters."""

    SUCCESS_MESSAGE_MISC = "物料信息已成功抛转至PIS"

    def __init__(self):
        self.logger = SyncLogger()

    def process_eip_webhook(self, adapter_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if adapter_name not in SyncFactory.list_adapters():
            return {"Status": "fail", "Message": f"未知的适配器: {adapter_name}"}

        adapter = SyncFactory.create(adapter_name)
        op = adapter.push_to_local(data)
        self._persist_record(op)
        self.logger.log_sync(op)

        if op.status == SyncStatus.SUCCESS:
            message = (
                self.SUCCESS_MESSAGE_MISC if adapter_name == "misc_material" else "同步成功"
            )
            return {"Status": "success", "Message": message}

        return {"Status": "fail", "Message": op.error_message or "同步失败"}

    def _persist_record(self, op: SyncOperationResult) -> None:
        completed_at = timezone.now()
        SyncRecord.objects.create(
            adapter_name=op.adapter_name,
            direction=op.direction.value,
            external_id=op.external_id or "",
            payload=op.payload,
            response=op.response,
            status=op.status.value,
            error_message=op.error_message or "",
            retry_count=op.retry_count,
            completed_at=completed_at,
        )

    def get_sync_history(
        self,
        adapter_name: Optional[str] = None,
        direction: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[SyncRecord]:
        qs = SyncRecord.objects.all()
        if adapter_name:
            qs = qs.filter(adapter_name=adapter_name)
        if direction:
            qs = qs.filter(direction=direction)
        if status:
            qs = qs.filter(status=status)
        return list(qs[:limit])
