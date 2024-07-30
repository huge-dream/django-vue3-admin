from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class IncomeData(CoreModel):
    date = models.DateField(verbose_name='日期', unique=True)
    data = models.JSONField(verbose_name='数据', null=True, blank=True)
    error = models.JSONField(verbose_name='错误信息', null=True, blank=True)

    def __str__(self):
        return str(self.date)

    class Meta:
        db_table = table_prefix + 'income_statement_data'
        verbose_name = '收入信息'
        verbose_name_plural = verbose_name
        ordering = ['-date']

    def clean(self):
        try:
            datetime.strptime(str(self.date), '%Y-%m-%d')
        except ValueError:
            raise ValidationError("日期格式错误。请使用YYYY-MM-DD格式。")

    def save(self, *args, **kwargs):
        self.clean()
        self.data = self.data or {}
        super().save(*args, **kwargs)
