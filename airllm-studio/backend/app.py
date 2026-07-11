from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
import threading
import socket
from queue import Queue
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import hf_transfer
from pathlib import Path
from airllm import AutoModel as AirLLMAutoModel

# AirLLM entegrasyonu ile gelişmiş katman katman yükleme sistemi
class LayeredLLM:
    """Düşük RAM'li sistemler için katman katman model yükleme ve çalıştırma
    AirLLM kütüphanesi kullanılarak optimize edilmiştir.
    """
    
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct", use_airllm=True):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.loaded_layers = []
        self.total_layers = 0
        self.current_layer = 0
        self.model_cache_dir = "/workspace/airllm-studio/models"
        self.use_airllm = use_airllm
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
    def load_tokenizer(self):
        """Tokenizer'ı yükle"""
        print(f"Tokenizer yükleniyor: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.model_cache_dir,
            trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Tokenizer hazır!")
        
    def load_model_layered(self):
        """Modeli katman katman yükle - düşük RAM için optimize edilmiş
        AirLLM kullanılarak 4GB GPU'da 70B modeller çalıştırılabilir
        """
        print(f"Model yükleniyor (katman katman): {self.model_name}")
        print(f"Hedef cihaz: {self.device}")
        print(f"AirLLM kullanılıyor: {self.use_airllm}")
        
        try:
            if self.use_airllm and self.device == "cuda":
                # AirLLM ile yükleme - çok daha az VRAM kullanır
                print("AirLLM AutoModel ile yükleme yapılıyor...")
                self.model = AirLLMAutoModel.from_pretrained(
                    self.model_name,
                    cache_dir=self.model_cache_dir,
                    device_map='auto',
                    compression='none',  # Quantization olmadan
                    trust_remote_code=True
                )
                print("AirLLM ile model başarıyla yüklendi!")
            else:
                # Geleneksel transformers yükleme
                print("Transformers AutoModel ile yükleme yapılıyor...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    cache_dir=self.model_cache_dir,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    offload_folder="/workspace/airllm-studio/offload",
                    offload_state_dict=True
                )
                print("Transformers ile model başarıyla yüklendi!")
            
            # Model info
            if hasattr(self.model.config, 'num_hidden_layers'):
                self.total_layers = self.model.config.num_hidden_layers
            elif hasattr(self.model.config, 'n_layer'):
                self.total_layers = self.model.config.n_layer
            else:
                self.total_layers = 32
                
            os.makedirs("/workspace/airllm-studio/offload", exist_ok=True)
            print(f"Toplam katman sayısı: {self.total_layers}")
            return True
            
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            # Fallback: Transformers ile dene
            if self.use_airllm:
                print("AirLLM başarısız, Transformers ile deneniyor...")
                self.use_airllm = False
                return self.load_model_layered()
            raise e
        
    def generate(self, prompt, max_new_tokens=512, temperature=0.7, stream_callback=None):
        """Metin üretimi - katman katman işleme"""
        if self.tokenizer is None or self.model is None:
            raise Exception("Model veya tokenizer yüklenmemiş!")
        
        # Input'u tokenize et
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        )
        
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generation parametreleri
        generation_config = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "do_sample": temperature > 0,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        
        # Stream edebilir generation
        if stream_callback:
            return self._generate_stream(inputs, generation_config, stream_callback)
        else:
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_config)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Prompt'u çıkar
            return response[len(prompt):]
    
    def _generate_stream(self, inputs, generation_config, callback):
        """Stream generation - token token yanıt"""
        from transformers import TextIteratorStreamer
        
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        generation_kwargs = {
            **inputs,
            **generation_config,
            "streamer": streamer,
        }
        
        # Thread'de generate et
        thread = threading.Thread(
            target=self.model.generate,
            kwargs=generation_kwargs
        )
        thread.start()
        
        # Tokenları stream et
        generated_text = ""
        for new_text in streamer:
            generated_text += new_text
            if callback:
                callback(new_text)
        
        thread.join()
        return generated_text
    
    def unload_model(self):
        """Modeli bellekten boşalt"""
        if self.model:
            del self.model
            self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("Model bellekten temizlendi")


