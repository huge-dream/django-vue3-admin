"""
Creation date: 2024/7/19
Creation Time: 下午3:01
DIR PATH: backend/jtgame/income_statement
Project Name: Manager_dvadmin
FILE NAME: urls.py
Editor: 30386
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'incomedata', IncomeDataViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('incomedata/get_income/', IncomeDataViewSet.as_view({'get': 'get_income'})),
    # path('get_income/', get_income, name='get_income'),
]
