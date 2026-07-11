@echo off
chcp 65001 >nul
title AirLLM Studio - Otomatik Derleyici
color 0A

echo ========================================
echo   AirLLM Studio - Tek Tikla Hazirlama
echo ========================================
echo.

:: Python Kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python yuklu degil!
    echo Lutfen python.org adresinden yukleyin ve PATH'e ekleyin.
    pause
    exit /b
)

:: Sanal Ortam
if not exist "venv" (
    echo Sanal ortam olusturuluyor...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Kutuphaneler
echo Kutuphaneler yukleniyor (bu sure alabilir)...
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

:: EXE Olusturma
echo EXE paketleniyor...
pyinstaller --onefile --name "AirLLM_Studio" --add-data "frontend;frontend" --add-data "backend;backend" --hidden-import flask --hidden-import torch --hidden-import flask_cors backend/app.py

echo.
if exist "dist\AirLLM_Studio.exe" (
    echo BASARILI! Uygulama dist klasorunde.
    start "" "dist\AirLLM_Studio.exe"
) else (
    echo HATA: EXE olusturulamedi.
)
pause
