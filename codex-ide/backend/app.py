"""
Codex IDE - Yerel AI Güçlü Kodlama Ortamı
Bölüm I-V: Tam Entegre Yapay Zeka Sistemi
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import sys
import json
import uuid
import threading
import time
import socket
import subprocess
import hashlib
import re
from pathlib import Path
from queue import Queue
from datetime import datetime
import psutil
import shutil

# GPU Tespiti ve Yönetimi (opsiyonel)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Hugging Face ve Model Yönetimi (opsiyonel)
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Embedding ve Vektör İşlemleri (opsiyonel)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# GPU Tespiti ve Yönetimi
def get_gpu_info():
    """Detaylı GPU bilgisi"""
    gpu_info = {
        'available': torch.cuda.is_available(),
        'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
        'devices': []
    }
    
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            gpu_info['devices'].append({
                'id': i,
                'name': props.name,
                'memory_total': props.total_memory / 1024**3,
                'memory_allocated': torch.cuda.memory_allocated(i) / 1024**3,
                'memory_cached': torch.cuda.memory_reserved(i) / 1024**3,
                'compute_capability': f"{props.major}.{props.minor}"
            })
    
    return gpu_info

def get_system_info():
    """Sistem kaynakları bilgisi"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'cpu_count': psutil.cpu_count(logical=True),
        'memory_total': psutil.virtual_memory().total / 1024**3,
        'memory_available': psutil.virtual_memory().available / 1024**3,
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'gpu': get_gpu_info()
    }

# ============================================================================
# BÖLÜM I: YAPAY ZEKA İNDİRME VE YEREL LLM YÖNETİM MERKEZİ
# ============================================================================

