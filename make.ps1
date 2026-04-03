# ============================================================
# PIS Project Startup Script - Windows PowerShell Makefile
# ============================================================
# Usage:
#   .\make.ps1 help                    Show all commands
#   .\make.ps1 dev                     Start dev environment (frontend + backend + Celery)
#   .\make.ps1 dev-backend             Start backend only
#   .\make.ps1 dev-frontend           Start frontend only
#   .\make.ps1 dev-celery             Start Celery only
#   .\make.ps1 stop                    Stop all services
#   .\make.ps1 status                  Check service status
#   .\make.ps1 logs                    View all logs
#   .\make.ps1 logs-backend            View backend logs
#   .\make.ps1 logs-frontend           View frontend logs
#   .\make.ps1 logs-celery             View Celery logs
#   .\make.ps1 restart                 Restart all services
#   .\make.ps1 restart-celery          Restart Celery
# ============================================================

param(
    [string]$Target = "help",
    [string]$ENV = "dev"
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$ScriptsDir = Join-Path $ProjectRoot "scripts"

# Path configuration
$PID_DIR = Join-Path $ProjectRoot ".pids"
$LOG_DIR = Join-Path $ProjectRoot "backend\logs"

function Ensure-Directories {
    if (!(Test-Path $PID_DIR)) { New-Item -ItemType Directory -Path $PID_DIR -Force | Out-Null }
    if (!(Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }
}

function Run-Script {
    param([string]$ScriptName)
    $scriptPath = Join-Path $ScriptsDir "$ScriptName.ps1"
    if (Test-Path $scriptPath) {
        & $scriptPath $ENV
    } else {
        # fallback to bash if ps1 doesn't exist
        $bashPath = Join-Path $ScriptsDir "$ScriptName.sh"
        if (Test-Path $bashPath) {
            bash $bashPath $ENV
        } else {
            Write-Host "[ERROR] Script not found: $ScriptName"
            exit 1
        }
    }
}

switch ($Target.ToLower()) {
    "help" {
        Write-Host ""
        Write-Host "========================================"
        Write-Host "  PIS Project Startup Script (ENV=$ENV)"
        Write-Host "========================================"
        Write-Host ""
        Write-Host "  Startup Commands:"
        Write-Host "    .\make.ps1 dev              Start dev environment (frontend+backend+Celery)"
        Write-Host "    .\make.ps1 dev-backend     Start backend only"
        Write-Host "    .\make.ps1 dev-frontend    Start frontend only"
        Write-Host "    .\make.ps1 dev-celery      Start Celery only"
        Write-Host ""
        Write-Host "  Stop/Restart:"
        Write-Host "    .\make.ps1 stop            Stop all services"
        Write-Host "    .\make.ps1 restart         Restart all services"
        Write-Host "    .\make.ps1 restart-celery  Restart Celery"
        Write-Host ""
        Write-Host "  View Logs:"
        Write-Host "    .\make.ps1 logs            View all logs"
        Write-Host "    .\make.ps1 logs-backend    View backend logs"
        Write-Host "    .\make.ps1 logs-frontend   View frontend logs"
        Write-Host "    .\make.ps1 logs-celery     View Celery logs"
        Write-Host ""
        Write-Host "  Status:"
        Write-Host "    .\make.ps1 status          Check service status"
        Write-Host ""
        Write-Host "  Environment:"
        Write-Host "    .\make.ps1 -ENV prod dev  Use production environment"
        Write-Host ""
        Write-Host "========================================"
    }

    "dev" {
        Ensure-Directories
        Write-Host "========================================"
        Write-Host "  Starting Dev Environment (ENV=$ENV)"
        Write-Host "========================================"
        Write-Host ""
        Write-Host "  Backend: http://localhost:8000"
        Write-Host "  Frontend: http://localhost:8080"
        Write-Host "  Celery: Worker + Beat"
        Write-Host ""
        Run-Script "start-backend"
        Run-Script "start-frontend"
        Run-Script "start-celery"
    }

    "dev-backend" {
        Ensure-Directories
        Write-Host "Starting backend service (ENV=$ENV)..."
        Run-Script "start-backend"
    }

    "dev-frontend" {
        Write-Host "Starting frontend service (ENV=$ENV)..."
        Run-Script "start-frontend"
    }

    "dev-celery" {
        Ensure-Directories
        Write-Host "Starting Celery (ENV=$ENV)..."
        Run-Script "start-celery"
    }

    "stop" {
        Write-Host "Stopping all services..."
        Run-Script "stop-all"
        Write-Host "All services stopped"
    }

    "restart" {
        Write-Host "Restarting all services..."
        Run-Script "stop-all"
        Start-Sleep -Seconds 2
        Ensure-Directories
        Run-Script "start-backend"
        Run-Script "start-frontend"
        Run-Script "start-celery"
    }

    "restart-celery" {
        Run-Script "stop-celery"
        Start-Sleep -Seconds 1
        Ensure-Directories
        Run-Script "start-celery"
    }

    "logs" {
        Write-Host "========================================"
        Write-Host "  Viewing All Logs (Ctrl+C to exit)"
        Write-Host "========================================"
        Run-Script "view-logs"
    }

    "logs-backend" {
        Write-Host "========================================"
        Write-Host "  Viewing Backend Logs (Ctrl+C to exit)"
        Write-Host "========================================"
        & (Join-Path $ScriptsDir "view-logs.ps1") backend
    }

    "logs-frontend" {
        Write-Host "========================================"
        Write-Host "  Viewing Frontend Logs (Ctrl+C to exit)"
        Write-Host "========================================"
        & (Join-Path $ScriptsDir "view-logs.ps1") frontend
    }

    "logs-celery" {
        Write-Host "========================================"
        Write-Host "  Viewing Celery Logs (Ctrl+C to exit)"
        Write-Host "========================================"
        & (Join-Path $ScriptsDir "view-logs.ps1") celery
    }

    "status" {
        Write-Host "========================================"
        Write-Host "  Service Status Check"
        Write-Host "========================================"
        Run-Script "check-status"
    }

    "clean-logs" {
        Write-Host "Cleaning log files..."
        if (Test-Path $LOG_DIR) {
            Get-ChildItem $LOG_DIR -Filter "*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
        }
        Write-Host "Logs cleaned"
    }

    "clean-pids" {
        Write-Host "Cleaning PID files..."
        if (Test-Path $PID_DIR) {
            Get-ChildItem $PID_DIR -Filter "*.pid" | Remove-Item -Force -ErrorAction SilentlyContinue
        }
        Write-Host "PID files cleaned"
    }

    default {
        Write-Host "[ERROR] Unknown command: $Target"
        Write-Host "Run '.\make.ps1 help' to see available commands"
        exit 1
    }
}

exit 0
