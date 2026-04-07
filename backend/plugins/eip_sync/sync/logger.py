import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sync.base import SyncOperationResult


class SyncLogger:
    def __init__(self, name: str = "pis.sync"):
        self.logger = logging.getLogger(name)

    def log_sync(self, record: "SyncOperationResult", level: str = "INFO") -> None:
        message = (
            f"[{record.adapter_name}] direction={record.direction.value} "
            f"status={record.status.value} external_id={record.external_id} "
            f"error={record.error_message or 'none'}"
        )
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
