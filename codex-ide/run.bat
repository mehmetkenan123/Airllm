@echo off
chcp 65001 >nul
title Codex IDE v4.0 - Ultra Advanced Edition

echo ==================================================
echo   CODEX IDE v4.0 - ULTRA ADVANCED EDITION
echo   Humanity's Most Advanced Development Environment
echo ==================================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Install dependencies if needed
echo Checking dependencies...
pip show flask >nul 2>&1 || pip install flask --quiet
pip show psutil >nul 2>&1 || pip install psutil --quiet
echo [OK] Dependencies ready
echo.

REM Create models directory
if not exist "models" mkdir models
echo [OK] Models directory ready
echo.

echo Starting Codex IDE v4.0...
echo ==================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed!
    pause
)
