@echo off

if not exist raya.exe (
    echo raya.exe not found.
    echo Please run build.bat first.
    pause
    exit /b 1
)

raya.exe --validation

pause