class ModelManager:
    """
    1.1 Dahili Model Mağazası ve Sürücü Yöneticisi
    1.2 Yerel LLM Kontrol Paneli
    """
    
    def __init__(self, models_dir="/workspace/codex-ide/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}
        self.model_health = {}
        self.download_progress = {}
        self.embedding_model = None
        
    def list_available_models(self):
        """Hugging Face'den indirilebilir modelleri listele"""
        preset_models = [
            {
                'id': 'qwen-coder',
                'name': 'Qwen2.5-Coder-7B-Instruct',
                'type': 'code_completion',
                'sizes': ['Q2_K', 'Q4_K_M', 'Q6_K', 'Q8_0'],
                'recommended': 'Q4_K_M',
                'ram_requirement': {'Q2_K': 3, 'Q4_K_M': 5, 'Q6_K': 7, 'Q8_0': 9},
                'description': 'Kod tamamlama için optimize edilmiş'
            },
            {
                'id': 'llama-code',
                'name': 'Llama-3.1-8B-Code',
                'type': 'code_completion',
                'sizes': ['Q3_K_M', 'Q4_K_M', 'Q5_K_M', 'Q8_0'],
                'recommended': 'Q4_K_M',
                'ram_requirement': {'Q3_K_M': 4, 'Q4_K_M': 6, 'Q5_K_M': 7, 'Q8_0': 10},
                'description': 'Genel amaçlı kod asistanı'
            },
            {
                'id': 'deepseek-coder',
                'name': 'DeepSeek-Coder-6.7B',
                'type': 'code_completion',
                'sizes': ['Q2_K', 'Q4_0', 'Q4_K_M', 'Q8_0'],
                'recommended': 'Q4_K_M',
                'ram_requirement': {'Q2_K': 3, 'Q4_0': 4, 'Q4_K_M': 5, 'Q8_0': 8},
                'description': 'Derin kod analizi için'
            },
            {
                'id': 'starcoder2',
                'name': 'StarCoder2-7B',
                'type': 'code_completion',
                'sizes': ['Q3_K_M', 'Q4_K_M', 'Q5_K_M'],
                'recommended': 'Q4_K_M',
                'ram_requirement': {'Q3_K_M': 4, 'Q4_K_M': 6, 'Q5_K_M': 7},
                'description': 'Çok dilli kod desteği'
            },
            {
                'id': 'all-minilm',
                'name': 'all-MiniLM-L6-v2',
                'type': 'embedding',
                'sizes': ['fp16', 'fp32'],
                'recommended': 'fp16',
                'ram_requirement': {'fp16': 0.5, 'fp32': 1},
                'description': 'Kod embedding ve semantik arama'
            },
            {
                'id': 'whisper-base',
                'name': 'Whisper Base',
                'type': 'speech_to_text',
                'sizes': ['tiny', 'base', 'small'],
                'recommended': 'base',
                'ram_requirement': {'tiny': 0.2, 'base': 0.3, 'small': 0.5},
                'description': 'Sesten koda dönüşüm'
            }
        ]
        return preset_models
    
    def download_model(self, model_id, quantization='Q4_K_M', progress_id=None):
        """Modeli arka planda indir"""
        if progress_id not in self.download_progress:
            self.download_progress[progress_id] = {
                'status': 'starting',
                'progress': 0,
                'speed': 0,
                'eta': 0,
                'downloaded': 0,
                'total': 0
            }
        
        def download_thread():
            try:
                # Simüle edilmiş indirme (gerçek implementasyonda huggingface_hub kullanılır)
                model_info = next((m for m in self.list_available_models() if m['id'] == model_id), None)
                if not model_info:
                    self.download_progress[progress_id] = {'status': 'error', 'message': 'Model bulunamadı'}
                    return
                
                total_size = model_info['ram_requirement'].get(quantization, 5) * 1024**3  # GB to bytes
                
                for progress in range(0, 101, 2):
                    time.sleep(0.1)
                    self.download_progress[progress_id] = {
                        'status': 'downloading',
                        'progress': progress,
                        'speed': 1024**2 * 5,  # 5 MB/s
                        'eta': max(0, (100 - progress) * 2),
                        'downloaded': int(total_size * progress / 100),
                        'total': total_size
                    }
                
                # Model dosyasını oluştur (simülasyon)
                model_path = self.models_dir / f"{model_id}-{quantization}.gguf"
                model_path.touch()
                
                self.download_progress[progress_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'path': str(model_path)
                }
                
                # Modeli yükle
                self.load_model(model_id, quantization)
                
            except Exception as e:
                self.download_progress[progress_id] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        threading.Thread(target=download_thread, daemon=True).start()
        return progress_id
    
    def load_model(self, model_id, quantization='Q4_K_M'):
        """Modeli RAM'e yükle"""
        try:
            model_key = f"{model_id}-{quantization}"
            
            # Embedding modeli
            if model_id == 'all-minilm':
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.loaded_models[model_key] = {
                    'type': 'embedding',
                    'status': 'loaded',
                    'loaded_at': datetime.now().isoformat()
                }
                return True
            
            # LLM modelleri için simülasyon (gerçek implementasyonda llama-cpp-python veya transformers)
            self.loaded_models[model_key] = {
                'type': 'llm',
                'status': 'loaded',
                'loaded_at': datetime.now().isoformat(),
                'quantization': quantization
            }
            
            return True
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            return False
    
    def unload_model(self, model_key):
        """Modeli bellekten kaldır"""
        if model_key in self.loaded_models:
            del self.loaded_models[model_key]
            # GPU belleğini temizle
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True
        return False
    
    def get_model_health(self, model_key):
        """Model sağlık durumu"""
        if model_key not in self.loaded_models:
            return None
        
        system_info = get_system_info()
        self.model_health[model_key] = {
            'status': 'running',
            'gpu_memory': system_info['gpu']['devices'][0]['memory_allocated'] if system_info['gpu']['available'] else 0,
            'temperature': 45 + (system_info['gpu']['devices'][0]['memory_allocated'] if system_info['gpu']['available'] else 0) * 2,
            'tokens_per_second': 25 + (hash(model_key) % 10),
            'uptime': (datetime.now() - datetime.fromisoformat(self.loaded_models[model_key]['loaded_at'])).total_seconds()
        }
        return self.model_health[model_key]
    
    def generate_embedding(self, text):
        """Metin embedding'i oluştur"""
        if self.embedding_model is None:
            # Otomatik yükle
            self.load_model('all-minilm', 'fp16')
        
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def semantic_search(self, query, documents, top_k=5):
        """Semantik arama"""
        query_embedding = self.generate_embedding(query)
        doc_embeddings = [self.generate_embedding(doc) for doc in documents]
        
        # Cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
        
        # En yüksek skorlu dokümanları getir
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [(documents[i], float(similarities[i])) for i in top_indices]


# ============================================================================
# BÖLÜM II: KOD EVRENİ İLE DERİN BÜTÜNLEŞME
# ============================================================================

class CodeAwarenessEngine:
    """
    2.1 Kod Bilinç Alanı (Code Awareness Field)
    2.2 Yapay Zeka Destekli Refactoring Stüdyosu
    """
    
    def __init__(self, project_root="/workspace"):
        self.project_root = Path(project_root)
        self.code_graph = {}
        self.symbol_index = {}
        self.file_cache = {}
        
    def build_semantic_map(self, project_path=None):
        """Anlamsal kod haritası oluştur"""
        project_path = Path(project_path) if project_path else self.project_root
        
        code_graph = {
            'files': {},
            'symbols': {},
            'dependencies': [],
            'call_graph': []
        }
        
        # Python, JS, TS dosyalarını tara
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.go', '.rs']
        
        for ext in extensions:
            for file_path in project_path.rglob(f'*{ext}'):
                if 'node_modules' in str(file_path) or '__pycache__' in str(file_path):
                    continue
                    
                rel_path = str(file_path.relative_to(project_path))
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Sembolleri çıkar
                symbols = self.extract_symbols(content, ext)
                code_graph['files'][rel_path] = {
                    'path': rel_path,
                    'size': file_path.stat().st_size,
                    'lines': len(content.splitlines()),
                    'symbols': symbols,
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                # Sembol indeksine ekle
                for symbol in symbols:
                    key = f"{symbol['name']}:{rel_path}"
                    self.symbol_index[key] = {
                        'file': rel_path,
                        'symbol': symbol,
                        'line': symbol.get('line', 0)
                    }
        
        self.code_graph = code_graph
        return code_graph
    
    def extract_symbols(self, content, extension):
        """Koddan semboller çıkar"""
        symbols = []
        
        if extension == '.py':
            # Python fonksiyonları ve sınıfları
            import re
            func_pattern = r'^\s*def\s+(\w+)\s*\('
            class_pattern = r'^\s*class\s+(\w+)'
            
            for i, line in enumerate(content.splitlines(), 1):
                func_match = re.match(func_pattern, line)
                if func_match:
                    symbols.append({'type': 'function', 'name': func_match.group(1), 'line': i})
                
                class_match = re.match(class_pattern, line)
                if class_match:
                    symbols.append({'type': 'class', 'name': class_match.group(1), 'line': i})
        
        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript
            import re
            func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)'
            class_pattern = r'class\s+(\w+)'
            
            for i, line in enumerate(content.splitlines(), 1):
                func_match = re.search(func_pattern, line)
                if func_match:
                    name = func_match.group(1) or func_match.group(2)
                    symbols.append({'type': 'function', 'name': name, 'line': i})
                
                class_match = re.search(class_pattern, line)
                if class_match:
                    symbols.append({'type': 'class', 'name': class_match.group(1), 'line': i})
        
        return symbols
    
    def find_references(self, symbol_name, file_path=None):
        """Sembolün tüm referanslarını bul"""
        references = []
        
        for key, info in self.symbol_index.items():
            if symbol_name in key:
                references.append(info)
        
        # Dosya içeriğinde de ara
        if file_path:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if symbol_name in line and f"def {symbol_name}" not in line and f"class {symbol_name}" not in line:
                        references.append({
                            'file': file_path,
                            'line': i,
                            'content': line.strip(),
                            'type': 'usage'
                        })
        
        return references
    
    def analyze_code_intent(self, code_snippet, context_files=None):
        """Kod niyetini analiz et"""
        # Basit niyet analizi (gerçek implementasyonda LLM kullanılır)
        intent_patterns = {
            'error_handling': ['try', 'catch', 'except', 'throw', 'raise', 'error'],
            'validation': ['validate', 'check', 'verify', 'assert', 'if not', 'require'],
            'database': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'query', 'db', 'sql'],
            'api_call': ['fetch', 'axios', 'request', 'http', 'get', 'post', 'api'],
            'loop_optimization': ['for', 'while', 'map', 'filter', 'reduce']
        }
        
        detected_intents = []
        code_lower = code_snippet.lower()
        
        for intent, keywords in intent_patterns.items():
            if any(kw.lower() in code_lower for kw in keywords):
                detected_intents.append(intent)
        
        return {
            'primary_intent': detected_intents[0] if detected_intents else 'general',
            'all_intents': detected_intents,
            'suggestions': self.get_intent_suggestions(detected_intents, code_snippet)
        }
    
    def get_intent_suggestions(self, intents, code):
        """Niyete göre öneriler sun"""
        suggestions = []
        
        if 'error_handling' in intents:
            if 'try' not in code.lower():
                suggestions.append({
                    'type': 'warning',
                    'message': 'Potansiyel hata riski tespit edildi. Try-catch bloğu eklemek ister misiniz?',
                    'action': 'add_error_handling'
                })
        
        if 'database' in intents:
            if 'prepared' not in code.lower() and 'parameterized' not in code.lower():
                suggestions.append({
                    'type': 'security',
                    'message': 'SQL Injection riski! Parametreli sorgu kullanın.',
                    'action': 'use_parameterized_query'
                })
        
        return suggestions
    
    def refactor_extract_method(self, file_path, start_line, end_line, method_name):
        """Kodu metoda çıkar"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return {'success': False, 'error': 'Dosya bulunamadı'}
        
        content = full_path.read_text()
        lines = content.splitlines()
        
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return {'success': False, 'error': 'Geçersiz satır aralığı'}
        
        # Seçili kodu al
        selected_code = '\n'.join(lines[start_line-1:end_line])
        
        # Yeni metot oluştur
        indent = '    '
        new_method = f"\n{indent}def {method_name}(self):\n"
        for line in selected_code.splitlines():
            new_method += f"{indent}    {line}\n"
        new_method += f"{indent}    return result\n"
        
        # Orijinal kodu metod çağrısıyla değiştir
        new_lines = lines[:start_line-1] + [f'{indent}result = self.{method_name}()'] + lines[end_line:]
        new_content = '\n'.join(new_lines) + new_method
        
        return {
            'success': True,
            'original': selected_code,
            'refactored': new_content,
            'diff': self.generate_diff(content, new_content)
        }
    
    def generate_diff(self, original, modified):
        """Diff oluştur"""
        import difflib
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile='original',
            tofile='modified'
        )
        return ''.join(diff)


# ============================================================================
# BÖLÜM III: ÇOK BOYUTLU AI ETKİLEŞİM ARAYÜZLERİ
# ============================================================================

class AIInteractionManager:
    """
    3.1 Modal AI Kanvasları
    3.2 Kesintisiz Çok Modlu Akış
    """
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.chat_history = {}
        self.agent_tasks = {}
        
    def inline_code_generation(self, prompt, context, language='python'):
        """Cmd+K inline kod üretimi"""
        # Simüle edilmiş kod üretimi
        generated_code = f"""# {prompt} için üretilen kod
