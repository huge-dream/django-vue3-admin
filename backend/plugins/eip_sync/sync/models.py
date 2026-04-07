from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


class SyncRecord(CoreModel):
    """Inbound/outbound sync audit row."""

    SYNC_DIRECTION_CHOICES = (
        ("eip_to_pis", "EIP to PIS"),
        ("pis_to_eip", "PIS to EIP"),
    )

    SYNC_STATUS_CHOICES = (
        ("pending", "待处理"),
        ("success", "成功"),
        ("failed", "失败"),
        ("retrying", "重试中"),
    )

    adapter_name = models.CharField(max_length=50, verbose_name="适配器名称", db_index=True)
    direction = models.CharField(max_length=20, choices=SYNC_DIRECTION_CHOICES, verbose_name="同步方向")
    external_id = models.CharField(max_length=100, blank=True, verbose_name="外部单号", db_index=True)
    payload = models.JSONField(null=True, blank=True, verbose_name="请求数据")
    response = models.JSONField(null=True, blank=True, verbose_name="响应数据")
    status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default="pending",
        verbose_name="状态",
        db_index=True,
    )
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    retry_count = models.IntegerField(default=0, verbose_name="重试次数")
    retry_max = models.IntegerField(default=3, verbose_name="最大重试次数")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    class Meta:
        db_table = table_prefix + "sync_record"
        verbose_name = "数据同步记录"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        indexes = [
            models.Index(fields=["adapter_name", "status"]),
            models.Index(fields=["external_id"]),
            models.Index(fields=["create_datetime"]),
        ]

    def __str__(self) -> str:
        return f"{self.adapter_name} - {self.direction} - {self.status}"
