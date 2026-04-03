# ============================================================
# Stop All Services (Windows PowerShell)
# ============================================================

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PID_DIR = Join-Path $ProjectRoot ".pids"

function Stop-ServiceByName {
    param([string]$Name, [string]$Pattern)

    $pidFile = Join-Path $PID_DIR "$Name.pid"

    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "[$Name] Stopping service (PID: $pid)..."
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 500
                $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($proc) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
                Write-Host "[$Name] Stopped"
            }
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }

    # Try to find by process name
    $wmiQuery = "SELECT ProcessId, Name, CommandLine FROM Win32_Process WHERE Name LIKE '%$Pattern%' OR CommandLine LIKE '%$Pattern%'"
    $procs = Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue
    if ($procs) {
        foreach ($p in $procs) {
            Write-Host "[$Name] Found by pattern PID: $($p.ProcessId), stopping..."
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

# Stop each service
Stop-ServiceByName "backend" "uvicorn"
Stop-ServiceByName "frontend" "node"
Stop-ServiceByName "celery_worker" "celery"
Stop-ServiceByName "celery_beat" "celery"

# Additional cleanup
Write-Host "[Cleanup] Checking for residual processes..."

# Cleanup uvicorn
$wmiQuery = "SELECT ProcessId, Name FROM Win32_Process WHERE Name LIKE '%uvicorn%'"
Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "[Cleanup] Stopping uvicorn (PID: $($_.ProcessId))"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# Cleanup gunicorn
$wmiQuery = "SELECT ProcessId, Name FROM Win32_Process WHERE Name LIKE '%gunicorn%'"
Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "[Cleanup] Stopping gunicorn (PID: $($_.ProcessId))"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# Cleanup node/vite
$wmiQuery = "SELECT ProcessId, Name, CommandLine FROM Win32_Process WHERE Name LIKE '%node%' AND (CommandLine LIKE '%vite%' OR CommandLine LIKE '%dev%')"
Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "[Cleanup] Stopping vite (PID: $($_.ProcessId))"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "[Done] All services stopped"
exit 0
