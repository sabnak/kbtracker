# King's Bounty Tracker - Common Setup Functions
# Shared between setup.ps1 and update.ps1

$GithubZipUrl = "https://github.com/sabnak/kbtracker/archive/refs/heads/main.zip"

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
	$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
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
