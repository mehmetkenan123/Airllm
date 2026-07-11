# 🚀 AirLLM Studio - Yerel LLM Uygulaması

Düşük donanımlı bilgisayarlarda bile büyük dil modellerini (LLM) çalıştırabileceğiniz, AirLLM benzeri katman katman yükleme sistemi ile geliştirilmiş yerel AI stüdyosu.

## ✨ Özellikler

### 🧠 Otomatik Model Yönetimi
- **HuggingFace Entegrasyonu**: 7 popüler model arasından seçim yapın
  - Qwen2.5 7B Instruct (Önerilen)
  - Llama 3.2 3B Instruct (Düşük RAM için ideal)
  - Phi-3 Mini 3.8B
  - Gemma 2 2B (En hafif)
  - Mistral 7B Instruct
  - Qwen2.5 14B Instruct
  - Llama 3.1 8B Instruct

- **Tek Tıkla İndirme**: Modeller otomatik olarak HuggingFace'den indirilir
- **Katman Katman Yükleme**: Düşük RAM kullanımı için optimize edilmiş
- **İlerleme Takibi**: İndirme ve yükleme durumunu gerçek zamanlı izleyin
- **Model Boşaltma**: Bellekten kolayca temizleyin

### 💬 Sohbet Arayüzü
- Modern, responsive tasarım
- Çoklu konuşma desteği
- Konuşma geçmişi takibi
- Dosya yükleme özelliği
- Gerçek zamanlı model durumu göstergesi

### 🖥️ Sistem Özellikleri
- CPU ve GPU desteği
- RAM kullanım optimizasyonu
- Otomatik device detection
- Sistem kaynakları izleme

## 📦 Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
cd /workspace/airllm-studio/backend
pip install -r requirements.txt
```

### 2. Backend'i Başlatın

```bash
cd /workspace/airllm-studio/backend
python app.py
```

Backend `http://localhost:5000` adresinde çalışacaktır.

### 3. Frontend'i Başlatın

Yeni bir terminal penceresinde:

```bash
cd /workspace/airllm-studio/frontend
python -m http.server 8080
```

Frontend `http://localhost:8080` adresinde çalışacaktır.

### 4. Tarayıcıda Açın

```
http://localhost:8080
```

## 🎯 Kullanım

### Model Yükleme Adımları:

1. **Modeller Sekmesine Gidin**: Sol menüden "🧠 Modeller" butonuna tıklayın
2. **Model Seçin**: Listeden istediğiniz modeli seçin
   - Düşük RAM (<8GB): Gemma 2 2B veya Llama 3.2 3B
   - Orta RAM (8-16GB): Qwen2.5 7B, Phi-3 Mini, Mistral 7B
   - Yüksek RAM (>16GB): Qwen2.5 14B, Llama 3.1 8B
3. **İndir ve Yükle**: Butona tıklayın ve bekleyin
4. **Sohbete Başlayın**: Model yüklendiğinde otomatik olarak sohbet aktif olur

### Sohbet Etme:

1. Mesajınızı yazın
2. İsterseniz dosya ekleyin
3. Gönder butonuna tıklayın
4. AI yanıtını bekleyin

### Yeni Konuşma:

- Sol menüden "+ Yeni Sohbet" butonuna tıklayın
- Her konuşma bağımsız geçmişe sahiptir

## 🔧 Teknik Detaylar

### Katman Katman Yükleme Sistemi

AirLLM'den esinlenen bu sistem:
- Model ağırlıklarını gerektiğinde yükler
- CPU ve RAM kullanımını optimize eder
- Düşük donanımlarda büyük modeller çalıştırmanızı sağlar

### Desteklenen Dosya Formatları

- PDF (.pdf)
- Metin (.txt)
- Word (.docx)
- Ve daha fazlası...

### API Endpoints

- `GET /api/models` - Kullanılabilir modelleri listele
- `POST /api/models/download` - Model indir ve yükle
- `POST /api/models/unload` - Modeli bellekten boşalt
- `GET /api/models/progress/<id>` - İndirme ilerlemesini kontrol et
- `POST /api/chat` - Sohbet mesajı gönder
- `POST /api/upload` - Dosya yükle
- `GET /api/system/info` - Sistem bilgilerini al

## ⚙️ Yapılandırma

### Model Cache Dizini

Modeller varsayılan olarak şu dizine indirilir:
```
/workspace/airllm-studio/models/
```

### Offload Dizini

Düşük RAM için state dictionary offloading:
```
/workspace/airllm-studio/offload/
```

### Dosya Upload Dizini

Yüklenen dosyalar:
```
/workspace/airllm-studio/uploads/
```

## 🛠️ Sorun Giderme

### Model Yüklenmiyor

1. İnternet bağlantınızı kontrol edin
2. HuggingFace erişiminizi test edin
3. Disk alanınızın yeterli olduğundan emin olun

### Yavaş Yanıt Süresi

- CPU kullanıyorsanız GPU'lu model deneyin
- Daha küçük model seçin (3B veya 2B)
- `max_new_tokens` parametresini düşürün

### RAM Yetersiz Hatası

- Daha küçük model seçin
- Diğer uygulamaları kapatın
- Modeli boşaltıp tekrar yükleyin

## 📊 Sistem Gereksinimleri

### Minimum:
- CPU: 4 çekirdek
- RAM: 8 GB
- Disk: 20 GB boş alan

### Önerilen:
- CPU: 8+ çekirdek
- RAM: 16+ GB
- GPU: 8+ GB VRAM (opsiyonel)
- Disk: 50+ GB SSD

## 🤝 Katkıda Bulunma

Projeyi geliştirmek için:
1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Push edin
5. Pull Request açın

## 📝 Lisans

Bu proje açık kaynak lisansı altında dağıtılmaktadır.

## 🔗 Bağlantılar

- [HuggingFace](https://huggingface.co)
- [Transformers Dokümantasyonu](https://huggingface.co/docs/transformers)
- [PyTorch](https://pytorch.org)

---

**AirLLM Studio** ile yerel AI deneyimini keşfedin! 🚀
