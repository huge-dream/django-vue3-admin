# Coding Conventions

**Analysis Date:** 2026-04-01

## Naming Patterns

### Backend (Python/Django)

**Files:**
- Python source files: snake_case (e.g., `email_utils.py`, `system_no_rule.py`)
- URL routing: `urls.py`
- Serializers: `serializers.py`
- Models: `models.py`
- Views: either single `views.py` or organized in `views/` directory with one file per resource

**Classes:**
- Models: PascalCase (e.g., `Company`, `Supplier`, `SystemNoRule`)
- ViewSets: PascalCase ending with `ViewSet` (e.g., `CompanyViewSet`, `InquiryViewSet`)
- Serializers: PascalCase ending with `Serializer` (e.g., `CompanySerializer`, `InquirySerializer`)
- Custom serializers for create/update: `ModelNameCreateUpdateSerializer`

**Functions/Methods:**
- snake_case (e.g., `allocate_system_number`, `get_request_username`)
- Private methods: prefixed with underscore (e.g., `_allocate_next_code_for_locked_rule`)

**Database Fields:**
- snake_case (e.g., `company_code`, `supplier_name`, `create_datetime`)
- Primary key: `id`
- Foreign keys: `model_name_id` or just `field_name` (e.g., `quotation_no`)
- Timestamps: `create_datetime`, `update_datetime`
- User tracking: `createuser`, `updateuser` (char fields, not FK)

**URL Patterns:**
- Router.register uses snake_case plural (e.g., `r'units'`, `r'companies'`, `r'inquiry'`)
- Full endpoint example: `/api/pisadmin/basicinfo/companies/`

### Frontend (Vue 3/TypeScript)

**Files:**
- Vue components: kebab-case in directory (e.g., `company/index.vue`)
- API modules: `api.ts` in same directory (e.g., `company/api.ts`)
- CRUD configuration: `.tsx` extension (e.g., `company/crud.tsx`)
- Stores: `userInfo.ts`, `dictionary.ts`
- Utilities: `service.ts`, `storage.ts`, `message.ts`

**Components:**
- Vue components use `<script setup lang="ts">` with Composition API
- Component name via `name` attribute (e.g., `name="CompanyMaintenance"`)
- Router names: PascalCase with dots (e.g., `PisadminRfqMiscInquiryDetail`)

**TypeScript:**
- Interfaces defined in stores/interface (e.g., `UserInfosStates`)
- Props: camelCase
- Events: camelCase

## Code Style

### Backend

**Formatting:**
- Python 3 with `from __future__ import annotations` for forward references
- UTF-8 encoding declared: `# -*- coding: utf-8 -*-`
- Indentation: 4 spaces
- Max line length: typically 120 characters (project standard)

**Import Organization:**
```python
# Standard library
from django.db import models, transaction
from django.utils import timezone
# Third-party
from rest_framework import serializers
# Local application
from dvadmin.utils.models import CoreModel, table_prefix
from apps.pisadmin.basicinfo.models import Company
```

**Django Patterns:**
- Models inherit from `CoreModel` (provides id, create_datetime, update_datetime, creator, modifier)
- ViewSets inherit from `CustomModelViewSet` (dvadmin base)
- Serializers inherit from `CustomModelSerializer` (dvadmin base)
- Use `table_prefix` from dvadmin for db_table names
- Use `select_for_update()` for row-level locking in transactions

**DRF Patterns:**
```python
class CompanyViewSet(CustomModelViewSet):
    """公司信息管理接口"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    create_serializer_class = CompanyCreateUpdateSerializer
    update_serializer_class = CompanyCreateUpdateSerializer
    search_fields = ["company_code", "company_name", "company_short_name"]
    ordering = ["-create_datetime"]
```

**Serializer Patterns:**
```python
class CompanySerializer(CustomModelSerializer):
    """公司信息-序列化器"""
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id"]

class CompanyCreateUpdateSerializer(CustomModelSerializer):
    """公司信息 创建/更新"""
    company_code = serializers.CharField(max_length=20)
```

**Custom Actions:**
```python
@action(methods=["put"], detail=True)
def confirm(self, request, pk=None):
    """确认操作"""
    instance = self.get_object()
    # ... logic
    return DetailResponse(data=serializer.data, msg="success")
```

**Response Patterns:**
- `DetailResponse` for single object responses
- `SuccessResponse` for list/delete success
- `ErrorResponse` for error cases

### Frontend

