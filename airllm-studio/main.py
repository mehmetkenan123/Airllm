#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AirLLM Studio - Next Generation AI-Powered IDE"""

import os, sys, threading, time, socket, uuid, json, webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.serving import run_simple
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, TextIteratorStreamer
import psutil

class LayeredLLM:
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.total_layers = 0
        self.model_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
    def load_tokenizer(self):
        print(f"📦 Tokenizer yükleniyor: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.model_cache_dir, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("✅ Tokenizer hazır!")
        
    def load_model_layered(self):
        print(f"🤖 Model yükleniyor: {self.model_name}")
        config = AutoConfig.from_pretrained(self.model_name, cache_dir=self.model_cache_dir, trust_remote_code=True)
        self.total_layers = getattr(config, 'num_hidden_layers', getattr(config, 'n_layer', 32))
        print(f"📊 Katman sayısı: {self.total_layers}")
        offload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offload")
        os.makedirs(offload_dir, exist_ok=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, cache_dir=self.model_cache_dir,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True, trust_remote_code=True,
            offload_folder=offload_dir, offload_state_dict=True
        )
        print(f"✅ Model yüklendi! {self.total_layers} katman")
        
    def generate(self, prompt, max_new_tokens=512, temperature=0.7, stream_callback=None):
        if not self.tokenizer or not self.model:
            raise Exception("Model yüklenmemiş!")
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
        if self.device == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        gen_cfg = {"max_new_tokens": max_new_tokens, "temperature": temperature, "do_sample": temperature > 0,
                   "top_p": 0.9, "repetition_penalty": 1.1, "pad_token_id": self.tokenizer.pad_token_id,
                   "eos_token_id": self.tokenizer.eos_token_id}
        if stream_callback:
            return self._generate_stream(inputs, gen_cfg, stream_callback)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_cfg)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):]
    
    def _generate_stream(self, inputs, gen_cfg, callback):
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        thread = threading.Thread(target=self.model.generate, kwargs={**inputs, **gen_cfg, "streamer": streamer})
        thread.start()
        text = ""
        for t in streamer:
            text += t
            if callback: callback(t)
        thread.join()
        return text
    
    def unload_model(self):
        if self.model: del self.model
        self.model = None
        if torch.cuda.is_available(): torch.cuda.empty_cache()

AVAILABLE_MODELS = [
    {"id": "qwen2.5-72b", "name": "Qwen2.5 72B", "path": "Qwen/Qwen2.5-72B-Instruct", "size": "~140GB", "category": "huge"},
    {"id": "llama3.1-70b", "name": "Llama 3.1 70B", "path": "meta-llama/Meta-Llama-3.1-70B-Instruct", "size": "~140GB", "category": "huge"},
    {"id": "qwen2.5-32b", "name": "Qwen2.5 32B", "path": "Qwen/Qwen2.5-32B-Instruct", "size": "~60GB", "category": "medium"},
    {"id": "qwen2.5-14b", "name": "Qwen2.5 14B", "path": "Qwen/Qwen2.5-14B-Instruct", "size": "~28GB", "category": "medium"},
    {"id": "qwen2.5-7b", "name": "Qwen2.5 7B", "path": "Qwen/Qwen2.5-7B-Instruct", "size": "~15GB", "category": "small"},
    {"id": "llama3.2-3b", "name": "Llama 3.2 3B", "path": "meta-llama/Llama-3.2-3B-Instruct", "size": "~7GB", "category": "small"},
    {"id": "phi3-mini", "name": "Phi-3 Mini", "path": "microsoft/Phi-3-mini-4k-instruct", "size": "~8GB", "category": "small"},
    {"id": "tinyllama", "name": "TinyLlama", "path": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "size": "~2GB", "category": "tiny"},
]

def scan_local_models():
    found = []
    roots = [os.path.dirname(os.path.abspath(__file__))]
    if os.name != 'nt': roots.extend([os.path.expanduser("~"), "/mnt"])
    keywords = ['models', 'huggingface', 'llm', 'safetensors']
    exts = ['.safetensors', '.bin', '.gguf', '.pt']
    count = 0
    try:
        for root in roots:
            if not os.path.exists(root): continue
            for dp, dns, fns in os.walk(root):
                if count > 3000: break
                dn = os.path.basename(dp).lower()
                if any(k in dn for k in keywords):
                    for f in fns:
                        if any(f.endswith(e) for e in exts):
                            fp = os.path.join(dp, f)
                            try:
                                sz = os.path.getsize(fp) / (1024**3)
                                if sz >= 0.1:
                                    found.append({"id": f"local_{count}", "name": f"{os.path.splitext(f)[0]} ({sz:.1f}GB)",
                                                  "path": fp, "size": f"~{sz:.1f}GB", "type": "local", "category": "local"})
                            except: pass
                        count += 1
                if dp.count(os.sep) - root.count(os.sep) > 6: dns.clear()
    except: pass
    print(f"✅ {len(found)} yerel model bulundu!")
    return found

def get_all_models(): return scan_local_models() + AVAILABLE_MODELS

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)
model_instance = current_model = None
model_loading = False
download_progress = {}
conversations = {}
files_db = {}

@app.route('/')
def index(): return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('frontend', path)

