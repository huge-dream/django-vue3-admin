# Codebase Structure

**Analysis Date:** 2026-04-01

## Directory Layout

```
pis/
├── backend/
│   ├── application/          # Django project config (settings, urls, asgi)
│   ├── apps/
│   │   ├── pisadmin/         # Custom procurement app
│   │   │   ├── basicinfo/   # Company, currency, supplier, unit, system no
│   │   │   └── miscprocurement/  # RFQ, price templates, cost sections
│   │   └── pissupplier/      # Supplier quotation module
│   ├── conf/
│   │   └── env.py            # Environment config (DB, Redis, Email)
│   ├── dvadmin/              # Base RBAC system
│   │   ├── system/           # Users, roles, menus, departments
│   │   └── utils/            # CoreModel, CustomViewSet, filters, etc.
│   ├── plugins/              # Plugin modules (celery, etc.)
│   ├── static/               # Static files
│   ├── templates/            # Django templates
│   └── util/                 # Utility scripts
├── web/                      # Vue 3 frontend
│   └── src/
│       ├── api/              # API client modules
│       ├── components/       # Reusable Vue components
│       ├── layout/           # App layout (header, sidebar, nav)
│       ├── router/           # Vue Router config
│       ├── stores/           # Pinia state stores
│       ├── utils/            # Helper functions
│       └── views/            # Page components
├── docker-compose.yml        # Container deployment (not in repo root)
├── Makefile                 # Build scripts
└── scripts/                 # Utility scripts
```

## Backend Directory Purposes

**`backend/application/`:**
- Purpose: Django project configuration entry point
- Key files:
  - `settings.py`: Main Django settings (imports from `conf/env.py`)
  - `urls.py`: Root URL routing (includes all app URLs)
  - `asgi.py`: ASGI config for HTTP + WebSocket
  - `ws_routing.py`: WebSocket URL patterns
  - `celery.py`: Celery task configuration

**`backend/conf/`:**
- Purpose: Environment-specific configuration
- Key file: `env.py` - Contains DATABASE_*, REDIS_*, EMAIL_* settings
- This file contains credentials - DO NOT commit to version control

**`backend/apps/pisadmin/basicinfo/`:**
- Purpose: Master data for procurement (companies, currencies, suppliers, units)
- Structure:
  - `models.py`: Company, Currency, Supplier, SupplierUser, Unit, SystemNoRule, EmailNotice
  - `views/`: company.py, currency.py, supplier.py, unit.py, system_no_rule.py, email_template.py, email_utils.py
  - `urls.py`: Routes to views
  - `admin.py`: Django admin registration

**`backend/apps/pisadmin/miscprocurement/`:**
- Purpose: RFQ (Request for Quotation) and cost template management
- Structure:
  - `models.py`: Inquiry, InquirySupplier, InquiryAttachment, InquiryMaterialCost, InquiryProcessCost, InquiryOtherCost, InquiryProfitCost, InquiryRfqItem, CostEstimateTemplateHead, CostEstimateTemplateBody, MiscLowPriceHeader, MiscLowPriceDetail, MiscNegotiationRecords, RFQOperationLogs
  - `views.py`: ViewSets for all models (1500+ lines with complex workflow logic)
  - `serializers.py`: DRF serializers
  - `urls.py`: Routes to views
  - `cost_template_builder.py`: Template construction utility

**`backend/apps/pissupplier/`:**
- Purpose: Supplier quotation management (separate from pisadmin for supplier-facing access)
- Structure:
  - `models.py`: QuotationMaster, QuotationMaterial, QuotationProcess, QuotationOther, QuotationProfit, QuotationItem, QuotationAttachment
  - `views.py`: Quotation ViewSets
  - `serializers.py`: DRF serializers
  - `urls.py`: Routes to views

**`backend/dvadmin/system/`:**
- Purpose: Base RBAC system (users, roles, menus, departments, logs)
- Structure:
  - `models.py`: Users, Role, Menu, MenuButton, MenuField, FieldPermission, Dept, Post, OperationLog, LoginLog, SystemConfig, Dictionary, FileList, Area, ApiWhiteList, MessageCenter
  - `views/`: ViewSets for each model
  - `urls.py`: Routes to views
  - `fixtures/`: Initial data fixtures
  - `management/commands/`: Django commands (init, init_area, check_dept_users)

**`backend/dvadmin/utils/`:**
- Purpose: Reusable utilities for all apps
- Key files:
  - `viewset.py`: CustomModelViewSet base class with standardized responses
  - `models.py`: CoreModel, SoftDeleteModel base classes
  - `filters.py`: DataLevelPermissionMargeFilter, CoreModelFilterBankend
  - `permission.py`: CustomPermission class
  - `pagination.py`: CustomPagination class
  - `serializers.py`: Common serializer utilities
  - `exception.py`: Custom exception handler
  - `json_response.py`: SuccessResponse, DetailResponse, ErrorResponse wrappers

## Frontend Directory Purposes

**`web/src/api/`:**
- Purpose: API client modules
- Structure:
  - `login/index.ts`: Login/auth API
  - `menu/index.ts`: Menu/permission API
  - `miscprocurement/priceTemplate.ts`: Cost template API
  - `procurement/priceTemplate.ts`: (duplicate or alternative)

