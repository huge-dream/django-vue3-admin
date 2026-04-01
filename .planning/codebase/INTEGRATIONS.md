# External Integrations

**Analysis Date:** 2026-04-01

## Database Connection

**Primary Database:**
- **Engine:** Microsoft SQL Server (via mssql-django 1.7)
- **Connection Driver:** ODBC Driver 18 for SQL Server
- **Database Name:** `pisdb`
- **Host:** `192.168.80.29`
- **Port:** `1433`
- **Credentials:** Configured in `backend/conf/env.py`
- **Configuration File:** `backend/conf/env.py` lines 14-24

**Connection Settings:**
```python
DATABASE_ENGINE = "mssql"
DATABASE_NAME = 'pisdb'
DATABASE_HOST = '192.168.80.29'
DATABASE_PORT = 1433
DATABASE_USER = "test"
DATABASE_PASSWORD = '123456'
OPTIONS = {
    "driver": "ODBC Driver 18 for SQL Server",
    "extra_params": "Encrypt=yes;TrustServerCertificate=yes"
}
```

**Alternative Database Support:**
- MySQL 8.0 (via mysqlclient 2.2.0)
- PostgreSQL (via psycopg2 2.9.9)

**Table Prefix:** `pis_` (Procurement Inquiry System)

**Django Settings:** `backend/application/settings.py` lines 105-119

## Redis Configuration

**Connection:**
- **Host:** `177.10.0.15`
- **Port:** `6379`
- **Password:** `redis_5pGXn2`
- **URL Format:** `redis://:redis_5pGXn2@177.10.0.15:6379`

**Usage in Application:**
- Redis DB 1: General caching (`REDIS_DB`)
- Redis DB 3: Celery broker (`CELERY_BROKER_DB`)

**Configuration File:** `backend/conf/env.py` lines 31-35

**Cache Backend Configuration:**
```python
REDIS_DB = 1
CELERY_BROKER_DB = 3
REDIS_PASSWORD = 'redis_5pGXn2'
REDIS_HOST = '177.10.0.15'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'
```

## Celery Task Queue

**Broker:** Redis (same server as cache)

**Configuration Source:** `backend/application/celery.py`

**Celery Setup:**
- Auto-discovers tasks from all installed apps
- Uses Django settings namespace for configuration (`CELERY_*`)
- Supports tenant-aware mode if `django_tenants` is installed
- Runs with `C_FORCE_ROOT = True` for root execution

**Retry Strategy:**
- Default retry delay: 180 seconds
- Maximum retries: 3
- Decorator: `@retry_base_task_error()`

**Task Result Storage:** Django Celery Results (`django_celery_results`)

**Celery Beat Configuration:**
- Timezone: `Asia/Shanghai`
- Result backend stores task results in database

**Django Settings Import:** `from django.conf:settings, namespace='CELERY'`

**Installed Apps Integration:**
```python
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

## WebSocket / Django Channels

**ASGI Application:** `backend/application/asgi.py`

**Protocol Support:**
- HTTP (via Django)
- WebSocket (via Channels)

**WebSocket URL Pattern:**
- Route: `ws/<str:service_uid>/`
- Consumer: `MegCenter` (from `application.websocketConfig`)
- Routing: `backend/application/ws_routing.py`

**Channel Layers:**
- Default (development): `InMemoryChannelLayer`
- Production: `channels_redis.core.RedisChannelLayer` (commented out)

**Authentication:**
- WebSocket connections validated via JWT token in `service_uid` parameter
- Token decoded using Django `SECRET_KEY`
- User ID extracted from decoded token
- Channel group format: `user_{user_id}`

**WebSocket Consumer Classes:**
- `DvadminWebSocket` - Base WebSocket consumer with JWT auth
- `MegCenter` - Message center consumer extending base class

**Message Flow:**
1. Client connects to `ws://host/ws/<jwt_token>/`
2. Token validated, user_id extracted
3. User added to channel group `user_{user_id}`
4. Messages pushed to user's channel group
5. `websocket_push()` function sends messages to specific users

**File:** `backend/application/websocketConfig.py` lines 57-114

## Authentication & Authorization

