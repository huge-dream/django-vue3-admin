# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **django-vue3-admin** based project with custom procurement/supplier management modules.

- **Backend**: Django 4.2.14 + Django REST Framework
- **Frontend**: Vue 3 + TypeScript + Vite + Element Plus + FastCRUD
- **Database**: MySQL 8.0 (configured via `backend/conf/env.py`)
- **Cache/Queue**: Redis + Celery
- **Real-time**: Django Channels (WebSocket)
- **Auth**: JWT via SimpleJWT

## Directory Structure

```
pis/
├── backend/
│   ├── application/          # Django project settings
│   │   ├── settings.py       # Main settings (imports from conf/env.py)
│   │   ├── urls.py           # Root URL routing
│   │   ├── asgi.py           # ASGI config (WebSocket support)
│   │   ├── wsgi.py           # WSGI config
│   │   └── celery.py         # Celery configuration
│   ├── apps/
│   │   ├── pisadmin/         # Custom procurement app
│   │   │   ├── basicinfo/    # Company, currency, supplier, unit, system no
│   │   │   └── miscprocurement/  # RFQ, price templates, cost sections
│   │   └── pissupplier/      # Supplier quotation module
│   ├── dvadmin/              # Core RBAC system
│   │   └── system/           # Users, roles, menus, departments, logs
│   └── conf/
│       └── env.py            # Environment configuration (DB, Redis credentials)
├── web/                      # Vue 3 frontend
│   └── src/
│       ├── views/pisadmin/   # Custom procurement pages
│       ├── views/pissupplier/# Supplier pages
│       └── views/system/     # Admin system pages
└── docker-compose.yml       # Docker deployment
```

## Common Commands

### Backend
```bash
cd backend

# Make migrations for custom apps
python manage.py makemigrations apps.pisadmin.apps.pisadmin
python manage.py makemigrations apps.pissupplier

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py init

# Initialize area data
python manage.py init_area

# Run development server
python manage.py runserver 0.0.0.0:8000

# Run with uvicorn (production-like)
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8
```

### Frontend
```bash
cd web
yarn install
yarn dev          # Development server (port 8080)
yarn build        # Production build
yarn build:dev    # Development build
yarn lint-fix     # Lint and fix
```

### Docker
```bash
docker-compose up -d
docker exec dvadmin3-django python manage.py makemigrations
docker exec dvadmin3-django python manage.py migrate
docker exec dvadmin3-django python manage.py init
```

## Configuration

Backend settings are split:
- `application/settings.py` - Django defaults
- `conf/env.py` - Environment-specific config (database, Redis, secrets)

## Key Dependencies

**Backend**: Django 4.2.14, djangorestframework 3.15.2, channels 4.1.0, celery, SimpleJWT

**Frontend**: Vue 3.4, Element Plus 2.8, FastCRUD 1.21, Vite 5.4, Pinia, Vue Router 4.4

## Notes

- Custom apps (`pisadmin`, `pissupplier`) extend the base `dvadmin` RBAC system
- The `miscprocurement` app handles询价 (RFQ) and cost template building
- Supplier quotations are managed in `pissupplier` app
- Default demo credentials: `superadmin` / `admin123456`

## Git 注意事项

**不要提交本地文档和 superpowers 相关文件**：
- `.claude/` 目录下的 superpowers 相关文件（`.planning/`、skills 等）
- `docs/` 目录下的本地文档
- 这些文件每个人开发任务不同，不应提交到仓库
