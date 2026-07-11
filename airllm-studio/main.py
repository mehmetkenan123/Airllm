import os
import sys
import webbrowser
import threading
import time
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.serving import run_simple

# AirLLM ve diğer modüller buraya import edilecek (gerçek uygulamada)
# from backend.app import app, initialize_model, chat_with_model

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Global değişkenler
MODEL_STATUS = "ready"
CURRENT_MODEL = None

@app.route('/')
def index():
    """Ana sayfayı serve et"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """CSS, JS vb. statik dosyaları serve et"""
    return send_from_directory('frontend', path)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Sistem durumunu döndür"""
    return jsonify({
        "status": MODEL_STATUS,
        "model": CURRENT_MODEL,
        "message": "AirLLM Studio çalışıyor."
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Sohbet isteğini işle (Buraya gerçek AI mantığı gelecek)"""
    data = request.json
    user_message = data.get('message', '')
    
    # Simüle edilmiş yanıt (Gerçek AirLLM entegrasyonu buraya)
    response_text = f"AirLLM Motoru: '{user_message}' mesajını aldım. Şu an model yükleniyor ve cevap hazırlanıyor..."
    
    return jsonify({
        "response": response_text,
        "model": CURRENT_MODEL or "default",
        "tokens": len(user_message.split()) * 2
    })

def open_browser():
    """Tarayıcıyı otomatik aç"""
    time.sleep(1.5)  # Sunucunun başlaması için bekle
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("🚀 AirLLM Studio Başlatılıyor...")
    print("⏳ Lütfen bekleyin, tarayıcı otomatik açılacak.")
    
    # Tarayıcıyı ayrı bir thread'de aç
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Sunucuyu başlat (host='0.0.0.0' dış erişime izin verir, gerekirse '127.0.0.1' yapın)
    # threaded=True aynı anda birden fazla istek için gereklidir
    try:
        run_simple('127.0.0.1', 5000, app, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"Hata oluştu: {e}")
        input("Çıkmak için Enter'a basın...")