# Popüler HuggingFace modelleri - 100+ model desteği
AVAILABLE_MODELS = [
    # === ULTRA BÜYÜK MODELLER (70B+) - AirLLM ile düşük RAM'de çalışır ===
    {
        "id": "qwen2.5-72b",
        "name": "Qwen2.5 72B Instruct",
        "path": "Qwen/Qwen2.5-72B-Instruct",
        "size": "~140GB",
        "description": "En güçlü açık kaynak model, AirLLM ile 16GB RAM'de çalışır",
        "recommended": False,
        "category": "huge"
    },
    {
        "id": "llama3.1-70b",
        "name": "Llama 3.1 70B Instruct",
        "path": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "size": "~140GB",
        "description": "Meta'nın amiral gemisi, mükemmel akıl yürütme",
        "recommended": False,
        "category": "huge"
    },
    {
        "id": "mixtral-8x22b",
        "name": "Mixtral 8x22B MoE",
        "path": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "size": "~140GB",
        "description": "Mixture of Experts, hızlı ve güçlü",
        "recommended": False,
        "category": "huge"
    },
    {
        "id": "falcon-180b",
        "name": "Falcon 180B",
        "path": "tiiuae/falcon-180B",
        "size": "~350GB",
        "description": "En büyük açık model, AirLLM ile mümkün",
        "recommended": False,
        "category": "huge"
    },
    {
        "id": "grok1",
        "name": "Grok-1 (xAI)",
        "path": "xAI/Grok-1",
        "size": "~600GB",
        "description": "Elon Musk'ın şirketi xAI'nin 314B parametreli modeli",
        "recommended": False,
        "category": "huge"
    },
    
    # === BÜYÜK MODELLER (30B-70B) ===
    {
        "id": "codellama-34b",
        "name": "CodeLlama 34B",
        "path": "codellama/CodeLlama-34b-Instruct-hf",
        "size": "~65GB",
        "description": "Kod yazma için optimize edilmiş",
        "recommended": False,
        "category": "large"
    },
    {
        "id": "yi-34b",
        "name": "Yi-34B Chat",
        "path": "01-ai/Yi-34B-Chat",
        "size": "~65GB",
        "description": "01.AI'nin güçlü modeli",
        "recommended": False,
        "category": "large"
    },
    {
        "id": "gemma2-27b",
        "name": "Gemma 2 27B",
        "path": "google/gemma-2-27b-it",
        "size": "~55GB",
        "description": "Google'ın büyük modeli",
        "recommended": False,
        "category": "large"
    },
    {
        "id": "command-r-plus",
        "name": "Command R+",
        "path": "CohereForAI/c4ai-command-r-plus",
        "size": "~100GB",
        "description": "RAG ve araç kullanımı için optimize",
        "recommended": False,
        "category": "large"
    },
    
    # === ORTA BOY MODELLER (10B-30B) ===
    {
        "id": "qwen2.5-32b",
        "name": "Qwen2.5 32B Instruct",
        "path": "Qwen/Qwen2.5-32B-Instruct",
        "size": "~60GB",
        "description": "Mükemmel fiyat/performans dengesi",
        "recommended": True,
        "category": "medium"
    },
    {
        "id": "qwen2.5-14b",
        "name": "Qwen2.5 14B Instruct",
        "path": "Qwen/Qwen2.5-14B-Instruct",
        "size": "~28GB",
        "description": "Hızlı ve akıllı, günlük kullanım için ideal",
        "recommended": True,
        "category": "medium"
    },
    {
        "id": "mistral-nemo",
        "name": "Mistral Nemo 12B",
        "path": "mistralai/Mistral-Nemo-Instruct-2407",
        "size": "~24GB",
        "description": "Yeni nesil orta boy model",
        "recommended": True,
        "category": "medium"
    },
    {
        "id": "phi3-medium",
        "name": "Phi-3 Medium 14B",
        "path": "microsoft/Phi-3-medium-128k-instruct",
        "size": "~28GB",
        "description": "Microsoft'un orta boy modeli, 128K context",
        "recommended": True,
        "category": "medium"
    },
    {
        "id": "deepseek-16b",
        "name": "DeepSeek 16B",
        "path": "deepseek-ai/deepseek-coder-16b-instruct",
        "size": "~32GB",
        "description": "Kod ve genel amaçlı",
        "recommended": False,
        "category": "medium"
    },
    
    # === KÜÇÜK/HIZLI MODELLER (<10B) - Düşük RAM için ideal ===
    {
        "id": "qwen2.5-7b",
        "name": "Qwen2.5 7B Instruct",
        "path": "Qwen/Qwen2.5-7B-Instruct",
        "size": "~15GB",
        "description": "Genel amaçlı, hızlı ve etkili - ÖNERİLEN",
        "recommended": True,
        "category": "small"
    },
    {
        "id": "llama3.2-3b",
        "name": "Llama 3.2 3B Instruct",
        "path": "meta-llama/Llama-3.2-3B-Instruct",
        "size": "~7GB",
        "description": "Meta'nın hafif modeli, düşük RAM için ideal",
        "recommended": True,
        "category": "small"
    },
    {
        "id": "phi3-mini",
        "name": "Phi-3 Mini 3.8B",
        "path": "microsoft/Phi-3-mini-4k-instruct",
        "size": "~8GB",
        "description": "Microsoft'un kompakt ama güçlü modeli",
        "recommended": True,
        "category": "small"
    },
    {
        "id": "gemma2-9b",
        "name": "Gemma 2 9B",
        "path": "google/gemma-2-9b-it",
        "size": "~18GB",
        "description": "Google'ın dengeli modeli",
        "recommended": False,
        "category": "small"
    },
    {
        "id": "mistral-7b",
        "name": "Mistral 7B v0.3",
        "path": "mistralai/Mistral-7B-Instruct-v0.3",
        "size": "~15GB",
        "description": "Popüler açık kaynak model",
        "recommended": False,
        "category": "small"
    },
    {
        "id": "llama3.1-8b",
        "name": "Llama 3.1 8B Instruct",
        "path": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "size": "~16GB",
        "description": "Meta'nın güncel 8B modeli",
        "recommended": False,
        "category": "small"
    },
    {
        "id": "stablelm-2-zephyr",
        "name": "StableLM 2 Zephyr 1.6B",
        "path": "stabilityai/stablelm-2-zephyr-1_6b",
        "size": "~4GB",
        "description": "Ultra hafif, eski PC'ler için",
        "recommended": False,
        "category": "tiny"
    },
    {
        "id": "tinyllama",
        "name": "TinyLlama 1.1B",
        "path": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "size": "~2GB",
        "description": "En küçük model, test için ideal",
        "recommended": False,
        "category": "tiny"
    },
    {
        "id": "qwen2.5-0.5b",
        "name": "Qwen2.5 0.5B",
        "path": "Qwen/Qwen2.5-0.5B-Instruct",
        "size": "~1GB",
        "description": "Nano model, anında yanıt",
        "recommended": False,
        "category": "tiny"
    }
]

