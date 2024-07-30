# Create your views here.
import os

from django.http import JsonResponse, FileResponse
from rest_framework.decorators import action

from dvadmin.utils.backends import logger
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from .models import AuthorizationInfo, AuthorizationConfig, AuthorizationLetter
from .tasks import generate_authorization_letter


class AuthorInfoSerializer(CustomModelSerializer):
    class Meta:
        model = AuthorizationInfo
        fields = '__all__'


class AuthorInfoViewSet(CustomModelViewSet):
    queryset = AuthorizationInfo.objects.all()
    serializer_class = AuthorInfoSerializer
    permission_classes = []


class AuthorConfigSerializer(CustomModelSerializer):
    class Meta:
        model = AuthorizationConfig
        fields = '__all__'


class AuthorConfigViewSet(CustomModelViewSet):
    queryset = AuthorizationConfig.objects.all()
    serializer_class = AuthorConfigSerializer
    permission_classes = []


class AuthorLetterSerializer(CustomModelSerializer):
    class Meta:
        model = AuthorizationLetter
        fields = '__all__'

    def update(self, instance, validated_data):
        if str(instance.status) != '1':
            return super().update(instance, validated_data)
        elif str(instance.status) == '2':
            raise Exception('文件正在生成中，暂不允许修改')
        else:
            raise Exception('已生成的授权书不允许修改')


class AuthorLetterViewSet(CustomModelViewSet):
    queryset = AuthorizationLetter.objects.all()
    serializer_class = AuthorLetterSerializer
    permission_classes = []

    def get_object(self) -> AuthorizationLetter:
        filter_kwargs = {'id': self.kwargs['pk']}
        obj = self.queryset.filter(**filter_kwargs).first()
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if str(instance.status) == '0':
            return super().destroy(request, *args, **kwargs)
        else:
            raise Exception('已生成的授权书不允许删除')

    @action(detail=True, methods=['get'])
    def generate(self, request, pk=None):
        obj = self.get_object()
        if obj.status == 2:
            return JsonResponse({'status': False, 'message': '任务已提交，请勿重复提交'})
        obj.status = 2
        obj.authorization_filepath = None
        obj.tips = '生成中'
        obj.save()
        generate_authorization_letter.delay(obj.id)
        return JsonResponse({'status': True, 'message': '已提交任务，处理中，请稍候'})

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            obj = self.get_object()
            if not obj.authorization_filepath:
                return JsonResponse({'status': False, 'message': '授权书未生成，请先生成'})

            file_path = obj.authorization_filepath
            if not os.path.exists(file_path):
                return JsonResponse({'status': False, 'message': '文件未找到'})

            response = FileResponse(open(file_path, 'rb'), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{obj.name}授权书.zip"'
            return response
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e)})

    @action(detail=False, methods=['get'])
    def clear(self, request, pk=None):
        if AuthorizationLetter.objects.filter(status=2).exists():
            return JsonResponse({'status': False, 'message': '存在正在生成的授权书，请稍后再试'})
        try:
            objs = AuthorizationLetter.objects.filter(authorization_filepath__isnull=False).values_list(
                'authorization_filepath', flat=True)
            save_path = set(objs)

            output_dir_config = AuthorizationConfig.objects.filter(key='output_dir').first()
            if not output_dir_config:
                return JsonResponse({'status': False, 'message': '未找到授权书输出路径配置'}, status=400)
            output_dir = output_dir_config.value

            file_count = 0
            file_clear_count = 0

            def safe_remove(_file_path):
                try:
                    if os.path.exists(_file_path):
                        os.remove(_file_path)
                        return True
                    return False
                except Exception as _:
                    logger.error(f'删除文件 {_file_path} 时发生错误: {str(_)}')
                    return False

            def safe_rmdir(_dir_path):
                try:
                    if os.path.exists(_dir_path):
                        os.rmdir(_dir_path)
                        return True
                    return False
                except Exception as _:
                    logger.error(f'删除目录 {_dir_path} 时发生错误: {str(_)}')
                    return False

            # 清理多余文件
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.abspath(os.path.join(root, file))
                    if file_path not in save_path:
                        if safe_remove(file_path):
                            file_clear_count += 1
                    file_count += 1

            dir_count = 0
            dir_clear_count = 0
            # 清理空目录
            for root, dirs, files in os.walk(output_dir, topdown=False):
                for _dir in dirs:
                    dir_path = os.path.abspath(os.path.join(root, _dir))
                    if not os.listdir(dir_path):
                        if safe_rmdir(dir_path):
                            dir_clear_count += 1
                    dir_count += 1
                if not os.listdir(root):
                    if safe_rmdir(root):
                        dir_clear_count += 1

            logger.info(
                f'清理了{file_clear_count}个文件，共{file_count}个文件, '
                f'清理了{dir_clear_count}个目录，共{dir_count}个目录'
            )
            return JsonResponse(
                {
                    'status': True,
                    'message': f'共清理{file_clear_count}个文件，共{file_count}个文件, '
                               f'共清理{dir_clear_count}个目录，共{dir_count}个目录'
                }
            )
        except Exception as e:
            logger.error(f'清理文件时发生错误: {str(e)}')
            return JsonResponse({'status': False, 'message': f'清理文件时发生错误: {str(e)}'})
