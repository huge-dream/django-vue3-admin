from datetime import datetime

from django.http import JsonResponse
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.game_manage.models import Games, Channel, Research, RevenueSplit, ResearchSplit
from jtgame.game_manage.utils import parse_request_data, handle_game, \
    handle_scheduling


# Create your views here.


class ChannelSerializer(CustomModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'
        read_only_fields = ["id"]


class ResearchSerializer(CustomModelSerializer):
    class Meta:
        model = Research
        fields = '__all__'
        read_only_fields = ["id"]


class GameSerializer(CustomModelSerializer):
    class Meta:
        model = Games
        fields = '__all__'
        read_only_fields = ["id"]


class RevenueSplitSerializer(CustomModelSerializer):
    class Meta:
        model = RevenueSplit
        fields = '__all__'
        read_only_fields = ["id"]


class ResearchSplitSerializer(CustomModelSerializer):
    class Meta:
        model = ResearchSplit
        fields = '__all__'
        read_only_fields = ["id"]


class GameViewSet(CustomModelViewSet):
    queryset = Games.objects.all()
    serializer_class = GameSerializer

    @action(detail=False, methods=['post'])
    def upload_dddd(self, request, *args, **kwargs):
        data = parse_request_data(request)
        sheets = data.get('sheets', [])
        messages = {'info': [], 'update': [], 'error': []}

        for sheet in sheets:
            if handle_game(sheet, messages):
                sheets.remove(sheet)

        for sheet in sheets:
            if handle_scheduling(sheet, messages):
                sheets.remove(sheet)

        logger.info(f'上传共{len(sheets)}个sheet页')
        if not sheets:
            logger.info('所有sheet页处理完成')
        else:
            logger.error(f'有{len(sheets)}个sheet页未处理: {sheets}')

        datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages_str = f'上传对接表 - {datetime_now}\n'
        messages_str += '信息:\n' + '\n'.join(messages['info']) + '\n'
        messages_str += '更新:\n' + '\n'.join(messages['update']) + '\n'
        messages_str += '错误:\n' + '\n'.join(messages['error']) + '\n'

        return JsonResponse({'message': messages_str, 'data': 'success'})


class ChannelViewSet(CustomModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class ResearchViewSet(CustomModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer


class RevenueSplitViewSet(CustomModelViewSet):
    queryset = RevenueSplit.objects.all()
    serializer_class = RevenueSplitSerializer


class ResearchSplitViewSet(CustomModelViewSet):
    queryset = ResearchSplit.objects.all()
    serializer_class = ResearchSplitSerializer
