@echo off
cd /d "%~dp0"
start "" cmd /c raya.exe

if not exist raya.exe (
    echo raya.exe not found.
    echo Please run build.bat first.
    pause
    exit /b 1
)

pause