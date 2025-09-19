# 初始化
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
django.setup()

from dvadmin.system.fixtures.initSerializer import MenuInitSerializer, SystemConfigInitSerializer, \
    DictionaryInitSerializer

from dvadmin.utils.core_initialize import CoreInitialize


class Initialize(CoreInitialize):

    def init_menu(self):
        """
        初始化菜单信息
        """
        self.init_base(MenuInitSerializer, unique_fields=['name', 'web_path', 'component', 'component_name'])
    def init_dictionary(self):
        """
        初始化字典表
        """
        self.init_base(DictionaryInitSerializer, unique_fields=['value', 'parent', ])

    def run(self):
        self.init_menu()
        self.init_dictionary()
        print(22)
if __name__ == '__main__':
    Initialize(app='release_info').run()