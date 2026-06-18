<# :
@echo off
rem King's Bounty Tracker - Start Server (Windows 10+)
rem This file is a batch + PowerShell polyglot: double-click runs the batch
rem header, which re-executes the rest of the file as a PowerShell script.
set "KBT_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "& ([ScriptBlock]::Create((Get-Content -LiteralPath '%~f0' -Raw)))"
exit /b %errorlevel%
#>

# ============================================================================
# King's Bounty Tracker - Start Server
# ============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# This script's own path comes from the batch header (KBT_SELF) because, when run
# as a script block from raw text, $PSCommandPath / $PSScriptRoot are not set.
$ScriptDir   = Split-Path -Parent $env:KBT_SELF
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPython  = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$EnvFile     = Join-Path $ProjectRoot ".env"

# --- Validate installation ---------------------------------------------------
if (-not (Test-Path $EnvFile)) {
    Write-Host "Setup has not been run. Please run install.bat first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found. Please run install.bat first." -ForegroundColor Red
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

# --- Start daemon in background ----------------------------------------------
Write-Host "Starting Profile Auto Scanner Daemon..." -ForegroundColor Gray
Set-Location $ProjectRoot
$DaemonJob = Start-Job -ScriptBlock {
    param($VenvPython, $ProjectRoot)
    Set-Location $ProjectRoot
    & $VenvPython -m src.tools.ProfileAutoScannerDaemon
} -ArgumentList $VenvPython, $ProjectRoot

Start-Sleep -Milliseconds 500
if ($DaemonJob.State -eq "Failed") {
    Write-Host "  Daemon failed to start" -ForegroundColor Red
    Receive-Job $DaemonJob
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  [OK] Daemon started" -ForegroundColor Green

# --- Start web server --------------------------------------------------------
Write-Host ""
Write-Host "King's Bounty Tracker" -ForegroundColor White
Write-Host "URL: http://localhost:$AppPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both daemon and server." -ForegroundColor Yellow
Write-Host ""

Start-Process "http://localhost:$AppPort"

try {
    & $VenvPython -m uvicorn src.main:app --host 127.0.0.1 --port $AppPort
} finally {
    Write-Host ""
    Write-Host "Stopping daemon..." -ForegroundColor Gray
    Stop-Job $DaemonJob -ErrorAction SilentlyContinue
    Remove-Job $DaemonJob -ErrorAction SilentlyContinue
    Write-Host "  [OK] Daemon stopped" -ForegroundColor Green
}