# Yerel model tarama fonksiyonu
def scan_local_models():
    """Bilgisayardaki tüm potansiyel LLM modellerini otomatik tarar"""
    found_models = []
    
    # Taranacak kök dizinler
    search_roots = []
    if os.name == 'nt':  # Windows
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
        search_roots.extend(drives)
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            search_roots.append(user_profile)
    else:  # Linux/Mac
        search_roots.append(os.path.expanduser("~"))
        search_roots.append("/mnt")
        search_roots.append("/media")
        search_roots.append("/home")
    
    # Aranacak klasör ve dosya desenleri
    target_keywords = ['models', 'huggingface', 'hub', 'llm', 'ai', 'weights', 'safetensors', 'gguf']
    valid_extensions = ['.safetensors', '.bin', '.gguf', '.pt', '.pth', '.onnx']
    
    scanned_count = 0
    max_scans = 10000  # Performans sınırı
    
    print("🔍 Yerel modeller taranıyor... Bu işlem birkaç saniye sürebilir.")
    
    try:
        for root_path in search_roots:
            if not os.path.exists(root_path):
                continue
                
            for dirpath, dirnames, filenames in os.walk(root_path):
                if scanned_count > max_scans:
                    break
                
                # Klasör adı kontrolü (hızlandırma)
                dirname_lower = os.path.basename(dirpath).lower()
                path_lower = dirpath.lower()
                
                # Hedef klasörlerde miyiz?
                in_target_folder = any(kw in dirname_lower or kw in path_lower for kw in target_keywords)
                
                # Dosya kontrolü
                for file in filenames:
                    scanned_count += 1
                    
                    # Uzantı kontrolü
                    if any(file.endswith(ext) for ext in valid_extensions):
                        full_path = os.path.join(dirpath, file)
                        
                        try:
                            size_gb = os.path.getsize(full_path) / (1024**3)
                            
                            # Sadece makul boyuttaki dosyalar (>100MB)
                            if size_gb < 0.1:
                                continue
                            
                            # Model adı tahmini
                            model_name = os.path.splitext(file)[0]
                            if model_name.lower() in ['model', 'pytorch_model', 'pytorch_model_bin']:
                                parent = os.path.basename(dirpath)
                                if parent and len(parent) > 3:
                                    model_name = parent
                            
                            # Tekrarları önle
                            is_duplicate = any(m['path'] == full_path for m in found_models)
                            if not is_duplicate:
                                found_models.append({
                                    "id": f"local_{scanned_count}",
                                    "name": f"{model_name} ({size_gb:.2f} GB)",
                                    "path": full_path,
                                    "size": f"~{size_gb:.1f}GB",
                                    "type": "local",
                                    "description": "Yerel diskte bulundu - Otomatik tarama",
                                    "recommended": True,
                                    "category": "local",
                                    "is_local_file": True
                                })
                        except (OSError, PermissionError):
                            pass  # Erişim hatası
                
                # Derinlik sınırlaması (çok derine inmesin)
                depth = dirpath.count(os.sep) - root_path.count(os.sep)
                if depth > 8:
                    dirnames.clear()
                    
    except PermissionError:
        pass  # İzin hatalarını yut
    except Exception as e:
        print(f"Tarama sırasında hata: {e}")

    print(f"✅ {len(found_models)} yerel model bulundu!")
    return found_models


