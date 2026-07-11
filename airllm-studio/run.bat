@echo off
chcp 65001 >nul
title AirLLM Studio v1.2.0 - Kurulum ve Calistirma

echo ========================================
echo   AirLLM Studio v1.2.0
echo   Tek Tikla Kurulum ve Calistirma
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python yuklu degil!
    echo Python yukleniyor...
    start https://www.python.org/downloads/
    echo.
    echo Python kurulum sayfasini actik.
    echo KURULUMDA "Add Python to PATH" secenegini ISARETLEYIN!
    echo.
    pause
    exit /b 1
)

echo [OK] Python bulundu: 
python --version
echo.

REM Gerekli kutuphaneleri yukle
echo [1/3] Gerekli Python kutuphaneleri yukleniyor...
pip install flask flask-cors psutil --quiet --upgrade
if %errorlevel% neq 0 (
    echo [UYARI] Bazı paketler yuklenemedi, devam ediliyor...
)
echo [OK] Kutuphaneler hazir.
echo.

REM Uygulamayi derle (EXE olustur)
echo [2/3] Uygulama EXE olarak derleniyor...
pip install pyinstaller --quiet
pyinstaller --onefile --name AirLLMStudio --clean main.py --noconfirm --log-level ERROR
if %errorlevel% neq 0 (
    echo [UYARI] Derleme sirasinda uyarilar olustu ama devam ediliyor...
)
echo [OK] Derleme tamamlandi.
echo.

REM EXE dosyasini calistir
echo [3/3] AirLLM Studio baslatiliyor...
echo.
if exist dist\AirLLMStudio.exe (
    start "" "dist\AirLLMStudio.exe"
) else (
    echo [HATA] EXE dosyasi olusturulamedi! Python ile calistiriliyor...
    start "" python main.py
)

echo.
echo ========================================
echo Uygulama arka planda baslatildi.
echo Tarayicinizda otomatik acilacak.
echo ========================================
timeout /t 3 >nul
exit
