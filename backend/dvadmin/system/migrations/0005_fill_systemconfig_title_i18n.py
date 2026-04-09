# -*- coding: utf-8 -*-
"""
填充系统配置标题多语言翻译
用法: python manage.py migrate system 0005
"""
from django.db import migrations


def fill_systemconfig_title_i18n(apps, schema_editor):
    SystemConfig = apps.get_model('system', 'SystemConfig')

    updated_count = 0
    for config in SystemConfig.objects.all():
        update_fields = []
        if not config.title_en:
            config.title_en = config.title
            update_fields.append('title_en')
        if not config.title_zh_tw:
            config.title_zh_tw = config.title
            update_fields.append('title_zh_tw')
        if update_fields:
            config.save(update_fields=update_fields)
            updated_count += 1
    print(f"Updated {updated_count} system config translations")


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_systemconfig_title_en_systemconfig_title_zh_tw'),
    ]

    operations = [
        migrations.RunPython(fill_systemconfig_title_i18n, reverse_func),
    ]
