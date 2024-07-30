"""
Creation date: 2024/7/8
Creation Time: 下午2:58
DIR PATH: backend/jtgame/daily_report
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'cnsoleaccunt', ConsoleAccountViewSet)
router.register(r'quickaccunt', QuickAccountViewSet)
router.register(r'reportdata', DailyReportViewSet)
router.register(r'consoles', ConsolesViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('reportdata/get_report/', DailyReportViewSet.as_view({'get': 'get_report'})),
    # path('manual_update/', manual_update, name='manual_update'),
]
