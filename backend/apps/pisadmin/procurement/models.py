import logging
from typing import Iterable, Optional

from django.db import models
from django.utils import timezone

from dvadmin.utils.models import CoreModel, table_prefix

logger = logging.getLogger(__name__)


class ProcMaterial(CoreModel):
    """策采料号信息"""

    CATEGORY_CHOICES = (
        (1, "注塑"),
        (2, "冲压"),
    )

    company_code = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)")
    material_code = models.CharField(max_length=50, verbose_name="料号", help_text="料号(物料编码)")
    material_name_zh = models.CharField(max_length=50, verbose_name="中文品名", help_text="中文品名")
    material_name_en = models.CharField(max_length=50, verbose_name="英文品名", help_text="英文品名", null=True, blank=True)
    material_name_vi = models.CharField(max_length=50, verbose_name="越文品名", help_text="越文品名", null=True, blank=True)
    specification = models.CharField(max_length=50, verbose_name="品名规格", help_text="品名规格")
    unit = models.CharField(max_length=50, verbose_name="单位", help_text="单位")
    source_code = models.CharField(max_length=50, verbose_name="来源码", help_text="来源码", null=True, blank=True)
    model_type = models.CharField(max_length=50, verbose_name="機種別", help_text="機種別", null=True, blank=True)
    product_category = models.CharField(max_length=50, verbose_name="产品分类", help_text="产品分类", null=True, blank=True)
    group_code = models.CharField(max_length=50, verbose_name="分群码", help_text="分群码", null=True, blank=True)
    material_group = models.CharField(max_length=50, verbose_name="物料群组", help_text="物料群组", null=True, blank=True)
    market_class = models.CharField(max_length=50, verbose_name="市场分类", help_text="市场分类", null=True, blank=True)
    approval_status = models.CharField(max_length=50, verbose_name="料号状态", help_text="料号状态(承认否)", null=True, blank=True)
    partid_category_id = models.IntegerField(choices=CATEGORY_CHOICES, verbose_name="物料分类", help_text="物料分类(1：注塑，2：冲压)", null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name="启用否", help_text="启用否(1:启用 0:禁用)")

    class Meta:
        db_table = table_prefix + "proc_materials"
        verbose_name = "策采料号信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        unique_together = ("company_code", "material_code")

    def __str__(self):
        return self.material_name_zh or self.material_code