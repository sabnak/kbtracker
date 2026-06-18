#Requires -Version 5.1
# King's Bounty Tracker - Install / Update
# Windows 10+
#
# Single entry point: if the chosen installation directory already exists it is
# updated in place (source code and Python dependencies refreshed; the database,
# .env and .venv are left untouched). Otherwise a full installation is performed.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$GithubZipUrl = "https://github.com/sabnak/kbtracker/archive/refs/heads/main.zip"

# --- Relaunch from temp ------------------------------------------------------
# Updating overwrites InstallDir\local, which may hold this very script. Windows
# cannot delete the folder a running script lives in (nor a process's working
# directory), so on first launch we copy ourselves to a temp folder and relaunch
# from there. The relaunched copy runs outside InstallDir and can safely replace
# local\. The user's original working directory and the script's original
# location are passed through so the default install path still resolves.
if (-not $env:KBT_INSTALL_RELAUNCHED) {
    $Bootstrap = Join-Path $env:TEMP ("kbtracker_install_" + [System.Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $Bootstrap | Out-Null
    Copy-Item $PSCommandPath (Join-Path $Bootstrap "install.ps1")

    $env:KBT_INSTALL_RELAUNCHED = "1"
    $env:KBT_INSTALL_PWD    = (Get-Location).Path
    $env:KBT_INSTALL_ORIGIN = $PSScriptRoot

    # Start the child outside InstallDir so its working directory never locks it.
    Set-Location $env:TEMP
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Bootstrap "install.ps1")
    exit $LASTEXITCODE
}

# Keep this (relaunched) process out of InstallDir for the same lock reason.
Set-Location $env:TEMP

# --- Common helpers ----------------------------------------------------------

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

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Install-SourceCode([string]$InstallDir, [bool]$RemoveExisting) {
    Write-Step "Step 1: Downloading source code"

    $ZipPath = Join-Path $env:TEMP "kbtracker.zip"
    Invoke-WebRequest -Uri $GithubZipUrl -OutFile $ZipPath -UseBasicParsing
    Write-Ok "Downloaded"

    $ExtractTemp = Join-Path $env:TEMP "kbtracker_extract"
    if (Test-Path $ExtractTemp) { Remove-Item $ExtractTemp -Recurse -Force }
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractTemp
    $ExtractedRoot = Get-ChildItem $ExtractTemp | Select-Object -First 1

    if ($RemoveExisting -and (Test-Path $InstallDir)) {
        Remove-Item $InstallDir -Recurse -Force
    }

    if ($RemoveExisting) {
        Move-Item $ExtractedRoot.FullName $InstallDir
        Write-Ok "Extracted to: $InstallDir"
    } else {
        # Update mode: overwrite files except .venv and .env
        Get-ChildItem $ExtractedRoot.FullName | ForEach-Object {
            if ($_.Name -ne ".venv" -and $_.Name -ne ".env") {
                $destPath = Join-Path $InstallDir $_.Name
                if (Test-Path $destPath) {
                    Remove-Item $destPath -Recurse -Force
                }
                Copy-Item $_.FullName $destPath -Recurse -Force
            }
        }
        Write-Ok "Files updated in: $InstallDir"
    }

    Remove-Item $ExtractTemp -Recurse -Force
    Remove-Item $ZipPath -Force
}

function Install-Python([string]$InstallDir) {
    Write-Step "Step 2: Python 3.13"

    $py313ok = $false
    try {
        $null = & py -3.13 --version 2>&1
        $py313ok = $true
        Write-Ok "Python 3.13 found"
    } catch {}

    if (-not $py313ok) {
        Write-Host "  Installing Python 3.13 via winget..." -ForegroundColor Gray
        winget install --id Python.Python.3.13 --silent --accept-source-agreements --accept-package-agreements
        Refresh-Path
        try {
            $null = & py -3.13 --version 2>&1
            $py313ok = $true
            Write-Ok "Python 3.13 installed"
        } catch {
            throw "Python 3.13 installed but py launcher cannot find it. Please reopen this window and run again."
        }
    }

    $VenvDir = Join-Path $InstallDir ".venv"
    $VenvPip = Join-Path $VenvDir "Scripts\pip.exe"
    $VenvBabel = Join-Path $VenvDir "Scripts\pybabel.exe"

    if (-not (Test-Path $VenvDir)) {
        Write-Host "  Creating .venv inside $InstallDir ..." -ForegroundColor Gray
        & py -3.13 -m venv $VenvDir
        Write-Ok ".venv created"
    } else {
        Write-Ok ".venv already exists"
    }

    Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Gray
    & $VenvPip install -r (Join-Path $InstallDir "requirements.txt") --quiet
    Write-Ok "Packages installed"

    Write-Host "  Compiling translations..." -ForegroundColor Gray
    & $VenvBabel compile -d (Join-Path $InstallDir "src\i18n\translations")
    Write-Ok "Translations compiled"
}

# --- Default install directory -----------------------------------------------
# Two cases drive the default:
#   1. Launched from inside an installation (InstallDir\local\install.ps1): the
#      parent of the script's folder holds the source tree (a "src" dir), so we
#      default to it -- the common "update" case needs no typing.
#   2. Launched from anywhere else (a freshly downloaded script): there is no
#      source tree alongside it, so we default to a new KBTracker folder under
#      the directory the user launched from.
function Get-DefaultInstallDir {
    $origin = $env:KBT_INSTALL_ORIGIN
    if ($origin) {
        $parent = Split-Path $origin -Parent
        if ($parent -and (Test-Path (Join-Path $parent "src"))) {
            return $parent
        }
    }
    return Join-Path $env:KBT_INSTALL_PWD "KBTracker"
}

function Install-Fresh([string]$InstallDir) {
    # The app stores its data in SQLite files (app.db + per-game game_N.db)
    # created automatically under <InstallDir>\db on first run. No DB server.
    Write-Step "Step 3: Configuration"

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

    # --- Desktop shortcut ----------------------------------------------------
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

    Write-Host ""
    Write-Host "Setup complete!" -ForegroundColor Green
    Write-Host "Use the 'KBTracker' shortcut on your desktop to start the server later."
    Write-Host ""

    # --- Launch the installed app --------------------------------------------
    Write-Host "Starting King's Bounty Tracker..." -ForegroundColor White
    Write-Host "Open: http://localhost:$AppPort" -ForegroundColor Cyan
    Write-Host ""
    & $RunScript
}

function Complete-Update {
    Write-Host ""
    Write-Host "Update complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please restart the application for changes to take effect." -ForegroundColor Yellow
    Write-Host "  1. Close the running KBTracker application" -ForegroundColor Gray
    Write-Host "  2. Start it again using the desktop shortcut or run.ps1" -ForegroundColor Gray
    Write-Host ""
}

# --- Main --------------------------------------------------------------------
try {

Write-Host ""
Write-Host "King's Bounty Tracker - Install / Update" -ForegroundColor White
Write-Host ""

$InstallDir = Read-WithDefault "Installation directory" (Get-DefaultInstallDir)

# An existing installation is one whose directory already holds the source tree.
$IsUpdate = (Test-Path $InstallDir) -and (Test-Path (Join-Path $InstallDir "src"))

if ($IsUpdate) {
    Write-Host "Existing installation detected - updating in place." -ForegroundColor Cyan
} else {
    Write-Host "No installation found - performing a full install." -ForegroundColor Cyan
}

Install-SourceCode -InstallDir $InstallDir -RemoveExisting (-not $IsUpdate)
Install-Python -InstallDir $InstallDir

if ($IsUpdate) {
    Complete-Update
} else {
    Install-Fresh -InstallDir $InstallDir
}

} catch {
    Write-Host ""
    Write-Err "Failed: $_"
    Write-Host ""
    Read-Host "Press Enter to exit"
}
