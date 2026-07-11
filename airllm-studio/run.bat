@echo off
echo ========================================
echo   AirLLM Studio - Hızlı Başlatıcı
echo ========================================
echo.

REM Eğer EXE varsa direkt çalıştır
if exist "dist\AirLLM_Studio.exe" (
    echo 🚀 AirLLM Studio başlatılıyor...
    start dist\AirLLM_Studio.exe
    echo.
    echo ✅ Uygulama başlatıldı!
    echo 🌐 Tarayıcınızda http://localhost:5000 adresini kontrol edin.
) else (
    echo ⚠️  EXE dosyası bulunamadı!
    echo.
    echo Önce build.bat dosyasını çalıştırarak EXE oluşturun.
    echo.
    pause
)
