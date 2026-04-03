# 初始化
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
django.setup()

from dvadmin.utils.core_initialize import CoreInitialize
from dvadmin.system.fixtures.initSerializer import (
    UsersInitSerializer, DeptInitSerializer, RoleInitSerializer,
    MenuInitSerializer, ApiWhiteListInitSerializer, DictionaryInitSerializer,
    SystemConfigInitSerializer, RoleMenuInitSerializer, RoleMenuButtonInitSerializer
)


class Initialize(CoreInitialize):

    def init_dept(self):
        """
        初始化部门信息
        """
        self.init_base(DeptInitSerializer, unique_fields=['name', 'parent','key'])

    def init_role(self):
        """
        初始化角色信息
        """
        self.init_base(RoleInitSerializer, unique_fields=['key'])

    def init_users(self):
        """
        初始化用户信息
        """
        self.init_base(UsersInitSerializer, unique_fields=['username'])

    def init_menu(self):
        """
        初始化菜单信息
        """
        self.init_base(MenuInitSerializer, unique_fields=['name', 'web_path', 'component', 'component_name'])

    def init_role_menu(self):
        """
        初始化角色菜单信息
        """
        self.init_base(RoleMenuInitSerializer, unique_fields=['role__key', 'menu__web_path', 'menu__component_name'])

    def init_role_menu_button(self):
        """
        初始化角色菜单按钮信息
        """
        self.init_base(RoleMenuButtonInitSerializer, unique_fields=['role__key', 'menu_button__value'])

    def init_api_white_list(self):
        """
        初始API白名单
        """
        self.init_base(ApiWhiteListInitSerializer, unique_fields=['url', 'method', ])

    def init_dictionary(self):
        """
        初始化字典表
        """
        self.init_base(DictionaryInitSerializer, unique_fields=['value', 'parent', ])

    def init_system_config(self):
        """
        初始化系统配置表
        """
        self.init_base(SystemConfigInitSerializer, unique_fields=['key', 'parent', ])

    def run(self):
        self.init_dept()
        self.init_role()
        self.init_users()
        self.init_menu()
        self.init_role_menu()
        self.init_role_menu_button()
        self.init_api_white_list()
        self.init_dictionary()
        self.init_system_config()


if __name__ == "__main__":
    Initialize(app='dvadmin.system').run()
