@echo off
chcp 65001 >nul
title AirLLM Studio - Tek Tikla Kurulum ve Calistirma

echo ========================================
echo   AirLLM Studio - Otomatik Sihirbaz
echo ========================================
echo.

:: 1. PYTHON KONTROLU
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Bilgisayarinizda Python bulunamadi!
    echo.
    echo YAPILMASI GEREKENLER:
    echo 1. https://www.python.org/downloads/ adresine gidin.
    echo 2. En son Python surumunu indirin (orn: Python 3.12).
    echo 3. Kurulum sirasinda MUTLAKA "Add Python to PATH" kutusunu isaretleyin!
    echo 4. Kurulum bitince bu dosyaya tekrar cift tiklayin.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python bulundu: %PYVER%
echo.

:: 2. GEREKLI KUTUPHANELERIN KURULUMU
echo [ADIM 1/2] Gerekli kutuphaneler yukleniyor...
echo Bu islem internet hizina gore degisebilir, lutfen bekleyin...
python -m pip install --upgrade pip --quiet
pip install flask psutil requests --quiet
if %errorlevel% neq 0 (
    echo [HATA] Kutuphaneler yuklenirken hata olustu.
    pause
    exit /b 1
)
echo [OK] Kutuphaneler hazir.
echo.

:: 3. UYGULAMAYI CALISTIRMA
echo [ADIM 2/2] Uygulama baslatiliyor...
echo ----------------------------------------
start "" python "%~dp0main.py"

echo.
echo ========================================
echo AirLLM Studio arka planda baslatildi!
echo Tarayicinizda otomatik acilacaktir.
echo ========================================
timeout /t 2 >nul
exit
