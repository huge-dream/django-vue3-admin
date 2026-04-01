# ============================================================
# Start Celery Services (Windows PowerShell)
# Usage: .\start-celery.ps1 [dev|prod]
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
$WORKER_LOG = Join-Path $LOG_DIR "celery_worker.log"
$BEAT_LOG = Join-Path $LOG_DIR "celery_beat.log"

Set-Location $BackendDir

# Set Django environment
$env:DJANGO_SETTINGS_MODULE = "application.settings"

# Check if Worker is already running
$workerRunning = $false
if (Test-Path $WORKER_PID_FILE) {
    $PID = Get-Content $WORKER_PID_FILE -ErrorAction SilentlyContinue
    if ($PID -and (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
        $workerRunning = $true
        Write-Host "[Celery] Worker already running (PID: $PID), skipping"
    }
}

if (-not $workerRunning) {
    Write-Host "[Celery] Starting Worker..."

    # Check if celery is installed
    try {
        python -c "import celery" 2>$null
        if ($LASTEXITCODE -ne 0) { throw "celery not found" }
    } catch {
        Write-Host "[Error] Celery not installed"
        exit 1
    }

    # Start Celery Worker
    $proc = Start-Process -FilePath "celery" -ArgumentList "-A application worker -l info --logfile=$WORKER_LOG --pidfile=$WORKER_PID_FILE" -WorkingDirectory $BackendDir -PassThru -NoNewWindow -WindowStyle Hidden
    $proc.Id | Set-Content $WORKER_PID_FILE
    Write-Host "[Celery] Worker started (PID: $($proc.Id))"
}

# Check Beat
$beatRunning = $false
if (Test-Path $BEAT_PID_FILE) {
    $PID = Get-Content $BEAT_PID_FILE -ErrorAction SilentlyContinue
    if ($PID -and (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
        $beatRunning = $true
        Write-Host "[Celery Beat] Already running (PID: $PID), skipping"
    }
}

if (-not $beatRunning) {
    Write-Host "[Celery Beat] Starting scheduler..."

    # Start Celery Beat
    $proc = Start-Process -FilePath "celery" -ArgumentList "-A application beat -l info --logfile=$BEAT_LOG --pidfile=$BEAT_PID_FILE --scheduler django_celery_beat.schedulers:DatabaseScheduler" -WorkingDirectory $BackendDir -PassThru -NoNewWindow -WindowStyle Hidden
    $proc.Id | Set-Content $BEAT_PID_FILE
    Write-Host "[Celery Beat] Started (PID: $($proc.Id))"
}

# Wait for startup
Start-Sleep -Seconds 3

# Show status
if (Test-Path $WORKER_PID_FILE) {
    Write-Host "[Celery] Worker PID: $(Get-Content $WORKER_PID_FILE)"
    Write-Host "[Celery] Worker log: $WORKER_LOG"
}

if (Test-Path $BEAT_PID_FILE) {
    Write-Host "[Celery Beat] PID: $(Get-Content $BEAT_PID_FILE)"
    Write-Host "[Celery Beat] log: $BEAT_LOG"
}

Write-Host "[Celery] Startup complete"
exit 0
