from django_celery_beat.models import IntervalSchedule
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


class IntervalScheduleSerializer(ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class IntervalScheduleModelViewSet(ModelViewSet):
    """
    IntervalSchedule 调度间隔模型
    every 次数
    period 时间(天,小时,分钟,秒.毫秒)
    """
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer
    ordering = 'every'  # 默认排序
