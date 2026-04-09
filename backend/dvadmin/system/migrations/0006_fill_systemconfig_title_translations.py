# -*- coding: utf-8 -*-
"""
填充系统配置标题多语言翻译
"""
from django.db import migrations


def fill_translations(apps, schema_editor):
    SystemConfig = apps.get_model('system', 'SystemConfig')

    translations = {
        '基础配置': {'en': 'Basic Config', 'zh_tw': '基礎配置'},
        '系统配置': {'en': 'System Config', 'zh_tw': '系統配置'},
        '登录页配置': {'en': 'Login Page Config', 'zh_tw': '登錄頁配置'},
        '文件存储配置': {'en': 'File Storage Config', 'zh_tw': '文件存儲配置'},
        '网站标题': {'en': 'Site Title', 'zh_tw': '網站標題'},
        '网站名称': {'en': 'Site Name', 'zh_tw': '網站名稱'},
        '登录网站logo': {'en': 'Login Logo', 'zh_tw': '登錄網站logo'},
        '登录页背景图': {'en': 'Login Background', 'zh_tw': '登錄頁背景圖'},
        '版权信息': {'en': 'Copyright', 'zh_tw': '版權信息'},
        '备案信息': {'en': 'Filing Info', 'zh_tw': '備案信息'},
        '帮助链接': {'en': 'Help Link', 'zh_tw': '幫助鏈接'},
        '隐私链接': {'en': 'Privacy Link', 'zh_tw': '隱私鏈接'},
        '条款链接': {'en': 'Terms Link', 'zh_tw': '條款鏈接'},
        '网页标题': {'en': 'Page Title', 'zh_tw': '網頁標題'},
        '网站小图标': {'en': 'Site Favicon', 'zh_tw': '網站小圖標'},
        '开启验证码': {'en': 'Enable Captcha', 'zh_tw': '開啟驗證碼'},
        '创建用户默认密码': {'en': 'Default Password', 'zh_tw': '創建用戶默認密碼'},
        '存储引擎': {'en': 'Storage Engine', 'zh_tw': '存儲引擎'},
        '文件是否备份': {'en': 'File Backup', 'zh_tw': '文件是否備份'},
        '阿里云-AccessKey': {'en': 'Aliyun AccessKey', 'zh_tw': '阿裡雲-AccessKey'},
        '阿里云-Secret': {'en': 'Aliyun Secret', 'zh_tw': '阿裡雲-Secret'},
        '阿里云-Endpoint': {'en': 'Aliyun Endpoint', 'zh_tw': '阿裡雲-Endpoint'},
        '阿里云-上传路径': {'en': 'Aliyun Upload Path', 'zh_tw': '阿裡雲-上傳路徑'},
        '阿里云-Bucket': {'en': 'Aliyun Bucket', 'zh_tw': '阿裡雲-Bucket'},
        '阿里云-cdn地址': {'en': 'Aliyun CDN URL', 'zh_tw': '阿裡雲-cdn地址'},
        '腾讯云-SecretId': {'en': 'Tencent SecretId', 'zh_tw': '騰訊雲-SecretId'},
        '腾讯云-SecretKey': {'en': 'Tencent SecretKey', 'zh_tw': '騰訊雲-SecretKey'},
        '腾讯云-Region': {'en': 'Tencent Region', 'zh_tw': '騰訊雲-Region'},
        '腾讯云-Bucket': {'en': 'Tencent Bucket', 'zh_tw': '騰訊雲-Bucket'},
        '腾讯云-上传路径': {'en': 'Tencent Upload Path', 'zh_tw': '騰訊雲-上傳路徑'},
    }

    updated = 0
    for config in SystemConfig.objects.all():
        if config.title in translations:
            trans = translations[config.title]
            config.title_en = trans['en']
            config.title_zh_tw = trans['zh_tw']
            config.save(update_fields=['title_en', 'title_zh_tw'])
            updated += 1
    print(f"Updated {updated} config translations")


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_fill_systemconfig_title_i18n'),
    ]

    operations = [
        migrations.RunPython(fill_translations, reverse_func),
    ]
