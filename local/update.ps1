#Requires -Version 5.1
# King's Bounty Tracker - Update
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Load common functions
. (Join-Path $PSScriptRoot "common.ps1")

$DefaultDir = "$env:USERPROFILE\AppData\LocalLow\KBTracker"

try {

Write-Host ""
Write-Host "King's Bounty Tracker - Update" -ForegroundColor White
Write-Host ""

$InstallDir = Read-WithDefault "Installation directory" $DefaultDir

if (-not (Test-Path $InstallDir)) {
	throw "Installation directory not found: $InstallDir"
}

# --- Steps 1-2: Source code and Python --------------------------------------
Install-SourceCode -InstallDir $InstallDir -RemoveExisting $false
Install-Python -InstallDir $InstallDir

# --- Done --------------------------------------------------------------------
Write-Host ""
Write-Host "Update complete!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Please restart the application for changes to take effect." -ForegroundColor Yellow
Write-Host "  1. Close the running KBTracker application" -ForegroundColor Gray
Write-Host "  2. Start it again using the desktop shortcut or run.ps1" -ForegroundColor Gray
Write-Host ""

} catch {
	Write-Host ""
	Write-Err "Update failed: $_"
	Write-Host ""
	Read-Host "Press Enter to exit"
}
