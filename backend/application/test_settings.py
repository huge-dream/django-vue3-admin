"""
测试专用 Django Settings（``pytest`` / ``DJANGO_SETTINGS_MODULE=application.test_settings``）

**SQL Server（与服务器部署一致，默认）**

- 继承 ``application.settings`` 中的 ``DATABASE_*``（可用环境变量覆盖，见 ``conf/env.py``）。
- 复用业务库 ``DATABASE_NAME``：不 CREATE/DROP 库、不跑 ``migrate``，避免与线上一致库结构冲突。
- 依赖 ``mssql-django`` 的 ``DatabaseCreation`` 补丁（见下方 ``_install_shared_test_database``）。

**无 SQL Server 时（本地 CI / 开发机）**

- 设置环境变量 ``PIS_TEST_USE_SQLITE=1``（或 ``TEST_USE_SQLITE=1``）：使用项目目录下 ``.pytest/pis_test_runner.sqlite3``，
  走 Django **默认**测试库创建与 ``migrate``，不挂「复用库」逻辑。
"""
import os

from application.settings import *  # noqa

_use_sqlite_for_tests = os.environ.get(
    "PIS_TEST_USE_SQLITE", os.environ.get("TEST_USE_SQLITE", "")
).lower() in ("1", "true", "yes")

if _use_sqlite_for_tests:
    _sqlite_dir = BASE_DIR / ".pytest"
    _sqlite_dir.mkdir(exist_ok=True)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(_sqlite_dir / "pis_test_runner.sqlite3"),
            "TEST": {
                "SERIALIZE": False,
            },
        }
    }
else:
    DATABASES["default"].setdefault("TEST", {})
    DATABASES["default"]["TEST"]["NAME"] = DATABASE_NAME
    DATABASES["default"]["TEST"]["SERIALIZE"] = False


def _install_shared_test_database(creation_cls, base_module):
    """
    绑定测试到已有库：不建库、不 migrate，仅切换连接并初始化缓存表（失败则忽略）。
    """

    class _SharedTestDatabase(creation_cls):
        def _create_test_db(self, verbosity, autoclobber=False, keepdb=False):
            return self._get_test_db_name()

        def _destroy_test_db(self, test_database_name, verbosity):
            pass

        def create_test_db(
            self, verbosity=1, autoclobber=False, serialize=True, keepdb=False
        ):
            from django.conf import settings as django_settings
            from django.core.management import call_command

            test_database_name = self._get_test_db_name()
            if verbosity >= 1:
                self.log(
                    "Binding tests to shared database %s (skip migrate)..."
                    % self._get_database_display_str(verbosity, test_database_name)
                )

            self._create_test_db(verbosity, autoclobber, keepdb)

            self.connection.close()
            django_settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
            self.connection.settings_dict["NAME"] = test_database_name

            if serialize:
                self.connection._test_serialized_contents = (
                    self.serialize_db_to_string()
                )

            try:
                call_command(
                    "createcachetable",
                    database=self.connection.alias,
                )
            except Exception:
                pass

            self.connection.ensure_connection()
            return test_database_name

    base_module.DatabaseWrapper.creation_class = _SharedTestDatabase


if not _use_sqlite_for_tests:
    _engine = (DATABASES["default"].get("ENGINE") or "").lower()

    if "postgresql" in _engine:
        from django.db.backends.postgresql import base as _pg_base
        from django.db.backends.postgresql.creation import (
            DatabaseCreation as _PGDatabaseCreation,
        )

        _install_shared_test_database(_PGDatabaseCreation, _pg_base)

    elif "mysql" in _engine:
        from django.db.backends.mysql import base as _my_base
        from django.db.backends.mysql.creation import (
            DatabaseCreation as _MySQLDatabaseCreation,
        )

        _install_shared_test_database(_MySQLDatabaseCreation, _my_base)

    elif "mssql" in _engine or "sql_server" in _engine:
        import mssql.base
        from mssql.creation import DatabaseCreation as _MsSqlDatabaseCreation

        _install_shared_test_database(_MsSqlDatabaseCreation, mssql.base)
