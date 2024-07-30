from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import action

from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet
from jtgame.tencent_docx.models import TencentDocxUser


# Create your views here.


class TencentDocxUserSerializer(CustomModelSerializer):
    class Meta:
        model = TencentDocxUser
        fields = '__all__'
        read_only_fields = ["id"]


class TencentDocxUserViewSet(CustomModelViewSet):
    queryset = TencentDocxUser.objects.all()
    serializer_class = TencentDocxUserSerializer

    @action(detail=False, methods=['get'])
    def tencentdocx_authorize_callback(self, request, *args, **kwargs):
        data = request.query_params
        print(data)

        return JsonResponse(data, status=200)
