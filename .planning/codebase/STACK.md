# Technology Stack

**Analysis Date:** 2026-04-01

## Languages

**Primary:**
- Python 3.x - Backend development
- TypeScript 4.9.4 - Frontend development
- JavaScript (ESNext) - Frontend runtime

**Secondary:**
- Vue 3.4.38 - Frontend UI framework
- HTML/CSS - Frontend markup and styling

## Backend Framework

**Django Core:**
- Django 4.2.14 - Web framework
- Django REST Framework 3.15.2 - REST API development
- channels 4.1.0 - WebSocket support
- Celery 5.x (via dvadmin3-celery 3.1.6) - Async task queue

**Authentication:**
- djangorestframework-simplejwt 5.4.0 - JWT token authentication
- django-simple-captcha 0.6.0 - CAPTCHA verification

**Database:**
- mssql-django 1.7 - SQL Server driver (configured for pisdb)
- mysqlclient 2.2.0 - MySQL driver (also available)
- psycopg2 2.9.9 - PostgreSQL driver

**Key Django Plugins:**
- django-cors-headers 4.4.0 - Cross-origin resource sharing
- django-filter 24.2 - Database query filtering
- django-ranged-response 0.2.0 - HTTP range response support
- django-restql 0.15.4 - GraphQL-like query language for REST
- drf-yasg 1.21.7 - Swagger/OpenAPI documentation
- django-timezone-field 7.0 - Timezone support
- django-comment-migrate 0.1.7 - Comment migration utility
- Pillow 10.4.0 - Image processing
- openpyxl 3.1.5 - Excel file handling
- requests 2.32.4 - HTTP client
- pypinyin 0.51.0 - Chinese pinyin conversion
- ua-parser 0.18.0 - User agent parsing
- user-agents 2.2.0 - User agent detection
- six 1.16.0 - Python 2/3 compatibility
- whitenoise 6.7.0 - Static file serving
- pyparsing 3.1.2 - Parsing expression grammar
- typing-extensions 4.12.2 - Type hint extensions
- tzlocal 5.2 - Timezone localization

**Server:**
- uvicorn 0.30.3 - ASGI server
- gunicorn 23.0.0 - WSGI server
- gevent 24.2.1 - Async networking library

**Cloud Storage:**
- oss2 2.19.1 - Alibaba Cloud OSS integration
- cos-python-sdk-v5 1.9.37 - Tencent Cloud COS integration

## Frontend Framework

**Core:**
- Vue 3.4.38 - Progressive JavaScript framework
- TypeScript 4.9.4 - Typed superset of JavaScript
- Vite 5.4.1 - Next-generation frontend build tool
- Pinia 2.0.28 - State management
- Vue Router 4.4.3 - SPA routing
- Vue I18n 9.14.0 - Internationalization

**UI Component Libraries:**
- Element Plus 2.8.0 - UI component library
- @element-plus/icons-vue 2.3.1 - Element Plus icons
- Vant 4.9.19 - Mobile UI component library
- vant4-kit 1.0.3 - Vant utility kit

**FastCRUD:**
- @fast-crud/fast-crud 1.21.2 - Quick CRUD development
- @fast-crud/fast-extends 1.21.2 - FastCRUD extensions
- @fast-crud/ui-element 1.21.2 - Element Plus UI for FastCRUD
- @fast-crud/ui-interface 1.21.2 - FastCRUD UI interface

**Data Visualization:**
- echarts 5.5.1 - Interactive charting library
- echarts-gl 2.0.9 - ECharts 3D visualization
- echarts-wordcloud 2.1.0 - Word cloud for ECharts
- vxe-table 4.6.18 - Grid/table component
- xe-utils 3.5.30 - Utility functions for vxe-table

**Build & Development:**
- @vitejs/plugin-vue 5.1.2 - Vue plugin for Vite
- @vitejs/plugin-vue-jsx 4.0.1 - Vue JSX support
- vite-plugin-vue-setup-extend 0.4.0 - Vue setup syntax extension
- sass 1.56.2 - CSS preprocessor
- less 4.3.0 - CSS preprocessor
- autoprefixer 10.4.20 - CSS vendor prefixing
- postcss 8.4.21 - CSS transformation tool
- tailwindcss 3.2.7 - Utility-first CSS framework
- rollup 4.60.1 - Module bundler

