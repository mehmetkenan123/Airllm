@echo off
echo ========================================
echo    Codex IDE - Yerel AI Kodlama Ortami
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python yuklu degil!
    echo Python 3.8+ yuklemeniz gerekiyor.
    pause
    exit /b 1
)

echo [+] Python bulundu
echo.

REM Gerekli paketleri yukle
echo [+] Gerekli paketler yukleniyor...
pip install flask flask-cors torch transformers sentence-transformers psutil hf-transfer accelerate --quiet

echo.
echo [+] Sunucu baslatiliyor...
echo ========================================
echo.

REM Backend'i baslat
python backend/app.py

pause
