# ============================================================
# PIS Project Startup Script - Makefile
# PIS 项目启动脚本
# ============================================================
# 使用方法:
#   make help                    查看所有可用命令
#   make dev                     启动开发环境（前端 + 后端 + Celery）
#   make dev-backend             仅启动后端
#   make dev-frontend            仅启动前端
#   make dev-celery              仅启动 Celery
#   make stop                    停止所有服务
#   make status                  查看服务状态
#   make logs                    查看所有日志
#   make logs-backend            查看后端日志
#   make logs-frontend           查看前端日志
#   make logs-celery             查看 Celery 日志
#   make restart                 重启所有服务
#   make restart-celery          重启 Celery
# ============================================================

# 默认环境
ENV ?= dev

# 路径配置
PROJECT_ROOT := $(shell pwd)
BACKEND_DIR := $(PROJECT_ROOT)/backend
FRONTEND_DIR := $(PROJECT_ROOT)/web
SCRIPTS_DIR := $(PROJECT_ROOT)/scripts
LOG_DIR := $(BACKEND_DIR)/logs

# PID 文件目录
PID_DIR := $(PROJECT_ROOT)/.pids

# 后端服务端口
BACKEND_PORT := 8000
FRONTEND_PORT := 8080

# 帮助信息
.PHONY: help
help:
	@echo ""
	@echo "========================================"
	@echo "  PIS 项目启动脚本 (ENV=$(ENV))"
	@echo "========================================"
	@echo ""
	@echo "  启动命令:"
	@echo "    make dev              启动开发环境（前端+后端+Celery）"
	@echo "    make dev-backend     仅启动后端服务"
	@echo "    make dev-frontend    仅启动前端服务"
	@echo "    make dev-celery      仅启动 Celery"
	@echo ""
	@echo "  停止/重启:"
	@echo "    make stop            停止所有服务"
	@echo "    make restart         重启所有服务"
	@echo "    make restart-celery  重启 Celery"
	@echo ""
	@echo "  日志查看:"
	@echo "    make logs            查看所有日志"
	@echo "    make logs-backend    查看后端日志"
	@echo "    make logs-frontend   查看前端日志"
	@echo "    make logs-celery     查看 Celery 日志"
	@echo ""
	@echo "  状态查看:"
	@echo "    make status          查看所有服务状态"
	@echo ""
	@echo "  环境切换:"
	@echo "    ENV=prod make dev    使用生产环境配置启动"
	@echo ""
	@echo "========================================"

# ============================================================
# 创建必要的目录
# ============================================================
$(PID_DIR):
	@mkdir -p $(PID_DIR)

$(LOG_DIR):
	@mkdir -p $(LOG_DIR)

# ============================================================
# 启动开发环境 - 全部服务
# ============================================================
.PHONY: dev
dev: $(PID_DIR) $(LOG_DIR)
	@echo "========================================"
	@echo "  启动开发环境 (ENV=$(ENV))"
	@echo "========================================"
	@echo ""
	@echo "  后端: http://localhost:$(BACKEND_PORT)"
	@echo "  前端: http://localhost:$(FRONTEND_PORT)"
	@echo "  Celery: Worker + Beat"
	@echo ""
	@bash $(SCRIPTS_DIR)/start-backend.sh $(ENV)
	@bash $(SCRIPTS_DIR)/start-frontend.sh $(ENV)
	@bash $(SCRIPTS_DIR)/start-celery.sh $(ENV)

# ============================================================
# 启动后端
# ============================================================
.PHONY: dev-backend
dev-backend: $(PID_DIR) $(LOG_DIR)
	@echo "启动后端服务 (ENV=$(ENV))..."
	@bash $(SCRIPTS_DIR)/start-backend.sh $(ENV)

# ============================================================
# 启动前端
# ============================================================
.PHONY: dev-frontend
dev-frontend:
	@echo "启动前端服务 (ENV=$(ENV))..."
	@bash $(SCRIPTS_DIR)/start-frontend.sh $(ENV)

# ============================================================
# 启动 Celery
# ============================================================
.PHONY: dev-celery
dev-celery: $(PID_DIR) $(LOG_DIR)
	@echo "启动 Celery (ENV=$(ENV))..."
	@bash $(SCRIPTS_DIR)/start-celery.sh $(ENV)

# ============================================================
# 停止所有服务
# ============================================================
.PHONY: stop
stop:
	@echo "停止所有服务..."
	@bash $(SCRIPTS_DIR)/stop-all.sh
	@echo "所有服务已停止"

# ============================================================
# 重启所有服务
# ============================================================
.PHONY: restart
restart:
	@echo "重启所有服务..."
	@$(MAKE) stop
	@sleep 2
	@$(MAKE) dev

# ============================================================
# 重启 Celery
# ============================================================
.PHONY: restart-celery
restart-celery:
	@bash $(SCRIPTS_DIR)/stop-celery.sh
	@sleep 1
	@bash $(SCRIPTS_DIR)/start-celery.sh $(ENV)

# ============================================================
# 查看日志
# ============================================================
.PHONY: logs
logs:
	@echo "========================================"
	@echo "  查看所有日志 (Ctrl+C 退出)"
	@echo "========================================"
	@bash $(SCRIPTS_DIR)/view-logs.sh all

.PHONY: logs-backend
logs-backend:
	@echo "========================================"
	@echo "  查看后端日志 (Ctrl+C 退出)"
	@echo "========================================"
	@bash $(SCRIPTS_DIR)/view-logs.sh backend

.PHONY: logs-frontend
logs-frontend:
	@echo "========================================"
	@echo "  查看前端日志 (Ctrl+C 退出)"
	@echo "========================================"
	@bash $(SCRIPTS_DIR)/view-logs.sh frontend

.PHONY: logs-celery
logs-celery:
	@echo "========================================"
	@echo "  查看 Celery 日志 (Ctrl+C 退出)"
	@echo "========================================"
	@bash $(SCRIPTS_DIR)/view-logs.sh celery

# ============================================================
# 查看服务状态
# ============================================================
.PHONY: status
status:
	@echo "========================================"
	@echo "  服务状态检查"
	@echo "========================================"
	@bash $(SCRIPTS_DIR)/check-status.sh

# ============================================================
# 清理日志
# ============================================================
.PHONY: clean-logs
clean-logs:
	@echo "清理日志文件..."
	@find $(LOG_DIR) -type f -name "*.log" -exec rm -f {} \; 2>/dev/null || true
	@echo "日志已清理"

# ============================================================
# 清理 PID 文件（强制停止）
# ============================================================
.PHONY: clean-pids
clean-pids:
	@echo "清理 PID 文件..."
	@rm -f $(PID_DIR)/*.pid 2>/dev/null || true
	@echo "PID 文件已清理"
