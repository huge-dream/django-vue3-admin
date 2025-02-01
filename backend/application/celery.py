import functools
import os

from celery.signals import task_postrun

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

from django.conf import settings
from celery import platforms

# 租户模式
if "django_tenants" in settings.INSTALLED_APPS:
    from tenant_schemas_celery.app import CeleryApp as TenantAwareCeleryApp

    app = TenantAwareCeleryApp()
else:
    from celery import Celery

    app = Celery(f"application")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
platforms.C_FORCE_ROOT = True


def retry_base_task_error():
    """
    celery 失败重试装饰器
    :return:
    """

    def wraps(func):
        @app.task(bind=True, retry_delay=180, max_retries=3)
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                raise self.retry(exc=exc)

        return wrapper

    return wraps


@task_postrun.connect
def add_periodic_task_name(sender, task_id, task, args, kwargs, **extras):
    periodic_task_name = kwargs.get('periodic_task_name')
    if periodic_task_name:
        from django_celery_results.models import TaskResult
        # 更新 TaskResult 表中的 periodic_task_name 字段
        TaskResult.objects.filter(task_id=task_id).update(periodic_task_name=periodic_task_name)
