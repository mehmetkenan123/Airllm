@echo off
setlocal enabledelayedexpansion

:: Renk ve Başlık Ayarları
color 0B
title AirLLM Studio - Akilli Kurulum ve Baslatma

echo.
echo ============================================================
echo           AIRLLM STUDIO - OTOMATIK KURULUM SISTEMI
echo ============================================================
echo.

:: 1. ADIM: PYTHON KONTROLU
echo [1/4] Python kontrol ediliyor...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [HATA] Python bilgisayarinda bulunamadi!
    echo Lutfen python.org adresinden Python 3.10 veya uzerini yukleyin.
    echo Yukleme sirasinda 'Add Python to PATH' secenegini isaretlemeyi unutmayin.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [+] Python bulundu: %PY_VER%

:: 2. ADIM: SANAL ORTAM (VENV) KONTROLU
echo.
echo [2/4] Sanal ortam kontrolu...
if not exist "venv" (
    echo [+] Sanal ortam olusturuluyor (ilk kez biraz surebilir)...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [HATA] Sanal ortam olusturulurken bir sorun oldu.
        pause
        exit /b 1
    )
    echo [+] Sanal ortam basariyla olusturuldu.
) else (
    echo [+] Sanal ortam zaten mevcut, atlaniyor.
)

:: 3. ADIM: BAGIMLILIKLARI YUKLEME
echo.
echo [3/4] Gerekli kutuphaneler yukleniyor/kontrol ediliyor...
echo     (AirLLM, Torch, Flask, Transformers vb.)
echo.

:: Sanal ortami aktif et
call venv\Scripts\activate.bat

:: Pip'i guncelle
python -m pip install --upgrade pip --quiet --no-warn-script-location

:: requirements.txt var mi kontrol et, yoksa standart paketleri kur
if exist "airllm-studio\backend\requirements.txt" (
    echo [+] requirements.txt üzerinden yukleme yapiliyor...
    pip install -r airllm-studio\backend\requirements.txt
) else (
    echo [+] requirements.txt bulunamadi, temel paketler manuel yukleniyor...
    pip install flask flask-cors psutil airllm transformers accelerate torch sentencepiece protobuf safetensors huggingface-hub --no-warn-script-location
)

if !errorlevel! neq 0 (
    echo.
    echo [UYARI] Yukleme sirasinda bazi uyarilar alindi ancak devam ediliyor.
    echo Eger uygulama acilmazsa lutfen 'pip install -r requirements.txt' komutunu manuel calistirin.
)

echo [+] Kutuphaneler hazir.

:: 4. ADIM: UYGULAMAYI BASLATMA
echo.
echo [4/4] AirLLM Studio baslatiliyor...
echo ============================================================
echo.
echo -> Tarayicinizda otomatik olarak acilmasi bekleniyor...
echo -> Acilmazsa: http://localhost:5000 adresine gidin.
echo -> Kapatmak icin bu pencerede CTRL+C tusuna basin.
echo ============================================================
echo.

:: Backend klasorune git ve uygulamayi baslat
if exist "airllm-studio\backend\app.py" (
    cd airllm-studio\backend
    python app.py
) else (
    echo [KRITIK HATA] backend/app.py dosyasi bulunamadi!
    echo Dosya yolunu kontrol edin: airllm-studio\backend\app.py
    pause
    exit /b 1
)

pause
