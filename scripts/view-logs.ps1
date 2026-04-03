# ============================================================
# View Logs (Windows PowerShell)
# Usage: .\view-logs.ps1 [backend|frontend|celery|all]
# ============================================================

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$LOG_DIR = Join-Path $BackendDir "logs"

$TARGET = if ($args[0]) { $args[0] } else { "all" }

# Ensure log directory exists
if (!(Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# Create empty log files if they don't exist
$logFiles = @(
    (Join-Path $LOG_DIR "backend.log"),
    (Join-Path $LOG_DIR "frontend.log"),
    (Join-Path $LOG_DIR "celery_worker.log"),
    (Join-Path $LOG_DIR "celery_beat.log")
)
foreach ($log in $logFiles) {
    if (!(Test-Path $log)) { New-Item -ItemType File -Path $log -Force | Out-Null }
}

switch ($TARGET) {
    "backend" {
        Write-Host "Viewing backend logs: $LOG_DIR\backend.log"
        Get-Content (Join-Path $LOG_DIR "backend.log") -Wait -Tail 20
    }
    "frontend" {
        Write-Host "Viewing frontend logs: $LOG_DIR\frontend.log"
        Get-Content (Join-Path $LOG_DIR "frontend.log") -Wait -Tail 20
    }
    "celery" {
        Write-Host "Viewing Celery logs..."
        Write-Host "=== Worker ==="
        Get-Content (Join-Path $LOG_DIR "celery_worker.log") -Wait -Tail 10
    }
    "all" {
        Write-Host "Viewing all logs (Ctrl+C to exit)..."
        Write-Host ""
        Write-Host "=== Backend Logs ==="
        if ((Test-Path (Join-Path $LOG_DIR "backend.log")) -and (Get-Content (Join-Path $LOG_DIR "backend.log") -ErrorAction SilentlyContinue)) {
            Get-Content (Join-Path $LOG_DIR "backend.log") -Tail 20
        } else {
            Write-Host "(empty)"
        }
        Write-Host ""
        Write-Host "=== Frontend Logs ==="
        if ((Test-Path (Join-Path $LOG_DIR "frontend.log")) -and (Get-Content (Join-Path $LOG_DIR "frontend.log") -ErrorAction SilentlyContinue)) {
            Get-Content (Join-Path $LOG_DIR "frontend.log") -Tail 20
        } else {
            Write-Host "(empty)"
        }
        Write-Host ""
        Write-Host "=== Celery Worker Logs ==="
        if ((Test-Path (Join-Path $LOG_DIR "celery_worker.log")) -and (Get-Content (Join-Path $LOG_DIR "celery_worker.log") -ErrorAction SilentlyContinue)) {
            Get-Content (Join-Path $LOG_DIR "celery_worker.log") -Tail 20
        } else {
            Write-Host "(empty)"
        }
        Write-Host ""
        Write-Host "=== Celery Beat Logs ==="
        if ((Test-Path (Join-Path $LOG_DIR "celery_beat.log")) -and (Get-Content (Join-Path $LOG_DIR "celery_beat.log") -ErrorAction SilentlyContinue)) {
            Get-Content (Join-Path $LOG_DIR "celery_beat.log") -Tail 20
        } else {
            Write-Host "(empty)"
        }
        Write-Host ""
        Write-Host "--- Live monitoring all logs (Ctrl+C to exit) ---"
        Get-Content $logFiles -Wait
    }
    default {
        Write-Host "Usage: $PSCommandPath [backend|frontend|celery|all]"
        exit 1
    }
}

exit 0
