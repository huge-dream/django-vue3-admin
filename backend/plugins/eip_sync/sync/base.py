from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SyncDirection(str, Enum):
    EIP_TO_PIS = "eip_to_pis"
    PIS_TO_EIP = "pis_to_eip"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class SyncOperationResult:
    """In-memory result of a single sync operation (not the ORM SyncRecord)."""

    adapter_name: str = ""
    direction: SyncDirection = SyncDirection.EIP_TO_PIS
    external_id: str = ""
    payload: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    status: SyncStatus = SyncStatus.PENDING
    error_message: str = ""
    retry_count: int = 0
    created_at: Optional[datetime] = None


class BaseSyncAdapter(ABC):
    adapter_name: str = ""
    direction: SyncDirection = SyncDirection.EIP_TO_PIS

    def __init__(self, eip_client=None, logger=None):
        self.eip_client = eip_client
        self.logger = logger

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def transform_to_local(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def transform_to_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save_to_local(self, transformed_data: Dict[str, Any]) -> bool:
        pass

    def push_to_local(self, data: Dict[str, Any]) -> SyncOperationResult:
        created_at = datetime.now()
        record = SyncOperationResult(
            adapter_name=self.adapter_name,
            direction=self.direction,
            payload=data,
            created_at=created_at,
        )

        if not self.validate(data):
            record.status = SyncStatus.FAILED
            record.error_message = "数据校验失败"
            return record

        try:
            transformed = self.transform_to_local(data)
        except Exception as e:
            record.status = SyncStatus.FAILED
            record.error_message = f"数据转换失败: {e}"
            return record

        try:
            success = self.save_to_local(transformed)
            record.status = SyncStatus.SUCCESS if success else SyncStatus.FAILED
            record.external_id = transformed.get("external_id", "")
            if not success:
                record.error_message = record.error_message or "保存失败"
        except Exception as e:
            record.status = SyncStatus.FAILED
            record.error_message = f"保存失败: {e}"

        return record