**JWT Authentication:**
- **Package:** djangorestframework-simplejwt 5.4.0
- **Header Type:** `JWT`
- **Access Token Lifetime:** 1440 minutes (24 hours)
- **Refresh Token Lifetime:** 1 day
- **Rotate Refresh Tokens:** Enabled

**JWT Configuration (settings.py lines 321-329):**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1440),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("JWT",),
    "ROTATE_REFRESH_TOKENS": True,
}
```

**Authentication Backends:**
- `rest_framework_simplejwt.authentication.JWTAuthentication`
- `rest_framework.authentication.SessionAuthentication`

**Custom Backend:** `dvadmin.utils.backends.CustomBackend`

**REST Framework Default Authentication (settings.py lines 304-307):**
```python
"DEFAULT_AUTHENTICATION_CLASSES": (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",
),
```

**Permission:** `rest_framework.permissions.IsAuthenticated`

## Email Configuration

**SMTP Configuration (backend/conf/env.py lines 53-68):**
```python
EMAIL_FROM = "eip@avc.co"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_HOST = "mailflow.avc.co"
EMAIL_PORT = 25
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False
```

**Email Features:**
- Plain text connection (no SSL/TLS)
- System emails sent from `eip@avc.co`

## Cloud Storage Integrations

**Alibaba Cloud OSS:**
- Package: `oss2 2.19.1`
- Used for file storage

**Tencent Cloud COS:**
- Package: `cos-python-sdk-v5 1.9.37`
- Used for file storage

## API Documentation

**Swagger/OpenAPI:**
- Package: `drf-yasg 1.21.7`
- Login URL: `/apiLogin/`
- Logout URL: `/rest_framework:logout/`
- Auto schema generation with custom schema class
- JSON editor enabled in Swagger UI

**Configuration (settings.py lines 334-354):**
```python
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"basic": {"type": "basic"}},
    "LOGIN_URL": "apiLogin/",
    "LOGOUT_URL": "rest_framework:logout",
    "JSON_EDITOR": True,
    "DEFAULT_AUTO_SCHEMA_CLASS": "dvadmin.utils.swagger.CustomSwaggerAutoSchema",
}
```

## CORS Configuration

**CORS Settings (settings.py lines 177-181):**
```python
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
```

**CORS Middleware:** `corsheaders.middleware.CorsMiddleware`

## Static Files & Media

**Static Files:**
- URL: `/static/`
- Storage: Whitenoise with compression
- Storage Class: `whitenoise.storage.CompressedStaticFilesStorage`

**Media Files:**
- URL: `/media/`
- Root: `media` directory in project

**Configuration (settings.py lines 156-169):**
```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
MEDIA_ROOT = "media"
MEDIA_URL = "/media/"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)
```

## Proxy Configuration (Development)

**Vite Dev Server Proxy (vite.config.ts lines 37-44):**
```typescript
proxy: {
    '/gitee': {
        target: 'https://gitee.com',
        ws: true,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/gitee/, ''),
    },
}
```

## Environment Variables

**Configuration Source:** `backend/conf/env.py`

**Key Environment Variables:**
| Variable | Purpose |
|----------|---------|
| `DATABASE_ENGINE` | Database backend type |
| `DATABASE_HOST` | Database server host |
| `DATABASE_PORT` | Database server port |
| `DATABASE_USER` | Database username |
| `DATABASE_PASSWORD` | Database password |
| `REDIS_HOST` | Redis server host |
| `REDIS_PASSWORD` | Redis password |
| `DEBUG` | Debug mode flag |
| `EMAIL_HOST` | SMTP server |
| `EMAIL_PORT` | SMTP port |

**Note:** Actual credentials are stored in `backend/conf/env.py` (not committed to version control per best practices).

## Key Dependencies Between Systems

```
Frontend (Vue 3)
    |
    | HTTP/REST + WebSocket
    v
Backend (Django + DRF)
    |
    +---> Database (SQL Server/MySQL/PostgreSQL)
    +---> Cache (Redis)
    +---> Task Queue (Celery + Redis)
    +---> WebSocket (Channels + Redis)
    +---> Cloud Storage (OSS/COS)
    +---> Email (SMTP)
```

---

*Integration audit: 2026-04-01*
