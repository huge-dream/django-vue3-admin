import hashlib
import mimetypes

import django_filters
from django.conf import settings
from django.db import connection
from rest_framework import serializers
from rest_framework.decorators import action

from application import dispatch
from dvadmin.system.models import FileList
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class FileSerializer(CustomModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        if self.request.query_params.get('prefix'):
            if settings.ENVIRONMENT in ['local']:
                prefix = 'http://127.0.0.1:8000'
            elif settings.ENVIRONMENT in ['test']:
                prefix = 'http://{host}/api'.format(host=self.request.get_host())
            else:
                prefix = 'https://{host}/api'.format(host=self.request.get_host())
            if instance.file_url:
                return instance.file_url if instance.file_url.startswith('http') else f"{prefix}/{instance.file_url}"
            return (f'{prefix}/media/{str(instance.url)}')
        return instance.file_url or (f'media/{str(instance.url)}')

    class Meta:
        model = FileList
        fields = "__all__"

    def create(self, validated_data):
        file_engine = dispatch.get_system_config_values("file_storage.file_engine") or 'local'
        file_backup = dispatch.get_system_config_values("file_storage.file_backup")
        file = self.initial_data.get('file')
        file_size = file.size
        validated_data['name'] = str(file)
        validated_data['size'] = file_size
        md5 = hashlib.md5()
        for chunk in file.chunks():
            md5.update(chunk)
        validated_data['md5sum'] = md5.hexdigest()
        validated_data['engine'] = file_engine
        validated_data['mime_type'] = file.content_type
        ft = {'image':0,'video':1,'audio':2}.get(file.content_type.split('/')[0], None)
        validated_data['file_type'] = 3 if ft is None else ft
        if file_backup:
            validated_data['url'] = file
        if file_engine == 'oss':
            from dvadmin.utils.aliyunoss import ali_oss_upload
            file_path = ali_oss_upload(file, file_name=validated_data['name'])
            if file_path:
                validated_data['file_url'] = file_path
            else:
                raise ValueError("上传失败")
        elif file_engine == 'cos':
            from dvadmin.utils.tencentcos import tencent_cos_upload
            file_path = tencent_cos_upload(file, file_name=validated_data['name'])
            if file_path:
                validated_data['file_url'] = file_path
            else:
                raise ValueError("上传失败")
        else:
            validated_data['url'] = file
        # 审计字段
        try:
            request_user = self.request.user
            validated_data['dept_belong_id'] = request_user.dept.id
            validated_data['creator'] = request_user.id
            validated_data['modifier'] = request_user.id
        except:
            pass
        return super().create(validated_data)


class FileAllSerializer(CustomModelSerializer):
    
    class Meta:
        model = FileList
        fields = ['id', 'name']


class FileFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains", help_text="文件名")
    mime_type = django_filters.CharFilter(field_name="mime_type", lookup_expr="icontains", help_text="文件类型")

    class Meta:
        model = FileList
        fields = ['name', 'mime_type', 'upload_method', 'file_type']


class FileViewSet(CustomModelViewSet):
    """
    文件管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = FileList.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter
    permission_classes = []

    @action(methods=['GET'], detail=False)
    def get_all(self, request):
        data1 = self.get_serializer(self.get_queryset(), many=True).data
        data2 = []
        if dispatch.is_tenants_mode():
            from django_tenants.utils import schema_context
            with schema_context('public'):
                data2 = self.get_serializer(FileList.objects.all(), many=True).data
        return DetailResponse(data=data2+data1)

    def list(self, request, *args, **kwargs):
        if self.request.query_params.get('system', 'False') == 'True' and dispatch.is_tenants_mode():
            from django_tenants.utils import schema_context
            with schema_context('public'):
                return super().list(request, *args, **kwargs)
        return super().list(request, *args, **kwargs)
