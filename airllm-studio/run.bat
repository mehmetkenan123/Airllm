@echo off
chcp 65001 >nul
title AirLLM Studio - Windows Otomatik Kurulum

echo ========================================
echo   AirLLM Studio - Windows Hazirlama
echo ========================================
echo.

REM 1. Python Kontrolu (hem 'python' hem 'py' komutlarini dene)
set "PYTHON_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_CMD=python"

if "%PYTHON_CMD%"=="" (
    where py >nul 2>&1
    if %errorlevel% equ 0 set "PYTHON_CMD=py"
)

if "%PYTHON_CMD%"=="" (
    echo [HATA] Python sistemde bulunamadi!
    echo.
    echo Windows'ta Python kurulu degil veya PATH'e eklenmemis.
    echo.
    echo NE YAPMALISINIZ?
    echo 1. Asagidaki linkten Python 3.11+ indirin:
    echo    https://www.python.org/downloads/
    echo.
    echo 2. Kurulum ekraninda MUTLACA su kutucugu isaretleyin:
    echo    [x] Add Python to PATH
    echo.
    echo 3. Kurulum bitince bu dosyaya (run.bat) tekrar cift tiklayin.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

echo [OK] Python bulundu: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM 2. Gerekli kutuphaneleri kur
echo [1/3] Gerekli kutuphaneler yukleniyor...
%PYTHON_CMD% -m pip install --upgrade pip -q --root-user-action=ignore
%PYTHON_CMD% -m pip install flask flask-cors requests psutil -q --root-user-action=ignore
if errorlevel 1 (
    echo.
    echo [HATA] Kutuphane kurulumu basarisiz!
    echo Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)
echo [OK] Flask ve bagimliliklar hazir.
echo.

REM 3. main.py var mi kontrol et
if not exist "main.py" (
    echo [HATA] main.py dosyasi bulunamadi!
    pause
    exit /b 1
)
echo [OK] Uygulama dosyalari hazir.
echo.

REM 4. Uygulamayi baslat
echo [2/3] AirLLM Studio baslatiliyor...
echo [3/3] Tarayici otomatik acilacak...
echo.
echo ========================================
echo UYGULAMA CALISIYOR!
echo Tarayicinizda http://localhost:5000 acilacak.
echo Kapatmak icin bu pencereyi kapatin veya CTRL+C basin.
echo ========================================
echo.

%PYTHON_CMD% main.py

pause
