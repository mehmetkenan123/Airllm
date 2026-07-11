@echo off
chcp 65001 >nul
title AirLLM Studio - Kurulum ve Calistirici

echo ========================================
echo     AirLLM Studio - Tek Tıkla Çözüm
echo ========================================
echo.

REM === PYTHON BULMA (GELIŞTIRILMIŞ) ===
set PYTHON_CMD=

REM 1. Önce registry'den Python yolunu almayı dene
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Python\PythonCore" /s /v "InstallPath" 2^>nul ^| findstr /i "InstallPath"') do (
    if exist "%%b\python.exe" set "PYTHON_CMD=%%b\python.exe"
)

REM 2. Registry bulunamazsa, where komutuyla dene
if "%PYTHON_CMD%"=="" (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if "%PYTHON_CMD%"=="" set "PYTHON_CMD=%%i"
    )
)

REM 3. python3 komutunu dene
if "%PYTHON_CMD%"=="" (
    for /f "delims=" %%i in ('where python3 2^>nul') do (
        if "%PYTHON_CMD%"=="" set "PYTHON_CMD=%%i"
    )
)

REM 4. Yaygın Python kurulum yollarını manuel kontrol et
if "%PYTHON_CMD%"=="" if exist "C:\Python39\python.exe" set "PYTHON_CMD=C:\Python39\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Python38\python.exe" set "PYTHON_CMD=C:\Python38\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Python37\python.exe" set "PYTHON_CMD=C:\Python37\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Program Files\Python39\python.exe" set "PYTHON_CMD=C:\Program Files\Python39\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Program Files\Python38\python.exe" set "PYTHON_CMD=C:\Program Files\Python38\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Program Files\Python37\python.exe" set "PYTHON_CMD=C:\Program Files\Python37\python.exe"
if "%PYTHON_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
if "%PYTHON_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
if "%PYTHON_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python37\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python37\python.exe"

if "%PYTHON_CMD%"=="" (
    echo.
    echo HATA: Python bulunamadi!
    echo.
    echo Cozum onerileri:
    echo 1. Python'i python.org adresinden yukleyin
    echo 2. Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin
    echo 3. Komut satirini yeniden acin
    echo.
    echo Yuklu Python surumlerini kontrol etmek icin:
    echo   where python
    echo   where python3
    echo.
    pause
    exit /b 1
)

echo ✓ Python bulundu: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM === MENÜ ===
echo Ne yapmak istersiniz?
echo.
echo [1] Kurulum yap ve uygulamayi calistir (Development Mode)
echo [2] EXE dosyasi olustur (Production Mode)
echo [3] Sadece bagimliliklari yukle
echo [4] Cikis
echo.
set /p CHOICE="Seciminiz (1-4): "

if "%CHOICE%"=="1" goto :INSTALL_AND_RUN
if "%CHOICE%"=="2" goto :BUILD_EXE
if "%CHOICE%"=="3" goto :INSTALL_ONLY
if "%CHOICE%"=="4" goto :EOF

echo Gecersiz secim! Varsayilan olarak kurulum yapiliyor...
goto :INSTALL_AND_RUN

:INSTALL_AND_RUN
echo.
echo ========================================
echo   Adim 1/3: Sanal Ortam Olusturuluyor
echo ========================================
echo.

if not exist "venv" (
    "%PYTHON_CMD%" -m venv venv
    echo ✓ Sanal ortam olusturuldu.
) else (
    echo ✓ Sanal ortam zaten mevcut.
)

echo.
echo ========================================
echo   Adim 2/3: Bagimliliklar Yukleniyor
echo ========================================
echo.

call venv\Scripts\activate.bat

pip install --upgrade pip --quiet
if exist "requirements.txt" (
    pip install -r requirements.txt
) else if exist "airllm-studio\backend\requirements.txt" (
    pip install -r airllm-studio\backend\requirements.txt
) else (
    echo UYARI: requirements.txt bulunamadi!
    pip install flask torch transformers accelerate streamlit airllm
)

echo.
echo ========================================
echo   Adim 3/3: Uygulama Baslatiliyor
echo ========================================
echo.

if exist "airllm-studio\backend\app.py" (
    echo AirLLM Studio Flask uygulaması başlatılıyor...
    cd airllm-studio\backend
    python app.py
) else if exist "airllm-studio\main.py" (
    echo Ana uygulama başlatılıyor...
    python airllm-studio\main.py
) else (
    echo UYARI: backend/app.py veya main.py bulunamadi!
    echo Manuel olarak baslatin: python airllm-studio\backend\app.py
)

pause
goto :EOF

:BUILD_EXE
echo.
echo ========================================
echo   EXE Oluşturucu Modu
echo ========================================
echo.

if exist "airllm-studio\build_exe.py" (
    echo PyInstaller ile EXE oluşturuluyor...
    echo.
    
    if not exist "venv" (
        "%PYTHON_CMD%" -m venv venv
        echo ✓ Sanal ortam olusturuldu.
    )
    
    call venv\Scripts\activate.bat
    
    echo Gerekli paketler yükleniyor (bu işlem uzun sürebilir)...
    pip install --upgrade pip --quiet
    pip install pyinstaller --quiet
    
    if exist "airllm-studio\backend\requirements.txt" (
        pip install -r airllm-studio\backend\requirements.txt
    )
    
    echo.
    echo EXE paketleniyor...
    cd airllm-studio
    "%PYTHON_CMD%" build_exe.py
    cd ..
    
    echo.
    echo ========================================
    echo   İŞLEM TAMAMLANDI!
    echo ========================================
    echo.
    if exist "airllm-studio\dist\AirLLM_Studio.exe" (
        echo ✓ EXE dosyası başarıyla oluşturuldu:
        echo   airllm-studio\dist\AirLLM_Studio.exe
        echo.
        echo 💡 Uygulamayı çalıştırmak için bu dosyaya
        echo    çift tıklayabilirsiniz.
    ) else (
        echo ⚠ EXE oluşturulurken bir sorun oluşmuş olabilir.
        echo   airllm-studio\dist klasörünü kontrol edin.
    )
) else (
    echo HATA: build_exe.py bulunamadı!
    echo airllm-studio klasöründe olduğunuzdan emin olun.
)

echo.
pause
goto :EOF

:INSTALL_ONLY
echo.
echo ========================================
echo   Sadece Bağımlılıklar Yükleniyor
echo ========================================
echo.

if not exist "venv" (
    "%PYTHON_CMD%" -m venv venv
    echo ✓ Sanal ortam olusturuldu.
)

call venv\Scripts\activate.bat

pip install --upgrade pip --quiet
if exist "requirements.txt" (
    pip install -r requirements.txt
) else if exist "airllm-studio\backend\requirements.txt" (
    pip install -r airllm-studio\backend\requirements.txt
) else (
    echo UYARI: requirements.txt bulunamadi!
    pip install flask torch transformers accelerate streamlit airllm
)

echo.
echo ✓ Bağımlılıklar başarıyla yüklendi!
echo.
pause
goto :EOF
