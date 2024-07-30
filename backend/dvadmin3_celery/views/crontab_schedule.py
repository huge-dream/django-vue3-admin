from django_celery_beat.models import CrontabSchedule
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class CrontabScheduleSerializer(ModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']


class CrontabScheduleModelViewSet(ModelViewSet):
    """
    CrontabSchedule crontab调度模型
    minute 分钟
    hour 小时
    day_of_week 每周的周几
    day_of_month 每月的某一天
    month_of_year 每年的某一个月

    """
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSerializer
    ordering = 'minute'  # 默认排序