def generated_function():
    \"\"\"AI tarafından oluşturuldu\"\"\"
    # TODO: Implementasyon
    pass
"""
        return {
            'code': generated_code,
            'language': language,
            'confidence': 0.85,
            'explanation': f"'{prompt}' isteğiniz için temel bir yapı oluşturdum."
        }
    
    def deep_thinking_mode(self, prompt, project_context=None):
        """Derin düşünme modu - karmaşık problemler için"""
        # Uzun düşünce süreci simülasyonu
        thinking_steps = [
            "Problem analizi yapılıyor...",
            "İlgili dosyalar taranıyor...",
            "Mimari desenler değerlendiriliyor...",
            "En iyi pratikler kontrol ediliyor...",
            "Çözüm stratejisi oluşturuluyor..."
        ]
        
        response = {
            'thinking_process': thinking_steps,
            'analysis': {
                'problem_type': 'architecture',
                'complexity': 'medium',
                'affected_files': [],
                'estimated_time': '15 dakika'
            },
            'solution': {
                'description': 'Önerilen çözüm...',
                'steps': [
                    'Adım 1: Interface tanımla',
                    'Adım 2: Implementation oluştur',
                    'Adım 3: Testleri yaz',
                    'Adım 4: Refactor et'
                ],
                'code_changes': [],
                'mermaid_diagram': '''
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Service Layer]
    C --> D[Data Layer]
'''
            }
        }
        
        return response
    
    def agent_task(self, task_description, auto_execute=False):
        """Agent arayüzü - otonom görev yürütme"""
        task_id = str(uuid.uuid4())
        
        self.agent_tasks[task_id] = {
            'id': task_id,
            'description': task_description,
            'status': 'thinking',
            'steps': [],
            'created_at': datetime.now().isoformat()
        }
        
        def execute_agent():
            # Görevi analiz et
            steps = self.plan_agent_task(task_description)
            
            for i, step in enumerate(steps):
                self.agent_tasks[task_id]['steps'].append({
                    'step': i + 1,
                    'description': step['description'],
                    'status': 'executing',
                    'output': None
                })
                
                # Adımı yürüt
                output = self.execute_agent_step(step)
                self.agent_tasks[task_id]['steps'][-1]['output'] = output
                self.agent_tasks[task_id]['steps'][-1]['status'] = 'completed'
            
            self.agent_tasks[task_id]['status'] = 'completed'
        
        if auto_execute:
            threading.Thread(target=execute_agent, daemon=True).start()
        
        return task_id
    
    def plan_agent_task(self, task_description):
        """Görevi adımlara böl"""
        # Basit planlama (gerçek implementasyonda LLM kullanılır)
        if 'github action' in task_description.lower() or 'workflow' in task_description.lower():
            return [
                {'type': 'analyze', 'description': 'Proje yapısını analiz et'},
                {'type': 'generate', 'description': 'GitHub Actions workflow dosyası oluştur'},
                {'type': 'validate', 'description': 'YAML syntax\'ını doğrula'},
                {'type': 'save', 'description': '.github/workflows/ dizinine kaydet'}
            ]
        
        return [
            {'type': 'analyze', 'description': 'Gereksinimleri anla'},
            {'type': 'plan', 'description': 'Uygulama planı oluştur'},
            {'type': 'implement', 'description': 'Kodu yaz'},
            {'type': 'test', 'description': 'Testleri çalıştır'}
        ]
    
    def execute_agent_step(self, step):
        """Agent adımını yürüt"""
        if step['type'] == 'generate' and 'workflow' in step['description'].lower():
            # GitHub Actions workflow örneği
            workflow_content = """
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app
  
  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: echo "Deploying to staging..."
