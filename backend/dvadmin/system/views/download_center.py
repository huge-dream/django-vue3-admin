from rest_framework import serializers
from django.conf import settings
from django_filters.rest_framework import FilterSet, CharFilter

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.system.models import DownloadCenter


class DownloadCenterSerializer(CustomModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        if self.request.query_params.get('prefix'):
            if settings.ENVIRONMENT in ['local']:
                prefix = 'http://127.0.0.1:8000'
            elif settings.ENVIRONMENT in ['test']:
                prefix = 'http://{host}/api'.format(host=self.request.get_host())
            else:
                prefix = 'https://{host}/api'.format(host=self.request.get_host())
            return (f'{prefix}/media/{str(instance.url)}')
        return f'media/{str(instance.url)}'

    class Meta:
        model = DownloadCenter
        fields = "__all__"
        read_only_fields = ["id"]


class DownloadCenterFilterSet(FilterSet):
    task_name = CharFilter(field_name='task_name', lookup_expr='icontains')
    file_name = CharFilter(field_name='file_name', lookup_expr='icontains')

    class Meta:
        model = DownloadCenter
        fields = ['task_status', 'task_name', 'file_name']


class DownloadCenterViewSet(CustomModelViewSet):
    queryset = DownloadCenter.objects.all()
    serializer_class = DownloadCenterSerializer
    filter_class = DownloadCenterFilterSet
    permission_classes = []
    extra_filter_class = []

    def get_queryset(self):
        # 判断是否是 Swagger 文档生成阶段，防止报错
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.model.objects.none()

        # 正常请求下的逻辑
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(creator=self.request.user)
