"""
测试专用 Django Settings
使用已存在的 pisdb 数据库运行测试，测试之间有事务隔离。
不创建/删除测试库，直接使用 pisdb。
"""
import os
import sys
from application.settings import *  # noqa

# Patch MSSQL creation class BEFORE any database connections are made
# 这必须在 Django settings 加载之后、任何 DB 操作之前完成
import mssql.base
from mssql.creation import DatabaseCreation


class NoCreateTestDatabase(DatabaseCreation):
    """跳过 CREATE/DROP DATABASE 的 MSSQL 创建逻辑"""

    def _create_test_db(self, verbosity=1, autoclobber=False, keepdb=False):
        return self.connection.settings_dict["NAME"]

    def _destroy_test_db(self, test_db_name, verbosity=1, keepdb=False):
        pass


mssql.base.DatabaseWrapper.creation_class = NoCreateTestDatabase

# 配置测试数据库
DATABASES["default"]["TEST"] = {
    "NAME": DATABASE_NAME,
}
