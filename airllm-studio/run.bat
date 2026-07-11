@echo off
echo ========================================
echo    AirLLM Studio - Baslatiliyor...
echo ========================================
echo.

REM Gerekli Python paketlerini kontrol et ve yukle
echo [+] Gerekli paketler kontrol ediliyor...
pip install -q flask flask-cors torch transformers accelerate airllm psutil huggingface_hub hf_transfer

echo.
echo [+] Yukleme tamamlandi! Uygulama baslatiliyor...
echo ========================================
echo.
echo Tarayiciyi manuel olarak acin: http://localhost:5000
echo.

REM Backend uygulamasini calistir
python backend/app.py

pause