@app.route('/api/status')
def get_status(): return jsonify({"status": "ready" if model_instance else "waiting", "model": current_model})

@app.route('/api/system/info')
def system_info():
    ram = psutil.virtual_memory()
    gpu = {"name": torch.cuda.get_device_name(0)} if torch.cuda.is_available() else "Yok"
    return jsonify({"ram_total": f"{ram.total/1024**3:.1f}GB", "ram_available": f"{ram.available/1024**3:.1f}GB",
                    "ram_percent": ram.percent, "gpu": gpu, "cuda_available": torch.cuda.is_available(), "model_loaded": current_model})

@app.route('/api/models')
def list_models(): return jsonify({"models": get_all_models(), "current_model": current_model, "model_loaded": model_instance is not None, "loading": model_loading})

@app.route('/api/models/download', methods=['POST'])
def download_model():
    global model_instance, current_model, model_loading, download_progress
    data = request.json
    model_path = data.get('model_path')
    if not model_path: return jsonify({'error': 'Model path gerekli'}), 400
    if model_loading: return jsonify({'error': 'Zaten yükleniyor'}), 400
    if current_model == model_path and model_instance: return jsonify({'message': 'Zaten yüklü'})
    model_loading = True
    pid = str(uuid.uuid4())
    download_progress[pid] = {'status': 'starting', 'progress': 0, 'message': 'Başlatılıyor...'}
    def bg():
        global model_instance, current_model, model_loading
        try:
            download_progress[pid] = {'status': 'downloading', 'progress': 30, 'message': 'Tokenizer...'}
            if model_instance: model_instance.unload_model()
            model_instance = LayeredLLM(model_path)
            model_instance.load_tokenizer()
            download_progress[pid] = {'status': 'loading', 'progress': 50, 'message': 'Model...'}
            model_instance.load_model_layered()
            download_progress[pid] = {'status': 'ready', 'progress': 100, 'message': 'Hazır!'}
            current_model = model_path
        except Exception as e:
            download_progress[pid] = {'status': 'error', 'progress': 0, 'message': str(e)}
        finally: model_loading = False
    threading.Thread(target=bg).start()
    return jsonify({'message': 'Başlatıldı', 'progress_id': pid, 'model': model_path})

@app.route('/api/models/progress/<pid>')
def get_progress(pid):
    if pid not in download_progress: return jsonify({'error': 'Bulunamadı'}), 404
    return jsonify(download_progress[pid])

@app.route('/api/models/unload', methods=['POST'])
def unload_model():
    global model_instance, current_model
    if model_instance:
        model_instance.unload_model()
        model_instance = current_model = None
        return jsonify({'message': 'Temizlendi'})
    return jsonify({'message': 'Zaten boş'})

@app.route('/api/chat', methods=['POST'])
def chat():
    global model_instance
    data = request.json
    msg = data.get('message', '')
    cid = data.get('conversation_id', 'default')
    prompt = data.get('system_prompt', 'Sen yardımsever bir AI asistansısın.')
    if not model_instance: return jsonify({'error': 'Model yok!', 'response': '⚠️ Model yüklenmedi'}), 400
    try:
        hist = conversations.get(cid, [])
        if hist:
            parts = [f"{m['role']}: {m['content']}" for m in hist[-10:]]
            full = prompt + "\n\n" + "\n".join(parts) + f"\nassistant: {msg}"
        else:
            full = f"{prompt}\n\nUser: {msg}\nAssistant:"
        resp = model_instance.generate(full, max_new_tokens=512)
        if cid not in conversations: conversations[cid] = []
        conversations[cid].extend([{'role': 'user', 'content': msg}, {'role': 'assistant', 'content': resp.strip()}])
        return jsonify({'response': resp.strip(), 'conversation_id': cid, 'model': current_model})
    except Exception as e:
        return jsonify({'error': str(e), 'response': f'Hata: {e}'}), 500

@app.route('/api/conversations', methods=['DELETE'])
def clear_conv():
    global conversations
    conversations = {}
    return jsonify({'message': 'Temizlendi'})

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files: return jsonify({'error': 'Dosya yok'}), 400
    f = request.files['file']
    cid = request.form.get('conversation_id', str(uuid.uuid4()))
    fn = f"{uuid.uuid4()}_{f.filename}"
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', fn)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    f.save(fp)
    if cid not in files_db: files_db[cid] = []
    files_db[cid].append({'id': str(uuid.uuid4()), 'filename': f.filename, 'filepath': fp})
    return jsonify({'conversation_id': cid, 'filename': f.filename})

def find_port(start=5000):
    p = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: s.bind(('0.0.0.0', p)); return p
            except OSError: p += 1

if __name__ == '__main__':
    print("=" * 60)
    print(" " * 15 + "🚀 AirLLM Studio")
    print("=" * 60)
    print(f"💻 CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available(): print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 RAM: {psutil.virtual_memory().total/1024**3:.1f} GB")
    port = find_port(5000)
    print(f"📡 http://localhost:{port}")
    print("=" * 60)
    def opener(): time.sleep(2); webbrowser.open(f'http://localhost:{port}')
    threading.Thread(target=opener, daemon=True).start()
    try: run_simple('127.0.0.1', port, app, threaded=True)
    except Exception as e: print(f"Hata: {e}")
