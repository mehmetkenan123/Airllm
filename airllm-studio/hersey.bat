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

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python bulundu: %PYVER%
echo.

:: 2. GEREKLI KUTUPHANELERIN KURULUMU
echo [ADIM 1/3] Gerekli kutuphaneler yukleniyor/guncelleniyor...
echo Bu islem internet hizina gore degisebilir, lutfen bekleyin...
python -m pip install --upgrade pip --quiet --disable-pip-version-check
pip install flask pyinstaller psutil requests transformers accelerate airllm torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [HATA] Kutuphaneler yuklenirken hata olustu. Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)
echo [OK] Kutuphaneler hazir.
echo.

:: 3. UYGULAMAYI DERLEME (EXE OLUSTURMA)
echo [ADIM 2/3] Uygulama derleniyor (EXE olusturuluyor)...
echo Bu islem ilk seferde biraz zaman alabilir, lutfen bekleyin...
echo.

pyinstaller --onefile --name AirLLMStudio --clean --noconfirm main.py
if %errorlevel% neq 0 (
    echo [HATA] Derleme basarisiz oldu! Hata mesajini inceleyin.
    pause
    exit /b 1
)

echo.
echo [OK] Derleme Basarili!
echo Olusturulan dosya: dist\AirLLMStudio.exe
echo.

:: 4. UYGULAMAYI CALISTIRMA
echo [ADIM 3/3] Uygulama baslatiliyor...
echo ----------------------------------------
start "" "dist\AirLLMStudio.exe"

echo.
echo ========================================
echo AirLLM Studio arka planda baslatildi!
echo Tarayicinizda otomatik acilacaktir.
echo Kapatmak icin bu pencereyi kapatabilirsiniz.
echo ========================================
timeout /t 5 >nul
exit
