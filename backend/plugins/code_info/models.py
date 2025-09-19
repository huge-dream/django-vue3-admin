from django.db import models

from django.db import models
from dvadmin.utils.models import CoreModel

table_prefix = "release_info_"


class ScanData(CoreModel):
    # 产品件号、供应商代码、生产批次、产品序列码、版本号、扫码时间、班次和人员信息
    code = models.CharField(null=True, blank=True, max_length=255, verbose_name='扫码值', help_text='扫码值')
    product_code = models.CharField(null=True, blank=True, max_length=255, verbose_name='产品件号', help_text='产品件号')
    supplier_code = models.CharField(null=True, blank=True, max_length=255, verbose_name='供应商代码', help_text='供应商代码')
    production_batch = models.CharField(null=True, blank=True, max_length=255, verbose_name='生产批次', help_text='生产批次')
    product_serial_number = models.CharField(null=True, blank=True, max_length=255, verbose_name='产品序列码', help_text='产品序列码')
    version_number = models.CharField(null=True, blank=True, max_length=255, verbose_name='版本号', help_text='版本号')
    shift = models.CharField(null=True, blank=True, max_length=255, verbose_name='班次', help_text='班次')
    STATUS_EMU = (
        (0, "重复扫码"),
        (1, "正常"),
        (2, "未识别码"),
    )
    status = models.IntegerField(default=1, choices=STATUS_EMU, verbose_name='状态', help_text='状态')

    class Meta:
        db_table = table_prefix + "scan_data"
        verbose_name = "扫码数据"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
