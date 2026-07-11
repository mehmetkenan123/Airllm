@echo off
echo ========================================
echo AirLLM Studio Baslatiliyor...
echo ========================================
echo.

cd /d "%~dp0"

echo [+] Backend sunucusu baslatiliyor...
echo.
python backend/app.py

pause