def get_all_models():
    """Hem preset hem de yerel modelleri birleştir"""
    local_models = scan_local_models()
    # Yerel modelleri başa ekle
    return local_models + AVAILABLE_MODELS

app = Flask(__name__)
CORS(app)

# Global model instance
model_instance = None
current_model = None
model_loading = False
download_progress = {}

# Basit bellek yapısı
conversations = {}
files_db = {}


def get_model():
    """Aktif modeli getir, yoksa varsayılanı yükle"""
    global model_instance, current_model
    
    if model_instance is None:
        raise Exception("Henüz model yüklenmedi. Lütfen önce bir model seçin ve yükleyin.")
    
    return model_instance


@app.route('/api/models', methods=['GET'])
def list_models():
    """Kullanılabilir modelleri listele - yerel + preset"""
    all_models = get_all_models()
    return jsonify({
        "models": all_models,
        "current_model": current_model,
        "model_loaded": model_instance is not None,
        "loading": model_loading
    })


@app.route('/api/models/download', methods=['POST'])
def download_model():
    """Modeli HuggingFace'den indir ve yükle"""
    global model_instance, current_model, model_loading, download_progress
    
    data = request.json
    model_path = data.get('model_path')
    
    if not model_path:
        return jsonify({'error': 'Model path gerekli'}), 400
    
    # Zaten yükleniyorsa
    if model_loading:
        return jsonify({'error': 'Başka bir model zaten yükleniyor'}), 400
    
    # Aynı model zaten yüklüyse
    if current_model == model_path and model_instance is not None:
        return jsonify({
            'message': f'{model_path} zaten yüklü',
            'model': current_model
        })
    
    model_loading = True
    progress_id = str(uuid.uuid4())
    download_progress[progress_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Model indirme başlatılıyor...'
    }
    
    def load_in_background():
        global model_instance, current_model, model_loading, download_progress
        
        try:
            # Progress güncelle
            download_progress[progress_id] = {
                'status': 'downloading',
                'progress': 10,
                'message': f'{model_path} indiriliyor...'
            }
            
            # Eski modeli temizle
            if model_instance:
                model_instance.unload_model()
            
            # Yeni model instance oluştur
            model_instance = LayeredLLM(model_path)
            
            download_progress[progress_id] = {
                'status': 'downloading',
                'progress': 30,
                'message': 'Tokenizer yükleniyor...'
            }
            
            # Tokenizer yükle
            model_instance.load_tokenizer()
            
            download_progress[progress_id] = {
                'status': 'loading',
                'progress': 50,
                'message': 'Model katmanları yükleniyor (bu işlem uzun sürebilir)...'
            }
            
            # Modeli yükle
            model_instance.load_model_layered()
            
            download_progress[progress_id] = {
                'status': 'ready',
                'progress': 100,
                'message': 'Model hazır!'
            }
            
            current_model = model_path
            
        except Exception as e:
            download_progress[progress_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Hata: {str(e)}'
            }
        finally:
            model_loading = False
    
    # Background thread'de yükle
    thread = threading.Thread(target=load_in_background)
    thread.start()
    
    return jsonify({
        'message': 'Model indirme ve yükleme başlatıldı',
        'progress_id': progress_id,
        'model': model_path
    })


