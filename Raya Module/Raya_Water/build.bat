@echo off

echo ========================================
echo RAYA Water Module - Build
echo ========================================

gcc raya.c -o raya.exe -lm

if errorlevel 1 (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)

echo.
echo BUILD SUCCESSFUL
echo Created: raya.exe
echo.

pause