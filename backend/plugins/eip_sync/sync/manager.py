from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.db import DatabaseError, transaction
from django.utils import timezone

from sync.base import SyncOperationResult, SyncStatus
from sync.factory import SyncFactory
from sync.logger import SyncLogger
from sync.models import SyncRecord

logger = logging.getLogger(__name__)


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

    def process_pricing_audit_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """EIP 核价审核结果：返回 ``Status`` 为 bool、成功文案与接口规范一致。"""
        adapter_name = "pricing_result"
        if adapter_name not in SyncFactory.list_adapters():
            return {"Status": False, "Message": f"未知的适配器: {adapter_name}"}

        adapter = SyncFactory.create(adapter_name)
        op = adapter.push_to_local(data)
        self._persist_record(op)
        self.logger.log_sync(op)

        if op.status == SyncStatus.SUCCESS:
            return {
                "Status": True,
                "Message": "审核结果已接收并更新本地单据状态",
            }

        err = op.error_message or "同步失败"
        if err.startswith("保存失败: "):
            err = err[len("保存失败: ") :]
        return {"Status": False, "Message": err}

    def _persist_record(self, op: SyncOperationResult) -> None:
        """写入审计表；失败仅记日志，不向上抛，避免 EIP 回调拿不到约定 JSON。

        使用独立 ``atomic()``：在 SQL Server 上失败语句会中止当前事务；嵌套块以保存点回滚，
        避免污染外层请求/测试事务（否则后续 ORM 报 TransactionManagementError）。
        """
        completed_at = timezone.now()
        try:
            with transaction.atomic():
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
        except DatabaseError as exc:
            logger.warning(
                "SyncRecord 落库失败（请确认已执行: python manage.py migrate sync）。%s",
                exc,
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
