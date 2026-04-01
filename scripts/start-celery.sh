#!/bin/bash
# ============================================================
# Start Celery Services
# 使用方法: ./start-celery.sh [dev|prod]
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

WORKER_PID_FILE="$PID_DIR/celery_worker.pid"
BEAT_PID_FILE="$PID_DIR/celery_beat.pid"
WORKER_LOG="$LOG_DIR/celery_worker.log"
BEAT_LOG="$LOG_DIR/celery_beat.log"

cd "$BACKEND_DIR"

# 设置 Django 环境
export DJANGO_SETTINGS_MODULE="application.settings"

# 检查是否已运行
check_celery() {
    if [ -f "$WORKER_PID_FILE" ]; then
        PID=$(cat "$WORKER_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

if check_celery; then
    echo "[Celery] Worker 已运行，跳过启动"
else
    echo "[Celery] 启动 Worker..."

    # 检查 celery 是否安装
    if ! python -c "import celery" 2>/dev/null; then
        echo "[错误] Celery 未安装"
        exit 1
    fi

    # 启动 Celery Worker
    nohup celery -A application worker \
        -l info \
        --logfile="$WORKER_LOG" \
        --pidfile="$WORKER_PID_FILE" \
        >> "$WORKER_LOG" 2>&1 &

    echo "[Celery] Worker 启动命令已执行"
fi

# 检查 Beat
if [ -f "$BEAT_PID_FILE" ]; then
    PID=$(cat "$BEAT_PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[Celery Beat] 已运行 (PID: $PID)，跳过启动"
    else
        rm -f "$BEAT_PID_FILE"
    fi
else
    echo "[Celery Beat] 启动调度器..."

    # 启动 Celery Beat
    nohup celery -A application beat \
        -l info \
        --logfile="$BEAT_LOG" \
        --pidfile="$BEAT_PID_FILE" \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler \
        >> "$BEAT_LOG" 2>&1 &

    echo "[Celery Beat] 启动命令已执行"
fi

# 等待检查
sleep 3

# 显示状态
if [ -f "$WORKER_PID_FILE" ]; then
    echo "[Celery] Worker PID: $(cat $WORKER_PID_FILE)"
    echo "[Celery] Worker 日志: $WORKER_LOG"
fi

if [ -f "$BEAT_PID_FILE" ]; then
    echo "[Celery Beat] PID: $(cat $BEAT_PID_FILE)"
    echo "[Celery Beat] 日志: $BEAT_LOG"
fi

echo "[Celery] 启动完成"
