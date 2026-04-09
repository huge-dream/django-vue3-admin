from rest_framework import routers
from dvadmin.test_app.views.blog import BlogViewSet
from dvadmin.test_app.views.product import ProductViewSet

test_app_url = routers.SimpleRouter()
test_app_url.register(r'blog', BlogViewSet, basename='blog')
test_app_url.register(r'product', ProductViewSet, basename='product')

urlpatterns = test_app_url.urls
