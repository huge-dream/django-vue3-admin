# -*- coding: utf-8 -*-
"""
填充菜单名称多语言翻译
用法: python manage.py migrate system 0003
"""
from django.db import migrations


def fill_menu_i18n(apps, schema_editor):
    Menu = apps.get_model('system', 'Menu')

    name_translations = {
        '系统管理': {'en': 'System Management', 'zh_tw': '系統設置'},
        '用户管理': {'en': 'User Management', 'zh_tw': '用戶管理'},
        '菜单管理': {'en': 'Menu Management', 'zh_tw': '選單管理'},
        '部门管理': {'en': 'Department Management', 'zh_tw': '部門管理'},
        '角色管理': {'en': 'Role Management', 'zh_tw': '角色管理'},
        '消息中心': {'en': 'Notification Center', 'zh_tw': '通知中心'},
        '接口白名单': {'en': 'API Whitelist', 'zh_tw': '接口白名單'},
        '下载中心': {'en': 'Download Center', 'zh_tw': '下載中心'},
        '常规配置': {'en': 'General Config', 'zh_tw': '常規配置'},
        '系统配置': {'en': 'System Config', 'zh_tw': '系統配置'},
        '字典管理': {'en': 'Dictionary Management', 'zh_tw': '字典管理'},
        '地区管理': {'en': 'Area Management', 'zh_tw': '地區管理'},
        '附件管理': {'en': 'File Management', 'zh_tw': '附件管理'},
        '日志管理': {'en': 'Log Management', 'zh_tw': '日誌管理'},
        '登录日志': {'en': 'Login Logs', 'zh_tw': '登錄日誌'},
        '操作日志': {'en': 'Operation Logs', 'zh_tw': '操作日誌'},
        '定时任务': {'en': 'Scheduled Tasks', 'zh_tw': '定時任務'},
        '任务管理': {'en': 'Task Management', 'zh_tw': '任務管理'},
        '任务日志': {'en': 'Task Logs', 'zh_tw': '任務日誌'},
        '个人信息': {'en': 'Personal Info', 'zh_tw': '個人信息'},
        '个人中心': {'en': 'Personal Center', 'zh_tw': '個人中心'},
        '修改密码': {'en': 'Change Password', 'zh_tw': '修改密碼'},
        '首页': {'en': 'Dashboard', 'zh_tw': '首頁'},
    }

    updated_count = 0
    for menu in Menu.objects.all():
        if menu.name in name_translations:
            trans = name_translations[menu.name]
            update_fields = []
            if not menu.name_en:
                menu.name_en = trans['en']
                update_fields.append('name_en')
            if not menu.name_zh_tw:
                menu.name_zh_tw = trans['zh_tw']
                update_fields.append('name_zh_tw')
            if update_fields:
                menu.save(update_fields=update_fields)
                updated_count += 1
    print(f"Updated {updated_count} menu translations")


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_menu_name_en_menu_name_zh_tw_menubutton_name_en_and_more'),
    ]

    operations = [
        migrations.RunPython(fill_menu_i18n, reverse_func),
    ]