**Formatting (Prettier):**
- Print width: 150 characters
- Tab width: 2 spaces
- Single quotes for strings
- Trailing commas: ES5
- Semicolons: yes
- End of line: LF

**Import Organization (ESLint):**
```typescript
// Vue/libraries
import { ref, onMounted } from 'vue'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
// Project imports
import * as api from './api'
import { useUserInfo } from '/@/stores/userInfo'
// Element Plus
import { ElMessage } from 'element-plus'
```

**Path Aliases:**
- `@/` maps to `src/` (e.g., `/@/utils/service`)
- Absolute imports use these aliases

**Vue Component Patterns:**
```vue
<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script setup lang="ts" name="CompanyMaintenance">
import { ref, onMounted } from 'vue'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

const { crudOptions } = createCrudOptions({ crudExpose })
useCrud({ crudExpose, crudOptions })

onMounted(() => {
  crudExpose?.doRefresh()
})
</script>

<style scoped></style>
```

**FastCRUD Configuration Pattern:**
```typescript
export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  return {
    crudOptions: {
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => api.AddObj(form),
        editRequest: async ({ form, row }) => api.UpdateObj({ ...form, id: row.id }),
        delRequest: async ({ row }) => api.DelObj(row.id)
      },
      columns: {
        company_code: {
          title: '公司代码',
          type: 'input',
          search: { show: true },
          form: { rules: [{ required: true, message: '请输入公司代码' }] }
        }
      }
    }
  }
}
```

**API Module Pattern:**
```typescript
// /@/utils/service exports `request`
import { request } from '/@/utils/service'

const apiPrefix = '/api/pisadmin/basicinfo/companies/'

export const GetList = (params: any) => request({ url: apiPrefix, method: 'get', params })
export const AddObj = (data: any) => request({ url: apiPrefix, method: 'post', data })
export const UpdateObj = (data: any) => request({ url: apiPrefix + data.id + '/', method: 'put', data })
export const DelObj = (id: string | number) => request({ url: apiPrefix + id + '/', method: 'delete' })
```

**Pinia Store Pattern:**
```typescript
export const useUserInfo = defineStore('userInfo', {
  state: (): UserInfosStates => ({
    userInfos: { /* initial state */ }
  }),
  actions: {
    async setUserInfos() { /* action */ }
  }
})
```

## Linting and Formatting Configuration

### Frontend (ESLint)

**Config File:** `web/.eslintrc.js`

**Parser:** `vue-eslint-parser` with `@typescript-eslint/parser`

**Key Rules:**
- `@typescript-eslint/no-unused-vars`: `'off'` (disabled)
- `@typescript-eslint/no-explicit-any`: `'off'` (disabled)
- `no-console`: `'error'` (console.log is error, use ElMessage instead)
- Vue component rules mostly `'off'` for flexibility

**Run Lint Fix:**
```bash
yarn lint-fix
```

### Frontend (Prettier)

**Config File:** `web/.prettierrc.js`

**Key Settings:**
```javascript
{
  printWidth: 150,
  tabWidth: 2,
  useTabs: false,
  semi: true,
  singleQuote: true,
  trailingComma: 'es5',
  bracketSpacing: true,
  arrowParens: 'always',
  endOfLine: 'lf'
}
```

### Backend (Python)

No explicit Python linting configuration detected. Python code follows PEP 8 implicitly.

## Error Handling

### Backend

- Use `try/except` blocks with specific exception handling
- Use `serializers.ValidationError` for API validation errors
- Use `ErrorResponse` from dvadmin for consistent error responses
- Log errors with `logger = logging.getLogger(__name__)`

### Frontend

- Use `ElMessage.error()` for user-facing error messages
- Use try/catch with async/await
- API errors handled in `service.ts` interceptors

## Logging

### Backend
```python
import logging
logger = logging.getLogger(__name__)

logger.warning("message with %s", value)
logger.exception("error message")  # includes traceback
```

### Frontend
- `console.log` allowed for debugging (stripped in production build)
- Production uses `ElMessage` for user feedback
- No structured logging library detected

## Comments and Documentation

### Backend
- Chinese docstrings for business logic (e.g., `"""公司信息-序列化器"""`)
- Complex methods have inline comments explaining logic
- Use `# pragma: no cover` for untested branches

### Frontend
- Component `name` attribute for debugging
- Chinese comments for complex business logic
- JSDoc style not strictly enforced

---

*Convention analysis: 2026-04-01*
