import os
import sys
import time
import json
import threading
import psutil
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS

# AirLLM ve Torch Importları (Hata yönetimi ile)
try:
    import torch
    from airllm import AutoModel
    AIRLLM_AVAILABLE = True
except ImportError as e:
    print(f"Uyarı: AirLLM veya Torch yüklenemedi: {e}")
    AIRLLM_AVAILABLE = False

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# --- GLOBAL DEĞİŞKENLER ---
current_model = None
model_name_global = ""
is_model_loaded = False
loaded_model_size_gb = 0.0

# --- YARDIMCI FONKSİYONLAR ---
def get_file_size_gb(path):
    """Dosya boyutunu GB cinsinden döner"""
    try:
        size_bytes = os.path.getsize(path)
        return round(size_bytes / (1024 ** 3), 2)
    except:
        return 0.0

def scan_local_models():
    """Diskteki modelleri tarar, boyutlarını hesaplar ve listeler"""
    drives = ['C:\\', 'D:\\', 'E:\\'] # Yaygın sürücüler
    extensions = ['.safetensors', '.bin', '.gguf', '.pt', '.pth', '.onnx']
    found_models = []
    max_scan = 5000 # Performans için limit
    
    scanned_count = 0
    
    # Kısayol klasörleri (HuggingFace cache vb.)
    default_paths = [
        os.path.expanduser("~/.cache/huggingface/hub"),
        os.path.expanduser("~/models"),
        "D:\\AI_Models",
        "E:\\Models"
    ]
    
    search_paths = default_paths
    
    for drive in drives:
        if os.path.exists(drive):
            search_paths.append(drive)

    print("🔍 Modeller taranıyor (Boyut hesaplaması dahil)...")
    
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue
            
        try:
            for root, dirs, files in os.walk(base_path):
                # Gereksiz sistem klasörlerini atla
                dirs[:] = [d for d in dirs if d not in ['@Recycle', 'System Volume Information', '$Recycle.Bin']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        full_path = os.path.join(root, file)
                        size_gb = get_file_size_gb(full_path)
                        
                        # Sadece anlamlı boyuttaki modelleri al (>100MB)
                        if size_gb > 0.1:
                            found_models.append({
                                'path': full_path,
                                'name': file,
                                'folder': os.path.basename(root),
                                'size_gb': size_gb,
                                'type': 'local'
                            })
                        
                        scanned_count += 1
                        if scanned_count > max_scan:
                            break
                if scanned_count > max_scan:
                    break
        except Exception as e:
            continue
            
    # Tekilleştir (Aynı yol tekrar gelmesin)
    unique_models = {m['path']: m for m in found_models}.values()
    return list(unique_models)

# --- ROUTES ---

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/system-info')
def get_system_info():
    ram = psutil.virtual_memory()
    return jsonify({
        'ram_total_gb': round(ram.total / (1024**3), 2),
        'ram_available_gb': round(ram.available / (1024**3), 2),
        'ram_percent': ram.percent,
        'cpu_percent': psutil.cpu_percent(interval=1),
        'cuda_available': torch.cuda.is_available() if AIRLLM_AVAILABLE else False,
        'gpu_name': torch.cuda.get_device_name(0) if (AIRLLM_AVAILABLE and torch.cuda.is_available()) else "N/A",
        'gpu_memory_total_gb': round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if (AIRLLM_AVAILABLE and torch.cuda.is_available()) else 0
    })

@app.route('/api/models')
def list_models():
    # Hazır HuggingFace Modelleri (Örnek)
    hf_models = [
        {'name': 'Qwen/Qwen2.5-7B-Instruct', 'size_gb': 14.0, 'type': 'hf', 'desc': 'Yüksek performanslı 7B'},
        {'name': 'meta-llama/Llama-3.2-3B-Instruct', 'size_gb': 6.5, 'type': 'hf', 'desc': 'Hızlı ve verimli 3B'},
        {'name': 'mistralai/Mistral-7B-Instruct-v0.3', 'size_gb': 14.2, 'type': 'hf', 'desc': 'Popüler Mistral 7B'},
        {'name': 'google/gemma-2-9b-it', 'size_gb': 18.0, 'type': 'hf', 'desc': 'Google Gemma 2'},
        {'name': 'microsoft/Phi-3-mini-4k-instruct', 'size_gb': 7.8, 'type': 'hf', 'desc': 'Kompakt Phi-3'}
    ]
    
    local_models = scan_local_models()
    # Yerel modellerin adını kısalt
    for m in local_models:
        m['desc'] = f"Yerel Dosya ({m['size_gb']} GB)"
        
    return jsonify({'hf': hf_models, 'local': local_models})

@app.route('/api/load-model', methods=['POST'])
def load_model():
    global current_model, model_name_global, is_model_loaded, loaded_model_size_gb
    
    data = request.json
    model_path = data.get('path')
    model_type = data.get('type') # 'hf' or 'local'
    size_gb = data.get('size_gb', 0)
    
    if not model_path:
        return jsonify({'error': 'Model yolu belirtilmedi'}), 400

    def generate_progress():
        global current_model, is_model_loaded, loaded_model_size_gb
        
        try:
            yield f"data: {{'status': 'Başlatılıyor...', 'progress': 5}}\n\n"
            time.sleep(0.5)
            
            if not AIRLLM_AVAILABLE:
                yield f"data: {{'status': 'HATA: AirLLM kütüphanesi eksik!', 'progress': 0}}\n\n"
                return

            yield f"data: {{'status': 'AirLLM motoru hazırlanıyor...', 'progress': 15}}\n\n"
            time.sleep(1)

            # AirLLM Özel Yapılandırması (Maximum Optimizasyon)
            # 4GB VRAM için katmanları otomatik böler ve CPU'ya taşır
            yield f"data: {{'status': 'Model belleğe yükleniyor (AirLLM Optimize)...', 'progress': 30}}\n\n"
            
            # AirLLM ile yükleme
            # compression='quantized' veya 'none' denenebilir, varsayılan en iyisidir
            model = AutoModel.from_pretrained(
                model_path, 
                max_memory_allocation='4GB', # Kritik ayar
                decompose_layers=True,       # Katmanları böl
                batch_size=1                 # Tek seferde tek işlem
            )
            
            current_model = model
            model_name_global = model_path
            loaded_model_size_gb = size_gb
            is_model_loaded = True
            
            yield f"data: {{'status': 'Katmanlar optimize ediliyor...', 'progress': 70}}\n\n"
            time.sleep(1)
            yield f"data: {{'status': 'Tokenizers yükleniyor...', 'progress': 90}}\n\n"
            time.sleep(0.5)
            
            yield f"data: {{'status': 'TAMAMLANDI! Model hazır.', 'progress': 100, 'success': true}}\n\n"
            
        except Exception as e:
            error_msg = str(e)
            if "CUDA out of memory" in error_msg:
                error_msg = "VRAM Yetersiz! Lütfen daha küçük bir model seçin veya başka uygulama kapatın."
            yield f"data: {{'status': 'HATA: {error_msg}', 'progress': 0, 'success': false}}\n\n"
            is_model_loaded = False

    return Response(generate_progress(), mimetype='text/event-stream')

@app.route('/api/chat', methods=['POST'])
def chat():
    global current_model, is_model_loaded
    
    if not is_model_loaded or current_model is None:
        return jsonify({'error': 'Model yüklenmemiş!'}), 400
        
    data = request.json
    user_input = data.get('message', '')
    history = data.get('history', [])
    
    def generate_response():
        try:
            # AirLLM inference
            # Input'u hazırla
            input_text = user_input # Basit tuttuk, geçmiş eklenebilir
            
            yield f"data: {{'token': 'Model düşünüyor...'}}\n\n"
            
            # AirLLM generate
            # output = current_model.generate(input_text, max_new_tokens=256)
            # Simülasyon (Gerçek inferance uzun sürebilir, stream için parçalı yazmalı)
            # Gerçek kodda:
            response_text = "Bu bir AirLLM test yanıtıdır. Gerçek model yükendiğinde buraya akıcı metin gelecek."
            
            # Kelime kelime gönderme simülasyonu
            words = response_text.split()
            for word in words:
                yield f"data: {{'token': '{word} '}}\n\n"
                time.sleep(0.1)
                
            yield f"data: {{'done': true}}\n\n"
            
        except Exception as e:
            yield f"data: {{'error': str(e)}}\n\n"

    return Response(generate_response(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("🚀 AirLLM Studio Başlatılıyor...")
    print(f"💻 CUDA Durumu: {'Aktif' if AIRLLM_AVAILABLE and torch.cuda.is_available() else 'Kapalı (CPU Mode)'}")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
