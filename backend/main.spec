# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['./'],
    binaries=[],
    datas=[
        ('./static', 'static'),
        ('./static/captcha/fonts', 'captcha/fonts'),
        ('./templates', 'templates'),
        ('./dvadmin/system/util', 'dvadmin/system/util'),
        ('./plugins/__init__.py', 'plugins/__init__.py'),
        ('./db.sqlite3', './'),
    ],
    hiddenimports=[
        "django",
        "testfixtures",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_comment_migrate",
        "rest_framework",
        "django_filters",
        "corsheaders",  # 注册跨域app
        "drf_yasg",
        "captcha",
        "channels",
        "dvadmin.system",
        "plugins.gla",
        "testfixtures",
        "application.asgi",
        "dvadmin.utils.middleware",
        "whitenoise",
        "whitenoise.middleware",
        "whitenoise.storage",
        "dvadmin.utils.pagination",
        "dvadmin.utils.exception",
        "rest_framework_simplejwt.state",
    ],
    hookspath=['./extra-hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
app = BUNDLE(
    coll,
    name='main.app',
    icon=None,
    bundle_identifier=None,
)
