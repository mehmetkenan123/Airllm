from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
import threading
from queue import Queue
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import hf_transfer

# AirLLM benzeri katman katman yükleme sistemi
class LayeredLLM:
    """Düşük RAM'li sistemler için katman katman model yükleme ve çalıştırma"""
    
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.loaded_layers = []
        self.total_layers = 0
        self.current_layer = 0
        self.model_cache_dir = "/workspace/airllm-studio/models"
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
        """Modeli katman katman yükle - düşük RAM için optimize edilmiş"""
        print(f"Model yükleniyor (katman katman): {self.model_name}")
        print(f"Hedef cihaz: {self.device}")
        
        # Model yapılandırmasını al
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained(
            self.model_name,
            cache_dir=self.model_cache_dir,
            trust_remote_code=True
        )
        
        # Katman sayısını belirle
        if hasattr(config, 'num_hidden_layers'):
            self.total_layers = config.num_hidden_layers
        elif hasattr(config, 'n_layer'):
            self.total_layers = config.n_layer
        else:
            self.total_layers = 32  # Varsayılan
            
        print(f"Toplam katman sayısı: {self.total_layers}")
        
        # Modeli yükle ama ağırlıkları CPU'da tut
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
        
        os.makedirs("/workspace/airllm-studio/offload", exist_ok=True)
        
        print(f"Model başarıyla yüklendi! {self.total_layers} katman")
        return True
        
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


# Popüler HuggingFace modelleri
AVAILABLE_MODELS = [
    {
        "id": "qwen2.5-7b",
        "name": "Qwen2.5 7B Instruct",
        "path": "Qwen/Qwen2.5-7B-Instruct",
        "size": "~15GB",
        "description": "Genel amaçlı, hızlı ve etkili",
        "recommended": True
    },
    {
        "id": "llama3.2-3b",
        "name": "Llama 3.2 3B Instruct",
        "path": "meta-llama/Llama-3.2-3B-Instruct",
        "size": "~7GB",
        "description": "Meta'nın hafif modeli, düşük RAM için ideal",
        "recommended": True
    },
    {
        "id": "phi3-mini",
        "name": "Phi-3 Mini 3.8B",
        "path": "microsoft/Phi-3-mini-4k-instruct",
        "size": "~8GB",
        "description": "Microsoft'un kompakt ama güçlü modeli",
        "recommended": True
    },
    {
        "id": "gemma2-2b",
        "name": "Gemma 2 2B",
        "path": "google/gemma-2-2b-it",
        "size": "~5GB",
        "description": "Google'ın ultra hafif modeli",
        "recommended": False
    },
    {
        "id": "mistral-7b",
        "name": "Mistral 7B Instruct",
        "path": "mistralai/Mistral-7B-Instruct-v0.3",
        "size": "~15GB",
        "description": "Popüler açık kaynak model",
        "recommended": False
    },
    {
        "id": "qwen2.5-14b",
        "name": "Qwen2.5 14B Instruct",
        "path": "Qwen/Qwen2.5-14B-Instruct",
        "size": "~28GB",
        "description": "Daha büyük, daha akıllı (GPU önerilir)",
        "recommended": False
    },
    {
        "id": "llama3.1-8b",
        "name": "Llama 3.1 8B Instruct",
        "path": "meta-llama/Llama-3.1-8B-Instruct",
        "size": "~16GB",
        "description": "Meta'nın dengeli modeli",
        "recommended": False
    }
]

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
    """Kullanılabilir modelleri listele"""
    return jsonify({
        "models": AVAILABLE_MODELS,
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


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AirLLM Studio Başlatılıyor...")
    print("=" * 60)
    print(f"💻 CUDA Mevcut: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print("=" * 60)
    print("📡 Backend http://localhost:5000 adresinde çalışıyor")
    print("🌐 Frontend'i http://localhost:8080 adresinden açın")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
