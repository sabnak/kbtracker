#Requires -Version 5.1
# King's Bounty Tracker - Update
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$DefaultDir = "$env:USERPROFILE\AppData\LocalLow\KBTracker"

function Write-Step([string]$Text) {
	Write-Host ""
	Write-Host "=== $Text ===" -ForegroundColor Cyan
}

function Write-Ok([string]$Text) {
	Write-Host "  [OK] $Text" -ForegroundColor Green
}

function Write-Warn([string]$Text) {
	Write-Host "  [!]  $Text" -ForegroundColor Yellow
}

function Write-Err([string]$Text) {
	Write-Host "  [ERROR] $Text" -ForegroundColor Red
}

function Read-WithDefault([string]$Prompt, [string]$Default) {
	$val = Read-Host "$Prompt [$Default]"
	if ([string]::IsNullOrWhiteSpace($val)) { return $Default }
	return $val.Trim()
}

try {

# --- Header ------------------------------------------------------------------
Write-Host ""
Write-Host "King's Bounty Tracker - Update" -ForegroundColor White
Write-Host ""

$InstallDir = Read-WithDefault "Installation directory" $DefaultDir

if (-not (Test-Path $InstallDir)) {
	throw "Installation directory not found: $InstallDir"
}

# --- Check if git repository -------------------------------------------------
Write-Step "Checking installation type"

$GitDir = Join-Path $InstallDir ".git"
$IsGitRepo = Test-Path $GitDir

if ($IsGitRepo) {
	Write-Ok "Git repository detected"

	# --- Update from git -----------------------------------------------------
	Write-Step "Updating from git"

	Push-Location $InstallDir
	try {
		Write-Host "  Fetching latest changes..." -ForegroundColor Gray
		& git fetch origin 2>&1 | Out-Null

		Write-Host "  Pulling changes..." -ForegroundColor Gray
		$gitOutput = & git pull origin main 2>&1

		if ($LASTEXITCODE -ne 0) {
			throw "Git pull failed: $gitOutput"
		}

		if ($gitOutput -match "Already up to date") {
			Write-Ok "Already up to date"
		} else {
			Write-Ok "Code updated successfully"
		}
	} finally {
		Pop-Location
	}
} else {
	Write-Warn "Not a git repository"
	Write-Host "  This installation was set up from a ZIP file." -ForegroundColor Gray
	Write-Host "  To update, please run setup.ps1 again or clone from git manually." -ForegroundColor Gray
	Write-Host ""
	throw "Cannot update non-git installation automatically"
}

# --- Update dependencies (optional) ------------------------------------------
$VenvDir = Join-Path $InstallDir ".venv"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

if (Test-Path $VenvPip) {
	$updateDeps = (Read-Host "  Update Python dependencies? [y/N]").Trim().ToLower()
	if ($updateDeps -eq "y") {
		Write-Step "Updating dependencies"
		Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Gray
		& $VenvPip install -r (Join-Path $InstallDir "requirements.txt") --quiet --upgrade
		Write-Ok "Dependencies updated"
	}
}

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
