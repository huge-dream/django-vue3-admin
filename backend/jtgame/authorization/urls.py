"""
Creation date: 2024/5/12
Creation Time: 下午11:04
DIR PATH: backend/dvadmin/authorization_letter
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: cuckoo
"""
from rest_framework.routers import DefaultRouter

from .views import AuthorInfoViewSet, AuthorConfigViewSet, AuthorLetterViewSet


router = DefaultRouter()
router.register(r'authorization/info', AuthorInfoViewSet)
router.register(r'authorization/config', AuthorConfigViewSet)
router.register(r'authorization/letter', AuthorLetterViewSet)


urlpatterns = router.urls
