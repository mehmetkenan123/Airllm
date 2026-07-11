@echo off
chcp 65001 >nul
title AirLLM Studio - Tek Tikla Baslatma
cls

echo ========================================
echo   AirLLM Studio - Tek Tikla Baslatma
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python yuklu degil!
    echo.
    echo 1. https://python.org adresine gidin
    echo 2. Python 3.8 veya uzerini yukleyin
    echo 3. Kurulum sirasinda "Add Python to PATH" secenegini MUTLAKA isaretleyin
    echo.
    pause
    exit /b 1
)

echo [1/3] Python bulundu - 
python --version

echo [2/3] Gerekli kutuphaneler kontrol ediliyor...
pip install flask flask-cors torch transformers psutil --quiet 2>nul
echo     Kutuphaneler hazir!

echo [3/3] AirLLM Studio baslatiliyor...
echo.
echo ----------------------------------------
echo Tarayicinizda otomatik acilacak...
echo Elle erismek icin: http://localhost:5000
echo ----------------------------------------
echo.

python main.py

pause
