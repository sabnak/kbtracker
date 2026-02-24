#Requires -Version 5.1
# King's Bounty Tracker - Start Server
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $PSCommandPath
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPython  = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EnvFile     = Join-Path $ProjectRoot ".env"

# --- Validate installation ---------------------------------------------------
if (-not (Test-Path $EnvFile)) {
    Write-Host "Setup has not been run. Please run setup.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

function Test-PortAvailable([int]$Port) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

# --- Read port from .env -----------------------------------------------------
$AppPort = "9333"
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match "^APP_PORT=(.+)$") { $AppPort = $Matches[1].Trim() }
}

if (-not (Test-PortAvailable ([int]$AppPort))) {
    Write-Host "Port $AppPort is already in use." -ForegroundColor Red
    Write-Host "Free the port or change APP_PORT in: $EnvFile" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# --- Start daemon in a new window --------------------------------------------
$DaemonCmd = "Set-Location '$ProjectRoot'; & '$VenvPython' -m src.tools.ProfileAutoScannerDaemon"
Start-Process powershell -ArgumentList `
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", `
    "-Command", $DaemonCmd

# --- Start web server --------------------------------------------------------
Write-Host ""
Write-Host "King's Bounty Tracker" -ForegroundColor White
Write-Host "URL: http://localhost:$AppPort" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""

Set-Location $ProjectRoot
& $VenvPython -m uvicorn src.main:app --host 127.0.0.1 --port $AppPort
