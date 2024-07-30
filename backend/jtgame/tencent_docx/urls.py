"""
Creation date: 2024/7/24
Creation Time: 下午2:41
DIR PATH: backend/jtgame/tencent_docx
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'tencentdocx_user', TencentDocxUserViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('tencentdocx_user/tencentdocx_authorize_callback/', TencentDocxUserViewSet.as_view({'get': 'tencentdocx_authorize_callback'})),
]
