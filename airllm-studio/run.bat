@echo off
chcp 65001 >nul
title AirLLM Studio v1.3 - Kurulum ve Baslatma

echo ========================================
echo   AirLLM Studio v1.3 - Tek Tikla
echo ========================================
echo.

REM Python kontrolu
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Python yuklu degil!
    echo Python 3.8+ yukleyin: https://python.org
    echo KURULUMDA "Add Python to PATH" isaretleyin!
    pause
    exit /b 1
)

echo [1/3] Python bulundu: 
python --version
echo.

echo [2/3] Kutuphaneler kontrol ediliyor...
pip show flask psutil >nul 2>nul
if %errorlevel% neq 0 (
    echo Eksik kutuphaneler yukleniyor...
    pip install flask psutil --quiet --no-warn-script-location
    echo Yukleme tamamlandi!
) else (
    echo Kutuphaneler hazir.
)
echo.

echo [3/3] AirLLM Studio baslatiliyor...
echo Tarayici otomatik acilacak...
echo.
echo ========================================
echo.

REM Uygulamayi baslat
python main.py

pause