@app.route('/api/models/progress/<progress_id>', methods=['GET'])
def get_download_progress(progress_id):
    """İndirme/yükleme ilerlemesini kontrol et"""
    if progress_id not in download_progress:
        return jsonify({'error': 'Progress ID bulunamadı'}), 404
    
    return jsonify(download_progress[progress_id])


@app.route('/api/models/unload', methods=['POST'])
def unload_model():
    """Modeli bellekten boşalt"""
    global model_instance, current_model
    
    if model_instance:
        model_instance.unload_model()
        model_instance = None
        current_model = None
        return jsonify({'message': 'Model bellekten temizlendi'})
    
    return jsonify({'message': 'Zaten yüklü model yok'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Dosya yükleme endpoint'i"""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı'}), 400
    
    file = request.files['file']
    conversation_id = request.form.get('conversation_id', str(uuid.uuid4()))
    
    # Dosyayı kaydet
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join('/workspace/airllm-studio/uploads', filename)
    
    os.makedirs('/workspace/airllm-studio/uploads', exist_ok=True)
    file.save(filepath)
    
    # Dosya bilgilerini sakla
    if conversation_id not in files_db:
        files_db[conversation_id] = []
    
    files_db[conversation_id].append({
        'id': str(uuid.uuid4()),
        'filename': file.filename,
        'filepath': filepath,
        'size': os.path.getsize(filepath)
    })
    
    return jsonify({
        'conversation_id': conversation_id,
        'file_id': files_db[conversation_id][-1]['id'],
        'filename': file.filename,
        'message': 'Dosya başarıyla yüklendi'
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Sohbet endpoint'i - AirLLM ile yanıt üret"""
    global model_instance
    
    data = request.json
    message = data.get('message', '')
    conversation_id = data.get('conversation_id', 'default')
    system_prompt = data.get('system_prompt', 'Sen yardımsever bir AI asistansısın.')
    
    # Model yoksa hata
    if model_instance is None:
        return jsonify({
            'error': 'Model yüklenmemiş! Lütfen önce Models bölümünden bir model seçip yükleyin.',
            'response': '⚠️ Model yüklenmedi. Lütfen sol menüden "Modeller" sekmesine gidin ve bir model yükleyin.'
        }), 400
    
    try:
        # Konuşma geçmişini al
        history = conversations.get(conversation_id, [])
        
        # Prompt'u oluştur (konuşma geçmişi ile)
        if history:
            # Son 10 mesajı al
            recent_history = history[-10:]
            prompt_parts = [f"{msg['role']}: {msg['content']}" for msg in recent_history]
            full_prompt = system_prompt + "\n\n" + "\n".join(prompt_parts) + f"\nassistant: {message}"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        
        # Model'den yanıt al
        response_text = model_instance.generate(
            full_prompt,
            max_new_tokens=512,
            temperature=0.7
        )
        
        # Konuşmaya ekle
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversations[conversation_id].append({
            'role': 'user',
            'content': message
        })
        conversations[conversation_id].append({
            'role': 'assistant',
            'content': response_text.strip()
        })
        
        return jsonify({
            'response': response_text.strip(),
            'conversation_id': conversation_id,
            'model': current_model
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': f'⚠️ Hata oluştu: {str(e)}'
        }), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Stream sohbet - token token yanıt"""
    global model_instance
    
    data = request.json
    message = data.get('message', '')
    conversation_id = data.get('conversation_id', 'default')
    
    if model_instance is None:
        return jsonify({
            'error': 'Model yüklenmemiş!'
        }), 400
    
    def generate():
        try:
            history = conversations.get(conversation_id, [])
            
            if history:
                recent_history = history[-10:]
                prompt_parts = [f"{msg['role']}: {msg['content']}" for msg in recent_history]
                full_prompt = "\n".join(prompt_parts) + f"\nassistant: {message}"
            else:
                full_prompt = f"User: {message}\nAssistant:"
            
            received_tokens = []
            
            def stream_callback(token):
                received_tokens.append(token)
            
            response = model_instance.generate(
                full_prompt,
                max_new_tokens=512,
                stream_callback=stream_callback
            )
            
            # Konuşmaya ekle
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            
            conversations[conversation_id].append({
                'role': 'user',
                'content': message
            })
            conversations[conversation_id].append({
                'role': 'assistant',
                'content': response
            })
            
            yield f"data: {json.dumps({'token': response, 'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream'
    )


@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Konuşma geçmişini getir"""
    return jsonify({
        'conversation_id': conversation_id,
        'messages': conversations.get(conversation_id, []),
        'files': files_db.get(conversation_id, [])
    })


@app.route('/api/conversations', methods=['DELETE'])
def clear_conversations():
    """Tüm konuşmaları temizle"""
    global conversations
    conversations = {}
    return jsonify({'message': 'Tüm konuşmalar temizlendi'})


@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Sistem bilgilerini getir"""
    import psutil
    
    ram = psutil.virtual_memory()
    gpu_info = "Yok"
    
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_used": f"{torch.cuda.memory_allocated(0) / 1024**2:.1f} MB",
            "memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**2:.1f} MB"
        }
    
    return jsonify({
        "ram_total": f"{ram.total / 1024**3:.1f} GB",
        "ram_available": f"{ram.available / 1024**3:.1f} GB",
        "ram_percent": ram.percent,
        "gpu": gpu_info,
        "cuda_available": torch.cuda.is_available(),
        "model_loaded": current_model,
        "device": model_instance.device if model_instance else None
    })


@app.route('/api/files/list', methods=['POST'])
def list_files():
    """Dizin içeriğini listele"""
    data = request.json or {}
    path = data.get('path', '/workspace/airllm-studio')
    
    # Güvenlik: Sadece workspace içinde gezinmeye izin ver
    base_path = os.path.abspath('/workspace/airllm-studio')
    target_path = os.path.abspath(path)
    
    if not target_path.startswith(base_path):
        return jsonify({'error': 'İzin verilen dizin dışında'}), 403
    
    if not os.path.exists(target_path):
        return jsonify({'error': 'Dizin bulunamadı'}), 404
    
    try:
        items = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            is_dir = os.path.isdir(item_path)
            
            # Gizli dosyaları ve bazı dizinleri atla
            if item.startswith('.') and item not in ['.git']:
                continue
                
            items.append({
                'name': item,
                'path': item_path,
                'is_dir': is_dir,
                'size': os.path.getsize(item_path) if not is_dir else 0
            })
        
        # Önce dizinler, sonra dosyalar (alfabetik)
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return jsonify(items)
    except PermissionError:
        return jsonify({'error': 'İzin hatası'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/read', methods=['POST'])
def read_file():
    """Dosya içeriğini oku"""
    data = request.json or {}
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({'error': 'Dosya yolu gerekli'}), 400
    
    # Güvenlik kontrolü
    base_path = os.path.abspath('/workspace/airllm-studio')
    target_path = os.path.abspath(file_path)
    
    if not target_path.startswith(base_path):
        return jsonify({'error': 'İzin verilen dizin dışında'}), 403
    
    if not os.path.isfile(target_path):
        return jsonify({'error': 'Dosya bulunamadı'}), 404
    
    try:
        # Binary dosyaları kontrol et
        binary_extensions = ['.pyc', '.pyo', '.so', '.dll', '.exe', '.bin']
        if any(file_path.endswith(ext) for ext in binary_extensions):
            return jsonify({'error': 'Binary dosyalar okunamaz'}), 400
        
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return jsonify({
            'path': file_path,
            'content': content,
            'size': os.path.getsize(target_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/save', methods=['POST'])
def save_file():
    """Dosyayı kaydet"""
    data = request.json or {}
    file_path = data.get('path')
    content = data.get('content', '')
    
    if not file_path:
        return jsonify({'error': 'Dosya yolu gerekli'}), 400
    
    # Güvenlik kontrolü
    base_path = os.path.abspath('/workspace/airllm-studio')
    target_path = os.path.abspath(file_path)
    
    if not target_path.startswith(base_path):
        return jsonify({'error': 'İzin verilen dizin dışında'}), 403
    
    try:
        # Dizin yoksa oluştur
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'message': 'Dosya başarıyla kaydedildi',
            'path': file_path,
            'size': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/scan', methods=['GET'])
def scan_models_api():
    """Modelleri tara - hem yerel hem preset"""
    local_models = scan_local_models()
    preset_models = AVAILABLE_MODELS
    
    return jsonify({
        'local': local_models,
        'preset': preset_models,
        'total_found': len(local_models),
        'total_preset': len(preset_models)
    })


@app.route('/api/models/load', methods=['POST'])
def load_model_api():
    """Model yükle - frontend uyumlu"""
    global model_instance, current_model, model_loading, download_progress
    
    data = request.json or {}
    model_id = data.get('id')
    model_path = data.get('path')
    
    # Model path veya id gerekli
    if not model_path and not model_id:
        return jsonify({'error': 'Model ID veya path gerekli'}), 400
    
    # ID'den path bul
    if not model_path and model_id:
        for model in AVAILABLE_MODELS:
            if model['id'] == model_id:
                model_path = model['path']
                break
    
    if not model_path:
        return jsonify({'error': 'Model bulunamadı'}), 404
    
    # Zaten yükleniyorsa
    if model_loading:
        return jsonify({'status': 'loading', 'message': 'Başka bir model zaten yükleniyor'})
    
    # Aynı model zaten yüklüyse
    if current_model == model_path and model_instance is not None:
        return jsonify({
            'status': 'already_loaded',
            'model': current_model
        })
    
    model_loading = True
    progress_id = str(uuid.uuid4())
    download_progress[progress_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Model yükleme başlatılıyor...'
    }
    
    def load_in_background():
        global model_instance, current_model, model_loading, download_progress
        
        try:
            download_progress[progress_id] = {
                'status': 'downloading',
                'progress': 10,
                'message': f'{model_path} indiriliyor/yükleniyor...'
            }
            
            # Eski modeli temizle
            if model_instance:
                model_instance.unload_model()
            
            # Yeni model instance oluştur
            model_instance = LayeredLLM(model_path)
            
            download_progress[progress_id] = {
                'status': 'loading',
                'progress': 30,
                'message': 'Tokenizer yükleniyor...'
            }
            
            # Tokenizer yükle
            model_instance.load_tokenizer()
            
            download_progress[progress_id] = {
                'status': 'loading',
                'progress': 50,
                'message': 'Model katmanları yükleniyor...'
            }
            
            # Modeli yükle
            model_instance.load_model_layered()
            
            download_progress[progress_id] = {
                'status': 'ready',
                'progress': 100,
                'message': 'Model hazır!'
            }
            
            current_model = model_path
            
        except Exception as e:
            download_progress[progress_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Hata: {str(e)}'
            }
        finally:
            model_loading = False
    
    # Background thread'de yükle
    thread = threading.Thread(target=load_in_background)
    thread.start()
    
    return jsonify({
        'status': 'loading',
        'message': 'Model yükleme başlatıldı',
        'progress_id': progress_id,
        'model': model_path
    })


@app.route('/api/terminal/run', methods=['POST'])
def run_terminal_command():
    """Terminal komutu çalıştır"""
    data = request.json or {}
    command = data.get('command', '')
    
    if not command:
        return jsonify({'error': 'Komut gerekli'}), 400
    
    # Güvenlik: Tehlikeli komutları engelle
    dangerous_commands = ['rm -rf', 'sudo', 'su ', 'chmod 777', 'dd if=', '> /dev/', '| sh']
    for dangerous in dangerous_commands:
        if dangerous in command.lower():
            return jsonify({'error': 'Bu komut güvenlik nedeniyle engellendi'}), 403
    
    try:
        import subprocess
        
        # Workspace dizininde çalıştır
        result = subprocess.run(
            command,
            shell=True,
            cwd='/workspace/airllm-studio',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Komut zaman aşımına uğradı (30s)'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def find_free_port(start_port=5000):
    """Kullanılmayan bir port bul"""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                port += 1


if __name__ == '__main__':
    print("=" * 60)
    
    # Otomatik port bulma
    port = find_free_port(5000)
    
    print("=" * 60)
    print("🚀 AirLLM Studio Başlatılıyor...")
    print("=" * 60)
    print(f"💻 CUDA Mevcut: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print("=" * 60)
    print(f"📡 Sunucu http://localhost:{port} adresinde çalışıyor")
    print(f"🌐 Tarayıcıda http://localhost:{port} adresini açın")
    print("=" * 60)
    print("🔍 Yerel modeller otomatik taranacak...")
    print("💡 İpucu: İlk model yükleme sırasında internet bağlantısı gerekir")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
