# Architecture

**Analysis Date:** 2026-04-01

## Pattern Overview

**Overall:** Django REST Framework backend with Vue 3 SPA frontend, built on django-vue3-admin base

**Key Characteristics:**
- Backend uses Django 4.2 with DRF for API-first design
- Frontend is Vue 3 + TypeScript + Vite SPA
- JWT authentication via SimpleJWT
- Real-time support via Django Channels (WebSocket)
- Backend-controlled routing (menu/permissions served via API)
- Custom apps extend dvadmin base RBAC system

## Layers

**Django Application Layer:**
- Purpose: Main Django project configuration and URL routing
- Location: `backend/application/`
- Contains: `settings.py` (imports config from `conf/env.py`), `urls.py`, `asgi.py`, `wsgi.py`, `celery.py`
- Depends on: All Django apps
- Used by: uvicorn/ASGI server

**Custom Business Apps Layer (pisadmin, pissupplier):**
- Purpose: Procurement and supplier quotation business logic
- Location: `backend/apps/pisadmin/` and `backend/apps/pissupplier/`
- Contains: Models, Views (ViewSets), Serializers, URLs for procurement RFQ, cost templates, suppliers
- Depends on: dvadmin utils, Django REST Framework
- Used by: Frontend SPA via REST API

**dvadmin Core Layer:**
- Purpose: Base RBAC system - users, roles, menus, departments, permissions
- Location: `backend/dvadmin/system/`
- Contains: Auth models (Users, Roles, Menus), views, serializers
- Depends on: Django contrib apps
- Used by: Custom apps, frontend

**dvadmin Utils Layer:**
- Purpose: Reusable utilities - CustomModelViewSet, filters, permissions, pagination, exception handling
- Location: `backend/dvadmin/utils/`
- Contains: `viewset.py` (CustomModelViewSet base), `filters.py`, `permission.py`, `pagination.py`, `serializers.py`
- Depends on: Django REST Framework
- Used by: All ViewSets across apps

**Frontend SPA Layer:**
- Purpose: Vue 3 single-page application for UI
- Location: `web/src/`
- Contains: Components, views, stores (Pinia), router, API clients
- Depends on: Vue 3, Element Plus, FastCRUD, Pinia, Vue Router

## Data Flow

**Frontend-to-Backend API Flow:**

```
Vue Component (Page)
    -> Pinia Store (State Management)
    -> API Client (src/api/*/index.ts)
    -> HTTP Request (Axios wrapper)
    -> Django REST Framework ViewSet
    -> Django Serializer (Validation)
    -> Django Model (Database)
    -> Database Response
    -> Serializer Response
    -> JSON API Response
    -> Pinia Store Update
    -> Vue Component Re-render
```

**Authentication Flow:**

```
Login Page -> POST /api/login/ -> JWT Token Response
    -> Token stored in Session storage
    -> All subsequent requests include JWT header
    -> Backend validates JWT, attaches user to request
    -> Permission classes check role/menu permissions
```

**Menu/Routing Flow (Backend-Controlled):**

```
User Login -> GET /api/system/get_menu/
    -> Returns user-specific menu tree from Menu model
    -> Frontend builds routes dynamically
    -> Cached in frontendMenu store
```

**WebSocket Flow:**

```
Frontend connects to /ws/<service_uid>/
    -> Django Channels AuthMiddlewareStack validates JWT
    -> URLRouter routes to MegCenter consumer
    -> Consumer handles real-time messaging
```

## Key Design Patterns

**CustomModelViewSet Pattern:**
All custom ViewSets inherit from `dvadmin.utils.viewset.CustomModelViewSet` which extends DRF's `ModelViewSet`. This provides:
- Standardized JSON responses (`SuccessResponse`, `DetailResponse`, `ErrorResponse`)
- Automatic filtering with `DataLevelPermissionMargeFilter` (data scope permissions)
- Field-level permissions via `FieldPermission` model
- Import/export mixins
- Custom serializer selection per action (`create_serializer_class`, `update_serializer_class`)

**CoreModel Pattern:**
All models inherit from `dvadmin.utils.models.CoreModel` which provides:
- Audit fields: `creator`, `modifier`, `dept_belong_id`, `create_datetime`, `update_datetime`
- Auto-setting creator/modifier on create/update
- `SoftDeleteModel` support for soft deletes

