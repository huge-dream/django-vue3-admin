# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.pisadmin.basicinfo.models import SystemNoRule
from apps.pisadmin.basicinfo.system_no_allocate import allocate_system_number, format_sequence_date
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet

# 由服务端维护，禁止前端随表单覆盖（避免取号后被编辑保存冲掉）
_SEQUENCE_FIELDS_FROM_CLIENT_FORBIDDEN = (
    "sequence_date",
    "prev_sequence",
    "current_sequence",
    "last_generate_user",
    "last_generate_time",
)


class SystemNoRuleSerializer(CustomModelSerializer):
    """系统单号规则-序列化器"""

    class Meta:
        model = SystemNoRule
        fields = "__all__"
        read_only_fields = ["id"]


class SystemNoRuleCreateUpdateSerializer(CustomModelSerializer):
    """系统单号规则 创建/更新"""

    company_code = serializers.CharField(max_length=20)
    rule_code = serializers.CharField(max_length=50)
    reset_cycle = serializers.ChoiceField(choices=SystemNoRule.RESET_CYCLE_CHOICES)
    seq_length = serializers.IntegerField(min_value=1, max_value=20)

    class Meta:
        model = SystemNoRule
        fields = "__all__"

    def validate(self, attrs):
        company_code = attrs.get("company_code")
        if company_code is None and getattr(self.instance, "company_code", None) is not None:
            company_code = self.instance.company_code
        rule_code = attrs.get("rule_code")
        if rule_code is None and getattr(self.instance, "rule_code", None) is not None:
            rule_code = self.instance.rule_code
        instance_id = getattr(self.instance, "id", None)
        if company_code is not None and rule_code is not None:
            exists = SystemNoRule.objects.filter(company_code=company_code, rule_code=rule_code)
            if instance_id:
                exists = exists.exclude(id=instance_id)
            if exists.exists():
                raise serializers.ValidationError("同一厂区下的生成单据标识号不可重复")
        return attrs

    def create(self, validated_data):
        for k in _SEQUENCE_FIELDS_FROM_CLIENT_FORBIDDEN:
            validated_data.pop(k, None)
        rc = validated_data["reset_cycle"]
        validated_data["sequence_date"] = format_sequence_date(rc)
        validated_data["prev_sequence"] = 0
        validated_data["current_sequence"] = 1
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for k in _SEQUENCE_FIELDS_FROM_CLIENT_FORBIDDEN:
            validated_data.pop(k, None)
        new_cycle = validated_data.get("reset_cycle")
        if new_cycle is not None and new_cycle != instance.reset_cycle:
            validated_data["sequence_date"] = format_sequence_date(new_cycle)
            validated_data["prev_sequence"] = 0
            validated_data["current_sequence"] = 1
        return super().update(instance, validated_data)


class SystemNoRuleViewSet(CustomModelViewSet):
    """系统单号规则管理接口"""

    queryset = SystemNoRule.objects.all()
    serializer_class = SystemNoRuleSerializer
    create_serializer_class = SystemNoRuleCreateUpdateSerializer
    update_serializer_class = SystemNoRuleCreateUpdateSerializer
    search_fields = ["company_code", "rule_code", "factory_code", "prefix"]
    ordering = ["-create_datetime"]

    @action(methods=["post"], detail=False, url_path="generate_code")
    def generate_code(self, request):
        """生成单据号，含并发锁保证流水唯一（与 `allocate_system_number` 同源逻辑）"""

        company_code = request.data.get("company_code")
        rule_code = request.data.get("rule_code")
        if not company_code or not rule_code:
            return Response({"success": False, "message": "参数缺失：company_code 与 rule_code 必填", "code": None}, status=400)

        username = getattr(request.user, "username", None) or getattr(request.user, "name", None)
        try:
            code = allocate_system_number(
                company_code,
                rule_code,
                username=username,
                now=timezone.now(),
            )
        except serializers.ValidationError as exc:
            detail = getattr(exc, "detail", None)
            if isinstance(detail, list) and detail:
                msg = "; ".join(str(x) for x in detail)
            elif isinstance(detail, dict):
                msg = "; ".join(f"{k}: {v}" for k, v in detail.items())
            else:
                msg = str(detail) if detail is not None else str(exc)
            return Response({"success": False, "message": msg, "code": None}, status=400)
        except Exception as exc:  # pragma: no cover - defensive
            return Response({"success": False, "message": str(exc), "code": None}, status=500)

        return Response({"success": True, "message": "", "code": code})
