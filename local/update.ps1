#Requires -Version 5.1
# King's Bounty Tracker - Update
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# The update overwrites InstallDir\local, which holds this very script. Windows
# cannot delete the folder a running script lives in (nor the process working
# directory), so on first launch we copy ourselves to a temp folder and
# re-launch from there. The relaunched copy runs outside InstallDir and can
# safely replace local\.
if (-not $env:KBT_UPDATE_RELAUNCHED) {
	$Bootstrap = Join-Path $env:TEMP ("kbtracker_update_" + [System.Guid]::NewGuid().ToString("N"))
	New-Item -ItemType Directory -Path $Bootstrap | Out-Null
	Copy-Item (Join-Path $PSScriptRoot "update.ps1") $Bootstrap
	Copy-Item (Join-Path $PSScriptRoot "common.ps1") $Bootstrap

	$env:KBT_UPDATE_RELAUNCHED = "1"
	# Original script dir is lost after we relaunch from temp; pass it through so
	# the default install directory still resolves to the real installation.
	$env:KBT_UPDATE_ORIGIN = $PSScriptRoot

	# Start the child outside InstallDir so its working directory never locks it.
	Set-Location $env:TEMP
	& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Bootstrap "update.ps1")
	exit $LASTEXITCODE
}

# Keep this (relaunched) process out of InstallDir for the same lock reason.
Set-Location $env:TEMP

# Load common functions
. (Join-Path $PSScriptRoot "common.ps1")

$DefaultDir = (Resolve-Path (Join-Path $env:KBT_UPDATE_ORIGIN "..")).Path

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
