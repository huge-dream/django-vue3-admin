"""
Creation date: 2024/5/9
Creation Time: 下午2:42
DIR PATH: backend/dvadmin/attendance
Project Name: Manager_dvadmin
FILE NAME: models.py
Editor: cuckoo
"""
from django.db import models
from django.utils import timezone

from dvadmin.utils.models import CoreModel, table_prefix
from jtgame.utils import parse_iso_datetime


# Create your models here.


# 请假
class Leave(CoreModel):
    LEAVE_TYPE = ((0, '事假'), (1, '病假'), (2, '年假'), (3, '调休'), (4, '婚假'),
                  (5, '产假'), (6, '陪产假'), (7, '丧假'), (8, '其他'))
    LEAVE_STATIS = ((0, '待审批'), (1, '已通过'), (2, '已驳回'))

    # 请假类型
    leave_type = models.IntegerField(choices=LEAVE_TYPE, verbose_name='请假类型')
    # 请假开始时间
    start_time = models.DateTimeField(verbose_name='请假开始时间')
    # 请假结束时间
    end_time = models.DateTimeField(verbose_name='请假结束时间')
    # 请假原因
    reason = models.TextField(verbose_name='请假原因')
    # 请假时长
    duration = models.CharField(max_length=20, verbose_name='请假时长')
    # 参考时长
    reference_duration = models.CharField(max_length=20, verbose_name='参考时长')
    # 请假状态
    status = models.IntegerField(choices=LEAVE_STATIS, default=0, verbose_name='请假状态')

    class Meta:
        db_table = table_prefix + 'attendance_leave'
        verbose_name = '请假申请'
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            print(self.start_time, self.end_time)
            self.start_time = parse_iso_datetime(str(self.start_time))
            self.end_time = parse_iso_datetime(str(self.end_time))
            print(self.start_time, self.end_time)
            if self.start_time > self.end_time:
                raise models.ProtectedError('请假结束时间不能小于请假开始时间', self.end_time)
            if self.start_time and timezone.is_naive(self.start_time):
                self.start_time = timezone.make_aware(self.start_time)
            if self.end_time and timezone.is_naive(self.end_time):
                self.end_time = timezone.make_aware(self.end_time)

        super().save(*args, **kwargs)

