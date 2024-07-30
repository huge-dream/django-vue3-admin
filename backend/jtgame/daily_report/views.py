import json
from datetime import datetime
from time import sleep

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.daily_report.models import ConsoleAccount, QuickAccount, ReportData, Consoles
from jtgame.daily_report.utils import RenewConsole, ConsoleData


# Create your views here.


class ConsoleAccountSerializer(CustomModelSerializer):
    class Meta:
        model = ConsoleAccount
        fields = '__all__'


class ConsoleAccountViewSet(CustomModelViewSet):
    queryset = ConsoleAccount.objects.all()
    serializer_class = ConsoleAccountSerializer


class QuickAccountSerializer(CustomModelSerializer):
    class Meta:
        model = QuickAccount
        fields = '__all__'


class QuickAccountViewSet(CustomModelViewSet):
    queryset = QuickAccount.objects.all()
    serializer_class = QuickAccountSerializer


class DailyReportSerializer(CustomModelSerializer):
    class Meta:
        model = ReportData
        fields = '__all__'


class DailyReportViewSet(CustomModelViewSet):
    queryset = ReportData.objects.all()
    serializer_class = DailyReportSerializer

    @action(detail=False, methods=['get', 'post'])
    def get_report(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                post_data = json.loads(request.body)
                if not post_data or 'date' not in post_data:
                    return JsonResponse({"error": "Invalid data"}, status=400)
                result = self.queryset.filter(date=post_data.get('date')).first()
                return JsonResponse(result.data if result else {}, status=200)
            except Exception as e:
                return JsonResponse({"error": f"Server error: {e}"}, status=500)
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            result = self.queryset.filter(date=date).first()
            return JsonResponse(result.data if result else {}, status=200)


class ConsolesSerializer(CustomModelSerializer):
    class Meta:
        model = Consoles
        fields = '__all__'


class ConsolesViewSet(CustomModelViewSet):
    queryset = Consoles.objects.all()
    serializer_class = ConsolesSerializer

    def get_object(self) -> Consoles:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    @action(detail=True, methods=['put'])
    def renew(self, request, pk=None):
        try:
            instance = self.get_object()
            if instance.renewal_status:
                return JsonResponse({'status': False, 'message': '续费失败', 'data': '服务器正在续费中，请稍后再试'})

            instance_id = instance.instance_id
            instance_account = instance.account

            # 通过instance_id和account找到对应的服务器账号
            console_account = ConsoleAccount.objects.filter(account=instance_account).first()
            if not console_account:
                raise Exception('未找到对应的服务器账号')
            instance.renewal_status = True
            instance.save()
            response = RenewConsole(console_account, instance_id)

            # 更新日报
            logger.info('准备更新服务器信息, 等待5秒...')
            sleep(3)
            # DailyReport().make_daily_report(update=True)
            print(ConsoleData().make_daily_report(update=True))
            logger.info('更新服务器信息完成')
            instance.renewal_status = False
            instance.save()
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'status': False, 'message': '续费失败', 'data': str(e)})


# @csrf_exempt
# def get_report(request):
#     if request.method == 'POST':
#         try:
#             post_data = json.loads(request.body)
#             if not post_data or 'date' not in post_data:
#                 return JsonResponse({"error": "Invalid data"}, status=400)
#             result = ReportData.objects.filter(date=post_data.get('date')).first()
#             return JsonResponse(result.data if result else {}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": f"Server error: {e}"}, status=500)
#     else:
#         date = datetime.now().strftime('%Y-%m-%d')
#         result = ReportData.objects.filter(date=date).first()
#         return JsonResponse(result.data if result else {}, status=200)


# @csrf_exempt
# def manual_update(request):
#     print('manual_update')
#     if request.method == 'GET':
#         try:
#             task__make_daily_report.delay()
#             return JsonResponse({"message": "更新任务已经开始"})
#         except Exception as e:
#             return JsonResponse({"error": f"服务器错误: {e}"})
#     else:
#         return JsonResponse({"error": "请求方法不允许"})
