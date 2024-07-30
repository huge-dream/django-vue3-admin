from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from dvadmin.utils.models import table_prefix, CoreModel


# Create your models here.


# 服务器账号
class ConsoleAccount(CoreModel):
    account = models.CharField(max_length=50, verbose_name='账号')
    access_key = models.CharField(max_length=100, verbose_name='Access Key')
    secret_key = models.CharField(max_length=100, verbose_name='Secret Key')

    def __str__(self):
        return self.account

    class Meta:
        db_table = table_prefix + 'daily_report_console_account'
        verbose_name = '服务器账号'
        verbose_name_plural = verbose_name
        ordering = ['account']


# quick账号
class QuickAccount(CoreModel):
    account = models.CharField(max_length=50, verbose_name='账号')
    password = models.CharField(max_length=50, verbose_name='密码')

    def __str__(self):
        return self.account

    class Meta:
        db_table = table_prefix + 'daily_report_quick_account'
        verbose_name = 'quick账号'
        verbose_name_plural = verbose_name
        ordering = ['account']


class ReportData(CoreModel):
    date = models.DateField(verbose_name='日期', unique=True)
    data = models.JSONField(verbose_name='数据', null=True, blank=True)

    def __str__(self):
        return str(self.date)

    class Meta:
        db_table = table_prefix + 'daily_report_data'
        verbose_name = '日报信息'
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


class Consoles(CoreModel):
    account = models.CharField(max_length=50, verbose_name='所属账号')
    instance_id = models.CharField(max_length=50, verbose_name='实例ID')
    instance_name = models.CharField(max_length=50, verbose_name='实例名称')
    status = models.CharField(max_length=50, verbose_name='状态')
    instance_type_id = models.CharField(max_length=50, verbose_name='规格')
    cpus = models.CharField(max_length=50, verbose_name='CPU')
    memory_size = models.CharField(max_length=50, verbose_name='内存')
    eip_address = models.CharField(max_length=50, verbose_name='主IPv4地址')
    primary_ip_address = models.CharField(max_length=50, verbose_name='次IPv4地址')
    instance_charge_type = models.CharField(max_length=50, verbose_name='实例计费类型')
    expired_at = models.DateTimeField(verbose_name='到期时间')
    renewal_status = models.BooleanField(default=False, verbose_name='续费状态')

    def __str__(self):
        return self.instance_name

    class Meta:
        db_table = table_prefix + 'daily_report_consoles'
        verbose_name = '实例信息'
        verbose_name_plural = verbose_name
        ordering = ['expired_at']

    def save(self, *args, **kwargs):
        if self.expired_at and timezone.is_naive(self.expired_at):
            self.expired_at = timezone.make_aware(self.expired_at)
        super().save(*args, **kwargs)
