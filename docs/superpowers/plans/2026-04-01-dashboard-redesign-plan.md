# Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement role-based buyer/supplier dashboard with unified API, real business data, and Vue 3 frontend components.

**Architecture:** Role-based data filtering via unified `/api/dashboard/` endpoint. Backend computes KPIs from Inquiry/QuotationMaster/Supplier tables. Frontend uses Pinia store with separate buyer/supplier state branches.

**Tech Stack:** Django REST Framework, Vue 3 + TypeScript + Pinia + ECharts

---

## Backend Implementation

### File Structure

**Create:**
- `backend/apps/pisadmin/dashboard/__init__.py`
- `backend/apps/pisadmin/dashboard/apps.py`
- `backend/apps/pisadmin/dashboard/urls.py`
- `backend/apps/pisadmin/dashboard/serializers.py`
- `backend/apps/pisadmin/dashboard/views.py`

**Modify:**
- `backend/application/urls.py` - add `path("api/pisadmin/dashboard/", include("apps.pisadmin.dashboard.urls"))`

---

### Task 1: Create Dashboard App Skeleton

- [ ] **Step 1: Create `backend/apps/pisadmin/dashboard/__init__.py`**
```python
```

- [ ] **Step 2: Create `backend/apps/pisadmin/dashboard/apps.py`**
```python
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pisadmin.dashboard'
```

- [ ] **Step 3: Create `backend/apps/pisadmin/dashboard/urls.py`**
```python
from django.urls import path
from .views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
```

- [ ] **Step 4: Register app in `backend/application/settings.py`**
Add `'apps.pisadmin.dashboard'` to `INSTALLED_APPS` list.

- [ ] **Step 5: Add URL to `backend/application/urls.py`**
Add `path("api/pisadmin/dashboard/", include("apps.pisadmin.dashboard.urls"))` to urlpatterns.

- [ ] **Step 6: Commit**
```bash
git add backend/apps/pisadmin/dashboard/ backend/application/urls.py backend/application/settings.py
git commit -m "feat(dashboard): create dashboard app skeleton with URL routing"
```

---

### Task 2: Implement Dashboard Serializers

- [ ] **Step 1: Write `backend/apps/pisadmin/dashboard/serializers.py`**

```python
from rest_framework import serializers


class BuyerKPISerializer(serializers.Serializer):
    total_inquiries = serializers.IntegerField()
    pending_inquiries = serializers.IntegerField()
    completed_quotes = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()


class BuyerTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    inquiry_no = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class SupplierKPISerializer(serializers.Serializer):
    total_quotes = serializers.IntegerField()
    pending_quotes = serializers.IntegerField()
    won_quotes = serializers.IntegerField()
    conversion_rate = serializers.FloatField()


class SupplierQuoteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    inquiry_no = serializers.CharField()
    item_name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit = serializers.CharField()
    deadline = serializers.DateTimeField()


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class TrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    count = serializers.IntegerField(required=False)
    quotes = serializers.IntegerField(required=False)
    won = serializers.IntegerField(required=False)


class BuyerDashboardSerializer(serializers.Serializer):
    kpi = BuyerKPISerializer()
    tasks = BuyerTaskSerializer(many=True)
    messages = MessageSerializer(many=True)
    trend = TrendSerializer(many=True)


class SupplierDashboardSerializer(serializers.Serializer):
    kpi = SupplierKPISerializer()
    pending_quotes = SupplierQuoteSerializer(many=True)
    messages = MessageSerializer(many=True)
    trend = TrendSerializer(many=True)


class DashboardResponseSerializer(serializers.Serializer):
    buyer = BuyerDashboardSerializer(allow_null=True)
    supplier = SupplierDashboardSerializer(allow_null=True)
```

- [ ] **Step 2: Commit**
```bash
git add backend/apps/pisadmin/dashboard/serializers.py
git commit -m "feat(dashboard): add dashboard serializers"
```

---

### Task 3: Implement Dashboard View

- [ ] **Step 1: Write `backend/apps/pisadmin/dashboard/views.py`**