**`web/src/components/`:**
- Purpose: Reusable Vue components
- Key components:
  - `table/index.vue`: Custom table component with FastCRUD
  - `auth/auth*.vue`: Permission directive components
  - `fileSelector/`: File upload component
  - `foreignKey/`: Foreign key selector
  - `importExcel/`: Excel import component

**`web/src/layout/`:**
- Purpose: Application layout structure
- Subdirectories:
  - `component/`: aside.vue, header.vue, main.vue
  - `navBars/`: breadcrumb, tagsView, user menu
  - `navMenu/`: vertical and horizontal menu components
  - `main/`: classic, columns, defaults, transverse layout variants
  - `routerView/`: iframes, link, parent route views

**`web/src/router/`:**
- Purpose: Vue Router configuration
- Key files:
  - `index.ts`: Router creation, beforeEach guards, token validation
  - `route.ts`: Static and dynamic route definitions
  - `frontEnd.ts`: Frontend-controlled routing logic
  - `backEnd.ts`: Backend-controlled routing logic

**`web/src/stores/`:**
- Purpose: Pinia state management
- Key stores:
  - `userInfo.ts`: User authentication state
  - `frontendMenu.ts`: Menu tree cache
  - `themeConfig.ts`: UI theme settings
  - `tagsViewRoutes.ts`: Open tab tracking
  - `routesList.ts`: Available routes
  - `permission.ts`: Permission state

**`web/src/views/`:**
- Purpose: Page-level Vue components
- Structure mirrors backend apps:
  - `pisadmin/basicinfo/`: company, currency, supplier, unit, systemno, emailnotice
  - `pisadmin/miscprocurement/`: cost_template, misc_materials, misc_parts, misc_stations
  - `system/`: admin pages (dept, menu, role, user, dictionary, config, etc.)
  - `pissupplier/` (if exists): Supplier-facing pages

## Key Configuration File Locations

**Backend Configuration:**
- `backend/application/settings.py` - Main Django settings
- `backend/conf/env.py` - Environment variables (DB, Redis, Email)
- `backend/application/urls.py` - URL routing
- `backend/application/asgi.py` - ASGI/WebSocket config

**Frontend Configuration:**
- `web/src/settings.ts` - Frontend settings (API base URLs, app info)
- `web/src/main.ts` - Vue app initialization
- `web/src/App.vue` - Root Vue component
- `web/vite.config.ts` - Vite build configuration

**Environment/Secrets (DO NOT COMMIT):**
- `backend/conf/env.py` - Database, Redis, Email credentials
- `.env` files (if present)

## Custom Apps vs Base dvadmin Structure

**Base dvadmin (`dvadmin/`):**
- Provided by django-vue3-admin template
- Contains generic functionality: user management, role management, menu management, RBAC
- Should NOT be modified for custom business logic
- Extended by custom apps for domain-specific features

**Custom Apps (`apps/pisadmin/`, `apps/pissupplier/`):**
- `pisadmin`: Internal procurement admin (RFQ, cost templates, supplier master, etc.)
- `pissupplier`: Supplier portal (quotations)
- Custom apps import and extend dvadmin's `CustomModelViewSet`, `CoreModel`, `CustomPermission`
- Custom apps define their own models, serializers, views, urls

**Extension Pattern:**
```python
from dvadmin.utils.viewset import CustomModelViewSet

class InquiryViewSet(CustomModelViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    # Inherits: create, list, retrieve, update, destroy, multiple_delete, get_by_ids
    # Custom actions added via @action decorator
```

## Docker/Container Structure

The project uses Docker for deployment (docker-compose not present in current branch):

**Backend Container:**
- Based on Python 3.x
- Runs Django via uvicorn (ASGI)
- Port: 8000
- Depends on: MySQL, Redis

**Frontend Container:**
- Based on Node.js for build
- nginx for serving built SPA
- Port: 8080 (dev), 80 (prod)

**External Dependencies:**
- MySQL 8.0: Database (configured via `conf/env.py`)
- Redis: Caching and Celery broker
- SMTP: Email notifications

## Where to Add New Code

**New Model (Backend):**
1. Add to appropriate app's `models.py`
2. Inherit from `CoreModel`
3. Create serializer in `serializers.py`
4. Create ViewSet extending `CustomModelViewSet`
5. Add URL route in app's `urls.py`
6. Run migrations: `python manage.py makemigrations apps.<app>.<app>`
7. Apply: `python manage.py migrate`

**New API Endpoint (Backend):**
1. If CRUD: Add ViewSet method or use default actions
2. If custom: Add `@action` method to ViewSet
3. Register route in app `urls.py` with `router.register()`

**New Page (Frontend):**
1. Create Vue component in `web/src/views/<app>/<module>/`
2. Add API client in `web/src/api/<module>/`
3. Menu added via backend `Menu` model (not frontend route config)
4. Component uses FastCRUD pattern with custom table and form components

**New Store (Frontend):**
1. Create in `web/src/stores/modules/` or root stores
2. Use Pinia `defineStore`
3. Persist sensitive data to Session storage

---

*Structure analysis: 2026-04-01*
