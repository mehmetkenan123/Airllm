#!/bin/bash
# AirLLM Studio - Tek Tıkla Çalıştır (Linux)
# Bu script: Python kontrolü -> Bağımlılıklar -> Derleme -> Çalıştırma yapar

echo "=========================================="
echo "  AirLLM Studio - Otomatik Kurulum"
echo "=========================================="

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Python Kontrolü
echo -e "${YELLOW}[1/4] Python kontrol ediliyor...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓ Python bulundu: $($PYTHON_CMD --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}✓ Python bulundu: $($PYTHON_CMD --version)${NC}"
else
    echo -e "${RED}✗ HATA: Python bulunamadı!${NC}"
    echo "Yükleniyor..."
    apt-get update && apt-get install -y python3 python3-pip python3-venv
    PYTHON_CMD="python3"
fi

# 2. Bağımlılıkları Yükle
echo -e "${YELLOW}[2/4] Gerekli kütüphaneler yükleniyor...${NC}"
$PYTHON_CMD -m pip install --quiet --upgrade pip
$PYTHON_CMD -m pip install --quiet flask flask-cors torch transformers accelerate psutil safetensors huggingface_hub

# 3. Uygulamayı Derle (PyInstaller ile EXE benzeri tek dosya)
echo -e "${YELLOW}[3/4] Uygulama derleniyor (bu işlem biraz sürebilir)...${NC}"
$PYTHON_CMD -m pip install --quiet pyinstaller

cd "$(dirname "$0")"
$PYTHON_CMD -m PyInstaller --onefile --name AirLLMStudio --clean main.py 2>&1 | tail -5

if [ -f "dist/AirLLMStudio" ]; then
    echo -e "${GREEN}✓ Derleme başarılı! Dosya: dist/AirLLMStudio${NC}"
else
    echo -e "${RED}✗ Derleme başarısız! Doğrudan Python ile başlatılıyor...${NC}"
fi

# 4. Uygulamayı Başlat
echo -e "${YELLOW}[4/4] AirLLM Studio başlatılıyor...${NC}"
echo "Tarayıcıda otomatik açılacak: http://localhost:5000"
echo "Durdurmak için Ctrl+C basın"
echo "=========================================="

if [ -f "dist/AirLLMStudio" ]; then
    ./dist/AirLLMStudio
else
    $PYTHON_CMD main.py
fi
