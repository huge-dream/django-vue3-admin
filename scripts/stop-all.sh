#!/bin/bash
# ============================================================
# Stop All Services
# 使用方法: ./stop-all.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.pids"

stop_service() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "[$name] 停止服务 (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            # 强制停止
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo "[$name] 已停止"
        else
            echo "[$name] 未运行"
        fi
        rm -f "$pid_file"
    else
        # 尝试通过进程名查找
        local pids=$(pgrep -f "$name" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "[$name] 通过进程名找到 PID: $pids，停止..."
            echo "$pids" | xargs kill 2>/dev/null || true
        fi
    fi
}

# 停止各个服务
stop_service "backend"
stop_service "frontend"
stop_service "celery_worker"
stop_service "celery_beat"

# 额外清理残留进程
echo "[清理] 检查残留进程..."

# 清理 uvicorn
pkill -f "uvicorn.*application.asgi" 2>/dev/null || true
pkill -f "gunicorn.*application.asgi" 2>/dev/null || true

# 清理 celery
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "celery.*beat" 2>/dev/null || true

# 清理 vite
pkill -f "vite" 2>/dev/null || true

echo "[完成] 所有服务已停止"
