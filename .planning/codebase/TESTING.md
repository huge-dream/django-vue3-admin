# Testing Patterns

**Analysis Date:** 2026-04-01

## Test Framework

### Backend (Python/Django)

**No dedicated test framework detected.**

- No `tests.py` files in Django apps
- No `pytest` configuration
- No `unittest` test suites
- Migrations are generated via `python manage.py makemigrations`

### Frontend (Vue 3/TypeScript)

**No test framework detected.**

- No Jest, Vitest, or other test runner configuration
- No `.test.ts`, `.spec.ts` files in `web/src/`
- Build and lint commands only, no test commands in `package.json`

## Test File Organization

### Backend Structure

```
backend/
├── application/          # Django settings
├── apps/
│   ├── pisadmin/         # Custom procurement app
│   │   ├── basicinfo/
│   │   │   ├── models.py
│   │   │   ├── views/
│   │   │   ├── urls.py
│   │   │   └── migrations/
│   │   └── miscprocurement/
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       └── migrations/
│   └── pissupplier/
└── dvadmin/              # Core RBAC system
```

**No `tests.py` directories or test files in application code.**

### Frontend Structure

```
web/
├── src/
│   ├── api/
│   ├── assets/
│   ├── components/
│   ├── directive/
│   ├── layout/
│   ├── plugin/
│   ├── router/
│   ├── stores/
│   ├── theme/
│   ├── types/
│   ├── utils/
│   ├── views/            # Page components
│   │   ├── pisadmin/
│   │   │   ├── basicinfo/
│   │   │   │   ├── company/
│   │   │   │   │   ├── index.vue
│   │   │   │   ├── api.ts
│   │   │   │   └── crud.tsx
│   │   │   └── miscprocurement/
│   │   │       ├── rfqmiscellaneous/
│   │   │       └── cost_template/
│   │   ├── pissupplier/
│   │   └── system/
│   ├── App.vue
│   └── main.ts
└── package.json
```

**No test files (`*.test.ts`, `*.spec.ts`) in `web/src/` directory.**

## Available Scripts

### Frontend (`web/package.json`)

```json
{
  "scripts": {
    "dev": "vite --force",
    "build:dev": "vite build --mode development",
    "build": "vite build",
    "build:local": "vite build --mode local_prod",
    "lint-fix": "eslint --fix --ext .js --ext .jsx --ext .vue src/",
    "build:flowH5": "vite build --config flowH5.config.ts"
  }
}
```

**No test-related scripts.**

### Backend

```bash
# Migrations
python manage.py makemigrations apps.pisadmin.apps.pisadmin
python manage.py makemigrations apps.pissupplier
python manage.py migrate

# Development server
python manage.py runserver 0.0.0.0:8000

# Production-like
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8
```

**No test commands.**

## CI/CD Pipeline

**No CI/CD configuration detected.**

- No GitHub Actions workflows (`.github/workflows/`)
- No `.gitlab-ci.yml`
- No Jenkinsfile
- Docker Compose present but no automated testing in Dockerfile

## Coverage

**No coverage tools configured.**

- No `coverage.py` configuration
- No `pytest-cov` or similar
- No Istanbul/nyc for frontend

## Manual Testing Approach

Based on project structure, manual testing likely involves:

### Backend API Testing

1. **Django Admin Interface** - Models registered in `admin.py` provide basic CRUD
2. **DRF Browsable API** - Available at `/api/` endpoints for interactive testing
3. **Direct HTTP requests** - Using curl or Postman

### Frontend Testing

1. **Browser testing** - Manual UI verification via `yarn dev`
2. **FastCRUD configuration** - CRUD options in `crud.tsx` files control behavior
3. **Vue DevTools** - For state inspection

## What Could Be Tested

### Backend

- **ViewSet endpoints**: Each ViewSet handles CRUD + custom actions
- **Serializer validation**: Input/output transformation
- **Model methods**: Business logic like `SystemNoRule.allocate_system_number()`
- **Transaction integrity**: Database operations wrapped in `transaction.atomic()`
- **Status workflow**: Inquiry state machine (open -> confirmed -> published -> quoting -> quote_ended -> bargaining -> negotiated -> approved -> awarded)

### Frontend

- **FastCRUD options**: Configuration in `createCrudOptions()`
- **API integration**: Request/response handling
- **Store actions**: Pinia store mutations
- **Router guards**: Authentication and authorization checks

## Recommendations for Testing Setup

### Backend

Add `pytest` with `pytest-django`:

```
# requirements.txt additions
pytest==7.4.0
pytest-django==4.5.0
pytest-cov==4.1.0
```

Create test files:
```
backend/apps/pisadmin/basicinfo/tests.py
backend/apps/pisadmin/miscprocurement/tests.py
```

### Frontend

Add Vitest for testing:

```bash
yarn add -D vitest @vue/test-utils jsdom
```

Add test script:
```json
{
  "scripts": {
    "test": "vitest",
    "coverage": "vitest run --coverage"
  }
}
```

Create test files:
```
web/src/views/pisadmin/basicinfo/company/__tests__/Company.spec.ts
```

## Build and Deployment

### Build Commands

**Frontend:**
```bash
cd web
yarn install
yarn build        # Production build
yarn build:dev    # Development build
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py init  # Create superuser
```

### Docker

The project uses Docker for deployment but no test containers.

---

*Testing analysis: 2026-04-01*
