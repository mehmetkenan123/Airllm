#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AirLLM Studio - Tek Dosya Sürüm (Full Stack)
Backend, Frontend ve AI Motoru tek dosyada birleşti.
"""
import os
import sys
import time
import threading
import webbrowser
import socket
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS

# --- AI MOTORU (Simülasyon / Gerçek Entegrasyon Hazır) ---
class AirLLMEngine:
    def __init__(self):
        self.model_name = "Qwen2.5-7B-Instruct-AirLLM"
        self.loaded = False
    
    def load_model(self, model_path=None):
        """Modeli yükle (Gerçek entegrasyon için buraya transformers kodu gelir)"""
        print(f"[AI] Model yükleniyor: {model_path or self.model_name}...")
        time.sleep(1) # Simülasyon gecikmesi
        self.loaded = True
        return True
    
    def generate_stream(self, prompt, max_tokens=256):
        """Streaming yanıt üretici"""
        if not self.loaded:
            yield "Hata: Model henüz yüklenmedi.\n"
            return
        
        # Basit bir yanıt simülasyonu (Gerçek AI burada devreye girer)
        response_text = f"AirLLM Studio'dan merhaba! '{prompt}' sorunuz işleniyor.\n\n"
        response_text += "Bu şu anda bir test yanıtıdır. Gerçek model entegrasyonu için 'transformers' kütüphanesi aktif edilecektir.\n"
        response_text += "Şu anki sistem durumu: Online ve hazır."
        
        for word in response_text.split():
            yield word + " "
            time.sleep(0.05) # Yazma efekti

# --- WEB SUNUCUSU ---
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
engine = AirLLMEngine()

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@app.route('/')
def index():
    return send_file('index.html') if os.path.exists('index.html') else jsonify({"error": "Frontend dosyası eksik"}), 404

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "model": engine.model_name if engine.loaded else "Yüklenmedi",
        "version": "1.0.0-Turbo"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    
    def generate():
        for token in engine.generate_stream(prompt):
            yield f"data: {token}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify([
        {"id": "qwen-2.5-7b", "name": "Qwen 2.5 7B (Optimized)"},
        {"id": "llama-3-8b", "name": "Llama 3 8B"},
        {"id": "phi-3-mini", "name": "Phi-3 Mini"}
    ])

# --- HTML ARAYÜZÜ (Dinamik Oluşturma) ---
def create_frontend():
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AirLLM Studio</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e2e; color: #fff; margin: 0; display: flex; height: 100vh; }
        #sidebar { width: 250px; background: #252537; padding: 20px; border-right: 1px solid #333; }
        #main { flex: 1; padding: 20px; display: flex; flex-direction: column; }
        h1 { color: #89b4fa; }
        .btn { background: #89b4fa; color: #1e1e2e; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .btn:hover { background: #b4befe; }
        #chat-box { flex: 1; background: #313244; border-radius: 10px; padding: 20px; overflow-y: auto; margin-bottom: 20px; }
        .msg { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #45475a; text-align: right; }
        .ai { background: #585b70; }
        #input-area { display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; border-radius: 5px; border: none; background: #313244; color: white; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>AirLLM Studio</h2>
        <p>Durum: <span id="status" style="color:#a6e3a1">Bağlanıyor...</span></p>
        <button class="btn" onclick="location.reload()" style="width:100%; margin-top:20px;">Yenile</button>
    </div>
    <div id="main">
        <h1>Hoşgeldiniz</h1>
        <div id="chat-box">
            <div class="msg ai">Merhaba! Ben AirLLM Asistanı. Nasıl yardımcı olabilirim?</div>
        </div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="Sorunuzu yazın..." onkeypress="if(event.key==='Enter') send()">
            <button class="btn" onclick="send()">Gönder</button>
        </div>
    </div>
    <script>
        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('status').innerText = data.status === 'online' ? 'Aktif (' + data.model + ')' : 'Kapalı';
            } catch(e) { document.getElementById('status').innerText = 'Hata'; }
        }
        async function send() {
            const input = document.getElementById('user-input');
            const box = document.getElementById('chat-box');
            const txt = input.value;
            if(!txt) return;
            
            box.innerHTML += `<div class="msg user">${txt}</div>`;
            input.value = '';
            box.scrollTop = box.scrollHeight;
            
            const res = await fetch('/api/chat', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: txt})
            });
            
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            box.innerHTML += `<div class="msg ai" id="ai-res"></div>`;
            const aiDiv = document.getElementById('ai-res');
            
            while(true) {
                const {done, value} = await reader.read();
                if(done) break;
                const chunk = decoder.decode(value);
                aiDiv.innerText += chunk;
                box.scrollTop = box.scrollHeight;
            }
        }
        setInterval(checkStatus, 2000);
        checkStatus();
    </script>
</body>
</html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def open_browser():
    time.sleep(2)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == '__main__':
    print("========================================")
    print("  AirLLM Studio Başlatılıyor...")
    print("========================================")
    
    # Frontend'i oluştur
    create_frontend()
    print("[OK] Arayüz hazırlandı.")
    
    # Port belirle
    PORT = get_free_port()
    print(f"[OK] Port seçildi: {PORT}")
    
    # Tarayıcıyı aç
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Sunucuyu başlat
    try:
        app.run(host='0.0.0.0', port=PORT, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"HATA: {e}")
        input("Çıkmak için Enter'a basın...")
