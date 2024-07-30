from django_celery_beat.models import PeriodicTask
from rest_framework import serializers

from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from ..views.crontab_schedule import CrontabScheduleSerializer
from ..views.interval_schedule import IntervalScheduleSerializer


class PeriodicTaskSerializer(CustomModelSerializer):
    interval_list = serializers.SerializerMethodField(read_only=True)
    crontab_list = serializers.SerializerMethodField(read_only=True)

    def get_interval_list(self, obj):
        return IntervalScheduleSerializer(obj.interval).data if obj.interval else {}

    def get_crontab_list(self, obj):
        return CrontabScheduleSerializer(obj.crontab).data if obj.crontab else {}

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class PeriodicTaskModelViewSet(CustomModelViewSet):
    """
    PeriodicTask celery 任务数据模型
    name 名称
    task celery任务名称
    interval 频率
    crontab 任务编排
    args 形式参数
    kwargs 位置参数
    queue 队列名称
    exchange 交换
    routing_key 路由密钥
    expires 过期时间
    enabled 是否开启

    """
    queryset = PeriodicTask.objects.exclude(name="celery.backend_cleanup")
    serializer_class = PeriodicTaskSerializer
    ordering = 'date_changed'  # 默认排序

    def tasks_as_choices(self, request, *args, **kwargs):
        """
        获取所有 tasks 名称
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        lis = []

        def get_data(datas):
            for item in datas:
                if isinstance(item, (str, int)) and item:
                    lis.append(item)
                else:
                    get_data(item)

        from celery import current_app
        tasks = list(sorted(name for name in current_app.tasks
                            if not name.startswith('celery.')))
        get_data((('', ''),) + tuple(zip(tasks, tasks)))
        return SuccessResponse(list(set(lis)))

    def operate_celery(self, request, *args, **kwargs):
        task_name = request.data.get('celery_name', '')
        data = {
            'task': None
        }
        test = f"""
from {'.'.join(task_name.split('.')[:-1])} import {task_name.split('.')[-1]}
task = {task_name.split('.')[-1]}.delay()
        """
        exec(test, data)
        if not data["task"]:
            ErrorResponse(msg="执行失败")
        return SuccessResponse({'task_id': data.get('task', ).id})
