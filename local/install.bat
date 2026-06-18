@echo off
setlocal enableextensions
cd /d "%~dp0"

rem ============================================================================
rem King's Bounty Tracker - Install / Update (Windows 10+)
rem
rem Plain batch installer. Heavy lifting uses built-in Windows tools
rem (curl, tar, robocopy, netstat); PowerShell is invoked only for the one-line
rem desktop-shortcut creation. Nothing reads or re-executes this file, so it
rem does not trip antivirus heuristics.
rem
rem If the chosen directory already holds the source tree it is updated in place
rem (the database, .env and .venv are left untouched); otherwise a full
rem installation is performed.
rem ============================================================================

set "ZIP_URL=https://github.com/sabnak/kbtracker/archive/refs/heads/main.zip"

rem --- Relaunch from %TEMP% for updates ----------------------------------------
rem An update overwrites InstallDir\local, which holds this very file, and cmd
rem keeps a running .bat locked. When we are inside an installation (..\src
rem exists) copy ourselves to TEMP and relaunch from there; the original
rem location is passed through KBT_ORIGIN so default paths still resolve.
if defined KBT_RELAUNCHED goto :main
if not exist "%~dp0..\src" goto :main
set "KBT_RELAUNCHED=1"
set "KBT_ORIGIN=%~dp0"
copy /y "%~f0" "%TEMP%\kbtracker_install.bat" >nul
cd /d "%TEMP%"
start "King's Bounty Tracker - Update" cmd /c call "%TEMP%\kbtracker_install.bat"
exit /b

:main
if not defined KBT_ORIGIN set "KBT_ORIGIN=%~dp0"

rem --- Default install directory ------------------------------------------------
rem Inside an installation (..\src exists) default to that installation -- the
rem common "update" case. Otherwise default to a KBTracker folder next to us.
if exist "%KBT_ORIGIN%..\src" (
	for %%I in ("%KBT_ORIGIN%..") do set "DEFAULT_DIR=%%~fI"
) else (
	for %%I in ("%KBT_ORIGIN%KBTracker") do set "DEFAULT_DIR=%%~fI"
)

echo.
echo King's Bounty Tracker - Install / Update
echo.
set "INSTALL_DIR=%DEFAULT_DIR%"
set /p "INSTALL_DIR=Installation directory [%DEFAULT_DIR%]: "

set "IS_UPDATE="
if exist "%INSTALL_DIR%\src" set "IS_UPDATE=1"
if defined IS_UPDATE (
	echo Existing installation detected - updating in place.
) else (
	echo No installation found - performing a full install.
)

rem --- Step 1: Source code ------------------------------------------------------
echo.
echo === Step 1: Downloading source code ===
curl.exe -L --ssl-no-revoke -o "%TEMP%\kbtracker.zip" "%ZIP_URL%"
if not exist "%TEMP%\kbtracker.zip" (
	echo   [ERROR] Download failed.
	pause & exit /b 1
)
rmdir /s /q "%TEMP%\kbtracker_extract" 2>nul
mkdir "%TEMP%\kbtracker_extract"
tar.exe -xf "%TEMP%\kbtracker.zip" -C "%TEMP%\kbtracker_extract"
set "SRC_ROOT="
for /d %%D in ("%TEMP%\kbtracker_extract\*") do set "SRC_ROOT=%%D"
if not defined SRC_ROOT (
	echo   [ERROR] Extraction failed.
	pause & exit /b 1
)

rem robocopy never purges extra files, so an update leaves .venv/.env (absent
rem from the archive) untouched. A fresh install starts from a clean folder.
if not defined IS_UPDATE if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"
robocopy "%SRC_ROOT%" "%INSTALL_DIR%" /E /NFL /NDL /NJH /NJS /NP >nul
rmdir /s /q "%TEMP%\kbtracker_extract" 2>nul
del /q "%TEMP%\kbtracker.zip" 2>nul
echo   [OK] Source ready in %INSTALL_DIR%

rem --- Step 2: Python ----------------------------------------------------------
echo.
echo === Step 2: Python 3.13 ===
py -3.13 --version >nul 2>&1
if errorlevel 1 (
	echo   Installing Python 3.13 via winget...
	winget install --id Python.Python.3.13 --silent --accept-source-agreements --accept-package-agreements
)
py -3.13 --version >nul 2>&1
if errorlevel 1 (
	echo   [ERROR] Python 3.13 not found. Reopen this window and run again.
	pause & exit /b 1
)
echo   [OK] Python 3.13 available

if not exist "%INSTALL_DIR%\.venv" py -3.13 -m venv "%INSTALL_DIR%\.venv"
echo   Installing packages from requirements.txt...
"%INSTALL_DIR%\.venv\Scripts\pip.exe" install -r "%INSTALL_DIR%\requirements.txt" --quiet
echo   Compiling translations...
"%INSTALL_DIR%\.venv\Scripts\pybabel.exe" compile -d "%INSTALL_DIR%\src\i18n\translations"
echo   [OK] Dependencies installed

if defined IS_UPDATE goto :finish_update
goto :fresh_config

rem --- Update done -------------------------------------------------------------
:finish_update
echo.
echo Update complete!
echo IMPORTANT: restart the application for changes to take effect.
echo.
pause
exit /b

rem --- Step 3: Fresh-install configuration -------------------------------------
:fresh_config
echo.
echo === Step 3: Configuration ===
:ask_port
set "APP_PORT=9333"
set /p "APP_PORT=  Application port [9333]: "
netstat -an | findstr ":%APP_PORT% " | findstr LISTENING >nul
if not errorlevel 1 (
	echo   Port %APP_PORT% is already in use. Choose a different port.
	goto :ask_port
)

rem The app creates its SQLite files under <InstallDir>\db on first run.
set "SAVE_PATH=%USERPROFILE%\Documents\my games"
>  "%INSTALL_DIR%\.env" echo GAME_DATA_PATH=:local
>> "%INSTALL_DIR%\.env" echo GAME_SAVE_PATH=%SAVE_PATH%
>> "%INSTALL_DIR%\.env" echo APP_PORT=%APP_PORT%
echo   [OK] .env written

set "RUN_BAT=%INSTALL_DIR%\local\run.bat"
set "LNK=%USERPROFILE%\Desktop\KBTracker.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%');$s.TargetPath='%RUN_BAT%';$s.WorkingDirectory='%INSTALL_DIR%';$s.Description='King''s Bounty Tracker';$s.Save()"
echo   [OK] Desktop shortcut created: KBTracker.lnk

echo.
echo Setup complete!
echo Use the 'KBTracker' shortcut on your desktop to start the server later.
echo.
echo Starting King's Bounty Tracker...
echo Open: http://localhost:%APP_PORT%
echo.
call "%RUN_BAT%"
exit /b
