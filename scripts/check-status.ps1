# ============================================================
# Check Service Status (Windows PowerShell)
# ============================================================

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PID_DIR = Join-Path $ProjectRoot ".pids"

function Test-ServicePort {
    param([int]$Port)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", $Port)
        $tcpClient.Close()
        return $true
    } catch {
        return $false
    }
}

function Check-Service {
    param([string]$Name, [int]$Port = 0)

    Write-Host -NoNewline "  $Name`: "

    $pidFile = Join-Path $PID_DIR "$Name.pid"

    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Running (PID: $pid)"
                return 0
            }
        }
    }

    # Check process name - PowerShell 5.1 compatible using WMI
    $patterns = @{
        "backend" = @("uvicorn", "gunicorn", "python")
        "frontend" = @("node", "npm")
        "celery_worker" = @("celery")
        "celery_beat" = @("celery")
    }

    if ($patterns.ContainsKey($Name)) {
        foreach ($pattern in $patterns[$Name]) {
            # Use WMI for reliable cross-version process matching
            $wmiQuery = "SELECT ProcessId, Name, CommandLine FROM Win32_Process WHERE Name LIKE '%$pattern%'"
            $procs = Get-WmiObject -Query $wmiQuery -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($procs) {
                Write-Host "Running (PID: $($procs.ProcessId))"
                return 0
            }
        }
    }

    # Check port
    if ($Port -gt 0) {
        if (Test-ServicePort -Port $Port) {
            Write-Host "Running (Port: $Port)"
            return 0
        }
    }

    Write-Host "Not running"
    return 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Service Status Check"
Write-Host "========================================"
Write-Host ""

Check-Service "backend" 8000
Check-Service "frontend" 8080
Check-Service "celery_worker"
Check-Service "celery_beat"
Write-Host ""

# Port check
Write-Host "Port Check:"

Write-Host -NoNewline "  8000 (backend): "
if (Test-ServicePort -Port 8000) {
    Write-Host "Open"
} else {
    Write-Host "Closed"
}

Write-Host -NoNewline "  8080 (frontend): "
if (Test-ServicePort -Port 8080) {
    Write-Host "Open"
} else {
    Write-Host "Closed"
}

Write-Host ""
exit 0
