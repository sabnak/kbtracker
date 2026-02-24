#Requires -Version 5.1
# King's Bounty Tracker - Setup
# Windows 10+

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$GithubZipUrl  = "https://github.com/sabnak/kbtracker/archive/refs/heads/main.zip"
$DefaultDir    = "$env:USERPROFILE\AppData\LocalLow\KBTracker"

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

try {

# --- Step 1: Download and extract from GitHub --------------------------------
Write-Host ""
Write-Host "King's Bounty Tracker - Setup" -ForegroundColor White
Write-Host ""

$InstallDir = Read-WithDefault "Installation directory" $DefaultDir

if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
}

Write-Step "Step 1/4: Downloading source code"
$ZipPath = Join-Path $env:TEMP "kbtracker.zip"
Invoke-WebRequest -Uri $GithubZipUrl -OutFile $ZipPath -UseBasicParsing
Write-Ok "Downloaded"

$ExtractTemp = Join-Path $env:TEMP "kbtracker_extract"
if (Test-Path $ExtractTemp) { Remove-Item $ExtractTemp -Recurse -Force }
Expand-Archive -Path $ZipPath -DestinationPath $ExtractTemp
$ExtractedRoot = Get-ChildItem $ExtractTemp | Select-Object -First 1
Move-Item $ExtractedRoot.FullName $InstallDir
Remove-Item $ExtractTemp -Recurse -Force
Remove-Item $ZipPath -Force
Write-Ok "Extracted to: $InstallDir"

# Paths inside the extracted project
$VenvDir    = Join-Path $InstallDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip    = Join-Path $VenvDir "Scripts\pip.exe"
$VenvBabel  = Join-Path $VenvDir "Scripts\pybabel.exe"

# --- Step 2: Python 3.14 -----------------------------------------------------
Write-Step "Step 2/4: Python 3.13"

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
        throw "Python 3.13 installed but py launcher cannot find it. Please reopen this window and run setup again."
    }
}

Write-Host "  Creating .venv inside $InstallDir ..." -ForegroundColor Gray
& py -3.13 -m venv $VenvDir
Write-Ok ".venv created"

Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Gray
& $VenvPip install -r (Join-Path $InstallDir "requirements.txt") --quiet
Write-Ok "Packages installed"

Write-Host "  Compiling translations..." -ForegroundColor Gray
& $VenvBabel compile -d (Join-Path $InstallDir "src\i18n\translations")
Write-Ok "Translations compiled"

# --- Step 3: PostgreSQL ------------------------------------------------------
Write-Step "Step 3/4: PostgreSQL"

$DbHost          = "localhost"
$DbPort          = "5432"
$PgSuperPassword = ""
$installNew      = $false

$pgService = Get-Service | Where-Object { $_.Name -like "postgresql*" } | Select-Object -First 1

if ($pgService) {
    Write-Ok "PostgreSQL service found: $($pgService.Name)"
    $pgChoice = (Read-Host "  Use existing or install new one? [existing/new]").Trim().ToLower()
    if ($pgChoice -eq "new") {
        $installNew = $true
    } else {
        # B.2 — use existing: ask port and superuser credentials
        $DbPort          = Read-WithDefault "  PostgreSQL port" "5432"
        $PgSuperPassword = Read-Host "  PostgreSQL superuser (postgres) password"
    }
} else {
    Write-Host "  No PostgreSQL service found." -ForegroundColor Gray
    $installNew = $true
}

if ($installNew) {
    # Scenario A — install on exotic port to avoid conflicts with any existing instance
    $DbPort          = "5433"
    $PgSuperPassword = [System.Guid]::NewGuid().ToString("N").Substring(0, 16)
    Write-Host "  Installing PostgreSQL 16 on port $DbPort via winget..." -ForegroundColor Gray
    winget install --id PostgreSQL.PostgreSQL.16 --silent --accept-source-agreements --accept-package-agreements `
        --override "--mode unattended --superpassword $PgSuperPassword --serverport $DbPort"
    Refresh-Path
    Write-Ok "PostgreSQL installed on port $DbPort"
}

# --- Step 4: App database config ---------------------------------------------
Write-Step "Step 4/4: Configuration"

$DbUser     = "kbtracker"
$DbPassword = "kbtracker"
$DbName     = "kbtracker"

Write-Host "  Default app DB credentials: user/password/db=kbtracker"
$choice = (Read-Host "  Press Enter for defaults, or type 'custom' to change").Trim().ToLower()

if ($choice -eq "custom") {
    $DbUser     = Read-WithDefault "  Username" $DbUser
    $DbPassword = Read-WithDefault "  Password" $DbPassword
    $DbName     = Read-WithDefault "  Database" $DbName
}

# Test PostgreSQL connection first
Write-Host "  Testing PostgreSQL connection..." -ForegroundColor Gray
$testScript = @"
import psycopg2
import sys
try:
    conn = psycopg2.connect(host='$DbHost', port=$DbPort, user='postgres', password='$PgSuperPassword', dbname='postgres')
    conn.close()
    sys.exit(0)
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
"@

$tempTest = Join-Path $env:TEMP "test_pg_conn.py"
$testScript | Out-File -FilePath $tempTest -Encoding ASCII -NoNewline
$testResult = & $VenvPython $tempTest 2>&1
Remove-Item $tempTest -Force
if ($LASTEXITCODE -ne 0) {
    throw "Cannot connect to PostgreSQL: $testResult"
}
Write-Ok "PostgreSQL connection successful"

# Create database and user
$createDbScript = @"
import psycopg2
import sys
try:
    conn = psycopg2.connect(host='$DbHost', port=$DbPort, user='postgres', password='$PgSuperPassword', dbname='postgres')
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("CREATE USER $DbUser WITH PASSWORD '$DbPassword'")
    except Exception:
        pass
    try:
        cur.execute("CREATE DATABASE $DbName OWNER $DbUser")
    except Exception:
        pass
    cur.close()
    conn.close()
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
"@

$tempScript = Join-Path $env:TEMP "create_kb_db.py"
$createDbScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline
$result = & $VenvPython $tempScript 2>&1
Remove-Item $tempScript -Force
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Could not create database automatically: $result"
    Write-Host "  Create manually: CREATE USER $DbUser WITH PASSWORD '$DbPassword'; CREATE DATABASE $DbName OWNER $DbUser;" -ForegroundColor Gray
} else {
    Write-Ok "Database and user created"
}

$AppPort = ""
while ($true) {
    $AppPort = Read-WithDefault "  Application port" "9333"
    if (Test-PortAvailable ([int]$AppPort)) { break }
    Write-Warn "Port $AppPort is already in use. Choose a different port."
}

$DatabaseUrl = "postgresql://${DbUser}:${DbPassword}@${DbHost}:${DbPort}/${DbName}"
$SavePath    = "$env:USERPROFILE\Documents\my games"

$envContent = @"
DATABASE_URL=$DatabaseUrl
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
