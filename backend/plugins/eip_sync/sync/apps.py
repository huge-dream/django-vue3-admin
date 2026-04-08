from django.apps import AppConfig


class SyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sync"
    verbose_name = "EIP 数据同步"

    def ready(self):
        # Register adapters with SyncFactory
        from sync.adapters import misc_material  # noqa: F401
        from sync.adapters import pricing_result  # noqa: F401
