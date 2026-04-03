#!/bin/bash
# ============================================================
# Start Frontend Service
# 使用方法: ./start-frontend.sh [dev|prod]
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/web"
PID_DIR="$PROJECT_ROOT/.pids"
LOG_DIR="$PROJECT_ROOT/backend/logs"

ENV=${1:-dev}

# 创建必要的目录
mkdir -p "$PID_DIR"
mkdir -p "$LOG_DIR"

PID_FILE="$PID_DIR/frontend.pid"
LOG_FILE="$LOG_DIR/frontend.log"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[前端] 已运行 (PID: $PID)，跳过启动"
        exit 0
    else
        echo "[前端] 清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

cd "$FRONTEND_DIR"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "[前端] 依赖未安装，正在安装..."
    yarn install
fi

echo "[前端] 启动服务 (ENV=$ENV)..."

# 根据环境选择启动方式
if [ "$ENV" = "prod" ]; then
    echo "[前端] 构建生产版本..."
    yarn build
    # 生产环境可以用 nginx 或静态服务器 served
    echo "[前端] 生产构建完成，请使用静态服务器 serving"
else
    # 开发环境
    nohup yarn dev >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
fi

# 等待启动
sleep 5

# 检查是否成功启动
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[前端] 启动成功 (PID: $PID)"
        echo "[前端] 访问地址: http://localhost:8080"
        echo "[前端] 日志文件: $LOG_FILE"
    else
        echo "[前端] 启动失败，请检查日志: $LOG_FILE"
        rm -f "$PID_FILE"
    fi
fi
