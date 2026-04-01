# 脚本文档

PIS 项目跨平台服务管理脚本。

## 概述

| 脚本 | Windows (PowerShell) | Unix/Linux/macOS (Bash) |
|------|---------------------|------------------------|
| 启动后端 | `start-backend.ps1` | `start-backend.sh` |
| 启动前端 | `start-frontend.ps1` | `start-frontend.sh` |
| 启动 Celery | `start-celery.ps1` | `start-celery.sh` |
| 停止所有 | `stop-all.ps1` | `stop-all.sh` |
| 停止 Celery | `stop-celery.ps1` | `stop-celery.sh` |
| 查看日志 | `view-logs.ps1` | `view-logs.sh` |
| 检查状态 | `check-status.ps1` | `check-status.sh` |

## 快速开始

### Windows (PowerShell)

```powershell
# 启动所有服务
.\make.ps1 dev

# 停止所有服务
.\make.ps1 stop

# 查看日志
.\make.ps1 logs

# 检查状态
.\make.ps1 status
```

### Unix/Linux/macOS (Bash)

```bash
# 启动所有服务
make dev

# 停止所有服务
make stop

# 查看日志
make logs

# 检查状态
make status
```

## 使用方法

### make.ps1 命令 (Windows PowerShell)

| 命令 | 说明 |
|------|------|
| `.\make.ps1 help` | 显示所有可用命令 |
| `.\make.ps1 dev` | 启动开发环境（前端 + 后端 + Celery） |
| `.\make.ps1 dev-backend` | 仅启动后端 |
| `.\make.ps1 dev-frontend` | 仅启动前端 |
| `.\make.ps1 dev-celery` | 仅启动 Celery |
| `.\make.ps1 stop` | 停止所有服务 |
| `.\make.ps1 restart` | 重启所有服务 |
| `.\make.ps1 restart-celery` | 仅重启 Celery |
| `.\make.ps1 logs` | 查看所有日志 |
| `.\make.ps1 logs-backend` | 查看后端日志 |
| `.\make.ps1 logs-frontend` | 查看前端日志 |
| `.\make.ps1 logs-celery` | 查看 Celery 日志 |
| `.\make.ps1 status` | 检查服务状态 |
| `.\make.ps1 clean-logs` | 清理日志文件 |
| `.\make.ps1 clean-pids` | 清理 PID 文件 |

### make 命令 (Unix/Linux/macOS Bash)

| 命令 | 说明 |
|------|------|
| `make help` | 显示所有可用命令 |
| `make dev` | 启动开发环境（前端 + 后端 + Celery） |
| `make dev-backend` | 仅启动后端 |
| `make dev-frontend` | 仅启动前端 |
| `make dev-celery` | 仅启动 Celery |
| `make stop` | 停止所有服务 |
| `make restart` | 重启所有服务 |
| `make restart-celery` | 仅重启 Celery |
| `make logs` | 查看所有日志 |
| `make logs-backend` | 查看后端日志 |
| `make logs-frontend` | 查看前端日志 |
| `make logs-celery` | 查看 Celery 日志 |
| `make status` | 检查服务状态 |
| `make clean-logs` | 清理日志文件 |
| `make clean-pids` | 清理 PID 文件 |

## 直接调用脚本

### Windows PowerShell

```powershell
# 启动后端
.\scripts\start-backend.ps1 [dev|prod]

# 启动前端
.\scripts\start-frontend.ps1 [dev|prod]

# 启动 Celery
.\scripts\start-celery.ps1 [dev|prod]

# 停止所有服务
.\scripts\stop-all.ps1

# 仅停止 Celery
.\scripts\stop-celery.ps1

# 查看日志
.\scripts\view-logs.ps1 [backend|frontend|celery|all]

# 检查状态
.\scripts\check-status.ps1
```

### Unix/Linux/macOS Bash

```bash
# 启动后端
./scripts/start-backend.sh [dev|prod]

# 启动前端
./scripts/start-frontend.sh [dev|prod]

# 启动 Celery
./scripts/start-celery.sh [dev|prod]

# 停止所有服务
./scripts/stop-all.sh

# 仅停止 Celery
./scripts/stop-celery.sh

# 查看日志
./scripts/view-logs.sh [backend|frontend|celery|all]

# 检查状态
./scripts/check-status.sh
```

## 环境参数

- `dev`（默认）：开发模式，带热重载
- `prod`：生产模式，使用优化构建

### Windows PowerShell
```powershell
.\make.ps1 dev -ENV prod
```

### Unix/Linux/macOS
```bash
ENV=prod make dev
```

## 端口

| 服务 | 端口 |
|------|------|
| 后端 (Django) | 8000 |
| 前端 (Vue) | 8080 |

## 日志文件

日志存储在 `backend/logs/`：

- `backend.log` - 后端应用日志
- `frontend.log` - 前端应用日志
- `celery_worker.log` - Celery Worker 日志
- `celery_beat.log` - Celery Beat 调度器日志

## PID 文件

PID 文件存储在 `.pids/`：

- `backend.pid`
- `frontend.pid`
- `celery_worker.pid`
- `celery_beat.pid`

## 跨平台兼容性

### Windows PowerShell
- 支持 Windows PowerShell 5.1 及 PowerShell 7+
- 使用 `System.Net.Sockets.TcpClient` 检查端口
- 使用 WMI 查询检测进程（兼容 PS 5.1 和 PS 7+）
- 所有输出使用英文（避免编码问题）

### Unix/Linux/macOS
- 需要 Bash 4.0+
- 使用 `nc`（netcat）检查端口（如果可用）
- 使用 `pgrep` 和 `pkill` 管理进程
- 输出使用中文

## 依赖要求

### 后端
- Python 3.10+
- Django 4.2.14
- uvicorn（开发）或 gunicorn（生产）
- Celery + Redis broker

### 前端
- Node.js 18+
- Yarn 或 npm

### Celery
- Redis 服务运行中
- django-celery-beat

## 故障排除

### 后端无法启动
1. 检查端口 8000 是否被占用
2. 检查 Python 依赖是否安装
3. 检查 Django 配置：确保 `backend/conf/env.py` 已配置

### 前端无法启动
1. 检查 Node.js 是否安装
2. 安装依赖：`cd web && yarn install`
3. 检查端口 8080 是否被占用

### Celery 无法启动
1. 检查 Redis 是否运行
2. 执行数据库迁移：`python manage.py migrate`
3. 查看 Celery 日志

### 编码问题
如果 PowerShell 显示乱码，确保使用 UTF-8 with BOM 编码保存的脚本文件。

## 脚本架构

```
scripts/
├── start-backend.ps1/.sh     # 启动 Django 后端服务
├── start-frontend.ps1/.sh    # 启动 Vue 前端开发服务器
├── start-celery.ps1/.sh      # 启动 Celery worker 和 beat
├── stop-all.ps1/.sh          # 停止所有服务
├── stop-celery.ps1/.sh       # 仅停止 Celery 服务
├── view-logs.ps1/.sh         # 查看和跟踪日志文件
├── check-status.ps1/.sh      # 检查服务运行状态
├── Makefile                   # Unix/Linux/macOS 编排
└── make.ps1                   # Windows PowerShell 编排
```

## 注意事项

- 所有脚本都是幂等的 - 多次运行是安全的
- 脚本会检测服务是否已运行，已运行则跳过启动
- 使用 PID 文件实现优雅关闭
- 停止时会清理残留进程
- PowerShell 脚本输出使用英文，避免编码问题
- Bash 脚本输出使用中文
