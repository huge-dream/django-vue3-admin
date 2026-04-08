# -*- coding: utf-8 -*-
from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone
from rest_framework import serializers
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


class SupplierUser(CoreModel):
    """供应商用户信息（独立主数据；通过 supplier_id 与供应商主档逻辑关联，非数据库外键）"""

    ROLE_CHOICES = (
        (1, "supplier_quote"),  # 供应商_报价
        (2, "supplier_misc_quote"),  # 供应商_杂采报价
        (3, "supplier_raw_quote"),  # 供应商_策采报价
    )

    supplier_id = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="供应商唯一ID",
        help_text="与供应商信息表 supplier_id 同值，可多条（多联系人）",
    )
    supplier_name = models.CharField(max_length=100, verbose_name="供应商全称", help_text="供应商全称")
    supplier_role = models.IntegerField(choices=ROLE_CHOICES, verbose_name="供应商角色", help_text="供应商角色")
    user_email = models.CharField(max_length=100, verbose_name="联络人邮箱", help_text="联络人邮箱")
    user_name = models.CharField(max_length=20, verbose_name="联络人", help_text="联络人")
    user_phone = models.CharField(max_length=100, verbose_name="联络人电话", help_text="联络人电话")
    status = models.IntegerField(default=1, verbose_name="有效否", help_text="有效否(1有效0无效)")

    class Meta:
        db_table = table_prefix + "supplier_users"
        verbose_name = "供应商用户信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime", "id")

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
    """单据编号规则；取号请用类方法 `allocate_system_number` / `allocate_system_numbers`。"""

    # 与前端「通用」厂区、规则维护一致
    DEFAULT_SYSTEM_NO_COMPANY_CODE = "GENERAL"

    RESET_CYCLE_CHOICES = (
        ("yy", "YY"),
        ("yyyy", "YYYY"),
        ("yymm", "YYMM"),
        ("yyyymm", "YYYYMM"),
        ("yymmdd", "YYMMDD"),
        ("yyyymmdd", "YYYYMMDD"),
    )

    RESET_CYCLE_STRFTIME = {
        "yy": "%y",
        "yyyy": "%Y",
        "yymm": "%y%m",
        "yyyymm": "%Y%m",
        "yymmdd": "%y%m%d",
        "yyyymmdd": "%Y%m%d",
    }

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

    @classmethod
    def format_sequence_date(cls, reset_cycle: str, when=None) -> str:
        fmt = cls.RESET_CYCLE_STRFTIME.get(reset_cycle or "")
        if not fmt:
            return ""
        dt = when if when is not None else timezone.now()
        return dt.strftime(fmt)

    @classmethod
    def sequence_period_matches(cls, rule: SystemNoRule, seq_date: str) -> bool:
        stored = (rule.sequence_date or "").strip()
        return bool(stored) and stored == seq_date

    @classmethod
    def _allocate_next_code_for_locked_rule(cls, rule: SystemNoRule, now) -> str:
        """假定 rule 已由 select_for_update 锁定；计算下一单号并更新 rule 内存字段（未 save）。"""
        seq_date = cls.format_sequence_date(rule.reset_cycle, now)
        if not seq_date:
            raise serializers.ValidationError("未支持的流水码重置类别")

        if not cls.sequence_period_matches(rule, seq_date):
            rule.prev_sequence = 0
            new_seq = 1
        else:
            nxt = int(rule.current_sequence or 0)
            new_seq = nxt if nxt > 0 else 1
            if (
                rule.last_generate_time is not None
                and int(rule.prev_sequence or 0) == 0
                and new_seq == 1
            ):
                new_seq = 2

        slen = max(int(rule.seq_length or 4), 1)
        max_seq = 10**slen - 1
        if new_seq > max_seq:
            raise serializers.ValidationError(
                f"流水码已达上限（长度 {slen} 位，最大 {max_seq}），请调整规则或联系管理员"
            )

        seq_str = str(new_seq).zfill(slen)
        code = "".join(
            [
                rule.prefix or "",
                rule.factory_code or "",
                seq_date,
                seq_str,
            ]
        )

        rule.sequence_date = seq_date
        rule.prev_sequence = new_seq
        rule.current_sequence = new_seq + 1
        return code

    @classmethod
    def allocate_system_number(
        cls,
        company_code: str,
        rule_code: str,
        *,
        username: str | None = None,
        now=None,
    ) -> str:
        """
        在事务内对匹配 (company_code, rule_code) 的规则行加锁，生成单号并更新流水字段。
        :param company_code: 交易厂区（与规则表一致，常用 DEFAULT_SYSTEM_NO_COMPANY_CODE）
        :param rule_code: 如 miscRFS / miscQTS
        """
        codes = cls.allocate_system_numbers(company_code, rule_code, 1, username=username, now=now)
        return codes[0]

    @classmethod
    def allocate_system_numbers(
        cls,
        company_code: str,
        rule_code: str,
        count: int,
        *,
        username: str | None = None,
        now=None,
    ) -> list[str]:
        """同一事务内连续取 count 个号（一次锁表），用于批量生成报价单等场景。"""
        if count <= 0:
            return []

        if not (company_code or "").strip() or not (rule_code or "").strip():
            raise serializers.ValidationError("取号参数缺失：company_code 与 rule_code 必填")

        company_code = str(company_code).strip()
        rule_code = str(rule_code).strip()
        now = now or timezone.now()

        with transaction.atomic():
            rule = (
                cls.objects.select_for_update()
                .filter(company_code=company_code, rule_code=rule_code)
                .first()
            )
            if not rule:
                raise serializers.ValidationError(
                    f"未配置取号规则：rule_code={rule_code}，company_code={company_code}，请在「单据编号规则」中维护。"
                )

            codes = []
            for _ in range(count):
                codes.append(cls._allocate_next_code_for_locked_rule(rule, now))

            rule.last_generate_user = username
            rule.last_generate_time = now
            rule.save(
                update_fields=[
                    "sequence_date",
                    "prev_sequence",
                    "current_sequence",
                    "last_generate_user",
                    "last_generate_time",
                    "update_datetime",
                ]
            )

        return codes

    class Meta:
        db_table = table_prefix + "system_no_rules"
        verbose_name = "系统单号规则"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
        unique_together = ("company_code", "rule_code")

    def __str__(self):
        return f"{self.rule_code}@{self.company_code}"


