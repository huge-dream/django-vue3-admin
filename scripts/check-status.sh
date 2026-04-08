#!/bin/bash
# ============================================================
# Check Service Status
# 使用方法: ./check-status.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_ROOT/.pids"

check_service() {
    local name=$1
    local pid_file="$PID_DIR/$name.pid"
    local port=$2

    echo -n "  $name: "

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "运行中 (PID: $pid)"
            return 0
        fi
    fi

    # 检查进程名
    local pids=$(pgrep -f "$name" 2>/dev/null | head -1 || true)
    if [ -n "$pids" ]; then
        echo "运行中 (PID: $pids)"
        return 0
    fi

    # 检查端口
    if [ -n "$port" ]; then
        if nc -z localhost "$port" 2>/dev/null; then
            echo "运行中 (端口: $port)"
            return 0
        fi
    fi

    echo "未运行"
    return 1
}

echo ""
check_service "backend" "8000"
check_service "frontend" "8080"
check_service "celery_worker" ""
check_service "celery_beat" ""
echo ""

# 端口检查
echo "端口检查:"
echo -n "  8000 (后端): "
nc -z localhost 8000 2>/dev/null && echo "开放" || echo "未开放"

echo -n "  8080 (前端): "
nc -z localhost 8080 2>/dev/null && echo "开放" || echo "未开放"

echo ""
