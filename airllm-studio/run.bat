@echo off
chcp 65001 >nul
title AirLLM Studio - Akıllı Kodlama Ortamı
echo ========================================
echo   🚀 AirLLM Studio Başlatılıyor...
echo   💻 Akıllı Kodlama Özellikleri Aktif
echo ========================================
echo.

REM Sanal ortam kontrolü
if not exist "venv" (
    echo [+] Sanal ortam oluşturuluyor...
    python -m venv venv
)

REM Sanal ortamı aktif et
call venv\Scripts\activate.bat

REM Gereksinimleri yükle
echo [+] Bağımlılıklar kontrol ediliyor...
pip install -q flask flask-cors torch transformers accelerate airllm psutil huggingface_hub hf_transfer

echo.
echo [+] Uygulama başlatılıyor...
echo [+] Tarayıcıda http://localhost:5000 adresini açın
echo ========================================
echo.

python backend\app.py
pause