```python
from datetime import timedelta

from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.pisadmin.miscprocurement.models import Inquiry
from apps.pissupplier.models import QuotationMaster
from apps.pisadmin.basicinfo.models import Supplier


def get_buyer_kpi(user):
    """采购方 KPI 计算"""
    total_inquiries = Inquiry.objects.filter(create_user=user.username).count()
    pending_inquiries = Inquiry.objects.filter(create_user=user.username, status__in=[1, 2, 3]).count()
    completed_quotes = QuotationMaster.objects.filter(
        inquiry_no__in=Inquiry.objects.filter(create_user=user.username).values('inquiry_no')
    ).count()
    total_suppliers = Supplier.objects.count()
    return {
        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'completed_quotes': completed_quotes,
        'total_suppliers': total_suppliers,
    }


def get_buyer_tasks(user):
    """采购方待办任务"""
    six_months_ago = timezone.now() - timedelta(days=180)
    inquiries = Inquiry.objects.filter(
        create_user=user.username,
        status__in=[1, 2, 3]
    ).order_by('-create_time')[:10]
    return [
        {
            'id': i.id,
            'title': i.title,
            'inquiry_no': i.inquiry_no,
            'status': dict(Inquiry.STATUS_CHOICES).get(i.status, str(i.status)),
            'created_at': i.create_time,
        }
        for i in inquiries
    ]


def get_supplier_kpi(user):
    """供应商 KPI 计算"""
    total_quotes = QuotationMaster.objects.filter(supplier_code=user.username).count()
    pending_quotes = QuotationMaster.objects.filter(supplier_code=user.username, status__in=[1, 2]).count()
    won_quotes = QuotationMaster.objects.filter(supplier_code=user.username, is_awarded=1).count()
    conversion_rate = (won_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    return {
        'total_quotes': total_quotes,
        'pending_quotes': pending_quotes,
        'won_quotes': won_quotes,
        'conversion_rate': round(conversion_rate, 2),
    }


def get_supplier_pending_quotes(user):
    """供应商待报价清单"""
    quotes = QuotationMaster.objects.filter(
        supplier_code=user.username,
        status__in=[1, 2]
    ).order_by('-creattime')[:10]
    result = []
    for q in quotes:
        inquiry = Inquiry.objects.filter(inquiry_no=q.inquiry_no).first()
        result.append({
            'id': q.autoid,
            'inquiry_no': q.inquiry_no,
            'item_name': inquiry.title if inquiry else '',
            'quantity': 0,
            'unit': '',
            'deadline': q.quote_deadline,
        })
    return result


def get_trend_data(user, is_buyer=True):
    """近6个月趋势数据"""
    six_months_ago = timezone.now() - timedelta(days=180)
    if is_buyer:
        data = (
            Inquiry.objects.filter(
                create_user=user.username,
                create_time__gte=six_months_ago
            )
            .annotate(month=TruncMonth('create_time'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
    else:
        data = (
            QuotationMaster.objects.filter(
                supplier_code=user.username,
                creattime__gte=six_months_ago
            )
            .annotate(month=TruncMonth('creattime'))
            .values('month')
            .annotate(quotes=Count('id'))
            .order_by('month')
        )
        # Add won counts
        result = []
        for d in data:
            won = QuotationMaster.objects.filter(
                supplier_code=user.username,
                creattime__month=d['month'].month,
                creattime__year=d['month'].year,
                is_awarded=1
            ).count()
            result.append({
                'month': d['month'].strftime('%Y-%m'),
                'quotes': d['quotes'],
                'won': won,
            })
        return result
    return [{'month': d['month'].strftime('%Y-%m'), 'count': d['count']} for d in data]


def get_messages(user):
    """消息通知 - 占位实现，后续接入通知系统"""
    return []


class DashboardView(APIView):
    """看板数据视图"""

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'buyer': None, 'supplier': None})

        # 判断用户角色
        # 这里需要根据实际角色系统判断，暂用用户名特征区分
        # 供应商用户：有 supplier_code 在 QuotationMaster 中
        has_supplier_role = QuotationMaster.objects.filter(supplier_code=user.username).exists()
        # 采购方用户：有 create_user 在 Inquiry 中
        has_buyer_role = Inquiry.objects.filter(create_user=user.username).exists()

        response_data = {'buyer': None, 'supplier': None}

        if has_buyer_role:
            response_data['buyer'] = {
                'kpi': get_buyer_kpi(user),
                'tasks': get_buyer_tasks(user),
                'messages': get_messages(user),
                'trend': get_trend_data(user, is_buyer=True),
            }

        if has_supplier_role:
            response_data['supplier'] = {
                'kpi': get_supplier_kpi(user),
                'pending_quotes': get_supplier_pending_quotes(user),
                'messages': get_messages(user),
                'trend': get_trend_data(user, is_buyer=False),
            }

        return Response(response_data)
```

