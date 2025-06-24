import json
import logging
import os

import django
from django.db.models import QuerySet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()
from django.core.management.base import BaseCommand

from application.settings import BASE_DIR
from dvadmin.system.models import Menu, Users, Dept, Role, ApiWhiteList, Dictionary, SystemConfig, RoleMenuButtonPermission, RoleMenuPermission
from dvadmin.system.fixtures.initSerializer import UsersInitSerializer, DeptInitSerializer, RoleInitSerializer, \
    MenuInitSerializer, ApiWhiteListInitSerializer, DictionaryInitSerializer, SystemConfigInitSerializer, \
    RoleMenuInitSerializer, RoleMenuButtonInitSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    生产初始化菜单: python3 manage.py generate_init_json 生成初始化的model名
    例如：
    全部生成：python3 manage.py generate_init_json
    只生成某个model的： python3 manage.py generate_init_json users
    """

    def serializer_data(self, serializer, query_set: QuerySet):
        serializer = serializer(query_set, many=True)
        data = json.loads(json.dumps(serializer.data, ensure_ascii=False))
        with open(os.path.join(BASE_DIR, f'init_{query_set.model._meta.model_name}.json'), 'w',encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return

    def add_arguments(self, parser):
        parser.add_argument("generate_name", nargs="*", type=str, help="初始化生成的表名")

    def generate_users(self):
        self.serializer_data(UsersInitSerializer, Users.objects.all())

    def generate_role(self):
        self.serializer_data(RoleInitSerializer, Role.objects.all())

    def generate_dept(self):
        self.serializer_data(DeptInitSerializer, Dept.objects.filter(parent_id__isnull=True))

    def generate_menu(self):
        self.serializer_data(MenuInitSerializer, Menu.objects.filter(parent_id__isnull=True))

    def generate_api_white_list(self):
        self.serializer_data(ApiWhiteListInitSerializer, ApiWhiteList.objects.all())

    def generate_dictionary(self):
        self.serializer_data(DictionaryInitSerializer, Dictionary.objects.filter(parent_id__isnull=True))

    def generate_system_config(self):
        self.serializer_data(SystemConfigInitSerializer, SystemConfig.objects.filter(parent_id__isnull=True))

    def generate_role_menu(self):
        self.serializer_data(RoleMenuInitSerializer, RoleMenuPermission.objects.all())

    def generate_role_menu_button(self):
        self.serializer_data(RoleMenuButtonInitSerializer, RoleMenuButtonPermission.objects.all())

    def handle(self, *args, **options):
        generate_name = options.get('generate_name')
        generate_name_dict = {
            "users": self.generate_users,
            "role": self.generate_role,
            "dept": self.generate_dept,
            "menu": self.generate_menu,
            "api_white_list": self.generate_api_white_list,
            "dictionary": self.generate_dictionary,
            "system_config": self.generate_system_config,
            "role_menu": self.generate_role_menu,
            "role_menu_button": self.generate_role_menu_button,
        }
        if not generate_name:
            for ele in generate_name_dict.keys():
                generate_name_dict[ele]()
            return

        for generate_name in generate_name:
            if generate_name not in generate_name_dict:
                print(f"该初始化方法尚未配置\n{generate_name_dict}")
                raise Exception(f"该初始化方法尚未配置,已配置项:{list(generate_name_dict.keys())}")
            generate_name_dict[generate_name]()
            return


if __name__ == '__main__':
    # with open(os.path.join(BASE_DIR, 'temp_init_menu.json')) as f:
    #     for menu_data in json.load(f):
    #         menu_data['creator'] = 1
    #         menu_data['modifier'] = 1
    #         menu_data['dept_belong_id'] = 1
    #         request.user = Users.objects.order_by('create_datetime').first()
    #         serializer = MenuInitSerializer(data=menu_data, request=request)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    a = Users.objects.filter()
    print(type(Users.objects.filter()))
