# -*- coding: utf-8 -*-
from rest_framework import routers

from apps.pisadmin.basicinfo.views.unit import UnitViewSet
from apps.pisadmin.basicinfo.views.currency import CurrencyViewSet
from apps.pisadmin.basicinfo.views.supplier import SupplierViewSet
from apps.pisadmin.basicinfo.views.company import CompanyViewSet
from apps.pisadmin.basicinfo.views.system_no_rule import SystemNoRuleViewSet

basicinfo_url = routers.SimpleRouter()
basicinfo_url.register(r'units', UnitViewSet)
basicinfo_url.register(r'currencies', CurrencyViewSet)
basicinfo_url.register(r'suppliers', SupplierViewSet)
basicinfo_url.register(r'companies', CompanyViewSet)
basicinfo_url.register(r'system_no_rules', SystemNoRuleViewSet)

urlpatterns = [] + basicinfo_url.urls
