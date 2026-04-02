# ============================================================
# Start Backend Service (Windows PowerShell)
# Usage: .\start-backend.ps1 [dev|prod]
#
# NOTE: For best compatibility on Windows, consider using Git Bash:
#   bash scripts/start-backend.sh
#
# The PowerShell version uses Start-Process which may have issues
# with some Python servers on Windows.
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

$PID_FILE = Join-Path $PID_DIR "backend.pid"
$LOG_FILE = Join-Path $LOG_DIR "backend.log"

# Check if already running
if (Test-Path $PID_FILE) {
    $PID = Get-Content $PID_FILE -ErrorAction SilentlyContinue
    if ($PID -and (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
        Write-Host "[Backend] Already running (PID: $PID), skipping"
        exit 0
    } else {
        Write-Host "[Backend] Cleaning stale PID file"
        Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    }
}


# Check dependencies
try {
    python -c "import uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "uvicorn not found" }
} catch {
    Write-Host "[Error] uvicorn not installed. Run: cd backend && pip install uvicorn"
    exit 1
}

# Set environment
$env:DJANGO_SETTINGS_MODULE = "application.settings"

Write-Host "[Backend] Starting service (ENV=$ENV)..."

# Select startup method based on environment
if ($ENV -eq "prod") {
    Write-Host "[Backend] Using gunicorn (production mode)"
    Start-Process -FilePath "python" -ArgumentList "-m gunicorn application.asgi:application -c gunicorn_conf.py --daemon -p $PID_FILE" -WorkingDirectory $BackendDir -RedirectStandardOutput $LOG_FILE -RedirectStandardError $LOG_FILE -WindowStyle Hidden
} else {
    Write-Host "[Backend] Using uvicorn (development mode with hot reload)"
    $proc = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory $BackendDir -PassThru -NoNewWindow
    $proc.Id | Set-Content $PID_FILE
}

# Wait for startup
Start-Sleep -Seconds 3

# Check if started successfully
if (Test-Path $PID_FILE) {
    $PID = Get-Content $PID_FILE
    if (Get-Process -Id $PID -ErrorAction SilentlyContinue) {
        Write-Host "[Backend] Started successfully (PID: $PID)"
        Write-Host "[Backend] Log file: $LOG_FILE"
    } else {
        Write-Host "[Backend] Failed to start, check log: $LOG_FILE"
        Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "[Backend] Failed to start, check log: $LOG_FILE"
}

exit 0
