@echo off
chcp 65001 >nul
title Codex IDE - Başlatılıyor...

echo ============================================================
echo    CODEX IDE - İnsanlık Tarihinin En Gelişmiş IDE'si
echo ============================================================
echo.

REM Python'un kurulu olup olmadığını kontrol et
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [HATA] Python bulunamadı!
    echo Lütfen Python 3.11+ yükleyin: https://python.org
    pause
    exit /b 1
)

echo [OK] Python bulundu
python --version

echo.
echo [BİLGİ] Gerekli paketler kontrol ediliyor...

REM Gerekli Python paketlerini yükle
pip install flask flask-cors psutil --quiet 2>nul
if %ERRORLEVEL% neq 0 (
    echo [UYARI] Bazı paketler yüklenemedi, devam ediliyor...
)

echo [OK] Paketler hazır
echo.
echo ============================================================
echo    Codex IDE Başlatılıyor...
echo ============================================================
echo.
echo 🌐 Tarayıcıda açılacak: http://localhost:8080
echo.
echo ⌨️  Kısayollar:
echo    Ctrl+Shift+P - Komut Paleti
echo    Ctrl+P       - Hızlı Dosya Aç
echo    Ctrl+B       - Sidebar Aç/Kapat
echo    Ctrl+`       - Terminal Aç/Kapat
echo    Ctrl+K       - AI Satır İçi
echo    Escape       - Panelleri Kapat
echo.
echo ============================================================
echo.

REM Uygulamayı başlat
python main.py

pause
