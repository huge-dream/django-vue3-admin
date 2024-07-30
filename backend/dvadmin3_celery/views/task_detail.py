# -*- coding: utf-8 -*-

"""
@author: 阿辉
@contact: QQ:2655399832
@Created on: 2022/9/21 16:30
@Remark:
"""

import django_filters
from django_celery_results.models import TaskResult

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class CeleryTaskDetailSerializer(CustomModelSerializer):
    """定时任务详情 序列化器"""

    class Meta:
        model = TaskResult
        fields = '__all__'


class CeleryTaskDetailFilterSet(django_filters.FilterSet):
    date_created = django_filters.BaseRangeFilter(field_name="date_created")

    class Meta:
        model = TaskResult
        fields = ['id', 'status', 'date_done', 'date_created', 'result', 'task_name']


class CeleryTaskDetailViewSet(CustomModelViewSet):
    """
    定时任务
    """
    queryset = TaskResult.objects.all()
    serializer_class = CeleryTaskDetailSerializer
    filter_class = CeleryTaskDetailFilterSet
