# ============================================================
# Start Celery Services (Windows PowerShell)
# Usage: .\start-celery.ps1 [dev|prod]
#
# IMPORTANT: Celery on Windows has known issues with PowerShell's
# Start-Process. For reliable operation on Windows, use Git Bash instead:
#
#   bash scripts/start-celery.sh
#
# The bash script uses nohup which works correctly with Celery's
# multiprocessing pool (billiard). Start-Process in PowerShell
# causes billiard to fail with "PermissionError" or "OSError: handle invalid".
# ============================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$PID_DIR = Join-Path $ProjectRoot ".pids"
$LOG_DIR = Join-Path $BackendDir "logs"

$ENV = if ($args[0]) { $args[0] } else { "dev" }

# Create directories
if (!(Test-Path $PID_DIR)) { New-Item -ItemType Directory -Path $PID_DIR -Force | Out-Null }
if (!(Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }

$WORKER_PID_FILE = Join-Path $PID_DIR "celery_worker.pid"
$BEAT_PID_FILE = Join-Path $PID_DIR "celery_beat.pid"
$PYTHON_EXE = Join-Path $BackendDir ".venv\Scripts\python.exe"
$CELERY_EXE = Join-Path $BackendDir ".venv\Scripts\celery.exe"

$WORKER_LOG = Join-Path $LOG_DIR "celery_worker.log"
$BEAT_LOG = Join-Path $LOG_DIR "celery_beat.log"

# Set Django environment for current process
$env:DJANGO_SETTINGS_MODULE = "application.settings"

# Helper function to find celery process by port or log
function Find-CeleryProcess {
    param([string]$Type)
    $allProcs = Get-Process -Name "celery" -ErrorAction SilentlyContinue
    return $allProcs
}

# Check if Worker is already running
$workerRunning = $false
$existingWorker = $null
if (Test-Path $WORKER_PID_FILE) {
    $PID = Get-Content $WORKER_PID_FILE -ErrorAction SilentlyContinue
    if ($PID) {
        $existingWorker = Get-Process -Id $PID -ErrorAction SilentlyContinue
        if ($existingWorker) {
            $workerRunning = $true
            Write-Host "[Celery] Worker already running (PID: $PID), skipping"
        }
    }
}

if (-not $workerRunning) {
    Write-Host "[Celery] Starting Worker..."

    # Check if celery is installed
    try {
        & $PYTHON_EXE -c "import celery" 2>$null
        if ($LASTEXITCODE -ne 0) { throw "celery not found" }
    } catch {
        Write-Host "[Error] Celery not installed"
        exit 1
    }

    # Get count of existing celery processes
    $beforeCount = (Get-Process -Name "celery" -ErrorAction SilentlyContinue).Count

    # Start Celery Worker using cmd /c to run in background session
    # Using --pool solo --concurrency 1 to avoid Windows multiprocessing issues with billiard
    $cmdArgs = "/c cd /d `"$BackendDir`" && set DJANGO_SETTINGS_MODULE=application.settings && start /b /wait cmd /k `"$CELERY_EXE -A application worker -l info --logfile=$WORKER_LOG --pidfile=$WORKER_PID_FILE --pool solo --concurrency 1`""
    Start-Process -FilePath "cmd.exe" -ArgumentList $cmdArgs -WindowStyle Hidden

    # Wait for process to start
    Start-Sleep -Seconds 3

    # Find the new celery worker process
    $afterProcs = Get-Process -Name "celery" -ErrorAction SilentlyContinue
    $newProc = $afterProcs | Where-Object { $_.Id -ne (Get-Content $BEAT_PID_FILE -ErrorAction SilentlyContinue) } | Select-Object -First 1

    if ($newProc) {
        $newProc.Id | Set-Content $WORKER_PID_FILE
        Write-Host "[Celery] Worker started (PID: $($newProc.Id))"
    } else {
        Write-Host "[Celery] Worker started (process tracking may be inaccurate on Windows)"
    }
}

# Check Beat
$beatRunning = $false
$existingBeat = $null
if (Test-Path $BEAT_PID_FILE) {
    $PID = Get-Content $BEAT_PID_FILE -ErrorAction SilentlyContinue
    if ($PID) {
        $existingBeat = Get-Process -Id $PID -ErrorAction SilentlyContinue
        if ($existingBeat) {
            $beatRunning = $true
            Write-Host "[Celery Beat] Already running (PID: $PID), skipping"
        }
    }
}

if (-not $beatRunning) {
    Write-Host "[Celery Beat] Starting scheduler..."

    # Get count before
    $beforeCount = (Get-Process -Name "celery" -ErrorAction SilentlyContinue).Count

    # Start Celery Beat
    $cmdArgs = "/c cd /d `"$BackendDir`" && set DJANGO_SETTINGS_MODULE=application.settings && start /b /wait cmd /k `"$CELERY_EXE -A application beat -l info --logfile=$BEAT_LOG --pidfile=$BEAT_PID_FILE --scheduler django_celery_beat.schedulers:DatabaseScheduler`""
    Start-Process -FilePath "cmd.exe" -ArgumentList $cmdArgs -WindowStyle Hidden

    # Wait for process to start
    Start-Sleep -Seconds 3

    # Find the new celery beat process
    $afterProcs = Get-Process -Name "celery" -ErrorAction SilentlyContinue
    $newBeat = $afterProcs | Select-Object -Last 1

    if ($newBeat) {
        $newBeat.Id | Set-Content $BEAT_PID_FILE
        Write-Host "[Celery Beat] Started (PID: $($newBeat.Id))"
    } else {
        Write-Host "[Celery Beat] Started (process tracking may be inaccurate on Windows)"
    }
}

# Wait for startup
Start-Sleep -Seconds 3

# Show status
if (Test-Path $WORKER_PID_FILE) {
    $wpid = Get-Content $WORKER_PID_FILE
    Write-Host "[Celery] Worker PID: $wpid"
}
Write-Host "[Celery] Worker log: $WORKER_LOG"

if (Test-Path $BEAT_PID_FILE) {
    $bpid = Get-Content $BEAT_PID_FILE
    Write-Host "[Celery Beat] PID: $bpid"
}
Write-Host "[Celery Beat] log: $BEAT_LOG"

Write-Host "[Celery] Startup complete"
exit 0
