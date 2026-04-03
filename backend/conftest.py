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
    """创建管理员用户（每次调用自动 rollback，username 使用 Sequence 确保唯一）"""
    from tests.factories.system_factory import UserFactory

    user = UserFactory(admin=True)
    return user


@pytest.fixture
def normal_user(db):
    """创建普通用户"""
    from tests.factories.system_factory import UserFactory

    user = UserFactory()
    return user

