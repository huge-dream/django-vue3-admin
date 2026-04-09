from rest_framework import routers

from .views import ProcMaterialViewSet

router = routers.SimpleRouter()
router.register(r'proc_materials', ProcMaterialViewSet)

urlpatterns = []
urlpatterns += router.urls
