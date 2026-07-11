@echo off
chcp 65001 >nul
title AirLLM Studio v2.0 - Professional Edition

echo ========================================
echo   AirLLM Studio v2.0
echo   Professional Edition
echo ========================================
echo.

REM Python check
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not installed!
    echo Install Python 3.8+: https://python.org
    echo CHECK "Add Python to PATH" during install!
    pause
    exit /b 1
)

echo [1/3] Python found: 
python --version
echo.

echo [2/3] Checking dependencies...
pip show flask psutil >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing missing packages...
    pip install flask psutil --quiet --no-warn-script-location
    echo Installation complete!
) else (
    echo Dependencies ready.
)
echo.

echo [3/3] Starting AirLLM Studio v2.0...
echo Browser will open automatically...
echo.
echo ========================================
echo.

REM Launch application
python main.py

pause
