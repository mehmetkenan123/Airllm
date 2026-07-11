@echo off
echo ========================================
echo   AirLLM Studio - EXE Oluşturucu
echo ========================================
echo.

REM Sanal ortam kontrolü
if not exist "venv" (
    echo [1/4] Python sanal ortamı oluşturuluyor...
    python -m venv venv
) else (
    echo [1/4] Sanal ortam zaten mevcut.
)

echo.
echo [2/4] Sanal ortam etkinleştiriliyor...
call venv\Scripts\activate.bat

echo.
echo [3/4] Gerekli kütüphaneler yükleniyor (bu işlem uzun sürebilir)...
pip install --upgrade pip
pip install -r backend\requirements.txt

echo.
echo [4/4] EXE dosyası paketleniyor...
python build_exe.py

echo.
echo ========================================
echo   İşlem Tamamlandı!
echo ========================================
echo.
echo 📦 EXE dosyası: dist\AirLLM_Studio.exe
echo.
echo 💡 Uygulamayı çalıştırmak için dist klasöründeki
echo    AirLLM_Studio.exe dosyasına çift tıklayın.
echo.
pause
