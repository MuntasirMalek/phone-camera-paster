@echo off
:: Install Phone Camera Paster as a background service (Windows)
:: Run this once as Administrator: install-service.bat

echo.
echo 📸 Installing Phone Camera Paster...
echo.

:: Get the current directory
set SCRIPT_DIR=%~dp0

:: Create a VBS script to run Python hidden (no window)
echo Set WshShell = CreateObject("WScript.Shell") > "%SCRIPT_DIR%run-hidden.vbs"
echo WshShell.Run "python ""%SCRIPT_DIR%server.py""", 0, False >> "%SCRIPT_DIR%run-hidden.vbs"

:: Add to Windows Startup folder
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%SCRIPT_DIR%run-hidden.vbs" "%STARTUP_FOLDER%\PhoneCameraPaster.vbs" >nul

:: Start it now
start "" wscript.exe "%SCRIPT_DIR%run-hidden.vbs"

echo.
echo ✅ Phone Camera Paster installed!
echo.
echo 📱 Open the URL shown on your phone's browser
echo.
echo To uninstall: Delete PhoneCameraPaster.vbs from your Startup folder
echo Location: %STARTUP_FOLDER%
echo.
pause