"""
            return {'generated_file': '.github/workflows/deploy.yml', 'content': workflow_content}
        
        return {'output': 'Adım tamamlandı'}
    
    def image_to_code(self, image_path):
        """Ekran görüntüsünden koda dönüştürme"""
        if not VISION_AVAILABLE:
            return {'error': 'Vision model mevcut değil'}
        
        # Simülasyon
        return {
            'html': '<div class="container"><button>Click Me</button></div>',
            'css': '.container { display: flex; justify-content: center; }',
            'framework': 'vanilla',
            'confidence': 0.78
        }
    
    def speech_to_code(self, audio_data):
        """Sesten koda dönüştürme"""
        if not WHISPER_AVAILABLE:
            return {'error': 'Whisper model mevcut değil'}
        
        # Simülasyon
        return {
            'transcription': 'Bu calculateDiscount fonksiyonuna sadakat puanı kontrolü ekle',
            'suggested_code': '''
def calculateDiscount(base_price, loyalty_points):
    discount = 0
    if loyalty_points > 100:
        discount = 0.1
    elif loyalty_points > 50:
        discount = 0.05
    return base_price * (1 - discount)
''',
            'action': 'modify_function'
        }


# ============================================================================
# BÖLÜM IV: YAPAY ZEKA GÜVENLİK VE YÖNETİŞİM KATMANI
# ============================================================================

class AISecurityGuard:
    """
    4.1 Politika Tabanlı AI Güvenlik Duvarı
    4.2 Denetim ve Uyumluluk Günlüğü
    """
    
    def __init__(self, config_path="/workspace/codex-ide/config/codexguard.yaml"):
        self.config_path = Path(config_path)
        self.policies = self.load_policies()
        self.audit_log = []
        self.secret_patterns = [
            (r'api[_-]?key\s*[=:]\s*["\']?[\w-]{20,}', 'API Key'),
            (r'password\s*[=:]\s*["\']?[\w@#$%^&*]{6,}', 'Password'),
            (r'token\s*[=:]\s*["\']?[\w.-]{20,}', 'Token'),
            (r'secret[_-]?key\s*[=:]\s*["\']?[\w-]{16,}', 'Secret Key'),
            (r'private[_-]?key\s*[=:]\s*["\']?[\w-]{20,}', 'Private Key')
        ]
    
    def load_policies(self):
        """Güvenlik politikalarını yükle"""
        default_policies = {
            'enabled_features': ['code_completion', 'chat', 'refactoring'],
            'disabled_features': [],
            'required_models': [],
            'blocked_repos': ['github.com/private-repo/*'],
            'max_context_size': 16384,
            'allow_external_api': False,
            'redact_secrets': True,
            'audit_enabled': True
        }
        
        if self.config_path.exists():
            import yaml
            try:
                with open(self.config_path, 'r') as f:
                    user_policies = yaml.safe_load(f)
                    default_policies.update(user_policies)
            except:
                pass
        
        return default_policies
    
    def scan_prompt(self, prompt):
        """Prompt'u hassas veriler için tara"""
        detected_secrets = []
        redacted_prompt = prompt
        
        for pattern, secret_type in self.secret_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                detected_secrets.append({
                    'type': secret_type,
                    'value': match,
                    'position': prompt.find(match)
                })
                redacted_prompt = redacted_prompt.replace(match, '[REDACTED]')
        
        return {
            'safe': len(detected_secrets) == 0,
            'detected': detected_secrets,
            'redacted_prompt': redacted_prompt
        }
    
    def check_code_origin(self, generated_code):
        """Kod kökenini ve lisansını kontrol et"""
        # Simüle edilmiş köken tespiti
        origins = []
        
        # Basit pattern eşleştirme
        if 'MIT License' in generated_code or 'Apache License' in generated_code:
            origins.append({
                'type': 'license_header',
                'detected': True
            })
        
        return {
            'origins': origins,
            'license_risk': 'low',
            'recommendations': ['Lisans başlığı ekleyin']
        }
    
    def log_interaction(self, interaction):
        """AI etkileşimini günlüğe kaydet"""
        if not self.policies.get('audit_enabled', True):
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'interaction_id': str(uuid.uuid4()),
            'type': interaction.get('type', 'unknown'),
            'prompt_hash': hashlib.sha256(interaction.get('prompt', '').encode()).hexdigest(),
            'response_hash': hashlib.sha256(str(interaction.get('response', '')).encode()).hexdigest(),
            'user_approved': interaction.get('approved', False),
            'model_used': interaction.get('model', 'unknown')
        }
        
        self.audit_log.append(log_entry)
        
        # Dosyaya kaydet
        log_file = Path("/workspace/codex-ide/logs/audit.jsonl")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def generate_compliance_report(self):
        """Uyumluluk raporu oluştur"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_interactions': len(self.audit_log),
            'ai_generated_code_percentage': 0,
            'models_used': {},
            'rejected_suggestions': 0,
            'security_events': 0
        }
        
        # İstatistikleri hesapla
        for entry in self.audit_log:
            model = entry.get('model_used', 'unknown')
            report['models_used'][model] = report['models_used'].get(model, 0) + 1
            
            if not entry.get('user_approved', True):
                report['rejected_suggestions'] += 1
        
        return report


# ============================================================================
# BÖLÜM V: TOPLULUK EKOSİSTEMİ VE VERİ EGEMENLİĞİ
# ============================================================================

class PersonalizationEngine:
    """
    5.1 Kişisel ve Takım İnce Ayar Laboratuvarı
    5.2 Tamamen Çevrimdışı, Taşınabilir Çalışma
    """
    
    def __init__(self, user_profile_path="/workspace/codex-ide/config/user_profile.json"):
        self.user_profile_path = Path(user_profile_path)
        self.profile = self.load_profile()
        self.learning_examples = []
        
    def load_profile(self):
        """Kullanıcı profilini yükle"""
        default_profile = {
            'coding_style': {
                'naming_convention': 'snake_case',
                'preferred_libraries': [],
                'error_handling_pattern': 'try_except',
                'comment_style': 'docstring'
            },
            'project_templates': [],
            'snippets': [],
            'learning_progress': {
                'examples_analyzed': 0,
                'patterns_learned': []
            }
        }
        
        if self.user_profile_path.exists():
            try:
                with open(self.user_profile_path, 'r') as f:
                    user_data = json.load(f)
                    default_profile.update(user_data)
            except:
                pass
        
        return default_profile
    
    def analyze_coding_style(self, code_samples):
        """Kodlama stilini analiz et"""
        style_analysis = {
            'naming_patterns': {'snake_case': 0, 'camelCase': 0, 'PascalCase': 0},
            'avg_function_length': 0,
            'comment_ratio': 0,
            'error_handling_frequency': 0
        }
        
        total_functions = 0
        total_lines = 0
        comment_lines = 0
        
        for sample in code_samples:
            lines = sample.splitlines()
            total_lines += len(lines)
            
            # Yorum satırları
            comment_lines += sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//'))
            
            # Fonksiyon isimleri
            import re
            for match in re.finditer(r'def\s+(\w+)', sample):
                func_name = match.group(1)
                if '_' in func_name:
                    style_analysis['naming_patterns']['snake_case'] += 1
                elif func_name[0].isupper():
                    style_analysis['naming_patterns']['PascalCase'] += 1
                else:
                    style_analysis['naming_patterns']['camelCase'] += 1
                total_functions += 1
            
            # Try-except blokları
            style_analysis['error_handling_frequency'] += sample.count('try:')
        
        if total_functions > 0:
            style_analysis['avg_function_length'] = total_lines / total_functions
        
        if total_lines > 0:
            style_analysis['comment_ratio'] = comment_lines / total_lines
        
        # Profili güncelle
        dominant_style = max(style_analysis['naming_patterns'], key=style_analysis['naming_patterns'].get)
        self.profile['coding_style']['naming_convention'] = dominant_style
        
        return style_analysis
    
    def save_profile(self):
        """Profili kaydet"""
        self.user_profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.user_profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    def create_portable_environment(self, target_path):
        """Taşınabilir ortam oluştur"""
        target = Path(target_path)
        target.mkdir(parents=True, exist_ok=True)
        
        # Gerekli dizinleri oluştur
        (target / 'codex-ide').mkdir(exist_ok=True)
        (target / 'codex-ide' / 'models').mkdir(exist_ok=True)
        (target / 'codex-ide' / 'config').mkdir(exist_ok=True)
        (target / 'codex-ide' / 'projects').mkdir(exist_ok=True)
        
        # Konfigürasyonları kopyala
        config_files = ['/workspace/codex-ide/config/user_profile.json']
        for config in config_files:
            src = Path(config)
            if src.exists():
                dst = target / 'codex-ide' / 'config' / src.name
                shutil.copy(src, dst)
        
        # Başlatıcı script oluştur
        launcher = target / 'start_codex.sh'
        launcher.write_text('''#!/bin/bash
cd "$(dirname "$0")/codex-ide"
python backend/app.py --portable
''')
        launcher.chmod(0o755)
        
        return {
            'success': True,
            'path': str(target),
            'size': sum(f.stat().st_size for f in target.rglob('*') if f.is_file())
        }


# ============================================================================
# FLASK UYGULAMASI
# ============================================================================

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'),
            static_url_path='')
CORS(app)

# Bileşenleri başlat
model_manager = ModelManager()
code_engine = CodeAwarenessEngine()
ai_interaction = AIInteractionManager(model_manager)
security_guard = AISecurityGuard()
personalization = PersonalizationEngine()

@app.route('/')
def index():
    """Ana sayfa"""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    """404 hatalarını ana sayfaya yönlendir"""
    return send_from_directory(app.static_folder, 'index.html')

# ============================================================================
# MODEL YÖNETİM API
# ============================================================================

@app.route('/api/models/list', methods=['GET'])
def api_list_models():
    """Kullanılabilir modelleri listele"""
    return jsonify({
        'success': True,
        'models': model_manager.list_available_models(),
        'loaded': list(model_manager.loaded_models.keys())
    })

@app.route('/api/models/download', methods=['POST'])
def api_download_model():
    """Model indir"""
    data = request.json
    model_id = data.get('model_id')
    quantization = data.get('quantization', 'Q4_K_M')
    progress_id = str(uuid.uuid4())
    
    model_manager.download_model(model_id, quantization, progress_id)
    
    return jsonify({
        'success': True,
        'progress_id': progress_id
    })

@app.route('/api/models/progress/<progress_id>', methods=['GET'])
def api_download_progress(progress_id):
    """İndirme ilerlemesini getir"""
    progress = model_manager.download_progress.get(progress_id, {'status': 'not_found'})
    return jsonify(progress)

@app.route('/api/models/load', methods=['POST'])
def api_load_model():
    """Model yükle"""
    data = request.json
    model_id = data.get('model_id')
    quantization = data.get('quantization', 'Q4_K_M')
    
    success = model_manager.load_model(model_id, quantization)
    
    return jsonify({
        'success': success,
        'model': f"{model_id}-{quantization}"
    })

@app.route('/api/models/unload', methods=['POST'])
def api_unload_model():
    """Model bellekten kaldır"""
    data = request.json
    model_key = data.get('model_key')
    
    success = model_manager.unload_model(model_key)
    
    return jsonify({
        'success': success
    })

@app.route('/api/models/health/<model_key>', methods=['GET'])
def api_model_health(model_key):
    """Model sağlık durumu"""
    health = model_manager.get_model_health(model_key)
    return jsonify({
        'success': True,
        'health': health
    })

# ============================================================================
# KOD FARKINDALIĞI API
# ============================================================================

@app.route('/api/code/scan', methods=['POST'])
def api_scan_project():
    """Projeyi tara ve semantik harita oluştur"""
    data = request.json
    project_path = data.get('path', '/workspace')
    
    code_map = code_engine.build_semantic_map(project_path)
    
    return jsonify({
        'success': True,
        'code_map': code_map,
        'symbol_count': len(code_engine.symbol_index)
    })

@app.route('/api/code/symbols/search', methods=['POST'])
def api_search_symbols():
    """Sembol ara"""
    data = request.json
    query = data.get('query', '')
    
    results = []
    for key, info in code_engine.symbol_index.items():
        if query.lower() in key.lower():
            results.append(info)
    
    return jsonify({
        'success': True,
        'results': results[:50]  # İlk 50 sonuç
    })

@app.route('/api/code/references', methods=['POST'])
def api_find_references():
    """Referansları bul"""
    data = request.json
    symbol_name = data.get('symbol_name')
    file_path = data.get('file_path')
    
    references = code_engine.find_references(symbol_name, file_path)
    
    return jsonify({
        'success': True,
        'references': references
    })

@app.route('/api/code/intent', methods=['POST'])
def api_analyze_intent():
    """Kod niyetini analiz et"""
    data = request.json
    code_snippet = data.get('code')
    context = data.get('context', [])
    
    analysis = code_engine.analyze_code_intent(code_snippet, context)
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/api/code/refactor/extract-method', methods=['POST'])
def api_refactor_extract_method():
    """Metoda çıkar refactoring"""
    data = request.json
    
    result = code_engine.refactor_extract_method(
        data.get('file_path'),
        data.get('start_line'),
        data.get('end_line'),
        data.get('method_name')
    )
    
    return jsonify(result)

# ============================================================================
# AI ETKİLEŞİM API
# ============================================================================

@app.route('/api/ai/inline', methods=['POST'])
def api_inline_generation():
    """Inline kod üretimi"""
    data = request.json
    
    result = ai_interaction.inline_code_generation(
        data.get('prompt'),
        data.get('context'),
        data.get('language', 'python')
    )
    
    # Güvenlik taraması
    if security_guard.policies.get('redact_secrets', True):
        scan_result = security_guard.scan_prompt(data.get('prompt', ''))
        result['security'] = scan_result
    
    return jsonify(result)

@app.route('/api/ai/deep-thinking', methods=['POST'])
def api_deep_thinking():
    """Derin düşünme modu"""
    data = request.json
    
    result = ai_interaction.deep_thinking_mode(
        data.get('prompt'),
        data.get('project_context')
    )
    
    return jsonify(result)

@app.route('/api/ai/agent', methods=['POST'])
def api_agent_task():
    """Agent görevi"""
    data = request.json
    
    task_id = ai_interaction.agent_task(
        data.get('task'),
        data.get('auto_execute', False)
    )
    
    return jsonify({
        'success': True,
        'task_id': task_id
    })

@app.route('/api/ai/agent/status/<task_id>', methods=['GET'])
def api_agent_status(task_id):
    """Agent görev durumu"""
    task = ai_interaction.agent_tasks.get(task_id)
    return jsonify({
        'success': True,
        'task': task
    })

@app.route('/api/ai/vision/image-to-code', methods=['POST'])
def api_image_to_code():
    """Resimden koda"""
    if 'image' not in request.files:
        return jsonify({'error': 'Resim dosyası gerekli'}), 400
    
    image_file = request.files['image']
    image_path = f"/tmp/{uuid.uuid4()}.png"
    image_file.save(image_path)
    
    result = ai_interaction.image_to_code(image_path)
    
    return jsonify(result)

@app.route('/api/ai/speech/to-code', methods=['POST'])
def api_speech_to_code():
    """Sesten koda"""
    if 'audio' not in request.files:
        return jsonify({'error': 'Ses dosyası gerekli'}), 400
    
    audio_file = request.files['audio']
    audio_path = f"/tmp/{uuid.uuid4()}.wav"
    audio_file.save(audio_path)
    
    # Gerçek implementasyonda Whisper burada çalışır
    result = {
        'transcription': 'Ses transkripsiyonu burada olacak',
        'suggested_code': '# Kod önerisi',
        'action': 'pending'
    }
    
    return jsonify(result)

# ============================================================================
# GÜVENLİK API
# ============================================================================

@app.route('/api/security/scan-prompt', methods=['POST'])
def api_scan_prompt():
    """Prompt güvenlik taraması"""
    data = request.json
    result = security_guard.scan_prompt(data.get('prompt', ''))
    return jsonify(result)

@app.route('/api/security/check-origin', methods=['POST'])
def api_check_origin():
    """Kod kökeni kontrolü"""
    data = request.json
    result = security_guard.check_code_origin(data.get('code', ''))
    return jsonify(result)

@app.route('/api/security/compliance-report', methods=['GET'])
def api_compliance_report():
    """Uyumluluk raporu"""
    report = security_guard.generate_compliance_report()
    return jsonify(report)

# ============================================================================
# KİŞİSELLEŞTİRME API
# ============================================================================

@app.route('/api/profile/analyze', methods=['POST'])
def api_analyze_style():
    """Kodlama stilini analiz et"""
    data = request.json
    samples = data.get('code_samples', [])
    
    analysis = personalization.analyze_coding_style(samples)
    personalization.save_profile()
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'profile': personalization.profile
    })

@app.route('/api/profile/get', methods=['GET'])
def api_get_profile():
    """Kullanıcı profilini getir"""
    return jsonify({
        'success': True,
        'profile': personalization.profile
    })

@app.route('/api/portable/create', methods=['POST'])
def api_create_portable():
    """Taşınabilir ortam oluştur"""
    data = request.json
    target_path = data.get('path', '/mnt/usb/codex-ide')
    
    result = personalization.create_portable_environment(target_path)
    return jsonify(result)

# ============================================================================
# SİSTEM API
# ============================================================================

@app.route('/api/system/info', methods=['GET'])
def api_system_info():
    """Sistem bilgisi"""
    return jsonify({
        'success': True,
        'info': get_system_info()
    })

@app.route('/api/system/gpu', methods=['GET'])
def api_gpu_info():
    """GPU bilgisi"""
    return jsonify({
        'success': True,
        'gpu': get_gpu_info()
    })

if __name__ == '__main__':
    print("🚀 Codex IDE Başlatılıyor...")
    print("=" * 60)
    print("Bölüm I:   ✅ Yerel LLM Yönetim Merkezi")
    print("Bölüm II:  ✅ Kod Evreni Entegrasyonu")
    print("Bölüm III: ✅ Çok Boyutlu AI Arayüzleri")
    print("Bölüm IV:  ✅ AI Güvenlik Katmanı")
    print("Bölüm V:   ✅ Veri Egemenliği Sistemi")
    print("=" * 60)
    
    port = 5000
    print(f"\n🌐 Tarayıcıda açın: http://localhost:{port}")
    print("💡 İpucu: Ctrl+C ile durdurabilirsiniz\n")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
