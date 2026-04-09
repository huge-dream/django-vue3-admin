# API 权限自动扫描与批量生成

**日期：** 2026-04-09

## 1. 概述

### 背景
后端接口权限很多，前端给角色分配权限时需要手动一个个添加按钮权限，操作繁琐。系统提供自动化能力，自动扫描 Django app 下的 ViewSet 接口，并批量生成 `MenuButton` 权限记录。

### 已实现功能

1. **菜单管理页面 - 自动扫描接口权限**：选中菜单 → 选择 Django app → 扫描预览 → 批量生成按钮权限
2. **角色管理页面 - 按钮权限分组展示**：按 Model > CRUD 语义分组展示，支持批量勾选，防抖合并请求
3. **后端批量更新接口**：减少数据库并发锁问题

---

## 2. 菜单管理 - 自动扫描功能

![image-20260409194934989](https://images-warehouse.oss-cn-hangzhou.aliyuncs.com/img/202604091949170.png)

![image-20260409194952656](https://images-warehouse.oss-cn-hangzhou.aliyuncs.com/img/202604091949701.png)

![image-20260409195119115](https://images-warehouse.oss-cn-hangzhou.aliyuncs.com/img/202604091951173.png)

![image-20260409195141404](https://images-warehouse.oss-cn-hangzhou.aliyuncs.com/img/202604091951457.png)

![image-20260409195244451](https://images-warehouse.oss-cn-hangzhou.aliyuncs.com/img/202604091952531.png)

### 流程

```
菜单管理页面 → 选中菜单 → 点击「自动扫描」→ 选择 App → 开始扫描
    → 预览分组表格（按 ViewSet 分组，可折叠）
    → 行内编辑 name/value → 勾选 → 确认生成
    → 批量创建 MenuButton 记录
```

### 后端新增 API

| API | URL | 方法 | 功能 |
|-----|-----|------|------|
| 获取 App 列表 | `/api/system/menu_button/scan_get_apps/` | GET | 扫描 dvadmin 下所有有 views/ 子目录的 app |
| 扫描 ViewSet | `/api/system/menu_button/scan_viewset/` | POST | 扫描指定 app 下所有 ViewSet，返回接口预览数据 |
| 批量创建 | `/api/system/menu_button/scan_batch_create/` | POST | 批量创建 MenuButton，跳过已存在记录 |

### ViewSet 扫描规则
- 扫描 `dvadmin/{app}/views/` 子目录下的所有 `.py` 文件
- 使用 `pkgutil.iterModules` 发现子模块
- 对每个模块，用 `inspect.getmembers` 找 `GenericViewSet` 子类
- 标准 CRUD action 通过硬编码字典映射（list/create/retrieve/update/partial_update/destroy）
- 自定义 `@action` 方法通过 `inspect.getmembers(method)` + `method.mapping` 发现
- 排除基类（名字含 Custom/Base/Generic/Abstract）
- 使用 `seen_viewset_ids = set()` 按 `id(cls)` 去重
- `value` 格式：`{app}:{Model}:{Action}`，如 `system:User:List`

### 前端组件
- `web/src/views/system/menu/components/ScanModal/index.vue`
- 两步流程：选择 App → 预览表格
- 分组折叠表格：el-collapse 按 ViewSet 分组
- 表格列：勾选 | 接口路径 | 方法 | 按钮名称(name) | 权限标识(value) | 状态
- 全选/取消全选工具栏
- 行内编辑：name 和 value 列支持点击编辑
- `is_existing=true` 的行禁止编辑，显示灰色
- 选择同步：el-table ref + `toggleRowSelection()` 同步 checkbox 状态

---

## 3. 角色管理 - 按钮权限分组展示

### 背景
角色分配权限页面原本是平铺所有按钮，找起来困难。

### 解决方案
按 **Model > CRUD 语义** 二级分组展示：

```
▼ User (5 个操作)
  ☑ 查询 (绿色) → List, Retrieve, Search, Export...
  ☑ 新增/修改 (蓝色) → Create, Update, Copy, Import...
  ☐ 删除 (红色) → Delete
  ☐ 其他 (灰色) → 自定义 action

▼ Role (4 个操作)
  ...
```

### 分组规则（value 格式 `app:model:action`）

| 意图 | 匹配关键词 | 标签颜色 |
|------|-----------|---------|
| 查询 | list, retrieve, export, search, query, detail, get | 绿色 |
| 新增/修改 | create, update, import, copy, add, edit, save | 蓝色 |
| 删除 | delete, remove, destroy | 红色 |
| 其他 | 未能匹配以上关键词的 action | 灰色 |

### 防抖批量更新
- 300ms 防抖：合并多次勾选操作为一次请求
- 后端新增批量接口：`PUT /api/system/role_menu_button_permission/batch_set_role_menu_btn/`
- 请求体：`{ roleId, menuId, buttons: [{btnId, isCheck, data_range, dept}] }`
- 避免 SQLite 数据库锁问题

### 后端变更
- `role_menu_button_permission.py`：`RoleMenuButtonSerializer` 添加 `value` 字段
- 新增 `batch_set_role_menu_btn` action

---

## 4. i18n 国际化

新增多语言 key：
- `scan.*` — 扫描功能相关（菜单页面）
- `role.buttons.intentRead/intentWrite/intentDelete/intentOther` — CRUD 意图标签
- `role.buttons.expandAll/collapseAll` — 展开/折叠

---

## 5. 文件清单

### 后端
| 文件 | 变更 |
|------|------|
| `dvadmin/system/views/menu_button.py` | 新增 3 个 action：scan_get_apps、scan_viewset、scan_batch_create |
| `dvadmin/system/views/role_menu_button_permission.py` | 添加 `value` 到 serializer；新增 `batch_set_role_menu_btn` |
| `dvadmin/test_app/` | 新增测试 app（Blog、Product ViewSet） |
| `application/settings.py` | 注册 test_app |
| `application/urls.py` | 注册 test_app 路由 |

### 前端
| 文件 | 变更 |
|------|------|
| `web/src/views/system/menu/components/ScanModal/index.vue` | 新增：扫描弹窗组件 |
| `web/src/views/system/menu/api.ts` | 新增 3 个 API |
| `web/src/views/system/menu/index.vue` | 集成自动扫描按钮 |
| `web/src/views/system/role/components/RoleMenuBtn.vue` | 重写：分组展示 + 防抖批量 |
| `web/src/views/system/role/components/api.ts` | 新增 batchSetRoleMenuBtn |
| `web/src/views/system/role/types.ts` | 添加 `value` 字段 |
| `web/src/i18n/pages/menu/{zh-cn,en,zh-tw}.ts` | 添加 scan.* key |
| `web/src/i18n/pages/role/{zh-cn,en,zh-tw,zh-tw}.ts` | 添加 intent*/expandAll/collapseAll key |

---

## 6. 验证步骤

- [ ] 菜单管理：选中菜单 → 自动扫描 → 选择 App → 预览 → 确认生成
- [ ] 扫描结果：已存在的不重复创建，新接口正常生成
- [ ] 行内编辑：name 和 value 可编辑，已存在行禁止编辑
- [ ] 全选/取消全选：工具栏按钮和分组 header 都能正确同步
- [ ] 角色权限：按钮按 Model > CRUD 语义分组展示
- [ ] 全选/半选状态：Model 级和 CRUD 意图级都有 indeterminate 状态
- [ ] 批量防抖：快速勾选多个按钮，最终只发一条请求
- [ ] 多语言：中/英/繁切换正常
