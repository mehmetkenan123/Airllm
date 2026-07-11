#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AirLLM Studio v2.0 - Professional Edition
A professional, lightweight local LLM interface designed as a high-performance alternative to LM Studio.
Single File Solution: Backend + AI Engine + Frontend
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

# --- AI ENGINE (Simulation + Real Integration Ready) ---
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
loaded_model_info = {"name": None, "layers": 0, "status": "unloaded"}

# Live logs storage
live_logs = []
MAX_LOGS = 100

def add_log(message, level="info"):
    global live_logs
    timestamp = time.strftime("%H:%M:%S")
    log_entry = {"timestamp": timestamp, "level": level, "message": message}
    live_logs.append(log_entry)
    if len(live_logs) > MAX_LOGS:
        live_logs.pop(0)

def load_model_engine(model_name, gpu_layers=20):
    global model, current_model_name, loaded_model_info
    if not AIRLLM_AVAILABLE:
        time.sleep(1)
        current_model_name = model_name
        loaded_model_info = {"name": model_name, "layers": gpu_layers, "status": "simulation"}
        add_log(f"Model {model_name} loaded in simulation mode", "info")
        return True
    try:
        model = AutoModel.from_pretrained(model_name, max_memory_allocated="4GB")
        current_model_name = model_name
        loaded_model_info = {"name": model_name, "layers": gpu_layers, "status": "loaded"}
        add_log(f"Model {model_name} loaded successfully", "success")
        return True
    except Exception as e:
        print(f"Model error: {e}")
        loaded_model_info = {"name": model_name, "layers": gpu_layers, "status": "failed", "error": str(e)}
        add_log(f"Model load failed: {str(e)}", "error")
        return False

def generate_response_stream(prompt, max_tokens=512, temperature=0.7, system_prompt=""):
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:" if system_prompt else prompt
    
    if not AIRLLM_AVAILABLE or model is None:
        # Simulation Mode
        response_text = f"[AirLLM Studio v2.0 Professional Edition]\n\nModel: {current_model_name or 'Ready (Simulation Mode)'}\nSettings: GPU Layers={loaded_model_info.get('layers', 0)}, Temperature={temperature}\n\nThis is a simulated response. The application is fully functional but running in demonstration mode.\n\nTo enable real AI inference, install the required packages:\n  pip install airllm torch transformers\n\nYour prompt was: \"{prompt}\"\n\nIn production mode, this would generate a contextual response using the selected model."
        words = response_text.split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            time.sleep(0.03)
        yield "data: [DONE]\n\n"
        return

    # Real Inference
    try:
        input_data = {'input': full_prompt}
        generation = model.generate(input_data, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
        full_text = generation[0] if isinstance(generation, list) else str(generation)
        tokens = full_text.split()
        for token in tokens:
            yield f"data: {json.dumps({'token': token + ' '})}\n\n"
            time.sleep(0.02)
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

# --- FLASK APPLICATION ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/models')
def get_models():
    models = [
        {"name": "Qwen/Qwen2.5-7B-Instruct", "info": "7B | Q4_K_M | ~4GB", "active": True},
        {"name": "TinyLlama/TinyLlama-1.1B", "info": "1.1B | Q4_K_M | ~1GB", "active": False},
        {"name": "microsoft/Phi-3-mini", "info": "3.8B | Q4_K_M | ~2GB", "active": False},
        {"name": "mistralai/Mistral-7B-v0.3", "info": "7B | Q4_K_M | ~4GB", "active": False},
        {"name": "Simülasyon Modu", "info": "Demo Mode | No Model Required", "active": False}
    ]
    return jsonify({"models": models})

@app.route('/api/system')
def get_system():
    return jsonify({
        "ram_used": round(psutil.virtual_memory().percent, 1),
        "cpu_percent": round(psutil.cpu_percent(interval=0.1), 1)
    })

@app.route('/api/logs')
def get_logs():
    return jsonify({"logs": live_logs})

@app.route('/api/log', methods=['POST'])
def post_log():
    data = request.json
    add_log(data.get('message', ''), data.get('level', 'info'))
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 512)
    system_prompt = data.get('system_prompt', '')
    
    add_log(f"Chat request received: {message[:50]}...", "info")
    
    def generate():
        for chunk in generate_response_stream(message, max_tokens=max_tokens, temperature=temperature, system_prompt=system_prompt):
            yield chunk
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def find_open_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                port += 1

def open_browser(url):
    def _open():
        time.sleep(1.5)
        webbrowser.open(url)
    threading.Thread(target=_open).start()

if __name__ == '__main__':
    print("========================================")
    print("  AirLLM Studio v2.0 Starting...")
    print("  Professional Edition")
    print("========================================")
    add_log("Application started", "success")
    port = find_open_port()
    url = f"http://localhost:{port}"
    print(f"Server: {url}")
    print("Opening browser...")
    open_browser(url)
    app.run(host='127.0.0.1', port=port, debug=False, threaded=True)
