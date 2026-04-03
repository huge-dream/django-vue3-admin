import os

from application.settings import BASE_DIR

# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 数据库 ENGINE ，默认演示使用 sqlite3 数据库，正式环境建议使用 mysql 数据库
# sqlite3 设置
# DATABASE_ENGINE = "django.db.backends.sqlite3"
# DATABASE_NAME = os.path.join(BASE_DIR, "db.sqlite3")

# 使用sqlserver时，改为此配置
DATABASE_ENGINE = "mssql"
DATABASE_NAME = 'pisdb'

# 数据库地址 改为自己数据库地址
DATABASE_HOST = '192.168.80.29'
# # 数据库端口
DATABASE_PORT = 1433
# # 数据库用户名
DATABASE_USER = "test"
# # 数据库密码
DATABASE_PASSWORD = '123456'

# 表前缀(小写)
TABLE_PREFIX = "pis_"  # Procurement Inquiry System
# ================================================= #
# ******** redis配置，无redis 可不进行配置  ******** #
# ================================================= #
REDIS_DB = 1
CELERY_BROKER_DB = 3
REDIS_PASSWORD = 'redis_5pGXn2'
REDIS_HOST = '192.168.80.90'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'
# ================================================= #
# ****************** 功能 启停  ******************* #
# ================================================= #
DEBUG = True
# 启动登录详细概略获取(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True
# 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
LOGIN_NO_CAPTCHA_AUTH = True
# ================================================= #
# ****************** 其他 配置  ******************* #
# ================================================= #

ALLOWED_HOSTS = ["*"]
# 列权限中排除App应用
COLUMN_EXCLUDE_APPS = []


# ================================================= #
# ****************** 邮件 配置  ******************* #
# ================================================= #
# 发送邮箱地址（From 显示）
EMAIL_FROM = "eip@avc.co"
# SMTP 登录账号（服务器不支持认证，留空）
EMAIL_HOST_USER = ""
# SMTP 登录密码/授权码（服务器不支持认证，留空）
EMAIL_HOST_PASSWORD = ""
# SMTP 服务器地址
EMAIL_HOST = "mailflow.avc.co"
# SMTP 端口
EMAIL_PORT = 25
# 是否使用 SSL（如果走 STARTTLS，将 EMAIL_USE_SSL 设为 False，EMAIL_USE_TLS=True）
# 服务器不支持STARTTLS，使用纯明文连接
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False

# ================================================= #
# *************** RustFS 对象存储 配置 *************** #
# ================================================= #
RUSTFS_ENDPOINT = "192.168.80.90:9000"
RUSTFS_ACCESS_KEY = "rustfsadmin"
RUSTFS_SECRET_KEY = "rustfsadmin"
RUSTFS_BUCKET = "pis-media"
RUSTFS_SECURE = False  # True=HTTPS, False=HTTP
RUSTFS_PATH_PREFIX = ""  # 存储路径前缀，可为空
RUSTFS_REGION = "us-east-1"  # RustFS 区域（可自定义）
