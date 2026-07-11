#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AirLLM Studio - Tek Dosya Sürüm (Windows Uyumlu)
Flask Web Arayüzü + AI Model Yönetimi
"""

import os
import sys
import time
import threading
import webbrowser
import socket
from flask import Flask, render_template_string, jsonify, request, Response
import psutil

# --- MODEL AYARLARI ---
AVAILABLE_MODELS = {
    "Qwen/Qwen2.5-0.5B-Instruct": "Hızlı ve hafif (0.5B)",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": "Dengeli performans (1.1B)",
    "microsoft/phi-2": "Microsoft Phi-2 (2.7B)",
    "google/gemma-2b-it": "Google Gemma 2B",
    "meta-llama/Llama-3.2-1B-Instruct": "Meta Llama 3.2 (1B)",
    "Qwen/Qwen2.5-1.5B-Instruct": "Orta seviye (1.5B)",
    "microsoft/Phi-3-mini-4k-instruct": "Phi-3 Mini",
    "local-model": "Yerel Model (Manuel)"
}

app = Flask(__name__)

# Global değişkenler
current_model = None
chat_history = []

# --- HTML ARAYÜZÜ ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AirLLM Studio</title>
    <style>
        :root { --bg: #1e1e2e; --panel: #2a2a3c; --text: #cdd6f4; --accent: #89b4fa; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: var(--accent); text-align: center; }
        .panel { background: var(--panel); padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        select, button, input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #444; background: #333; color: white; font-size: 14px; box-sizing: border-box; }
        button { background: var(--accent); color: #111; font-weight: bold; cursor: pointer; border: none; transition: 0.2s; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        #chat-box { height: 400px; overflow-y: auto; background: #111; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #444; }
        .msg { margin: 10px 0; padding: 10px; border-radius: 8px; max-width: 80%; }
        .user { background: #444; margin-left: auto; text-align: right; }
        .ai { background: var(--accent); color: #111; }
        .status { font-size: 12px; color: #aaa; text-align: center; margin-top: 10px; }
        .loading::after { content: '...'; animation: dots 1.5s infinite; }
        @keyframes dots { 0%{content:'.'} 33%{content:'..'} 66%{content:'...'} }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 AirLLM Studio</h1>
    
    <div class="panel">
        <label>Model Seç:</label>
        <select id="model-select"></select>
        <button onclick="loadModel()">Modeli Yükle / Değiştir</button>
        <div id="status" class="status">Durum: Beklemede</div>
    </div>

    <div class="panel">
        <div id="chat-box"></div>
        <textarea id="user-input" rows="3" placeholder="Mesajınızı yazın..."></textarea>
        <button onclick="sendMessage()" id="send-btn">Gönder</button>
    </div>
</div>

<script>
    const chatBox = document.getElementById('chat-box');
    const statusDiv = document.getElementById('status');
    const modelSelect = document.getElementById('model-select');

    // Modelleri yükle
    fetch('/api/models')
        .then(r => r.json())
        .then(data => {
            for (const [id, desc] of Object.entries(data)) {
                const opt = document.createElement('option');
                opt.value = id;
                opt.textContent = id + " (" + desc + ")";
                modelSelect.appendChild(opt);
            }
        });

    function updateStatus(msg) { statusDiv.textContent = "Durum: " + msg; }

    function loadModel() {
        const model = modelSelect.value;
        updateStatus("Model yükleniyor: " + model);
        fetch('/api/load', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model: model})
        })
        .then(r => r.json())
        .then(data => {
            if(data.success) updateStatus("Hazır: " + model);
            else updateStatus("Hata: " + data.error);
        });
    }

    function sendMessage() {
        const input = document.getElementById('user-input');
        const msg = input.value.trim();
        if (!msg) return;

        // Kullanıcı mesajını ekle
        chatBox.innerHTML += `<div class="msg user">${msg}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        // AI yanıt alanı oluştur
        const aiDiv = document.createElement('div');
        aiDiv.className = 'msg ai loading';
        aiDiv.textContent = 'Düşünüyor';
        chatBox.appendChild(aiDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        })
        .then(r => r.json())
        .then(data => {
            aiDiv.classList.remove('loading');
            aiDiv.textContent = data.response || "Hata oluştu.";
        });
    }
</script>
</body>
</html>
"""

# --- API ENDPOINTLERİ ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    return jsonify({
        "status": "running",
        "model": current_model,
        "ram_usage": f"{psutil.virtual_memory().percent}%",
        "cpu_usage": f"{psutil.cpu_percent()}%"
    })

@app.route('/api/models')
def get_models():
    return jsonify(AVAILABLE_MODELS)

@app.route('/api/load', methods=['POST'])
def load_model():
    global current_model
    data = request.json
    model_id = data.get('model')
    
    if not model_id:
        return jsonify({"success": False, "error": "Model ID gerekli"})
    
    # Simüle edilmiş yükleme (Gerçek implementasyon için transformers kütüphanesi gerekir)
    # Burada sadece simülasyon yapıyoruz ki uygulama çökmesin
    current_model = model_id
    time.sleep(1) # Yükleme gecikmesi taklidi
    
    return jsonify({"success": True, "message": f"{model_id} yüklendi."})

@app.route('/api/chat', methods=['POST'])
def chat():
    global chat_history
    data = request.json
    user_msg = data.get('message', '')
    
    if not user_msg:
        return jsonify({"response": "Lütfen bir mesaj girin."})
    
    chat_history.append({"role": "user", "content": user_msg})
    
    # Basit bir echo-bot simülasyonu (Gerçek AI entegrasyonu buraya gelecek)
    # Gerçek senaryoda burada HuggingFace modeli çağrılır.
    response_text = f"[Simülasyon] '{user_msg}' mesajını aldım. Şu an {current_model or 'modelsiz'} modundayım. Gerçek AI yanıtı için backend entegrasyonu gereklidir."
    
    chat_history.append({"role": "assistant", "content": response_text})
    
    return jsonify({"response": response_text})

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def open_browser(port):
    time.sleep(2)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == '__main__':
    print("AirLLM Studio Başlatılıyor...")
    port = find_free_port()
    print(f"Sunucu http://localhost:{port} adresinde çalışacak.")
    
    # Tarayıcıyı ayrı thread'de aç
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Hata: {e}")
        input("Çıkmak için Enter'a basın...")
