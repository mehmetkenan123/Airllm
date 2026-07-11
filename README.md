$ edit /workspace/airllm-studio/main.py
edit /workspace/airllm-studio/main.py
ERROR:
No replacement was performed, old_str `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AirLLM Studio v1.3.0 - LM Studio Tarzı Modern Arayüz
Tek Dosya Çözümü: Backend + AI Engine + Frontend
"""
import os
import sys
import time
import socket
import threading
import webbrowser
import json
import psutil
from flask import Flask, render_template_string, request, jsonify, Response, stream_with_context
# --- YAPAY ZEKA MOTORU (Simülasyon + Gerçek Entegrasyon Hazır) ---
try:
    from airllm import AutoModel
    AIRLLM_AVAILABLE = True
except ImportError:
    AIRLLM_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
model = None
current_model_name = None
def load_model_engine(model_name, gpu_layers=20):
    global model, current_model_name
    if not AIRLLM_AVAILABLE:
        time.sleep(1)
        current_model_name = model_name
        return True
    try:
        model = AutoModel.from_pretrained(model_name, max_memory_allocated="4GB")
        current_model_name = model_name
        return True
    except Exception as e:
        print(f"Model hatası: {e}")
        return False
def generate_response_stream(prompt, max_tokens=512, temperature=0.7):
    if not AIRLLM_AVAILABLE or model is None:
        # Simülasyon Modu
        response_text = f"AirLLM Studio v1.3 ile yanıtlanıyor. Model: {current_model_name or 'Hazır'}.\\n\\nKullanıcı: {prompt}\\n\\nBu bir simülasyon yanıtıdır. Gerçek model yüklenmediğinde bu mesaj görünür. Gerçek kullanım için 'pip install airllm torch transformers' komutunu çalıştırın."
        words = response_text.split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\\n\\n"
            time.sleep(0.05)
        yield "data: [DONE]\\n\\n"
        return
    # Gerçek Inferans
    try:
        input_data = {'input': prompt}
        generation = model.generate(input_data, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
        full_text = generation[0] if isinstance(generation, list) else str(generation)
        tokens = full_text.split()
        for token in tokens:
            yield f"data: {json.dumps({'token': token + ' '})}\\n\\n"
            time.sleep(0.03)
        yield "data: [DONE]\\n\\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
        yield "data: [DONE]\\n\\n"
# --- FLASK UYGULAMASI ---
app = Flask(__name__)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AirLLM Studio v1.3</title>
    <style>
        :root { --bg-dark: #1e1e1e; --bg-panel: #252526; --bg-input: #3c3c3c; --text-main: #cccccc; --text-highlight: #ffffff; --accent: #007fd4; --border: #3e3e42; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); height: 100vh; display: flex; overflow: hidden; }
        .sidebar { width: 260px; background-color: var(--bg-panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        .sidebar-header { padding: 15px; font-weight: bold; color: var(--text-highlight); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .new-chat-btn { background: var(--accent); border: none; color: white; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
        .history-list { flex: 1; overflow-y: auto; list-style: none; padding: 10px; }
        .history-item { padding: 10px; border-radius: 4px; cursor: pointer; font-size: 13px; }
        .history-item:hover { background-color: #37373d; }
        .main-content { flex: 1; display: flex; flex-direction: column; }
        .top-bar { height: 50px; background-color: var(--bg-panel); border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 20px; justify-content: space-between; }
        .model-selector { background: var(--bg-input); color: var(--text-main); border: 1px solid var(--border); padding: 5px 10px; border-radius: 4px; outline: none; }
        .status-indicator { font-size: 12px; color: #4ec9b0; }
        .chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
        .message { display: flex; gap: 15px; max-width: 800px; margin: 0 auto; width: 100%; line-height: 1.6; }
        .avatar { width: 30px; height: 30px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; flex-shrink: 0; }
        .avatar.user { background-color: var(--accent); color: white; }
        .avatar.ai { background-color: #4ec9b0; color: #1e1e1e; }
        .message-content { padding-top: 2px; white-space: pre-wrap; word-wrap: break-word; }
        .input-area { background-color: var(--bg-panel); padding: 20px; border-top: 1px solid var(--border); }
        .input-wrapper { max-width: 800px; margin: 0 auto; position: relative; display: flex; gap: 10px; }
        textarea { flex: 1; background-color: var(--bg-input); border: 1px solid var(--border); color: var(--text-main); padding: 12px; border-radius: 6px; resize: none; height: 50px; outline: none; }
        textarea:focus { border-color: var(--accent); }
        .send-btn { background-color: var(--accent); color: white; border: none; padding: 0 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .send-btn:disabled { background-color: #555; cursor: not-allowed; }
        .settings-panel { width: 280px; background-color: var(--bg-panel); border-left: 1px solid var(--border); padding: 15px; overflow-y: auto; }
        .settings-title { font-weight: bold; margin-bottom: 15px; color: var(--text-highlight); border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .setting-group { margin-bottom: 20px; }
        .setting-label { display: block; font-size: 12px; margin-bottom: 5px; color: #aaaaaa; }
        .setting-input { width: 100%; background: var(--bg-input); border: 1px solid var(--border); color: white; padding: 5px; border-radius: 4px; }
        .range-slider { width: 100%; accent-color: var(--accent); }
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: var(--bg-dark); }
        ::-webkit-scrollbar-thumb { background: #444; border-radius: 5px; }
        .typing-indicator span { display: inline-block; width: 6px; height: 6px; background-color: #aaa; border-radius: 50%; animation: typing 1s infinite; margin: 0 2px; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header"><span>AirLLM Studio</span><button class="new-chat-btn" onclick="startNewChat()">+ Yeni</button></div>
        <ul class="history-list" id="historyList"><li class="history-item active">Yeni Sohbet</li></ul>
    </div>
    <div class="main-content">
        <div class="top-bar">
            <select class="model-selector" id="modelSelect" onchange="changeModel()"><option value="loading">Modeller yükleniyor...</option></select>
            <span class="status-indicator" id="statusIndicator">● Hazır</span>
        </div>
        <div class="chat-container" id="chatContainer">
            <div class="message ai-message"><div class="avatar ai">AI</div><div class="message-content">Merhaba! AirLLM Studio v1.3'e hoşgeldiniz.</div></div>
        </div>
        <div class="input-area">
            <div class="input-wrapper">
                <textarea id="userInput" placeholder="Mesajınızı yazın..." onkeydown="handleKeyDown(event)"></textarea>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">Gönder</button>
            </div>
        </div>
    </div>
    <div class="settings-panel">
        <div class="settings-title">Ayarlar</div>
        <div class="setting-group">
            <label class="setting-label">GPU Katmanları</label>
            <input type="range" class="range-slider" id="gpuLayers" min="0" max="100" value="50" oninput="updateVal('gpuVal', this.value)">
            <div style="text-align: right; font-size: 11px; color: #888;"><span id="gpuVal">50</span></div>
        </div>
        <div class="setting-group">
            <label class="setting-label">Temperature</label>
            <input type="range" class="range-slider" id="temperature" min="0.1" max="1.5" step="0.1" value="0.7" oninput="updateVal('tempVal', this.value)">
            <div style="text-align: right; font-size: 11px; color: #888;"><span id="tempVal">0.7</span></div>
        </div>
        <div class="setting-group">
            <label class="setting-label">Sistem</label>
            <div style="font-size: 11px; color: #888;">RAM: <span id="ramUsage">-</span>% | CPU: <span id="cpuUsage">-</span>%</div>
        </div>
    </div>
    <script>
        let isGenerating = false;
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        window.onload = async () => { await fetchModels(); updateSystemStats(); setInterval(updateSystemStats, 5000); };
        function updateVal(id, val) { document.getElementById(id).innerText = val; }
        
        async function fetchModels() {
            try {
                const res = await fetch('/api/models');
                const data = await res.json();
                const select = document.getElementById('modelSelect');
                select.innerHTML = '';
                if (data.models && data.models.length > 0) {
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m; opt.innerText = m;
                        select.appendChild(opt);
                    });
                } else {
                    select.innerHTML = '<option value="sim">Simülasyon Modu</option>';
                }
            } catch (e) { console.error(e); }
        }
        function handleKeyDown(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }
        
        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'message ' + (role === 'user' ? 'user-message' : 'ai-message');
            div.innerHTML = '<div class="avatar ' + role + '">' + (role === 'user' ? 'Siz' : 'AI') + '</div><div class="message-content">' + text + '</div>';
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return div.querySelector('.message-content');
        }
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text || isGenerating) return;
            isGenerating = true;
            userInput.value = '';
            sendBtn.disabled = true;
            statusIndicator.innerText = "● Düşünüyor...";
            
            appendMessage('user', text);
            const aiDiv = appendMessage('ai', '<div class="typing-indicator"><span></span><span></span><span></span></div>');
            let fullResponse = "";
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: text,
                        model: document.getElementById('modelSelect').value,
                        gpu_layers: parseInt(document.getElementById('gpuLayers').value),
                        temperature: parseFloat(document.getElementById('temperature').value)
                    })
                });
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                aiDiv.innerHTML = "";
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const dataStr = line.replace('data: ', '').trim();
                            if (dataStr === '[DONE]') break;
                            try {
                                const data = JSON.parse(dataStr);
                                if (data.token) { fullResponse += data.token; aiDiv.innerText = fullResponse; chatContainer.scrollTop = chatContainer.scrollHeight; }
                            } catch (e) {}
                        }
                    }
                }
            } catch (error) { aiDiv.innerText = "Hata: " + error.message; }
            finally { isGenerating = false; sendBtn.disabled = false; statusIndicator.innerText = "● Hazır"; userInput.focus(); }
        }
        function startNewChat() { chatContainer.innerHTML = ''; appendMessage('ai', 'Yeni sohbet başlatıldı.'); }
        function changeModel() { statusIndicator.innerText = "● Yükleniyor..."; setTimeout(() => { statusIndicator.innerText = "● Hazır"; }, 1000); }
        
        async function updateSystemStats() {
            try {
                const res = await fetch('/api/system');
                const data = await res.json();
                document.getElementById('ramUsage').innerText = data.ram_used;
                document.getElementById('cpuUsage').innerText = data.cpu_percent;
            } catch (e) {}
        }
    </script>
</body>
</html>
"""` did not appear verbatim in /workspace/airllm-studio/main.py.
