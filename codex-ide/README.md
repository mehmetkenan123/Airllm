# Codex IDE - İnsanlık Tarihinin En Gelişmiş Geliştirme Ortamı

![Codex IDE Banner](./resources/banner.png)

**Codex IDE**, yerel LLM'lerle çalışan, tamamen çevrimdışı çalışabilen, düşük donanımlı bilgisayarlarda bile akıcı performans sunan açık kaynak bir geliştirme ortamıdır.

## ✨ Özellikler

### 🧠 Sinirsel Ağ Tabanlı Kod Anlama
- Kodun 4. boyutunu görme (zaman-simülasyon motoru)
- Kolektif zeka ağı (P2P bilgi paylaşımı)
- Duygusal kod analizi

### ⚛️ Kuantum İlhamlı Kod Optimizasyonu
- Süperpozisyon kod tamamlama
- Fraktal kod görselleştirme
- Entropi tabanlı kod kalite ölçer

### 🤖 Bilinçli Kod Asistanı
- 12 farklı AI kişiliği
- Rüya modu (arka plan derin düşünme)
- Empati tabanlı işbirliği

### 🔒 Çoklu Boyutlu Güvenlik
- Homomorfik kod şifreleme
- Yapay zeka bal küpü
- Sıfır bilgi kanıtlı kod incelemesi

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Node.js >= 18.0.0
- pnpm >= 9.0.0
- Python 3.11+ (opsiyonel)

### Kurulum

```bash
# Depoyu klonla
git clone https://github.com/codex-ide/codex-ide.git
cd codex-ide

# Bağımlılıkları yükle
pnpm install

# Geliştirme modunda başlat
pnpm dev
```

### Build

```bash
# Tüm platformlar için build
pnpm build

# Platform spesifik build
pnpm build:win
pnpm build:mac
pnpm build:linux
```

## 📁 Proje Yapısı

```
codex-ide/
├── apps/
│   ├── desktop/          # Electron ana uygulaması
│   ├── web/              # Web versiyonu
│   └── cli/              # Komut satırı aracı
├── packages/
│   ├── core/             # Çekirdek mantık
│   ├── editor/           # Monaco Editor wrapper
│   ├── ai-core/          # AI soyutlama katmanı
│   ├── ai-backends/      # AirLLM, llama.cpp backendlere
│   ├── model-manager/    # Model indirme ve yönetim
│   ├── indexing/         # Kod indeksleme
│   ├── lsp-client/       # Language Server Protocol
│   ├── terminal/         # xterm.js entegrasyonu
│   ├── git/              # isomorphic-git
│   ├── search/           # ripgrep entegrasyonu
│   ├── ui/               # Paylaşılan UI bileşenleri
│   ├── themes/           # Tema motoru
│   └── extensions/       # Eklenti sistemi
├── resources/            # İkonlar, fontlar, modeller
├── scripts/              # Derleme ve dağıtım scriptleri
├── docs/                 # Dokümantasyon
└── tests/                # Testler
```

## 🎨 Tasarım Felsefesi

> "Cam gibi şeffaf, rüya gibi akıcı, düşünce gibi hızlı"

- **%100 Erişilebilirlik**: WCAG AAA standartları
- **60fps Sabit**: Asla frame düşmesi yok
- **Multi-Input**: Dokunmatik, kalem, fare, klavye, ses, göz takibi

## 🛡️ Gizlilik

- Hiçbir kod parçası telemetri olarak gönderilmez
- AI istekleri sadece yerel modellere gider (varsayılan)
- Opsiyonel bulut API için açık kullanıcı onayı gerekir
- Hassas veri filtreleme varsayılan AÇIK

## 📄 Lisans

[MIT License](./LICENSE)

## 🤝 Katkıda Bulunma

[Katkı Rehberi](./CONTRIBUTING.md) dosyasını okuyun.

## 🔗 Bağlantılar

- [Dokümantasyon](./docs/)
- [Web Sitesi](https://codex-ide.dev)
- [Discord Topluluğu](https://discord.gg/codex-ide)
- [Model Mağazası](https://models.codex-ide.dev)

---

<p align="center">
  <sub>Codex IDE - Kod Evrenine Hoş Geldin</sub>
</p>