**Status Workflow Pattern (Inquiry/RFQ):**
The `Inquiry` model uses a status field with workflow transitions:
```
1(开立) -> 2(确认) -> 3(发布) -> 4(报价中) -> 5(报价结束)
                                                       -> 6(比议价中) -> 7(价格审核) -> 8(核价通过)
9(落标结束) or 0(作废)
```
Each transition is handled by a dedicated `@action` method on the ViewSet.

**Template-Generated Quotation Pattern:**
- `CostEstimateTemplateHead` + `CostEstimateTemplateBody` define a cost structure template
- When Inquiry is published, `_create_supplier_quotations` iterates the template to generate `QuotationMaster` + child tables for each supplier
- Template fields with `is_computed=1` or `supplier_required in (1,2)` are prefilled in quotations

## Module Responsibilities

**pisadmin.miscprocurement:**
- `Inquiry`: RFQ (Request for Quotation) master with workflow states
- `InquirySupplier`: Supplier invite list per RFQ
- `InquiryMaterialCost`, `InquiryProcessCost`, `InquiryOtherCost`, `InquiryProfitCost`: Cost breakdown per RFQ line item
- `InquiryRfqItem`: Upper-level material items for the RFQ
- `CostEstimateTemplateHead/Body`: Cost template structure definition
- `MiscLowPriceHeader/Detail`: Comparison price records (lowest price tracking)
- `MiscNegotiationRecords`: Bargaining records
- `RFQOperationLogs`: Audit trail for RFQ operations

**pisadmin.basicinfo:**
- `Company`: Company/factory information
- `Currency`: Currency and tax rate configuration
- `Supplier`: Supplier master data
- `SupplierUser`: Supplier user accounts
- `Unit`: Measurement units
- `SystemNoRule`: Document numbering rules (e.g., RFQ numbers, quotation numbers)
- `EmailNotice`: Email notification queue

**pissupplier:**
- `QuotationMaster`: Supplier quotation header
- `QuotationMaterial`, `QuotationProcess`, `QuotationOther`, `QuotationProfit`: Quotation cost lines
- `QuotationItem`: Upper-level product items in quotation
- `QuotationAttachment`: Quotation attachments

**dvadmin.system:**
- `Users`: User accounts with role/dept associations
- `Role`: Role definitions with permission keys
- `Menu`: Menu tree for UI and permission routing
- `MenuButton`: Button-level permissions on menus
- `MenuField`: Field-level permissions per model
- `Dept`: Department hierarchy
- `FieldPermission`: Role-field permission matrix
- `RoleMenuPermission`, `RoleMenuButtonPermission`: Role-menu assignments
- `OperationLog`, `LoginLog`: Audit logging
- `SystemConfig`: System configuration key-value store
- `Dictionary`: Dropdown value definitions
- `FileList`: File upload management
- `ApiWhiteList`: Public API endpoints bypassing auth

## Error Handling

**Backend Exception Handling:**
- Custom exception handler: `dvadmin.utils.exception.CustomExceptionHandler`
- DRF exceptions caught and formatted to standard JSON response
- Validation errors return 400 with field-specific messages

**Frontend Error Handling:**
- Axios interceptor catches HTTP errors
- 401 redirects to login
- 403 shows permission denied
- 500 shows generic error message
- API errors display returned `msg` field

## Cross-Cutting Concerns

**Authentication:** SimpleJWT with 24-hour access tokens, 1-day refresh tokens. `CustomBackend` allows username OR email login.

**Authorization:**
- Menu-level via `Menu` model and role assignments
- Button-level via `MenuButton` and `RoleMenuButtonPermission`
- Field-level via `MenuField` and `FieldPermission`
- Data scope via `DataLevelPermissionMargeFilter` (dept-based filtering)

**Logging:**
- API access logged via `ApiLoggingMiddleware`
- Operation logs stored in `OperationLog` model
- RFQ operations logged to `RFQOperationLogs`

**Validation:**
- Serializer-level validation in DRF
- Custom validators in `dvadmin.utils.validator`
- Business logic validation in ViewSet methods (e.g., workflow state checks)

---

*Architecture analysis: 2026-04-01*