- [ ] **Step 2: Commit**
```bash
git add backend/apps/pisadmin/dashboard/views.py
git commit -m "feat(dashboard): implement dashboard view with role-based data filtering"
```

---

## Frontend Implementation

### File Structure

**Create:**
- `web/src/api/pisadmin/dashboard.ts`
- `web/src/stores/modules/dashboard.ts`
- `web/src/views/pisadmin/dashboard/index.vue`
- `web/src/views/pisadmin/dashboard/BuyerDashboard.vue`
- `web/src/views/pisadmin/dashboard/SupplierDashboard.vue`
- `web/src/components/pisadmin/dashboard/KpiCard.vue`
- `web/src/components/pisadmin/dashboard/TrendChart.vue`
- `web/src/components/pisadmin/dashboard/MessageList.vue`
- `web/src/components/pisadmin/dashboard/BuyerTaskList.vue`
- `web/src/components/pisadmin/dashboard/SupplierQuoteList.vue`

**Modify:**
- `web/src/router/route.ts` - add dashboard routes

---

### Task 4: Create Frontend API and Store

- [ ] **Step 1: Create `web/src/api/pisadmin/dashboard.ts`**

```typescript
import request from '/@/utils/request';

export function getDashboard() {
  return request({
    url: '/api/pisadmin/dashboard/',
    method: 'get',
  });
}
```

- [ ] **Step 2: Create `web/src/stores/modules/dashboard.ts`**

```typescript
import { defineStore } from 'pinia';
import { getDashboard } from '/@/api/pisadmin/dashboard';

interface BuyerDashboard {
  kpi: {
    total_inquiries: number;
    pending_inquiries: number;
    completed_quotes: number;
    total_suppliers: number;
  } | null;
  tasks: Array<{
    id: number;
    title: string;
    inquiry_no: string;
    status: string;
    created_at: string;
  }>;
  messages: Array<{
    id: number;
    title: string;
    content: string;
    is_read: boolean;
    created_at: string;
  }>;
  trend: Array<{ month: string; count: number }>;
}

interface SupplierDashboard {
  kpi: {
    total_quotes: number;
    pending_quotes: number;
    won_quotes: number;
    conversion_rate: number;
  } | null;
  pending_quotes: Array<{
    id: number;
    inquiry_no: string;
    item_name: string;
    quantity: number;
    unit: string;
    deadline: string;
  }>;
  messages: Array<{
    id: number;
    title: string;
    content: string;
    is_read: boolean;
    created_at: string;
  }>;
  trend: Array<{ month: string; quotes: number; won: number }>;
}

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    buyer: null as BuyerDashboard | null,
    supplier: null as SupplierDashboard | null,
    loading: false,
  }),
  actions: {
    async fetchDashboard() {
      this.loading = true;
      try {
        const res: any = await getDashboard();
        this.buyer = res.data?.buyer || null;
        this.supplier = res.data?.supplier || null;
      } finally {
        this.loading = false;
      }
    },
  },
});
```

- [ ] **Step 3: Commit**
```bash
git add web/src/api/pisadmin/dashboard.ts web/src/stores/modules/dashboard.ts
git commit -m "feat(dashboard): add dashboard API and Pinia store"
```

---

### Task 5: Create Dashboard Components

- [ ] **Step 1: Create `web/src/components/pisadmin/dashboard/KpiCard.vue`**

