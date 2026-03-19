# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework import routers

from sscadmin.basicinfo.views.unit import UnitViewSet
from sscadmin.basicinfo.views.currency import CurrencyViewSet
from sscadmin.basicinfo.views.misc_material import MiscMaterialViewSet
from sscadmin.basicinfo.views.misc_station import MiscStationViewSet
from sscadmin.basicinfo.views.supplier import SupplierViewSet
from sscadmin.basicinfo.views.misc_part import MiscPartViewSet
from sscadmin.basicinfo.views.company import CompanyViewSet

basicinfo_url = routers.SimpleRouter()
basicinfo_url.register(r'units', UnitViewSet)
basicinfo_url.register(r'currencies', CurrencyViewSet)
basicinfo_url.register(r'misc_materials', MiscMaterialViewSet)
basicinfo_url.register(r'misc_stations', MiscStationViewSet)
basicinfo_url.register(r'suppliers', SupplierViewSet)
basicinfo_url.register(r'misc_parts', MiscPartViewSet)
basicinfo_url.register(r'companies', CompanyViewSet)

urlpatterns = [] + basicinfo_url.urls
