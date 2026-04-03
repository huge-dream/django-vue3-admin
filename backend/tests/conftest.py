import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """匿名 API 客户端"""
    return APIClient()


@pytest.fixture
def authenticate(api_client, admin_user):
    """已认证的 API 客户端（管理员）"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def admin_user(db):
    """创建管理员用户（每个测试独立事务，测试后自动 rollback）"""
    from dvadmin.system.models import Users

    user = Users.objects.create_user(
        username="test_admin",
        password="testpass123",
        is_superuser=True,
    )
    return user


@pytest.fixture
def normal_user(db):
    """创建普通用户"""
    from dvadmin.system.models import Users

    user = Users.objects.create_user(
        username="test_normal_user",
        password="testpass123",
        is_superuser=False,
    )
    return user
