# -*- coding: utf-8 -*-
from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class Unit(CoreModel):
    """计量单位"""
    unitname = models.CharField(max_length=50, verbose_name="计量单位名称", help_text="计量单位名称")
    unitcode = models.CharField(max_length=20, verbose_name="计量单位代码", help_text="计量单位代码", null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")

    class Meta:
        db_table = table_prefix + "units"
        verbose_name = "计量单位"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.unitname


class Currency(CoreModel):
    """货币"""
    currencyname = models.CharField(max_length=50, verbose_name="货币名称", help_text="货币名称")
    currencycode = models.CharField(max_length=20, verbose_name="货币代码", help_text="货币代码", null=True, blank=True)
    currencysymbol = models.CharField(max_length=10, verbose_name="货币符号", help_text="货币符号")
    factory = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)", null=True, blank=True)
    tax = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="税率", help_text="税率")
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")

    class Meta:
        db_table = table_prefix + "currencies"
        verbose_name = "币别税率"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.currencyname


class Supplier(CoreModel):
    """供应商信息"""
    company_code = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)", null=True, blank=True)
    supplier_id = models.CharField(max_length=20, unique=True, verbose_name="供应商唯一ID", help_text="供应商唯一ID")
    supplier_name = models.CharField(max_length=100, verbose_name="供应商全称", help_text="供应商全称")
    supplier_short_name = models.CharField(max_length=50, verbose_name="供应商简称", help_text="供应商简称")
    vendor_type = models.CharField(max_length=20, verbose_name="厂商性质", help_text="厂商性质", null=True, blank=True)
    payment_terms = models.CharField(max_length=20, verbose_name="付款条件", help_text="付款条件", null=True, blank=True)
    transaction_currency = models.CharField(max_length=20, verbose_name="交易货币", help_text="交易货币", null=True, blank=True)
    incoterms = models.CharField(max_length=20, verbose_name="国际条款", help_text="国际条款", null=True, blank=True)
    supplier_level = models.CharField(max_length=10, verbose_name="供应商等级", help_text="供应商等级", null=True, blank=True)
    contact_person = models.CharField(max_length=20, verbose_name="联络人", help_text="联络人")
    contact_phone = models.CharField(max_length=20, verbose_name="联络人电话", help_text="联络人电话")
    contact_email = models.CharField(max_length=50, verbose_name="联络人邮箱", help_text="联络人邮箱(账号)")
    country = models.CharField(max_length=20, verbose_name="国家", help_text="国家(如TW,CN)")
    province = models.CharField(max_length=20, verbose_name="省州", help_text="省州")
    city = models.CharField(max_length=20, verbose_name="城市", help_text="城市", null=True, blank=True)
    address = models.CharField(max_length=500, verbose_name="详细地址", help_text="详细地址", null=True, blank=True)
    postal_code = models.CharField(max_length=20, verbose_name="邮递区号", help_text="邮递区号", null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")

    class Meta:
        db_table = table_prefix + "suppliers"
        verbose_name = "供应商信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.supplier_name


class Company(CoreModel):
    """公司信息"""
    company_code = models.CharField(max_length=20, verbose_name="公司代码", help_text="公司代码")
    company_name = models.CharField(max_length=100, verbose_name="公司全称", help_text="公司全称", null=True, blank=True)
    company_short_name = models.CharField(max_length=50, verbose_name="公司简称", help_text="公司简称", null=True, blank=True)
    company_address = models.CharField(max_length=500, verbose_name="公司地址", help_text="公司地址", null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")
    createuser = models.CharField(max_length=20, verbose_name="创建人员", help_text="创建人员", null=True, blank=True)
    updateuser = models.CharField(max_length=20, verbose_name="更新人员", help_text="更新人员", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "company"
        verbose_name = "公司信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.company_name or self.company_code


class SystemNoRule(CoreModel):
    """单据编号规则；业务取号请用 `system_no_allocate.allocate_system_number`。"""

    RESET_CYCLE_CHOICES = (
        ("yy", "YY"),
        ("yyyy", "YYYY"),
        ("yymm", "YYMM"),
        ("yyyymm", "YYYYMM"),
        ("yymmdd", "YYMMDD"),
        ("yyyymmdd", "YYYYMMDD"),
    )

    RULE_CODE_CHOICES = (
        ("miscQTS", "杂采报价单"),
        ("miscRFS", "杂采询价单"),
    )

    company_code = models.CharField(max_length=20, verbose_name="交易厂区", help_text="交易厂区(公司)")
    rule_code = models.CharField(max_length=50, choices=RULE_CODE_CHOICES, verbose_name="生成单据标识号", help_text="标识一组单号规则")
    reset_cycle = models.CharField(max_length=16, choices=RESET_CYCLE_CHOICES, verbose_name="流水码重置类别", help_text="重置粒度")
    prefix = models.CharField(max_length=20, verbose_name="单据头", help_text="单据开头固定字符", null=True, blank=True)
    factory_code = models.CharField(max_length=20, verbose_name="厂区区分码", help_text="厂区区分码", null=True, blank=True)
    seq_length = models.IntegerField(verbose_name="流水码长度", help_text="流水码长度", default=4)
    createuser = models.CharField(max_length=50, verbose_name="单据创建人", help_text="单据创建人", null=True, blank=True)
    updateuser = models.CharField(max_length=50, verbose_name="单据修改人", help_text="单据修改人", null=True, blank=True)
    sequence_date = models.CharField(
        max_length=12,
        verbose_name="流水日期",
        help_text="与 reset_cycle 对应的日期段（如 yymmdd→260324）；新建/改重置类别时由服务端写入",
        null=True,
        blank=True,
    )
    prev_sequence = models.IntegerField(
        verbose_name="上一流水码",
        help_text="上一笔已成功发放的流水号；未发过为 0，与「下一流水码」相差 1",
        default=0,
    )
    current_sequence = models.IntegerField(
        verbose_name="下一流水码",
        help_text="下一笔待发流水号；新建/重置周期后为 1，每次取号成功后 +1",
        default=1,
    )
    last_generate_user = models.CharField(max_length=50, verbose_name="单据最后产生人", help_text="最后产生人", null=True, blank=True)
    last_generate_time = models.DateTimeField(verbose_name="单据最后产生时间", help_text="最后产生时间", null=True, blank=True)

    class Meta:
        db_table = table_prefix + "system_no_rules"
        verbose_name = "系统单号规则"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        unique_together = ("company_code", "rule_code")

    def __str__(self):
        return f"{self.rule_code}@{self.company_code}"
