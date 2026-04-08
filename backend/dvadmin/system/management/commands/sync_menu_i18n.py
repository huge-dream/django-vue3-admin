# -*- coding: utf-8 -*-
"""
同步菜单多语言数据
用法: python manage.py sync_menu_i18n
"""
import os
import json

from django.core.management.base import BaseCommand

from dvadmin.system.models import Menu, MenuButton


class Command(BaseCommand):
    help = '同步菜单多语言数据从init_menu.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有现有菜单的i18n字段为空后再同步',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)

        # 获取init_menu.json路径
        # sync_menu_i18n.py -> commands(1) -> management(2) -> system(3) -> dvadmin(4) -> backend(5)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        json_path = os.path.join(backend_dir, 'dvadmin', 'system', 'fixtures', 'init_menu.json')

        if not os.path.exists(json_path):
            self.stderr.write(f'文件不存在: {json_path}')
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            menu_data = json.load(f)

        menu_count = 0
        button_count = 0

        def process_menus(menus, parent_id=None):
            nonlocal menu_count, button_count

            for menu in menus:
                name_en = menu.get('name_en', '')
                name_zh_tw = menu.get('name_zh_tw', '')

                # 更新菜单
                filter_data = {
                    'name': menu['name'],
                    'web_path': menu.get('web_path', ''),
                    'component': menu.get('component', ''),
                    'component_name': menu.get('component_name', ''),
                }

                db_menu = Menu.objects.filter(**filter_data).first()
                if db_menu:
                    if reset or not db_menu.name_en:
                        db_menu.name_en = name_en
                    if reset or not db_menu.name_zh_tw:
                        db_menu.name_zh_tw = name_zh_tw
                    db_menu.save(update_fields=['name_en', 'name_zh_tw'])
                    menu_count += 1
                    self.stdout.write(f"  更新菜单: {menu['name']} -> en: {name_en}, zh_tw: {name_zh_tw}")

                # 处理菜单按钮
                for btn in menu.get('menu_button', []):
                    btn_name_en = btn.get('name_en', '')
                    btn_name_zh_tw = btn.get('name_zh_tw', '')

                    if db_menu:
                        db_btn = MenuButton.objects.filter(menu=db_menu, value=btn.get('value', '')).first()
                        if db_btn:
                            if reset or not db_btn.name_en:
                                db_btn.name_en = btn_name_en
                            if reset or not db_btn.name_zh_tw:
                                db_btn.name_zh_tw = btn_name_zh_tw
                            db_btn.save(update_fields=['name_en', 'name_zh_tw'])
                            button_count += 1
                            self.stdout.write(f"    更新按钮: {btn['name']} -> en: {btn_name_en}, zh_tw: {btn_name_zh_tw}")

                # 递归处理子菜单
                if menu.get('children'):
                    process_menus(menu['children'], menu.get('id'))

        self.stdout.write('开始同步菜单多语言数据...\n')

        for top_menu in menu_data:
            self.stdout.write(f"\n处理顶级菜单: {top_menu['name']}")
            process_menus([top_menu])

        self.stdout.write(self.style.SUCCESS(f'\n同步完成!'))
        self.stdout.write(f'  更新菜单数: {menu_count}')
        self.stdout.write(f'  更新按钮数: {button_count}')
