@echo off
setlocal enableextensions
cd /d "%~dp0.."

rem ============================================================================
rem King's Bounty Tracker - Start Server (Windows 10+)
rem Plain batch launcher: starts the background scanner daemon and the web
rem server. Nothing reads or re-executes this file.
rem ============================================================================

set "ROOT=%CD%"
set "VENV_PY=%ROOT%\.venv\Scripts\python.exe"
set "ENV_FILE=%ROOT%\.env"

rem --- Validate installation ---------------------------------------------------
if not exist "%ENV_FILE%" (
	echo Setup has not been run. Please run install.bat first.
	pause & exit /b 1
)
if not exist "%VENV_PY%" (
	echo Virtual environment not found. Please run install.bat first.
	pause & exit /b 1
)

rem --- Read port from .env -----------------------------------------------------
set "APP_PORT=9333"
for /f "tokens=1,* delims==" %%a in ('findstr /b /c:"APP_PORT=" "%ENV_FILE%"') do set "APP_PORT=%%b"

netstat -an | findstr ":%APP_PORT% " | findstr LISTENING >nul
if not errorlevel 1 (
	echo Port %APP_PORT% is already in use.
	echo Free the port or change APP_PORT in: %ENV_FILE%
	pause & exit /b 1
)

rem --- Start daemon in the same console ----------------------------------------
rem Running it with "start /b" shares this console's process group, so Ctrl+C
rem stops both the daemon and the web server together.
echo Starting Profile Auto Scanner Daemon...
start /b "" "%VENV_PY%" -m src.tools.ProfileAutoScannerDaemon

rem --- Start web server --------------------------------------------------------
echo.
echo King's Bounty Tracker
echo URL: http://localhost:%APP_PORT%
echo.
echo Press Ctrl+C to stop both daemon and server.
echo.
start "" "http://localhost:%APP_PORT%"

"%VENV_PY%" -m uvicorn src.main:app --host 127.0.0.1 --port %APP_PORT%
