#!/bin/bash
# ============================================================
# Stop Celery Services
# 使用方法: ./stop-celery.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.pids"

stop_celery() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"
    local pattern="$2"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "[$name] 停止 (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pid_file"
    fi

    # 清理残留
    pkill -f "celery.*$pattern" 2>/dev/null || true
}

stop_celery "celery_worker" "worker"
stop_celery "celery_beat" "beat"

echo "[完成] Celery 已停止"