```vue
<template>
  <el-card class="kpi-card" shadow="hover">
    <div class="kpi-content">
      <div class="kpi-icon" :style="{ background: iconBg }">
        <i :class="icon" :style="{ color: iconColor }"></i>
      </div>
      <div class="kpi-info">
        <div class="kpi-value">{{ value }}</div>
        <div class="kpi-label">{{ label }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  value: number | string;
  label: string;
  icon: string;
  iconBg?: string;
  iconColor?: string;
}>();
</script>

<style scoped lang="scss">
.kpi-card {
  border-radius: 12px;
  .kpi-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .kpi-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    i {
      font-size: 28px;
    }
  }
  .kpi-info {
    .kpi-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--el-text-color-primary);
    }
    .kpi-label {
      font-size: 14px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }
}
</style>
```

- [ ] **Step 2: Create `web/src/components/pisadmin/dashboard/TrendChart.vue`**

```vue
<template>
  <div ref="chartRef" class="trend-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  data: Array<{ month: string; count?: number; quotes?: number; won?: number }>;
  type: 'buyer' | 'supplier';
}>();

const chartRef = ref();

function initChart() {
  if (!chartRef.value) return;
  const chart = echarts.init(chartRef.value);

  const xData = props.data.map(d => d.month);

  if (props.type === 'buyer') {
    const yData = props.data.map(d => d.count || 0);
    chart.setOption({
      title: { text: '业务趋势', left: 'left' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: xData },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        data: yData,
        smooth: true,
        areaStyle: { opacity: 0.3 },
      }],
    });
  } else {
    const quotesData = props.data.map(d => d.quotes || 0);
    const wonData = props.data.map(d => d.won || 0);
    chart.setOption({
      title: { text: '报价与中标趋势', left: 'left' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['报价数', '中标数'], right: 0 },
      xAxis: { type: 'category', data: xData },
      yAxis: { type: 'value' },
      series: [
        { name: '报价数', type: 'line', data: quotesData, smooth: true },
        { name: '中标数', type: 'line', data: wonData, smooth: true },
      ],
    });
  }
}

onMounted(initChart);
watch(() => props.data, initChart);
</script>

<style scoped lang="scss">
.trend-chart {
  width: 100%;
  height: 300px;
}
</style>
```

- [ ] **Step 3: Create `web/src/components/pisadmin/dashboard/MessageList.vue`**

```vue
<template>
  <div class="message-list">
    <div v-for="msg in messages" :key="msg.id" class="message-item">
      <el-badge :is-dot="!msg.is_read" class="message-badge">
        <div class="message-content">
          <div class="message-title">{{ msg.title }}</div>
          <div class="message-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </el-badge>
    </div>
    <el-empty v-if="messages.length === 0" description="暂无消息" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  messages: Array<{
    id: number;
    title: string;
    content: string;
    is_read: boolean;
    created_at: string;
  }>;
}>();

function formatTime(time: string) {
  if (!time) return '';
  return new Date(time).toLocaleDateString();
}
</script>

<style scoped lang="scss">
.message-list {
  .message-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    &:last-child { border-bottom: none; }
  }
  .message-content {
    .message-title {
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
    .message-time {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }
}
</style>
```

- [ ] **Step 4: Create `web/src/components/pisadmin/dashboard/BuyerTaskList.vue`**

```vue
<template>
  <el-table :data="tasks" stripe style="width: 100%">
    <el-table-column prop="inquiry_no" label="询价单号" width="120" />
    <el-table-column prop="title" label="标题" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="创建时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.created_at) }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
defineProps<{
  tasks: Array<{
    id: number;
    title: string;
    inquiry_no: string;
    status: string;
    created_at: string;
  }>;
}>();

function getStatusType(status: string) {
  const map: Record<string, string> = {
    '开立': 'info',
    '确认': 'warning',
    '发布': 'primary',
    '报价中': 'success',
  };
  return map[status] || 'info';
}

function formatDate(date: string) {
  if (!date) return '';
  return new Date(date).toLocaleString();
}
</script>
```

- [ ] **Step 5: Create `web/src/components/pisadmin/dashboard/SupplierQuoteList.vue`**

