@echo off
chcp 65001 >nul
title AirLLM Studio - Kurulum ve Calistirma

echo ========================================
echo   AirLLM Studio - Tek Tikla Baslatma
echo ========================================
echo.

REM Python kontrolu (Hem PATH hem Kayit Defteri)
set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% equ 0 set PYTHON_CMD=python

if "%PYTHON_CMD%"=="" (
    if exist "C:\Python312\python.exe" set PYTHON_CMD=C:\Python312\python
)
if "%PYTHON_CMD%"=="" (
    if exist "C:\Python311\python.exe" set PYTHON_CMD=C:\Python311\python
)
if "%PYTHON_CMD%"=="" (
    if exist "C:\Python310\python.exe" set PYTHON_CMD=C:\Python310\python
)
if "%PYTHON_CMD%"=="" (
    if exist "C:\Python39\python.exe" set PYTHON_CMD=C:\Python39\python
)
if "%PYTHON_CMD%"=="" (
    if exist "C:\Python38\python.exe" set PYTHON_CMD=C:\Python38\python
)

if "%PYTHON_CMD%"=="" (
    echo HATA: Python yuklu degil veya bulunamadi!
    echo Lutfen https://www.python.org/downloads/ adresinden Python 3.8+ yukleyin.
    echo KURULUM EKRANINDA "Add Python to PATH" SECENEKINI MUTLAKA ISARETLEYIN!
    echo.
    pause
    exit /b 1
)

echo [+] Python bulundu: %PYTHON_CMD%
echo.

REM Gerekli kutuphaneleri kur
echo [+] Gerekli kutuphaneler kontrol ediliyor...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
%PYTHON_CMD% -m pip install flask flask-cors psutil --quiet

echo [+] Kutuphaneler hazir.
echo.
echo [+] AirLLM Studio baslatiliyor...
echo Tarayici otomatik acilacak...
echo.

REM Uygulamayi baslat
%PYTHON_CMD% "%~dp0main.py"

pause
