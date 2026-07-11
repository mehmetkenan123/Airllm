# 🚀 AirLLM Studio - EXE Oluşturma Kılavuzu

Windows için tek tıkla çalıştırılabilir (.exe) uygulama oluşturun!

## 📋 Önkoşullar

- Windows 10/11 (64-bit)
- Python 3.9 veya üzeri yüklü olmalı
- İnternet bağlantısı (ilk kurulum için)
- Minimum 20 GB boş disk alanı

## 🔨 EXE Oluşturma Adımları

### Yöntem 1: Tek Tıkla (Önerilen)

1. **`build.bat` dosyasına çift tıklayın**
   
   Bu otomatik olarak:
   - Python sanal ortamı oluşturur
   - Tüm bağımlılıkları yükler
   - EXE dosyasını oluşturur

2. **İşlem tamamlanmasını bekleyin** (5-15 dakika sürebilir)

3. **Oluşturulan EXE dosyası**: `dist\AirLLM_Studio.exe`

### Yöntem 2: Manuel (Terminal ile)

```bash
# 1. Proje klasörüne gidin
cd airllm-studio

# 2. Sanal ortam oluşturun
python -m venv venv

# 3. Sanal ortamı etkinleştirin
venv\Scripts\activate

# 4. Bağımlılıkları yükleyin
pip install -r backend\requirements.txt

# 5. EXE oluşturun
python build_exe.py
```

## 🎯 EXE'yi Çalıştırma

### Yöntem 1: Hızlı Başlatıcı

- **`run.bat` dosyasına çift tıklayın**
- Uygulama otomatik olarak başlar ve tarayıcınız açılır

### Yöntem 2: Manuel

1. `dist` klasörüne gidin
2. `AirLLM_Studio.exe` dosyasına çift tıklayın
3. Tarayıcınızda `http://localhost:5000` adresini ziyaret edin

## 📦 EXE Dosyasını Dağıtma

### Başka Bilgisayarlara Taşıma

⚠️ **ÖNEMLI**: EXE dosyası tek başına çalışmaz! Aşağıdakileri de taşımanız gerekir:

```
airllm-studio-dist/
├── AirLLM_Studio.exe      # Ana uygulama
├── frontend/              # Web arayüzü (GEREKLİ)
│   └── index.html
└── README_dist.txt        # Kullanım kılavuzu
```

### Dağıtım Paketi Oluşturma

```bash
# 1. Yeni bir klasör oluşturun
mkdir airllm-studio-portable

# 2. EXE ve frontend'i kopyalayın
copy dist\AirLLM_Studio.exe airllm-studio-portable\
xcopy /E frontend airllm-studio-portable\frontend\

# 3. ZIP dosyası oluşturun
# Klasöre sağ tıklayıp "Gönder > Sıkıştırılmış Klasör" seçin
```

### Kullanıcıya Talimatlar

Dağıtım paketini alan kullanıcılar:
1. ZIP dosyasını çıkarır
2. `AirLLM_Studio.exe` dosyasına çift tıklar
3. Tarayıcıda açılan sayfada model indirir ve kullanmaya başlar

## ⚙️ Gelişmiş Ayarlar

### Konsol Penceresini Göster/Gizle

`build_exe.py` dosyasında:
- `--windowed` : Konsolu gizler (normal kullanım için)
- Konsolu göstermek için bu parametreyi kaldırın (debug için)

### Özel İkon Eklemek

1. `.ico` formatında ikon dosyası hazırlayın
2. `build_exe.py` dosyasında `--icon=NONE` satırını bulun
3. Şu şekilde değiştirin: `--icon=ikonunuz.ico`

### Boyutu Küçültme

EXE boyutunu küçültmek için:
- Gereksiz kütüphaneleri `requirements.txt`'den çıkarın
- Sadece ihtiyacınız olan modelleri ekleyin
- UPX sıkıştırma kullanın: `--upx-dir=upx`

## 🐛 Sorun Giderme

### "Python bulunamadı" hatası

- Python'un yüklü olduğundan emin olun
- Python'u PATH'e ekleyin
- Python 3.9+ kullanın

### "Modül bulunamadı" hataları

```bash
# Sanal ortamı temizleyip yeniden oluşturun
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
python build_exe.py
```

### EXE çok büyük (>1GB)

- Normaldir! PyTorch ve Transformers büyük kütüphanelerdir
- İlk yüklemede tüm bağımlılıkları paketler
- Sonraki sürümlerde daha optimize edilebilir

### Antivirüs Engeli

- Bazı antivirüsler PyInstaller ile paketlenmiş dosyaları şüpheli bulabilir
- EXE'yi antivirüs istisnalarına ekleyin
- Kaynak kodu inceleyerek güvenliği doğrulayın

### Model İndirme Sorunları

- EXE ilk çalıştığında internet bağlantısı gerekli
- HuggingFace erişiminizi kontrol edin
- Proxy kullanıyorsanız ortam değişkenlerini ayarlayın:
  ```bash
  set HF_ENDPOINT=https://huggingface.co
  ```

## 📊 Performans İpuçları

### Daha Hızlı Başlangıç

- EXE'yi SSD'ye yükleyin
- İlk çalıştırmada model indirmeyi önceden yapın
- Arka plan uygulamalarını kapatın

### RAM Kullanımını Azaltma

- Küçük modeller tercih edin (Gemma 2B, Llama 3.2 3B)
- Modeli kullanmadığınızda boşaltın
- Windows sanal belleğini artırın

## 🔐 Güvenlik Notları

- EXE dosyası yerel çalışır, verileriniz bilgisayarınızdan çıkmaz
- Model dosyaları HuggingFace'den güvenli şekilde indirilir
- Kaynak kodu inceleyerek güvenlik doğrulaması yapabilirsiniz
- Üçüncü taraf sunuculara bağlantı yoktur (model indirme hariç)

## 📞 Yardım ve Destek

Sorun yaşarsanız:
1. `README.md` dosyasını kontrol edin
2. GitHub Issues'da sorunuzu açın
3. Konsol çıktısını (varsa) hata mesajıyla birlikte paylaşın

---

**AirLLM Studio** ile güçlü AI modellerini herkesin kullanımına sunun! 🚀
