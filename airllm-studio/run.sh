#!/bin/bash
# AirLLM Studio - Gelişmiş Terminal Başlatıcı
# Bu script uygulamayı başlatır ve tam terminal deneyimi sunar

cd /workspace/airllm-studio

echo "========================================"
echo "   🚀 AirLLM Studio - Terminal Mode"
echo "========================================"
echo ""

# Sistem Python'unu kullan (venv disk alanını dolduruyor)
echo "[*] Sistem Python kullanılıyor..."

# Gereksinimleri kontrol et ve yükle (sistem geneline)
echo "[*] Bağımlılıklar kontrol ediliyor..."
pip install -q flask flask-cors torch transformers accelerate sentencepiece protobuf airllm psutil hf_transfer 2>/dev/null || true

# Models klasörünü oluştur
mkdir -p models

echo ""
echo "[+] Sistem hazır!"
echo "[+] Backend başlatılıyor: http://localhost:5000"
echo "[+] Çıkmak için CTRL+C yapabilirsiniz"
echo ""
echo "========================================"

# Flask uygulamasını başlat
export FLASK_APP=backend/app
export FLASK_ENV=development

python3 -m flask run --host=0.0.0.0 --port=5000 --debug
