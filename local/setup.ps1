#Requires -Version 5.1
# King's Bounty Tracker - Setup
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Load common functions
. (Join-Path $PSScriptRoot "common.ps1")

$DefaultDir = "$env:USERPROFILE\AppData\LocalLow\KBTracker"

try {

Write-Host ""
Write-Host "King's Bounty Tracker - Setup" -ForegroundColor White
Write-Host ""

$InstallDir = Read-WithDefault "Installation directory" $DefaultDir

# --- Steps 1-2: Source code and Python --------------------------------------
Install-SourceCode -InstallDir $InstallDir -RemoveExisting $true
Install-Python -InstallDir $InstallDir

# --- Step 3: Configuration ---------------------------------------------------
# The app stores its data in SQLite files (app.db + per-game game_N.db) created
# automatically under <InstallDir>\db on first run. No database server needed.
Write-Step "Step 3/3: Configuration"

$AppPort = ""
while ($true) {
    $AppPort = Read-WithDefault "  Application port" "9333"
    if (Test-PortAvailable ([int]$AppPort)) { break }
    Write-Warn "Port $AppPort is already in use. Choose a different port."
}

$SavePath = "$env:USERPROFILE\Documents\my games"

$envContent = @"
GAME_DATA_PATH=:local
GAME_SAVE_PATH=$SavePath
APP_PORT=$AppPort
"@

$envPath = Join-Path $InstallDir ".env"
[System.IO.File]::WriteAllText($envPath, $envContent, [System.Text.UTF8Encoding]::new($false))

Write-Ok ".env written"

# --- Desktop shortcut --------------------------------------------------------
$RunScript    = Join-Path $InstallDir "local\run.ps1"
$ShortcutPath = "$env:USERPROFILE\Desktop\KBTracker.lnk"
$WshShell     = New-Object -ComObject WScript.Shell
$Shortcut     = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath       = "powershell.exe"
$Shortcut.Arguments        = "-ExecutionPolicy Bypass -NoProfile -File `"$RunScript`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description      = "King's Bounty Tracker"
$Shortcut.Save()
Write-Ok "Desktop shortcut created: KBTracker.lnk"

# --- Done --------------------------------------------------------------------
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Use the 'KBTracker' shortcut on your desktop to start the server."
Write-Host "Then open: http://localhost:$AppPort"
Write-Host ""

} catch {
    Write-Host ""
    Write-Host "Setup failed: $_" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
}