```vue
<template>
  <el-table :data="quotes" stripe style="width: 100%">
    <el-table-column prop="inquiry_no" label="询价单号" width="120" />
    <el-table-column prop="item_name" label="产品名称" />
    <el-table-column prop="quantity" label="数量" width="80" />
    <el-table-column prop="unit" label="单位" width="80" />
    <el-table-column prop="deadline" label="报价截止时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.deadline) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="100" fixed="right">
      <template #default="{ row }">
        <el-button type="primary" link @click="$emit('quote', row)">去报价</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
defineProps<{
  quotes: Array<{
    id: number;
    inquiry_no: string;
    item_name: string;
    quantity: number;
    unit: string;
    deadline: string;
  }>;
}>();

defineEmits(['quote']);

function formatDate(date: string) {
  if (!date) return '';
  return new Date(date).toLocaleString();
}
</script>
```

- [ ] **Step 6: Commit**
```bash
git add web/src/components/pisadmin/dashboard/ web/src/api/pisadmin/dashboard.ts web/src/stores/modules/dashboard.ts
git commit -m "feat(dashboard): add dashboard Vue components"
```

---

### Task 6: Create Dashboard Pages

- [ ] **Step 1: Create `web/src/views/pisadmin/dashboard/index.vue`**

```vue
<template>
  <div class="dashboard-index">
    <BuyerDashboard v-if="hasBuyerRole && !hasSupplierRole" />
    <SupplierDashboard v-else-if="hasSupplierRole && !hasBuyerRole" />
    <div v-else-if="hasBothRoles" class="role-select">
      <el-radio-group v-model="currentRole">
        <el-radio-button label="buyer">采购方看板</el-radio-button>
        <el-radio-button label="supplier">供应商看板</el-radio-button>
      </el-radio-group>
      <BuyerDashboard v-if="currentRole === 'buyer'" />
      <SupplierDashboard v-else />
    </div>
    <el-empty v-else description="您暂无看板权限" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import BuyerDashboard from './BuyerDashboard.vue';
import SupplierDashboard from './SupplierDashboard.vue';

const store = useDashboardStore();
const { buyer, supplier } = storeToRefs(store);

const currentRole = ref('buyer');

const hasBuyerRole = computed(() => !!buyer.value);
const hasSupplierRole = computed(() => !!supplier.value);
const hasBothRoles = computed(() => hasBuyerRole.value && hasSupplierRole.value);

store.fetchDashboard();
</script>

<style scoped lang="scss">
.dashboard-index {
  padding: 20px;
  .role-select {
    .el-radio-group {
      margin-bottom: 20px;
    }
  }
}
</style>
```

- [ ] **Step 2: Create `web/src/views/pisadmin/dashboard/BuyerDashboard.vue`**

```vue
<template>
  <div class="buyer-dashboard">
    <div class="header">
      <h2>采购方看板</h2>
      <span class="date">{{ currentDate }}</span>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_inquiries"
          label="询价单总数"
          icon="fa fa-file-text-o"
          icon-bg="#e6f7ff"
          icon-color="#1890ff"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.pending_inquiries"
          label="待报价询价单"
          icon="fa fa-clock-o"
          icon-bg="#fff7e6"
          icon-color="#fa8c16"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.completed_quotes"
          label="已完成报价"
          icon="fa fa-check-circle-o"
          icon-bg="#f6ffed"
          icon-color="#52c41a"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_suppliers"
          label="供应商总数"
          icon="fa fa-building-o"
          icon-bg="#f9f0ff"
          icon-color="#722ed1"
        />
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-row :gutter="16" class="main-row">
      <el-col :span="12">
        <el-card title="待办任务">
          <template #header>
            <span>待办任务</span>
          </template>
          <BuyerTaskList :tasks="tasks" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>业务趋势</span>
          </template>
          <TrendChart :data="trend" type="buyer" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Messages -->
    <el-card class="message-card">
      <template #header>
        <span>消息通知</span>
      </template>
      <MessageList :messages="messages" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import KpiCard from '/@/components/pisadmin/dashboard/KpiCard.vue';
import TrendChart from '/@/components/pisadmin/dashboard/TrendChart.vue';
import MessageList from '/@/components/pisadmin/dashboard/MessageList.vue';
import BuyerTaskList from '/@/components/pisadmin/dashboard/BuyerTaskList.vue';

const store = useDashboardStore();
const { buyer } = storeToRefs(store);

const kpi = computed(() => buyer.value?.kpi || {
  total_inquiries: 0,
  pending_inquiries: 0,
  completed_quotes: 0,
  total_suppliers: 0,
});
const tasks = computed(() => buyer.value?.tasks || []);
const trend = computed(() => buyer.value?.trend || []);
const messages = computed(() => buyer.value?.messages || []);

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
</script>

<style scoped lang="scss">
.buyer-dashboard {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    h2 { margin: 0; }
    .date { color: var(--el-text-color-secondary); }
  }
  .kpi-row { margin-bottom: 16px; }
  .main-row { margin-bottom: 16px; }
  .message-card { margin-top: 16px; }
}
</style>
```

