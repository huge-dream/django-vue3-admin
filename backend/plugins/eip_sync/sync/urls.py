from django.urls import path

from sync.views import MiscMaterialSyncView

urlpatterns = [
    path("misc-material/", MiscMaterialSyncView.as_view(), name="sync-misc-material"),
]
