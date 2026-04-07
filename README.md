# PIS - Procurement & Supplier Management System

## Project Overview

A Django-Vue3 based procurement and supplier management system with RBAC permission control.

## Project Architecture 🏗️

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 4.2.14 + Django REST Framework 3.15.2 |
| **Frontend** | Vue 3 + TypeScript + Vite 5.4 + Element Plus 2.8 + FastCRUD |
| **Database** | MySQL 8.0 |
| **Cache/Queue** | Redis + Celery |
| **Real-time** | Django Channels (WebSocket) |
| **Auth** | JWT via SimpleJWT |

### Directory Structure

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
└── scripts/                  # Service management scripts
    ├── start-backend.sh      # Start backend service
    ├── start-frontend.sh    # Start frontend service
    ├── start-celery.sh      # Start Celery worker/beat
    ├── stop-all.sh          # Stop all services
    └── check-status.sh      # Check service status
```

### Module Description

| Module | Description |
|--------|-------------|
| `pisadmin/basicinfo` | Basic info management: companies, currencies, suppliers, units, system numbering rules |
| `pisadmin/miscprocurement` | Miscellaneous procurement: RFQ, price templates, cost section builder |
| `pissupplier` | Supplier quotation module |
| `dvadmin/system` | Core RBAC system: users, roles, menus, departments, operation logs |

### Configuration

Backend settings are split:
- `application/settings.py` - Django defaults
- `conf/env.py` - Environment-specific config (database, Redis, secrets)

## Prerequisites

~~~
Python >= 3.11.0 (Minimum version 3.9+)
Node.js >= 16.0
Mysql >= 8.0 (Optional, default database: SQLite3, supports 5.7+, recommended version: 8.0)
Redis (Optional, latest version)
~~~

## Quick Start

### Backend

#### Method 1: Script Startup (Recommended)

```bash
# Go to project root
cd D:\AVC-PROJECT\pis

# Start backend service (development mode)
./scripts/start-backend.sh

# Start frontend service
./scripts/start-frontend.sh

# Start Celery async tasks (optional)
./scripts/start-celery.sh
```

**Script Description:**

| Script | Description |
|--------|-------------|
| `start-backend.sh` | Start backend service (auto-creates PID and log files) |
| `start-frontend.sh` | Start frontend dev server |
| `start-celery.sh` | Start Celery Worker and Beat |
| `stop-all.sh` | Stop all services |
| `stop-celery.sh` | Stop Celery only |
| `check-status.sh` | Check all service status |
| `view-logs.sh` | View service logs |

**View Logs:**
```bash
./scripts/view-logs.sh all      # View all logs
./scripts/view-logs.sh backend  # Backend logs only
./scripts/view-logs.sh celery   # Celery logs only
```

**Stop Services:**
```bash
./scripts/stop-all.sh           # Stop all services
./scripts/stop-celery.sh       # Stop Celery only
```

#### Method 2: Manual Startup

```bash
# 1. Go to backend directory
cd backend

# 2. Copy and configure environment file
cp ./conf/env.example.py ./conf/env.py
# Edit env.py to configure database information

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Run migrations
python3 manage.py makemigrations
python3 manage.py migrate

# 5. Initialize data
python3 manage.py init
python3 manage.py init_area

# 6. Start backend
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8
```

### Frontend

```bash
# Go to web directory
cd web

# Install dependencies
npm install yarn
yarn install --registry=https://registry.npm.taobao.org

# Start development server
yarn run dev
# Visit http://localhost:8080 in your browser
# Parameters such as boot port can be configured in the .env.development file

# Build for production
yarn run build
```

### Access

- Frontend URL: http://localhost:8080
- Backend API: http://localhost:8080/api
- Default account: `superadmin` / `admin123456`

### Docker

```shell
docker-compose up -d
# Initialize backend data (first execution only)
docker exec -ti dvadmin3-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```
