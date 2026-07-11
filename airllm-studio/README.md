# AirLLM Studio v1.3 - Yerel Yapay Zeka İstasyonu

![Version](https://img.shields.io/badge/version-1.3.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🚀 Genel Bakış

**AirLLM Studio**, düşük donanımlı bilgisayarlarda bile büyük dil modellerini (LLM) çalıştırmanızı sağlayan, LM Studio benzeri modern arayüze sahip, tamamen yerel bir yapay zeka istasyonudur. 

Gelişmiş **Katmanlı Yükleme (Layered Loading)** teknolojisi sayesinde, VRAM'i yetersiz olan ekran kartlarında veya sadece CPU kullanarak bile Llama 3, Qwen 2.5, Phi-3 gibi güçlü modelleri akıcı şekilde çalıştırabilirsiniz.

### ✨ Öne Çıkan Özellikler

*   🖥️ **Modern Web Arayüzü**: Karmaşık terminal komutlarına gerek yok. LM Studio tarzı, kullanıcı dostu, karanlık mod destekli grafik arayüz.
*   ⚡ **Düşük RAM Optimizasyonu**: Modelleri parça parça (katman katman) yükleyerek sistem belleğini (RAM/VRAM) %70'e kadar daha verimli kullanır.
*   🤖 **Çoklu Model Desteği**: HuggingFace üzerinden otomatik model indirme veya yerel `.gguf` modellerini yükleme imkanı.
*   💬 **Gerçek Zamanlı Sohbet**: Streaming (akan) metin üretimi ile cevabı beklemek yerine yazarken okuyun.
*   🔧 **Donanım İzleme**: Anlık GPU/CPU kullanımını ve bellek durumunu arayüzden takip edin.
*   🔒 **Tamamen Gizli ve Yerel**: Verileriniz asla internete çıkmaz, tamamen kendi bilgisayarınızda işlenir.

---

## 📦 Kurulum ve Çalıştırma (Tek Tıkla)

AirLLM Studio, karmaşık kurulum adımlarını ortadan kaldırmak için "Tek Dosya" mantığıyla tasarlanmıştır.

### Gereksinimler
*   Windows 10/11 İşletim Sistemi
*   Python 3.8 veya üzeri yüklü olmalı ([Python İndir](https://www.python.org/downloads/))
    *   *Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın!*

### Nasıl Çalıştırılır?

1.  Projeyi indirin veya klasöre çıkarın.
2.  Klasör içindeki **`run.bat`** dosyasına çift tıklayın.
3.  Sistem otomatik olarak:
    *   Gerekli kütüphaneleri kontrol eder ve eksikleri kurar.
    *   Arka plan servislerini başlatır.
    *   Varsayılan tarayıcınızda AirLLM Studio arayüzünü açar.

> **Not:** Siyah terminal pencereleri görebilirsiniz ancak bunlar arka planda çalışır ve işlem tamamlanınca kapanır. Asıl kullanım alanınız tarayıcıda açılan modern arayüzdür.

---

## 🛠️ Teknik Detaylar

### Mimari
AirLLM Studio, hafif bir Flask web sunucusu üzerinde çalışır ancak kullanıcıya masaüstü uygulaması deneyimi sunar.

*   **Backend**: Python (Flask, PyTorch, Transformers, AirLLM)
*   **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS + Chart.js)
*   **AI Motoru**: HuggingFace Transformers & AirLLM (Quantization Support)

### Performans İyileştirmeleri (v1.3)
*   **GPU Offloading**: Desteklenen NVIDIA kartlarda katmanları otomatik olarak ekran kartına kaydırır.
*   **Context Window Yönetimi**: Uzun sohbetlerde bellek taşmasını (OOM) önleyen dinamik temizleme mekanizması.
*   **Streaming Response**: Token oluşturuldukça anlık iletim sağlar, bekleme süresini minimize eder.

---

## 📸 Ekran Görüntüleri

Arayüz şu bölümlerden oluşur:
1.  **Sol Panel**: Sohbet geçmişi ve yeni sohbet başlatma.
2.  **Orta Panel**: Ana sohbet alanı, mesajlaşma ve model yanıtı.
3.  **Sağ Panel**: Model ayarları (Temperature, Max Tokens), GPU/CPU kullanım grafikleri ve sistem durumu.

---

## ❓ Sıkça Sorulan Sorular

**S: Hangi modelleri kullanabilirim?**
C: HuggingFace'te bulunan `.gguf` formatındaki çoğu modeli (Llama-3, Mistral, Gemma, Phi-3 vb.) kullanabilirsiniz. Uygulama içinden otomatik indirebilirsiniz.

**S: Ekran kartım yok, çalışır mı?**
C: Evet! AirLLM'in özel optimizasyonu sayesinde sadece işlemci (CPU) ve RAM kullanarak da modelleri çalıştırabilirsiniz, ancak yanıt süresi daha yavaş olabilir.

**S: Verilerim güvenli mi?**
C: Kesinlikle. Tüm işlemler yerel ağınızda (localhost) gerçekleşir. Hiçbir veri dışarı gönderilmez.

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunun

Hata bildirimleri ve özellik önerileri için proje deposu üzerinden bildirimde bulunabilirsiniz.

---
**Geliştirici Notu**: Bu sürüm (v1.3), kararlılık ve kullanıcı deneyimi odaklı yeniden yapılandırılmıştır. Terminal bağımlılığı ortadan kaldırılmış, tam GUI deneyimi sunulmuştur.
