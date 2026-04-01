# ============================================================
# Stop Celery Services (Windows PowerShell)
# ============================================================

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PID_DIR = Join-Path $ProjectRoot ".pids"

function Stop-CeleryService {
    param([string]$Name)

    $pidFile = Join-Path $PID_DIR "$Name.pid"

    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "[$Name] Stopping (PID: $pid)..."
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 500
                $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($proc) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
            }
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }

    # Cleanup residual
    $wmiQuery = "SELECT ProcessId, Name FROM Win32_Process WHERE Name LIKE '%celery%'"
    Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "[Cleanup] Stopping celery (PID: $($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Stop-CeleryService "celery_worker"
Stop-CeleryService "celery_beat"

Write-Host "[Done] Celery stopped"
exit 0
