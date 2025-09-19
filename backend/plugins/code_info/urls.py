from django.urls import path
from rest_framework import routers

from plugins.code_info.views.scan_data import ScanDataViewSet
from plugins.code_info.views.scan_record import ScanRecordViewSet

route_url = routers.SimpleRouter()

route_url.register(r'scan_data', ScanDataViewSet,basename='scan_data')
route_url.register(r'scan_record', ScanRecordViewSet)

urlpatterns = [

]
urlpatterns += route_url.urls
