# PIS - 采购与供应商管理系统

## 项目简介

基于 Django-Vue3 的采购与供应商管理系统，采用 RBAC 权限控制。

## 项目架构 🏗️

### 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Django 4.2.14 + Django REST Framework 3.15.2 |
| **前端** | Vue 3 + TypeScript + Vite 5.4 + Element Plus 2.8 + FastCRUD |
| **数据库** | MySQL 8.0 |
| **缓存/队列** | Redis + Celery |
| **实时通信** | Django Channels (WebSocket) |
| **认证** | JWT via SimpleJWT |

### 目录结构

```
pis/
├── backend/
│   ├── application/          # Django 项目配置
│   │   ├── settings.py       # 主配置（从 conf/env.py 导入配置）
│   │   ├── urls.py           # 根路由
│   │   ├── asgi.py           # ASGI 配置（支持 WebSocket）
│   │   └── celery.py         # Celery 配置
│   ├── apps/
│   │   ├── pisadmin/         # 采购管理应用
│   │   │   ├── basicinfo/    # 基础信息：公司、币种、供应商、单位、编码规则
│   │   │   └── miscprocurement/  # 杂项采购：询价、价格模板、成本节
│   │   └── pissupplier/      # 供应商报价模块
│   ├── dvadmin/              # 核心 RBAC 系统
│   │   └── system/           # 用户、角色、菜单、部门、日志
│   └── conf/
│       └── env.py            # 环境配置（数据库、Redis 凭证）
├── web/                      # Vue 3 前端
│   └── src/
│       ├── views/pisadmin/   # 采购管理页面
│       ├── views/pissupplier/# 供应商页面
│       └── views/system/     # 系统管理页面
└── scripts/                  # 服务管理脚本
    ├── start-backend.sh      # 启动后端服务
    ├── start-frontend.sh     # 启动前端服务
    ├── start-celery.sh       # 启动 Celery worker/beat
    ├── stop-all.sh           # 停止所有服务
    └── check-status.sh       # 查看服务状态
```

### 模块说明

| 模块 | 说明 |
|------|------|
| `pisadmin/basicinfo` | 基础信息管理：公司、币种、供应商、单位、系统编号规则 |
| `pisadmin/miscprocurement` | 杂项采购：询价（RFQ）、价格模板、成本节构建器 |
| `pissupplier` | 供应商报价模块 |
| `dvadmin/system` | 核心 RBAC 系统：用户、角色、菜单、部门、操作日志 |

### 配置说明

后端配置分离：
- `application/settings.py` - Django 默认配置
- `conf/env.py` - 环境特定配置（数据库、Redis、密钥）

## 准备工作

~~~
Python >= 3.8.0 (推荐3.8+版本)
nodejs >= 14.0 (推荐最新)
Mysql >= 5.7.0 (可选，默认数据库sqlite3，推荐8.0版本)
Redis(可选，最新版)
~~~

## 前端

```bash
# 进入前端目录
cd web

# 安装依赖
npm install yarn
npm install --registry=https://registry.npmmirror.com

# 启动开发服务器
yarn run dev
# 浏览器访问 http://localhost:8080
# .env.development 文件中可配置启动端口等参数

# 构建生产环境
yarn run build
```

## 后端

### 方式一：脚本启动（推荐）

项目提供了完整的启动脚本，位于项目根目录 `scripts/` 目录：

```bash
# 进入项目根目录
cd D:\AVC-PROJECT\pis

# 启动后端服务（开发模式）
./scripts/start-backend.sh

# 启动前端服务
./scripts/start-frontend.sh

# 启动 Celery 异步任务（可选）
./scripts/start-celery.sh
```

**脚本功能说明：**

| 脚本 | 说明 |
|------|------|
| `start-backend.sh` | 启动后端服务（自动创建 PID 和日志文件）|
| `start-frontend.sh` | 启动前端开发服务器 |
| `start-celery.sh` | 启动 Celery Worker 和 Beat |
| `stop-all.sh` | 停止所有服务 |
| `stop-celery.sh` | 仅停止 Celery 服务 |
| `check-status.sh` | 查看所有服务状态 |
| `view-logs.sh` | 查看服务日志 |

**查看日志：**
```bash
./scripts/view-logs.sh all      # 查看所有日志
./scripts/view-logs.sh backend  # 仅看后端日志
./scripts/view-logs.sh celery   # 仅看 Celery 日志
```

**停止服务：**
```bash
./scripts/stop-all.sh           # 停止所有服务
./scripts/stop-celery.sh       # 仅停止 Celery
```

### 方式二：手动启动

```bash
# 1. 进入后端目录
cd backend

# 2. 复制并配置环境文件
cp ./conf/env.example.py ./conf/env.py
# 编辑 env.py 配置数据库信息

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 执行数据库迁移
python3 manage.py makemigrations
python3 manage.py migrate

# 5. 初始化数据
python3 manage.py init
python3 manage.py init_area

# 6. 启动后端
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8
```

### 访问项目

- 前端地址：http://localhost:8080
- 后端接口：http://localhost:8080/api
- 默认账号：`superadmin` / `admin123456`

### Docker 部署

```shell
docker-compose up -d
# 初始化后端数据（第一次执行即可）
docker exec -ti dvadmin-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```