- [ ] **Step 3: Create `web/src/views/pisadmin/dashboard/SupplierDashboard.vue`**

```vue
<template>
  <div class="supplier-dashboard">
    <div class="header">
      <h2>供应商看板</h2>
      <span class="date">{{ currentDate }}</span>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_quotes"
          label="报价单总数"
          icon="fa fa-file-text-o"
          icon-bg="#e6f7ff"
          icon-color="#1890ff"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.pending_quotes"
          label="待报价"
          icon="fa fa-clock-o"
          icon-bg="#fff7e6"
          icon-color="#fa8c16"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.won_quotes"
          label="已中标"
          icon="fa fa-trophy"
          icon-bg="#f6ffed"
          icon-color="#52c41a"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.conversion_rate + '%'"
          label="中标率"
          icon="fa fa-percent"
          icon-bg="#f9f0ff"
          icon-color="#722ed1"
        />
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-row :gutter="16" class="main-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待报价清单</span>
          </template>
          <SupplierQuoteList :quotes="pendingQuotes" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>报价与中标趋势</span>
          </template>
          <TrendChart :data="trend" type="supplier" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Messages -->
    <el-card class="message-card">
      <template #header>
        <span>消息通知</span>
      </template>
      <MessageList :messages="messages" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import KpiCard from '/@/components/pisadmin/dashboard/KpiCard.vue';
import TrendChart from '/@/components/pisadmin/dashboard/TrendChart.vue';
import MessageList from '/@/components/pisadmin/dashboard/MessageList.vue';
import SupplierQuoteList from '/@/components/pisadmin/dashboard/SupplierQuoteList.vue';

const store = useDashboardStore();
const { supplier } = storeToRefs(store);

const kpi = computed(() => supplier.value?.kpi || {
  total_quotes: 0,
  pending_quotes: 0,
  won_quotes: 0,
  conversion_rate: 0,
});
const pendingQuotes = computed(() => supplier.value?.pending_quotes || []);
const trend = computed(() => supplier.value?.trend || []);
const messages = computed(() => supplier.value?.messages || []);

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
</script>

<style scoped lang="scss">
.supplier-dashboard {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    h2 { margin: 0; }
    .date { color: var(--el-text-color-secondary); }
  }
  .kpi-row { margin-bottom: 16px; }
  .main-row { margin-bottom: 16px; }
  .message-card { margin-top: 16px; }
}
</style>
```

- [ ] **Step 4: Commit**
```bash
git add web/src/views/pisadmin/dashboard/
git commit -m "feat(dashboard): add buyer/supplier dashboard pages"
```

---

### Task 7: Add Dashboard Routes

- [ ] **Step 1: Modify `web/src/router/route.ts`**

Add to `dynamicRoutes` array:
```typescript
{
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('/@/views/pisadmin/dashboard/index.vue'),
  meta: {
    title: 'message.router.dashboard',
    isLink: '',
    isHide: false,
    isKeepAlive: true,
    isAffix: false,
    isIframe: false,
    icon: 'iconfont icon-dashboard',
  },
},
```

- [ ] **Step 2: Commit**
```bash
git add web/src/router/route.ts
git commit -m "feat(dashboard): add dashboard route"
```

---

## Verification Checklist

- [ ] Backend: `GET /api/pisadmin/dashboard/` returns correct data structure
- [ ] Backend: Role-based filtering works (buyer only, supplier only, both)
- [ ] Frontend: Dashboard page loads without errors
- [ ] Frontend: KPI cards display correct data
- [ ] Frontend: Trend charts render correctly
- [ ] Frontend: Task/Quote lists display correctly
- [ ] Frontend: Role switching works for users with both roles
