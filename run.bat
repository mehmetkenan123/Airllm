@echo off
chcp 65001 >nul
title AirLLM Studio - Kurulum ve Calistirici

:: Null dosyası oluşumunu engelle
if exist "nul" del /q "nul" 2>nul

echo ========================================
echo     AirLLM Studio - Tek Tikla Cozum
echo ========================================
echo.

:: Python komutunu temizle
set "PYTHON_CMD="
set "CHOICE="

REM === PYTHON BULMA ===
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Python\PythonCore" /s /v "InstallPath" 2^>nul ^| findstr /i "InstallPath"') do (
    if exist "%%b\python.exe" set "PYTHON_CMD=%%b\python.exe"
)

if "%PYTHON_CMD%"=="" (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if "%PYTHON_CMD%"=="" set "PYTHON_CMD=%%i"
    )
)

if "%PYTHON_CMD%"=="" if exist "C:\Python39\python.exe" set "PYTHON_CMD=C:\Python39\python.exe"
if "%PYTHON_CMD%"=="" if exist "C:\Python38\python.exe" set "PYTHON_CMD=C:\Python38\python.exe"
if "%PYTHON_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
if "%PYTHON_CMD%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"

if "%PYTHON_CMD%"=="" (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)

echo Python bulundu: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM === MENU ===
echo Ne yapmak istersiniz?
echo.
echo [1] Kurulum yap ve uygulamayi calistir
echo [2] EXE dosyasi olustur
echo [3] Sadece bagimliliklari yukle
echo [4] Cikis
echo.
set /p CHOICE=Seciminiz (1-4): 

if "%CHOICE%"=="1" goto INSTALL_AND_RUN
if "%CHOICE%"=="2" goto BUILD_EXE
if "%CHOICE%"=="3" goto INSTALL_ONLY
if "%CHOICE%"=="4" goto EOF
goto INSTALL_AND_RUN

:INSTALL_AND_RUN
echo.
echo ========================================
echo   Adim 1/3: Sanal Ortam Olusturuluyor
echo ========================================

if not exist "venv" (
    "%PYTHON_CMD%" -m venv venv
    echo Sanal ortam olusturuldu.
) else (
    echo Sanal ortam zaten mevcut.
)

echo.
echo ========================================
echo   Adim 2/3: Bagimliliklar Yukleniyor
echo ========================================

call venv\Scripts\activate.bat
pip install --upgrade pip --quiet

if exist "airllm-studio\backend\requirements.txt" (
    pip install -r airllm-studio\backend\requirements.txt
) else (
    pip install flask torch transformers accelerate airllm
)

echo.
echo ========================================
echo   Adim 3/3: Uygulama Baslatiliyor
echo ========================================

if exist "airllm-studio\backend\app.py" (
    cd /d "%~dp0airllm-studio\backend"
    "%PYTHON_CMD%" app.py
) else (
    echo UYARI: app.py bulunamadi!
)

pause
goto EOF

:BUILD_EXE
echo.
echo ========================================
echo   EXE Olusturucu Modu
echo ========================================

if not exist "venv" (
    "%PYTHON_CMD%" -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install pyinstaller --quiet

if exist "airllm-studio\build_exe.py" (
    cd /d "%~dp0airllm-studio"
    "%PYTHON_CMD%" build_exe.py
    cd /d "%~dp0"
    echo EXE olusturuldu: airllm-studio\dist\AirLLM_Studio.exe
) else (
    echo HATA: build_exe.py bulunamadi!
)

pause
goto EOF

:INSTALL_ONLY
echo.
echo ========================================
echo   Sadece Bagimliliklar Yukleniyor
echo ========================================

if not exist "venv" (
    "%PYTHON_CMD%" -m venv venv
)
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet

if exist "airllm-studio\backend\requirements.txt" (
    pip install -r airllm-studio\backend\requirements.txt
)

echo Bagimliliklar yuklendi!
pause
goto EOF

:EOF
