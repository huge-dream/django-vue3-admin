# -*- coding: utf-8 -*-
"""
系统单号：基于 `SystemNoRule` 取号（与 `system_no_rules` 表一致）。

组装规则：prefix + factory_code + sequence_date + str(本次流水).zfill(seq_length)
示例：杂采询价单 miscRFS，prefix=RFS、厂区空、按日 yymmdd → RFS2603240001；厂区 SZ → RFSSZ2603240001。
"""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.pisadmin.basicinfo.models import SystemNoRule

# 与前端「通用」厂区、SystemNoRule 维护一致
DEFAULT_SYSTEM_NO_COMPANY_CODE = "GENERAL"

RESET_CYCLE_STRFTIME = {
    "yy": "%y",
    "yyyy": "%Y",
    "yymm": "%y%m",
    "yyyymm": "%Y%m",
    "yymmdd": "%y%m%d",
    "yyyymmdd": "%Y%m%d",
}


def format_sequence_date(reset_cycle: str, when=None) -> str:
    fmt = RESET_CYCLE_STRFTIME.get(reset_cycle or "")
    if not fmt:
        return ""
    dt = when if when is not None else timezone.now()
    return dt.strftime(fmt)


def sequence_period_matches(rule: SystemNoRule, seq_date: str) -> bool:
    stored = (rule.sequence_date or "").strip()
    return bool(stored) and stored == seq_date


def _allocate_next_code_for_locked_rule(rule: SystemNoRule, now) -> str:
    """
    假定 rule 已由 select_for_update 锁定；计算下一单号并更新 rule 内存字段（未 save）。
    """
    seq_date = format_sequence_date(rule.reset_cycle, now)
    if not seq_date:
        raise serializers.ValidationError("未支持的流水码重置类别")

    if not sequence_period_matches(rule, seq_date):
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


def allocate_system_number(
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
    :param username: 写入 last_generate_user
    :return: 完整单号字符串
    """
    codes = allocate_system_numbers(company_code, rule_code, 1, username=username, now=now)
    return codes[0]


def allocate_system_numbers(
    company_code: str,
    rule_code: str,
    count: int,
    *,
    username: str | None = None,
    now=None,
) -> list[str]:
    """
    同一事务内连续取 `count` 个号（一次锁表），用于批量生成报价单等场景。
    """
    if count <= 0:
        return []

    if not (company_code or "").strip() or not (rule_code or "").strip():
        raise serializers.ValidationError("取号参数缺失：company_code 与 rule_code 必填")

    company_code = str(company_code).strip()
    rule_code = str(rule_code).strip()
    now = now or timezone.now()

    with transaction.atomic():
        rule = (
            SystemNoRule.objects.select_for_update()
            .filter(company_code=company_code, rule_code=rule_code)
            .first()
        )
        if not rule:
            raise serializers.ValidationError(
                f"未配置取号规则：rule_code={rule_code}，company_code={company_code}，请在「单据编号规则」中维护。"
            )

        codes = []
        for _ in range(count):
            codes.append(_allocate_next_code_for_locked_rule(rule, now))

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
