"""
Creation date: 2024/5/9
Creation Time: 下午2:42
DIR PATH: backend/dvadmin/attendance
Project Name: Manager_dvadmin
FILE NAME: view.py
Editor: cuckoo
"""
import datetime

from django.http import JsonResponse
from pandas import DataFrame
from rest_framework.decorators import action

from dvadmin.system.models import Dictionary
from dvadmin.system.views.message_center import MessageCenterCreateSerializer
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.utils import parse_iso_datetime
from .models import Leave
from .utils import calculate_work_hours


class LeaveSerializer(CustomModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message_data = {
            'title': f'{time_now} 请假申请',
            'content': f'您有一条新的请假申请待审批\n'
                       f'请假人：{instance.creator.name}\n'
                       f'请假时间：{instance.start_time}至{instance.end_time}\n'
                       f'申请时间：{time_now}',
            'target_type': 1,
            'target_role': [6],
        }

        serializer = MessageCenterCreateSerializer(data=message_data)
        if serializer.is_valid():
            serializer.save()
        return instance

    # 如果未进行审批，则允许修改，否则不允许修改，返回错误信息
    def update(self, instance, validated_data):
        if str(instance.status) == '0':
            return super().update(instance, validated_data)
        else:
            raise Exception('已审批的请假单不允许修改')


class LeaveViewSet(CustomModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = []

    def get_object(self) -> Leave:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    # 如果审批通过，则不允许删除，否则允许删除
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.status)
        if str(instance.status) == '1':
            raise Exception('已审批的请假单不允许删除')
        else:
            return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['put'])
    def approve(self, request, pk=None):
        try:
            instance = self.get_object()
            if str(instance.status) == '1':
                return JsonResponse({'status': False, 'message': '已审批的请假单不允许再次审批'})
            elif str(instance.status) == '2' and not request.data.get('status'):
                return JsonResponse({'status': False, 'message': '已驳回的请假单无需再次驳回'})
            instance.status = request.data.get('status', instance.status)
            instance.save()

            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message_data = {
                'title': f'{time_now} 请假审批通过' if instance.status == 1 else f'{time_now} 请假审批未通过',
                'content': f'您的请假申请已审批，审批结果：{instance.get_status_display()}\n审批时间：{time_now}',
                'target_type': 0,
                'target_user': [instance.creator.id],
            }

            serializer = MessageCenterCreateSerializer(data=message_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({'status': False, 'message': '创建消息失败', 'data': serializer.errors})
            return JsonResponse({'status': True, 'message': '审批成功', 'data': LeaveSerializer(instance).data})
        except Exception as e:
            return JsonResponse({'status': False, 'message': '审批失败', 'data': str(e)})

    @action(detail=False, methods=['POST'])
    def calculate_leave_duration(self, request, pk=None):
        try:
            start_time = parse_iso_datetime(str(request.data.get('start_time')))
            end_time = parse_iso_datetime(str(request.data.get('end_time')))

            work_start_morning = str(Dictionary.objects.filter(label="work_start_morning").values_list(
                'value', flat=True).first())[:5]
            work_end_morning = str(Dictionary.objects.filter(label="work_end_morning").values_list(
                'value', flat=True).first())[:5]
            work_start_afternoon = str(Dictionary.objects.filter(label="work_start_afternoon").values_list(
                'value', flat=True).first())[:5]
            work_end_afternoon = str(Dictionary.objects.filter(label="work_end_afternoon").values_list(
                'value', flat=True).first())[:5]

            duration, status = calculate_duration(
                start_time, end_time, work_start_morning, work_end_morning, work_start_afternoon, work_end_afternoon)
            return JsonResponse({'status': True, 'message': status, 'data': duration})
        except Exception as e:
            return JsonResponse({'status': False, 'message': '计算失败', 'data': str(e)})


def calculate_duration(start_time, end_time, work_start_morning,
                       work_end_morning, work_start_afternoon, work_end_afternoon):
    try:
        leave_days, leave_hours = calculate_work_hours(
            start_time, end_time, work_start_morning, work_end_morning, work_start_afternoon, work_end_afternoon)

        result = f'{int(leave_days)}天{int(leave_hours)}小时', '计算成功'
    except Exception as e:
        result = '0天0小时', f'failed: {str(e)}'
    return result
