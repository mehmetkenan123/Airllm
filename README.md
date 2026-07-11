# AirLLM Studio

🚀 **Düşük Bellekli Büyük Dil Modelleri için Gelişmiş Arayüz**

AirLLM Studio, 4GB GPU VRAM ile 70B parametreli modelleri çalıştırmanızı sağlayan güçlü bir uygulamadır.

## ✨ Özellikler

- 🎯 **Düşük Bellek Kullanımı**: 4GB GPU ile 70B modeller çalıştırın
- 🔥 **AirLLM Entegrasyonu**: Otomatik katman katman yükleme
- 💻 **Çift Mod**: Development (Streamlit) ve Production (EXE) modları
- 🚀 **Tek Tıkla Çalıştır**: run.bat ile tüm işlemler otomatik
- 📦 **Kolay Kurulum**: Python otomatik bulunur ve yapılandırılır

## 🚀 Hızlı Başlangıç

### Windows Kullanıcıları

1. `run.bat` dosyasına çift tıklayın
2. Menüden istediğiniz seçeneği seçin:
   - **[1]** Kurulum yap ve uygulamayı çalıştır
   - **[2]** EXE dosyası oluştur
   - **[3]** Sadece bağımlılıkları yükle

### Manuel Kurulum

```bash
# Sanal ortam oluştur
python -m venv venv

# Aktif et
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
streamlit run app.py
```

## 📋 Gereksinimler

- Python 3.7+
- 4GB+ RAM (CPU modu için)
- 4GB+ VRAM (GPU modu için, opsiyonel)
- Windows 10/11 (EXE oluşturmak için)

## 🔧 Gelişmiş Kullanım

### EXE Oluşturma

```bash
# run.bat üzerinden veya manuel:
cd airllm-studio
python build_exe.py
```

Oluşturulan EXE dosyası: `airllm-studio/dist/AirLLM_Studio.exe`

### AirLLM ile Model Yükleme

```python
from airllm import AutoModel as AirLLMAutoModel

model = AirLLMAutoModel.from_pretrained(
    'mistralai/Mistral-7B-Instruct-v0.3',
    max_memory_allocated_gb=4,
)
```

## 📁 Proje Yapısı

```
/workspace/
├── run.bat              # Tek tıkla kurulum ve çalıştırma
├── requirements.txt     # Python bağımlılıkları
├── app.py              # Streamlit uygulaması
├── README.md           # Bu dosya
└── airllm-studio/
    ├── main.py         # Ana uygulama
    ├── build_exe.py    # EXE oluşturucu script
    ├── backend/
    │   ├── app.py      # Backend API
    │   └── requirements.txt
    └── frontend/       # Frontend dosyaları
```

## 🐛 Sorun Giderme

### Python Bulunamadı Hatası

`run.bat` otomatik olarak şu yolları kontrol eder:
- Windows Registry
- PATH环境变量
- Yaygın kurulum yolları (C:\Python39, C:\Program Files\Python*, vb.)

Çözüm:
1. Python'i [python.org](https://python.org) adresinden yükleyin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Komut satırını yeniden açın

### Bağımlılık Hataları

```bash
# Sanal ortamı temizle ve yeniden oluştur
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 📄 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler ve issue'lar açıktır!

---

**Geliştirici:** AirLLM Studio Team  
**Versiyon:** 1.0.0  
**Son Güncelleme:** 2024