**Utilities:**
- axios 1.7.4 - HTTP client
- qs 6.11.0 - Query string parsing
- lodash-es 4.17.21 - Utility library
- js-cookie 3.0.5 - Cookie handling
- mitt 3.0.1 - Tiny event emitter
- nprogress 0.2.0 - Progress bar
- sortablejs 1.15.0 - Drag and drop sorting
- vue-draggable-plus 0.6.0 - Vue draggable component
- screenfull 6.0.2 - Fullscreen API wrapper
- print-js 1.6.0 - Print functionality
- qrcodejs2-fixes 0.0.2 - QR code generation
- cropperjs 1.6.2 - Image cropping
- vue-cropper 1.0.8 - Vue image cropper
- countup.js 2.8.0 - Animated number counting
- e-icon-picker 2.1.1 - Icon picker
- element-tree-line 0.2.1 - Tree line for Element
- font-awesome 4.7.0 - Icon library
- @iconify/vue 4.1.2 - Icon library
- vue-clipboard3 2.0.0 - Clipboard API wrapper
- ts-md5 1.3.1 - MD5 hashing
- vue-grid-layout 3.0.0-beta1 - Grid layout
- vue-qr 4.0.9 - QR code for Vue
- jsplumb 2.15.6 - Visual connectivity
- @wangeditor/editor 5.1.23 - Rich text editor
- @wangeditor/editor-for-vue 5.1.12 - Vue wrapper for WangEditor
- js-table2excel 1.1.2 - Table to Excel export
- date-holidays 3.24.1 - Holiday data
- lunar-javascript 1.7.1 - Chinese lunar calendar
- upgrade 1.1.0 - Upgrade utility
- @great-dream/dvadmin3-celery-web 3.1.3 - Celery web UI

**Development Tools:**
- eslint 8.57.1 - Linting
- eslint-plugin-vue 9.27.0 - Vue ESLint plugin
- @typescript-eslint/parser 5.46.0 - TypeScript ESLint parser
- @typescript-eslint/eslint-plugin 5.46.0 - TypeScript ESLint plugin
- prettier 2.8.1 - Code formatting
- vue-eslint-parser 9.4.3 - Vue template parser
- @types/node 18.19.42 - Node.js type definitions
- @types/nprogress 0.2.3 - NProgress type definitions
- @types/sortablejs 1.15.8 - SortableJS type definitions
- @types/lodash 4.17.7 - Lodash type definitions
- baseline-browser-mapping 2.9.19 - Browser capability mapping

## Infrastructure

**Database:**
- MySQL 8.0 - Primary relational database (configured)
- SQL Server (via ODBC Driver 18) - Alternative database option

**Cache & Queue:**
- Redis - Caching, session storage, Celery broker
- Celery - Async task processing

**Container:**
- Docker - Containerization
- Docker Compose - Multi-container orchestration

## Configuration Files

**Backend:**
- `backend/conf/env.py` - Environment configuration (DB, Redis, Email)
- `backend/application/settings.py` - Django settings (imports from conf/env.py)
- `backend/application/celery.py` - Celery configuration
- `backend/application/asgi.py` - ASGI configuration (WebSocket support)
- `backend/application/ws_routing.py` - WebSocket URL routing
- `backend/application/websocketConfig.py` - WebSocket consumer implementation

**Frontend:**
- `web/package.json` - Node.js dependencies and scripts
- `web/vite.config.ts` - Vite build configuration
- `web/tsconfig.json` - TypeScript compiler options

## Project Structure

```
pis/
├── backend/
│   ├── application/          # Django project configuration
│   │   ├── settings.py        # Main Django settings
│   │   ├── urls.py           # Root URL configuration
│   │   ├── asgi.py          # ASGI application (HTTP + WebSocket)
│   │   ├── celery.py        # Celery task configuration
│   │   ├── ws_routing.py    # WebSocket routing
│   │   └── websocketConfig.py # WebSocket consumers
│   ├── apps/
│   │   ├── pisadmin/        # Custom procurement app
│   │   │   ├── basicinfo/   # Company, currency, supplier, unit
│   │   │   └── miscprocurement/ # RFQ, price templates, cost sections
│   │   └── pissupplier/     # Supplier quotation module
│   ├── dvadmin/             # Core RBAC system (dvadmin3)
│   │   └── system/          # Users, roles, menus, departments
│   └── conf/
│       └── env.py           # Environment configuration
├── web/                     # Vue 3 frontend
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── api/            # API clients
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router config
│   ├── vite.config.ts      # Vite configuration
│   └── tsconfig.json       # TypeScript config
└── docker-compose.yml      # Docker deployment
```

## Build Commands

**Backend:**
```bash
python manage.py makemigrations  # Create migrations
python manage.py migrate          # Apply migrations
python manage.py runserver        # Development server
uvicorn application.asgi:application --workers 8  # Production
```

**Frontend:**
```bash
yarn dev        # Development server (port 8080)
yarn build      # Production build
yarn lint-fix   # Lint and auto-fix
```

---

*Stack analysis: 2026-04-01*
