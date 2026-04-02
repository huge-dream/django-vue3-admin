# ============================================================
# Start Frontend Service (Windows PowerShell)
# Usage: .\start-frontend.ps1 [dev|prod]
#
# NOTE: For best compatibility on Windows, consider using Git Bash:
#   bash scripts/start-frontend.sh
#
# The PowerShell version uses Start-Process which may have issues
# with some Node.js development servers.
# ============================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$FrontendDir = Join-Path $ProjectRoot "web"
$PID_DIR = Join-Path $ProjectRoot ".pids"
$LOG_DIR = Join-Path $ProjectRoot "backend"
$LOG_DIR = Join-Path $LOG_DIR "logs"

$ENV = if ($args[0]) { $args[0] } else { "dev" }

# Create directories
if (!(Test-Path $PID_DIR)) { New-Item -ItemType Directory -Path $PID_DIR -Force | Out-Null }
if (!(Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }

$PID_FILE = Join-Path $PID_DIR "frontend.pid"
$LOG_FILE = Join-Path $LOG_DIR "frontend.log"

# Check if already running
if (Test-Path $PID_FILE) {
    $PID = Get-Content $PID_FILE -ErrorAction SilentlyContinue
    if ($PID -and (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
        Write-Host "[Frontend] Already running (PID: $PID), skipping"
        exit 0
    } else {
        Write-Host "[Frontend] Cleaning stale PID file"
        Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    }
}


# Check if yarn is available
$yarnCmd = Get-Command yarn -ErrorAction SilentlyContinue
if (!$yarnCmd) {
    Write-Host "[Frontend] yarn not found, trying npm..."
    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if (!$npmCmd) {
        Write-Host "[Error] npm not installed"
        exit 1
    }
    $useNpm = $true
} else {
    $useNpm = $false
}

# Check dependencies
if (!(Test-Path "node_modules")) {
    Write-Host "[Frontend] Dependencies not installed, installing..."
    if ($useNpm) {
        npm install
    } else {
        yarn install
    }
}

Write-Host "[Frontend] Starting service (ENV=$ENV)..."

# Select startup method based on environment
if ($ENV -eq "prod") {
    Write-Host "[Frontend] Building production version..."
    if ($useNpm) {
        npm run build
    } else {
        yarn build
    }
    Write-Host "[Frontend] Production build complete, use static server"
} else {
    if ($useNpm) {
        $proc = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $FrontendDir -PassThru -NoNewWindow
    } else {
        $proc = Start-Process -FilePath "yarn" -ArgumentList "dev" -WorkingDirectory $FrontendDir -PassThru -NoNewWindow
    }
    $proc.Id | Set-Content $PID_FILE
}

# Wait for startup
Start-Sleep -Seconds 5

# Check if started successfully
if (Test-Path $PID_FILE) {
    $PID = Get-Content $PID_FILE
    if (Get-Process -Id $PID -ErrorAction SilentlyContinue) {
        Write-Host "[Frontend] Started successfully (PID: $PID)"
        Write-Host "[Frontend] Access: http://localhost:8080"
        Write-Host "[Frontend] Log file: $LOG_FILE"
    } else {
        Write-Host "[Frontend] Failed to start, check log: $LOG_FILE"
        Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue
    }
}

exit 0
