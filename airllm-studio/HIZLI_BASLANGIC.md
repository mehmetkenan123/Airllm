# 🚀 AirLLM Studio - Tek Tıkla EXE Uygulaması

Artık AirLLM Studio, **tek bir .exe dosyası** olarak çalışıyor! Hiçbir kurulum gerektirmez.

## 📦 EXE Nasıl Oluşturulur? (Windows)

### Yöntem 1: Çift Tıklama (En Kolay)
1. `build.bat` dosyasına çift tıklayın
2. İşlem tamamlanmasını bekleyin (5-10 dakika sürebilir)
3. `dist/AirLLM_Studio.exe` dosyası oluşacak

### Yöntem 2: Terminal
```bash
cd airllm-studio
build.bat
```

## ▶️ EXE Nasıl Çalıştırılır?

### Yöntem 1: Çift Tıklama
- `run.bat` dosyasına çift tıklayın
- VEYA `dist/AirLLM_Studio.exe` dosyasına çift tıklayın

### Yöntem 2: Terminal
```bash
run.bat
```
veya
```bash
dist\AirLLM_Studio.exe
```

## ✨ Özellikler

✅ **Tek Dosya**: Tüm bağımlılıklar içinde paketlenmiş  
✅ **Otomatik Tarayıcı**: Uygulama başladığında tarayıcı otomatik açılır  
✅ **Model İndirme**: İlk çalıştırmada seçtiğiniz model otomatik indirilir  
✅ **Düşük RAM**: Katman katman yükleme ile 4GB RAM'de bile çalışır  
✅ **7 Hazır Model**: Qwen, Llama, Phi, Gemma, Mistral  

## 🎯 Kullanım Akışı

1. **EXE'yi Oluştur**: `build.bat` → Bekle → `dist/AirLLM_Studio.exe` oluşur
2. **Uygulamayı Başlat**: `run.bat` veya direkt EXE'ye çift tıkla
3. **Model Seç**: Arayüzden istediğin modeli seç (örn: Qwen2.5-7B)
4. **İndir**: "İndir" butonuna tıkla (ilk seferde ~2-5 GB)
5. **Sohbet Et**: Model yüklendikten sonra sohbet etmeye başla!

## 📊 Sistem Gereksinimleri

| Minimum | Önerilen |
|---------|----------|
| Windows 10/11 | Windows 10/11 |
| 4 GB RAM | 8+ GB RAM |
| 10 GB Boş Alan | 20+ GB Boş Alan |
| İnternet (model indirme için) | SSD + İyi İnternet |

## 🔧 Sorun Giderme

### ❌ "EXE oluşturulamadı" hatası
```bash
# Manuel olarak deneyin:
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
pip install pyinstaller
python build_exe.py
```

### ❌ "Model indirilemiyor" hatası
- İnternet bağlantınızı kontrol edin
- HuggingFace erişimi engelli olabilir, VPN deneyin
- Alternatif olarak modeli manuel indirip `models/` klasörüne koyun

### ❌ "Port 5000 kullanımda" hatası
- Başka bir uygulama 5000 portunu kullanıyor olabilir
- Görev Yöneticisi'nden Python süreçlerini kapatın
- Veya `main.py` içindeki port numarasını değiştirin

## 📁 Dosya Yapısı

```
airllm-studio/
├── main.py              # Ana uygulama (EXE'nin giriş noktası)
├── build.bat            # EXE oluşturucu
├── run.bat              # Hızlı başlatıcı
├── build_exe.py         # PyInstaller yapılandırması
├── backend/
│   ├── app.py           # Flask backend + AirLLM
│   └── requirements.txt # Bağımlılıklar
├── frontend/
│   └── index.html       # Web arayüzü
├── dist/                # Oluşturulan EXE buraya gelir
│   └── AirLLM_Studio.exe
└── models/              # İndirilen modeller (otomatik oluşur)
```

## 💡 İpuçları

- **İlk EXE boyutu** ~300-500 MB olabilir (tüm kütüphaneler dahil)
- **Model boyutları** ayrı indirilir (2-8 GB arası)
- **Güvenlik uyarısı**: İlk çalıştırmada Windows Defender uyarı verebilir, "izin ver" deyin
- **Hızlandırma**: SSD'de çalıştırın, ilk model indirme uzun sürebilir

## 🌐 GitHub'a Yükleme

Projenizi GitHub'a yüklemek için:

```bash
cd airllm-studio
git init
git add .
git commit -m "AirLLM Studio - Tek tıkla çalışan LLM uygulaması"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/airllm-studio.git
git push -u origin main
```

⚠️ **Önemli**: `.gitignore` dosyası büyük dosyaları (venv, dist, modeller) hariç tutar!

---

🎉 **Artık hazır!** Kullanıcılarınız sadece `run.bat`'a tıklayarak uygulamanızı kullanabilir.
