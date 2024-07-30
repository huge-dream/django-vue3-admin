# -*- coding: utf-8 -*-

"""
@author: 阿辉
@contact: QQ:2655399832
@Created on: 2022/9/21 16:30
@Remark:
"""
import json

from celery import current_app
from django.core.exceptions import ValidationError
from django_celery_beat.models import PeriodicTask, CrontabSchedule, cronexp, IntervalSchedule
from rest_framework import serializers
from rest_framework.decorators import action

from dvadmin.utils.json_response import SuccessResponse, ErrorResponse

CrontabSchedule.__str__ = lambda self: '{0} {1} {2} {3} {4} {5}'.format(
    cronexp(self.minute), cronexp(self.hour),
    cronexp(self.day_of_month), cronexp(self.month_of_year),
    cronexp(self.day_of_week), str(self.timezone)
)

from dvadmin.utils.serializers import CustomModelSerializer

from dvadmin.utils.viewset import CustomModelViewSet


def get_job_list():
    from application import settings
    task_list = []
    task_dict_list = []
    for app in settings.INSTALLED_APPS:
        try:
            exec(f"""
from {app} import tasks
for ele in [i for i in dir(tasks) if i.startswith('task__')]:
    task_dict = dict()
    task_dict['label'] = '{app}.tasks.' + ele
    task_dict['value'] = '{app}.tasks.' + ele
    task_list.append('{app}.tasks.' + ele)
    task_dict_list.append(task_dict)
                """)
        except ImportError:
            pass
    return {'task_list': task_list, 'task_dict_list': task_dict_list}


class CeleryCrontabScheduleSerializer(CustomModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ('timezone',)


class PeriodicTasksSerializer(CustomModelSerializer):
    crontab = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class PeriodicTasksCreateSerializer(CustomModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = '__all__'


class CeleryTaskModelViewSet(CustomModelViewSet):
    """
    CeleryTask 添加任务调度
    """

    queryset = PeriodicTask.objects.exclude(name="celery.backend_cleanup")
    serializer_class = PeriodicTasksSerializer
    create_serializer_class = PeriodicTasksCreateSerializer
    filter_fields = ['name', 'task', 'enabled']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    def job_list(self, request, *args, **kwargs):
        """获取所有任务"""
        result = get_job_list()
        task_list = result.get('task_dict_list')
        return SuccessResponse(msg='获取成功', data=task_list, total=len(task_list))

    def create(self, request, *args, **kwargs):
        body_data = request.data.copy()
        schedule_type = body_data.get('scheduleType')
        schedule = body_data.get('schedule')
        task = body_data.get('task')
        task_list = get_job_list().get('task_list')
        data_dict = {'task': task, 'name': body_data.get('name')}

        if task not in task_list:
            return ErrorResponse(msg="添加失败, 没有该任务", data=None)

        if schedule_type == 0:
            # 处理间隔调度
            interval_schedule = IntervalSchedule.objects.filter(id=schedule).first()
            if not interval_schedule:
                return ErrorResponse(msg="无效的间隔调度ID", data=None)
            data_dict['interval'] = interval_schedule
            data_dict.pop('crontab', None)
        else:
            # 处理定时调度
            cron_schedule = CrontabSchedule.objects.filter(id=schedule).first()
            if not cron_schedule:
                return ErrorResponse(msg="无效的定时调度ID", data=None)
            data_dict['crontab'] = cron_schedule
            data_dict.pop('interval', None)

        data_dict['enabled'] = False

        try:
            periodic_task = PeriodicTask.objects.create(**data_dict)
        except ValidationError as e:
            return ErrorResponse(msg=f"添加失败: {e.messages}", data=None)

        serializer = PeriodicTasksCreateSerializer(periodic_task)
        return SuccessResponse(msg="添加成功", data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        """删除定时任务"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return SuccessResponse(data=[], msg="删除成功")

    def run_task(self, request, *args, **kwargs):
        """立即运行任务"""
        instance = self.get_object()
        task_name = instance.task
        task_args = instance.args
        task_kwargs = instance.kwargs

        # 获取Celery任务
        celery_task = current_app.tasks.get(task_name)

        if not celery_task:
            return ErrorResponse(msg="任务不存在", data=None)

        # 解析任务参数
        try:
            args = json.loads(task_args) if task_args else []
            kwargs = json.loads(task_kwargs) if task_kwargs else {}
        except ValueError as e:
            return ErrorResponse(msg=f"参数解析错误: {str(e)}", data=None)

        # 手动触发任务
        celery_task.apply_async(args=args, kwargs=kwargs)

        return SuccessResponse(msg="任务已执行", data=None)

    @action(detail=True, methods=['post'])
    def update_status(self, request, *args, **kwargs):
        """开始/暂停任务"""
        instance = self.get_object()
        body_data = request.data
        instance.enabled = body_data.get('enabled')
        instance.save()
        return SuccessResponse(msg="修改成功", data=None)
