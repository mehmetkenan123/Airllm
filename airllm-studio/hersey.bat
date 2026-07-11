@echo off
chcp 65001 >nul
title AirLLM Studio - Tek Tıkla Kurulum ve Çalıştırma

echo ========================================
echo   AirLLM Studio - Otomatik Sihirbaz
echo ========================================
echo.

:: 1. PYTHON KONTROLÜ
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Bilgisayarınızda Python bulunamadı!
    echo.
    echo YAPILMASI GEREKENLER:
    echo 1. https://www.python.org/downloads/ adresine gidin.
    echo 2. En son Python surumunu indirin (örn: Python 3.12).
    echo 3. Kurulum sırasında MUTLAKA "Add Python to PATH" kutusunu isaretleyin!
    echo 4. Kurulum bitince bu dosyaya tekrar cift tiklayin.
    echo.
    pause
    exit /b 1
)

echo [OK] Python bulundu: 
python --version
echo.

:: 2. GEREKLİ KÜTÜPHANELERİN KURULUMU
echo [ADIM 1/3] Gerekli kütüphaneler kontrol ediliyor...
pip install flask pyinstaller psutil requests --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [HATA] Kütüphaneler yüklenirken hata oluştu. Internet bağlantınızı kontrol edin.
    pause
    exit /b 1
)
echo [OK] Kütüphaneler hazır.
echo.

:: 3. UYGULAMAYI DERLEME (EXE OLUŞTURMA)
echo [ADIM 2/3] Uygulama derleniyor (EXE oluşturuluyor)...
echo Bu işlem ilk seferde biraz zaman alabilir, lütfen bekleyin...
echo.

pyinstaller --onefile --name AirLLMStudio --clean main.py
if %errorlevel% neq 0 (
    echo [HATA] Derleme başarısız oldu! Hata mesajını inceleyin.
    pause
    exit /b 1
)

echo.
echo [OK] Derleme Başarılı!
echo Oluşturulan dosya: dist\AirLLMStudio.exe
echo.

:: 4. UYGULAMAYI ÇALIŞTIRMA
echo [ADIM 3/3] Uygulama başlatılıyor...
echo ----------------------------------------
start "" "dist\AirLLMStudio.exe"

echo.
echo ========================================
echo AirLLM Studio arka planda başlatıldı!
echo Tarayıcınızda otomatik açılacaktır.
echo Kapatmak için bu pencereyi kapatabilirsiniz.
echo ========================================
timeout /t 5 >nul
exit
