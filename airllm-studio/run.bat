@echo off
chcp 65001 >nul
title AirLLM Studio - Tek Tikla Baslatma

echo ========================================
echo   AirLLM Studio - Otomatik Kurulum
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python yuklu degil!
    echo Lutfen https://python.org adresinden Python 3.8+ yukleyin.
    echo KURULUMDA "Add Python to PATH" SECENEKINI ISARETLEYIN!
    pause
    exit /b 1
)

echo [OK] Python bulundu: 
python --version
echo.

REM Gerekli kutuphaneleri kur
echo [1/3] Kutuphaneler kurulumda...
pip install flask flask-cors -q --root-user-action=ignore
if errorlevel 1 (
    echo HATA: Kutuphane kurulumu basarisiz!
    pause
    exit /b 1
)
echo [OK] Flask ve bagimliliklar hazir.
echo.

REM Uygulamayi baslat
echo [2/3] AirLLM Studio baslatiliyor...
echo [3/3] Tarayici otomatik acilacak...
echo.
echo ========================================
echo UYGULAMA CALISIYOR!
echo Tarayicinizda http://localhost adresi acilacak.
echo Kapatmak icin bu pencereyi kapatin veya CTRL+C basin.
echo ========================================
echo.

python main.py

pause
