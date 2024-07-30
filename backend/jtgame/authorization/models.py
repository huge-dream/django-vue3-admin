from django.db import models

from dvadmin.system.models import Dept
from dvadmin.utils.models import CoreModel, table_prefix
from jtgame.utils import parse_iso_datetime


# Create your models here.


class AuthorizationInfo(CoreModel):
    entity = models.CharField(max_length=50, verbose_name='主体')
    name = models.CharField(max_length=50, verbose_name='版号')
    publisher = models.CharField(max_length=100, verbose_name='出版社')
    software_registration_number = models.CharField(max_length=50, verbose_name='软著登记编号')
    isbn = models.CharField(max_length=50, verbose_name='出版物号')
    publication_approval_number = models.CharField(max_length=50, verbose_name='出版复批文号')
    authorization_start_date = models.DateField(verbose_name='授权开始日期')
    authorization_end_date = models.DateField(verbose_name='授权结束日期')
    icp_license = models.CharField(max_length=50, verbose_name='ICP备案/许可证书', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'authorization_info'
        verbose_name = '版号信息'
        verbose_name_plural = verbose_name
        ordering = ['-authorization_end_date']


class AuthorizationConfig(CoreModel):
    TYPE_LIST = (
        (0, "text"),
        (1, "number"),
        (2, "date"),
        (6, "boolean"),
    )
    key = models.CharField(max_length=50, verbose_name='配置键', unique=True)
    value = models.TextField(verbose_name='配置值')
    type = models.IntegerField(choices=TYPE_LIST, default=0, verbose_name="数据值类型", help_text="数据值类型")

    def __str__(self):
        return self.key

    class Meta:
        db_table = table_prefix + 'authorization_config'
        verbose_name = '授权书配置'
        verbose_name_plural = verbose_name
        ordering = ['key']


class AuthorizationLetter(CoreModel):
    STATUS_CHOICES = (
        (0, '未生成'),
        (1, '已生成'),
        (2, '正在生成'),
        (3, '生成失败'),
        (4, '发送失败')
    )

    name = models.CharField(max_length=50, verbose_name='游戏名称')
    release_date = models.DateField(verbose_name='发行日期')
    authorization_filepath = models.CharField(max_length=255, verbose_name='授权书文件路径', null=True, blank=True)
    tips = models.TextField(verbose_name='备注', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='生成状态')

    class Meta:
        db_table = table_prefix + 'authorization_letter'
        verbose_name = '授权书文件'
        verbose_name_plural = verbose_name
        ordering = ['-release_date']

    def clean(self):
        self.name = self.name.strip().replace(' ', '')
        return super().clean()
