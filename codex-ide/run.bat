@echo off
chcp 65001 >nul
cls
echo ============================================================
echo CODEX IDE v5.0 - Başlatılıyor...
echo ============================================================
echo.

cd /d "%~dp0"

REM Python versiyonunu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı! Python 3.8+ gerekli.
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Gerekli paketleri yükle
echo Paketler kontrol ediliyor...
pip install psutil packaging --quiet 2>nul
echo [OK] Paketler hazır
echo.

REM Veritabanı dizinlerini oluştur
if not exist "models" mkdir models
if not exist "config" mkdir config
if not exist "tests" mkdir tests
if not exist "docs" mkdir docs
echo [OK] Dizinler hazır
echo.

echo ============================================================
echo Codex IDE başlatılıyor...
echo ============================================================
echo.
echo 🌐 Tarayıcıda açın: http://localhost:8080
echo 📁 Proje dizini: %CD%
echo.
echo ⌨️  Kısayollar:
echo    Ctrl+Shift+P - Komut Paleti
echo    Ctrl+K - AI Chat
echo    Ctrl+B - Sidebar Toggle
echo.
echo ============================================================
echo.

REM Uygulamayı başlat
python backend/app.py

pause
