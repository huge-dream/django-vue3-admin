#!/bin/bash
# ============================================================
# Start Backend Service
# 使用方法: ./start-backend.sh [dev|prod]
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
PID_DIR="$PROJECT_ROOT/.pids"
LOG_DIR="$BACKEND_DIR/logs"

ENV=${1:-dev}

# 创建必要的目录
mkdir -p "$PID_DIR"
mkdir -p "$LOG_DIR"

PID_FILE="$PID_DIR/backend.pid"
LOG_FILE="$LOG_DIR/backend.log"

# 检查是否已运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[后端] 已运行 (PID: $PID)，跳过启动"
        exit 0
    else
        echo "[后端] 清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

cd "$BACKEND_DIR"

# 检查依赖
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "[错误] 未安装 uvicorn，请先: cd backend && pip install uvicorn"
    exit 1
fi

# 设置环境变量
export DJANGO_SETTINGS_MODULE="application.settings"

echo "[后端] 启动服务 (ENV=$ENV)..."

# 根据环境选择启动方式
if [ "$ENV" = "prod" ]; then
    # 生产环境使用 gunicorn
    echo "[后端] 使用 gunicorn 启动 (生产模式)"
    nohup python -m gunicorn application.asgi:application \
        -c gunicorn_conf.py \
        --daemon \
        -p "$PID_FILE" \
        >> "$LOG_FILE" 2>&1
else
    # 开发环境使用 uvicorn (带 reload)
    echo "[后端] 使用 uvicorn 启动 (开发模式，带热重载)"
    nohup python main.py \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
fi

# 等待启动
sleep 3

# 检查是否成功启动
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[后端] 启动成功 (PID: $PID)"
        echo "[后端] 日志文件: $LOG_FILE"
    else
        echo "[后端] 启动失败，请检查日志: $LOG_FILE"
        rm -f "$PID_FILE"
    fi
else
    # uvicorn 模式
    sleep 2
    if pgrep -f "uvicorn.*application.asgi" > "$PID_FILE" 2>/dev/null; then
        echo "[后端] 启动成功 (PID: $(cat $PID_FILE))"
        echo "[后端] 日志文件: $LOG_FILE"
    else
        echo "[后端] 启动失败，请检查日志: $LOG_FILE"
    fi
fi
