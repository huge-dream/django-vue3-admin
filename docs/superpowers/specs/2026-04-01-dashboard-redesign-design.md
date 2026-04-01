# 控制台看板重构设计文档

## 1. 概述

### 1.1 背景
当前系统首页使用硬编码模拟数据，需要重构为真实业务数据看板。

### 1.2 目标
- 区分采购方看板和供应商看板两种视图
- 基于用户角色动态返回对应的看板数据
- 后端提供统一 API，前端按角色渲染

### 1.3 设计图
- 采购方看板：`D:\AVC-PROJECT\docs\采购方看板.png`
- 供应商看板：`D:\AVC-PROJECT\docs\供应商看板.png`

---

## 2. API 设计

### 2.1 接口信息

| 项目 | 值 |
|------|-----|
| 方法 | GET |
| 路径 | `/api/dashboard/` |
| 认证 | JWT Token |
| 响应格式 | JSON |

### 2.2 响应结构

```json
{
  "buyer": {
    "kpi": {
      "total_inquiries": 0,
      "pending_inquiries": 0,
      "completed_quotes": 0,
      "total_suppliers": 0
    },
    "tasks": [
      {
        "id": 0,
        "title": "string",
        "inquiry_no": "string",
        "status": "string",
        "created_at": "datetime"
      }
    ],
    "messages": [
      {
        "id": 0,
        "title": "string",
        "content": "string",
        "is_read": false,
        "created_at": "datetime"
      }
    ],
    "trend": [
      {"month": "2026-01", "count": 0}
    ]
  },
  "supplier": {
    "kpi": {
      "total_quotes": 0,
      "pending_quotes": 0,
      "won_quotes": 0,
      "conversion_rate": 0.0
    },
    "pending_quotes": [
      {
        "id": 0,
        "inquiry_no": "string",
        "item_name": "string",
        "quantity": 0,
        "unit": "string",
        "deadline": "datetime"
      }
    ],
    "messages": [],
    "trend": [
      {"month": "2026-01", "quotes": 0, "won": 0}
    ]
  }
}
```

### 2.3 业务规则
- 用户同时有采购方和供应商角色：两个模块都返回
- 用户只有采购方角色：只返回 `buyer` 模块，`supplier` 为 `null`
- 用户只有供应商角色：只返回 `supplier` 模块，`buyer` 为 `null`

---

## 3. 后端实现

### 3.1 应用位置
新建 `backend/apps/pisadmin/dashboard/` 应用

### 3.2 数据来源

**采购方 KPI 计算：**
| 指标 | 数据来源 |
|------|----------|
| total_inquiries | Inquiry 表中当前用户创建的记录数 |
| pending_inquiries | Inquiry 状态为"待报价"的记录数 |
| completed_quotes | QuotationMaster 中已报价的记录数 |
| total_suppliers | Supplier 表总数 |

**供应商 KPI 计算：**
| 指标 | 数据来源 |
|------|----------|
| total_quotes | QuotationMaster 中属于当前供应商的记录数 |
| pending_quotes | QuotationMaster 状态为"待报价"的记录数 |
| won_quotes | QuotationMaster 状态为"已中标"的记录数 |
| conversion_rate | won_quotes / total_quotes * 100 |

**待办任务（采购方）：**
- 查询条件：Inquiry 状态为"待处理"，分配给当前用户

**待报价清单（供应商）：**
- 查询条件：QuotationMaster 状态为"待报价"，属于当前供应商

**消息通知：**
- 使用现有通知表，按时间倒序取最新 5 条

**趋势图数据：**
- 近 6 个月的记录创建数，按月聚合

### 3.3 序列化器

```python
# dashboard/serializers.py
class BuyerKPISerializer(serializers.Serializer): ...
class SupplierKPISerializer(serializers.Serializer): ...
class BuyerTaskSerializer(serializers.ModelSerializer): ...
class SupplierQuoteSerializer(serializers.ModelSerializer): ...
class MessageSerializer(serializers.ModelSerializer): ...
class TrendSerializer(serializers.Serializer): ...
class DashboardResponseSerializer(serializers.Serializer): ...
```

### 3.4 视图

```python
# dashboard/views.py
class DashboardView(APIView):
    def get(self, request):
        # 根据用户角色过滤返回数据
        ...
```

### 3.5 URL 配置

```python
# pisadmin/urls.py
path('dashboard/', include('apps.pisadmin.dashboard.urls'))
```

---

## 4. 前端实现

### 4.1 路由设计

| 路径 | 组件 | 说明 |
|------|------|------|
| `/dashboard` | `DashboardIndex.vue` | 根路由，根据角色重定向 |
| `/dashboard/buyer` | `BuyerDashboard.vue` | 采购方看板 |
| `/dashboard/supplier` | `SupplierDashboard.vue` | 供应商看板 |

### 4.2 页面布局

```
┌─────────────────────────────────────────────────┐
│  Header: 欢迎语 + 当前日期                        │
├─────────────────────────────────────────────────┤
│  KPI Cards (4个指标卡片横向排列)                  │
├─────────────────────────────────────────────────┤
│  Main Content (左右分栏)                         │
│  ┌────────────────┐  ┌─────────────────────┐   │
│  │  待办/待报价清单  │  │  趋势图              │   │
│  │  (列表组件)      │  │  (ECharts 折线图)    │   │
│  └────────────────┘  └─────────────────────┘   │
├─────────────────────────────────────────────────┤
│  消息通知 (横向卡片列表)                          │
└─────────────────────────────────────────────────┘
```

### 4.3 组件结构

```
web/src/
├── views/
│   └── pisadmin/
│       └── dashboard/
│           ├── index.vue           # 重定向组件
│           ├── BuyerDashboard.vue # 采购方看板
│           └── SupplierDashboard.vue # 供应商看板
├── components/
│   └── dashboard/
│       ├── KpiCard.vue            # KPI 卡片
│       ├── TrendChart.vue          # 趋势图
│       ├── MessageList.vue         # 消息列表
│       ├── BuyerTaskList.vue        # 采购方待办
│       └── SupplierQuoteList.vue    # 供应商待报价
└── stores/
    └── dashboard.ts                # Pinia Store
```

### 4.4 Store 设计

```typescript
// stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    buyer: {
      kpi: null,
      tasks: [],
      messages: [],
      trend: []
    },
    supplier: {
      kpi: null,
      pendingQuotes: [],
      messages: [],
      trend: []
    },
    loading: false
  }),
  actions: {
    async fetchDashboard() { ... }
  }
})
```

### 4.5 API 服务

```typescript
// api/dashboard.ts
export function getDashboard() {
  return request.get('/api/dashboard/')
}
```

---

## 5. 权限控制

### 5.1 后端
- 根据 `request.user` 的角色过滤返回数据
- 无角色用户返回空数据

### 5.2 前端
- 根据 `user.roles` 判断显示哪个看板菜单
- 未授权用户访问看板路由时跳转至首页

---

## 6. 实现顺序

1. 后端 API 开发（dashboard 应用、序列化器、视图、URL）
2. 前端 API 服务和 Store
3. 通用组件（KpiCard、TrendChart、MessageList）
4. 采购方看板页面
5. 供应商看板页面
6. 路由配置和权限控制
