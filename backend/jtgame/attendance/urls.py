"""
Creation date: 2024/5/9
Creation Time: 下午2:42
DIR PATH: backend/dvadmin/attendance
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: cuckoo
"""

from rest_framework.routers import DefaultRouter

from .views import LeaveViewSet

router = DefaultRouter()
router.register(r'leave', LeaveViewSet)

urlpatterns = router.urls
