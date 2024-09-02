from django.urls import path
from rest_framework import routers

from dvadmin.kefu.views.sip_user import SipUserViewSet
from dvadmin.kefu.views.group import GroupViewSet
from dvadmin.kefu.views.dis_number import DisNumberViewSet
from dvadmin.kefu.views.sip_trunk import SipTrunkViewSet
from dvadmin.kefu.views.record import RecordViewSet
from dvadmin.kefu.views.report import ReportViewSet
from dvadmin.kefu.views.customer import CustomerViewSet
from dvadmin.kefu.views.asr import AsrViewSet
from dvadmin.system.views.login_log import LoginLogViewSet


system_url = routers.SimpleRouter()
system_url.register(r'sipuser', SipUserViewSet)
system_url.register(r'disnumber', DisNumberViewSet)
system_url.register(r'group', GroupViewSet)
system_url.register(r'trunk', SipTrunkViewSet)
system_url.register(r'record', RecordViewSet)
system_url.register(r'report', ReportViewSet)
system_url.register(r'customer', CustomerViewSet)
system_url.register(r'asr', AsrViewSet)

urlpatterns = [
    path('user/export/', SipUserViewSet.as_view({'post': 'export_data', })),
    path('user/import/', SipUserViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('login_log/', LoginLogViewSet.as_view({'get': 'list'})),
    path('login_log/<int:pk>/', LoginLogViewSet.as_view({'get': 'retrieve'})),
]
urlpatterns += system_url.urls