class EmailNotice(CoreModel):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("sending", "sending"),
        ("success", "success"),
        ("failed", "failed"),
    )

    subject = models.CharField(max_length=256, verbose_name="邮件主题")
    body = models.TextField(null=True, blank=True, verbose_name="邮件正文")
    to_emails = models.JSONField(default=list, verbose_name="收件人")
    cc_emails = models.JSONField(default=list, verbose_name="抄送")
    bcc_emails = models.JSONField(default=list, verbose_name="密送")
    attachments = models.JSONField(default=list, verbose_name="附件")
    biz_type = models.CharField(max_length=64, null=True, blank=True, verbose_name="业务类型")
    biz_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="业务标识")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending", db_index=True, verbose_name="发送状态")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="发送时间")
    message_id = models.CharField(max_length=128, null=True, blank=True, verbose_name="消息ID")
    last_error = models.TextField(null=True, blank=True, verbose_name="失败原因")
    payload = models.JSONField(default=dict, verbose_name="发送参数")
    response = models.JSONField(default=dict, verbose_name="服务端响应")
    retry_count = models.IntegerField(default=0, verbose_name="重试次数")

    class Meta:
        db_table = table_prefix + "proc_email_notice"
        verbose_name = "邮件通知"
        verbose_name_plural = verbose_name
        ordering = ("-update_datetime", "-id")

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.subject
