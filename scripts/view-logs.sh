#!/bin/bash
# ============================================================
# View Logs
# 使用方法: ./view-logs.sh [backend|frontend|celery|all]
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$BACKEND_DIR/logs"

TARGET=${1:-all}

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 创建空的日志文件（如果不存在）
touch "$LOG_DIR/backend.log" 2>/dev/null || true
touch "$LOG_DIR/frontend.log" 2>/dev/null || true
touch "$LOG_DIR/celery_worker.log" 2>/dev/null || true
touch "$LOG_DIR/celery_beat.log" 2>/dev/null || true

case "$TARGET" in
    backend)
        echo "查看后端日志: $LOG_DIR/backend.log"
        tail -f "$LOG_DIR/backend.log"
        ;;
    frontend)
        echo "查看前端日志: $LOG_DIR/frontend.log"
        tail -f "$LOG_DIR/frontend.log"
        ;;
    celery)
        echo "查看 Celery 日志..."
        echo "=== Worker ==="
        tail -f "$LOG_DIR/celery_worker.log" &
        echo "=== Beat ==="
        tail -f "$LOG_DIR/celery_beat.log"
        ;;
    all)
        echo "查看所有日志 (Ctrl+C 退出)..."
        echo ""
        echo "=== 后端日志 ==="
        tail -n 20 "$LOG_DIR/backend.log" 2>/dev/null || echo "(空)"
        echo ""
        echo "=== 前端日志 ==="
        tail -n 20 "$LOG_DIR/frontend.log" 2>/dev/null || echo "(空)"
        echo ""
        echo "=== Celery Worker 日志 ==="
        tail -n 20 "$LOG_DIR/celery_worker.log" 2>/dev/null || echo "(空)"
        echo ""
        echo "=== Celery Beat 日志 ==="
        tail -n 20 "$LOG_DIR/celery_beat.log" 2>/dev/null || echo "(空)"
        echo ""
        echo "--- 实时监控所有日志 (Ctrl+C 退出) ---"
        tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log" "$LOG_DIR/celery_worker.log" "$LOG_DIR/celery_beat.log"
        ;;
    *)
        echo "用法: $0 [backend|frontend|celery|all]"
        exit 1
        ;;
esac
