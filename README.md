<div align="center">

# 📚 Novel Translator v2.0
### Professional AI-Powered Translation Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()
[![AI Providers](https://img.shields.io/badge/AI_Providers-13-purple.svg)]()

**Yapay Zeka Destekli Profesyonel Roman Çeviri Platformu**

Tutarlı, akıcı ve yüksek kaliteli çeviriler için özel olarak tasarlanmış eksiksiz çözüm.

[Özellikler](#-yeni-özellikler-v20) • [Kurulum](#-kurulum) • [Hızlı Başlangıç](#-hızlı-başlangıç-ilk-kullanım) • [API'ler](#-çeviri-sağlayıcıları-13-farklı-ai) • [Dokümantasyon](#-dokümantasyon)

![Novel Translator](https://img.shields.io/badge/Made_with-❤️-red.svg)
![Translators](https://img.shields.io/badge/For-Translators-orange.svg)

</div>

---

## ⭐ Yeni Özellikler (v2.0)

### 🚀 Toplu Çeviri
- Birden fazla bölümü tek seferde çevirin
- Gerçek zamanlı ilerleme takibi
- Background task desteği
- İptal ve devam ettirme özelliği

### 📊 Gelişmiş Dashboard
- Kapsamlı istatistikler
- Maliyet analizi ve takibi
- Token kullanım raporu
- AI sağlayıcı karşılaştırması

### 📄 Çoklu Format Export
- **PDF**: Profesyonel e-kitap formatı
- **EPUB**: E-okuyucu uyumlu
- **DOCX**: Düzenlenebilir Word belgesi
- **TXT**: Evrensel metin formatı

### 💰 Maliyet Takibi
- Token bazlı maliyet hesaplama
- Proje bazlı harcama raporu
- AI sağlayıcı maliyet karşılaştırması
- Gerçek zamanlı maliyet tahmini

### 💾 Yedekleme Sistemi
- Otomatik ve manuel yedekleme
- Proje tam yedekleme (bölümler + sözlük)
- Tek tıkla geri yükleme
- Yedek geçmişi yönetimi

### 📖 Sözlük İçe/Dışa Aktarma
- CSV formatında export
- Excel (XLSX) formatında export
- Toplu sözlük import
- Proje arası sözlük paylaşımı

### 🎨 Tema Sistemi
- **Karanlık Tema**: Göz dostu, modern
- **Aydınlık Tema**: Klasik görünüm
- **Otomatik Tema**: Sistem tercihine göre

### ⌨️ Klavye Kısayolları
- `Ctrl + N`: Yeni proje
- `Ctrl + D`: Dashboard
- `Ctrl + T`: Çeviri başlat
- `Ctrl + S`: Kaydet
- `Ctrl + F`: Ara

## ✨ Temel Özellikler

### 🎯 Çeviri Özellikleri
- **🤖 Otomatik Terim Tespiti**: AI çeviri yaparken önemli terimleri otomatik sözlüğe ekler
  - Karakter isimleri
  - Yer adları
  - Yetenekler/Büyüler
  - Özel eşyalar
  - Organizasyonlar
- **Akıllı Hafıza**: Karakter isimleri ve özel terimler otomatik kaydedilir
- **Sözlük Yönetimi**: Manuel terim ekleme ve düzenleme
- **Bağlam Farkındalığı**: Önceki bölümlerden bağlam kullanma
- **Önbellek Sistemi**: Tekrar çeviri yapılmaz

### 🤖 Çeviri Sağlayıcıları (13 Farklı API!)

#### AI Modelleri (Akıllı Çeviri + Terim Tespiti)
1. **Google Gemini** 💎 - Hızlı ve ekonomik - ÜCRETSIZ!
2. **OpenAI (ChatGPT)** 🧠 - GPT-4 ile üstün kalite
3. **Anthropic Claude** 🤖 - Doğal ve akıcı çeviriler
4. **Groq** ⚡ - Çok hızlı işleme - ÜCRETSIZ!
5. **DeepSeek** 🔬 - Ekonomik güçlü model
6. **Perplexity** ♾️ - Güncel bilgi desteği

#### Profesyonel Çeviri API'leri (En Yüksek Kalite)
7. **DeepL** 🌐 - #1 Çeviri kalitesi (Novel için ideal!)
8. **Google Cloud Translate** 🌍 - Güvenilir ve hızlı
9. **Microsoft Translator** 🔷 - Azure destekli
10. **Yandex Translate** 🇷🇺 - Rusça ve Türkçe'de mükemmel

#### Ücretsiz/Açık Kaynak
11. **LibreTranslate** 🆓 - Açık kaynak, gizlilik odaklı
12. **MyMemory** 📚 - Dünyanın en büyük translation memory

### 📁 Proje Yönetimi
- Seri bazlı organizasyon
- Bölüm bazlı çeviri
- Durum takibi (Pending, Processing, Completed)
- İstatistikler ve raporlar

## 🚀 Kurulum

### Sistem Gereksinimleri
- **Python**: 3.8 veya üzeri (3.11 önerilir)
- **pip**: Python paket yöneticisi
- **Disk**: ~500MB boş alan
- **RAM**: Minimum 2GB
- **İnternet**: İlk kurulum ve AI kullanımı için

### 📥 Hızlı Kurulum (3 Adım)

#### 1️⃣ Projeyi İndirin
```bash
# Git ile klonlayın
git clone https://github.com/yourusername/Novel-Translator.git
cd Novel-Translator

# veya ZIP olarak indirip açın
```

#### 2️⃣ Bağımlılıkları Yükleyin
```bash
# Tüm gerekli paketleri yükle
pip install -r requirements.txt
```

**Not**: İlk kurulumda ~100MB paket indirilecek (~2-5 dakika).

#### 3️⃣ Başlatın!
```bash
# Otomatik kurulum ve başlatma
python run.py
```

**Windows Kullanıcıları**: `start.bat` dosyasına çift tıklayın.

### ✅ İlk Çalıştırma

Uygulama otomatik olarak:
- ✅ Veritabanını oluşturur (`novel_translator.db`)
- ✅ Klasörleri oluşturur (`exports/`, `backups/`)
- ✅ Web sunucusunu başlatır (Port 8000)
- ✅ Tarayıcıda açılır: `http://localhost:8000`

### 🔧 Alternatif Başlatma Yöntemleri
```bash
# Direkt uvicorn ile
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Farklı port ile
uvicorn main:app --port 8001

# Production modu (reload kapalı)
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📖 Hızlı Başlangıç (İlk Kullanım)

### 🎯 5 Dakikada Başlayın!

Detaylı kılavuz için: [`QUICKSTART.md`](QUICKSTART.md) dosyasına bakın.

### 1. AI Yapılandırması (1 dakika)
1. **Ayarlar** → AI sağlayıcı seçin
2. API anahtarı girin
3. Model ve parametreleri ayarlayın
4. Kaydet

#### API Anahtarı Alın:

**AI Modelleri:**
- 💎 [Google Gemini](https://makersuite.google.com/app/apikey) - **ÜCRETSİZ**
- 🧠 [OpenAI](https://platform.openai.com/api-keys) - Ücretli
- 🤖 [Anthropic Claude](https://console.anthropic.com/) - Ücretli
- ⚡ [Groq](https://console.groq.com/) - **ÜCRETSİZ**
- 🔬 [DeepSeek](https://platform.deepseek.com/) - Ekonomik
- ♾️ [Perplexity](https://www.perplexity.ai/settings/api) - Ücretli

**Profesyonel Çeviri:**
- 🌐 [DeepL](https://www.deepl.com/pro-api) - 500K karakter/ay ücretsiz
- 🌍 [Google Cloud Translate](https://cloud.google.com/translate) - $20/1M karakter
- 🔷 [Microsoft Translator](https://azure.microsoft.com/services/cognitive-services/translator/) - 2M karakter/ay ücretsiz
- 🇷🇺 [Yandex Translate](https://cloud.yandex.com/services/translate) - Ücretli

**Ücretsiz/Açık Kaynak:**
- 🆓 [LibreTranslate](https://libretranslate.com/) - **TAMAMEN ÜCRETSİZ**
- 📚 MyMemory - API key gerektirmez, **ÜCRETSİZ**

### 2. Proje Oluştur
1. **Projeler** → **Yeni Proje**
2. Bilgileri doldurun
3. AI sağlayıcı seçin

### 3. Bölüm Ekle ve Çevir
1. **Çeviri** → Proje seç
2. **Bölüm Ekle** → Metni yapıştır
3. **Ekle ve Çevir** veya **Sadece Ekle**

### 4. Sözlük Yönetimi

#### 🤖 Otomatik Terim Ekleme (YENİ! 🆕)
AI çeviri yaparken önemli terimleri **otomatik olarak** tespit edip sözlüğe ekler:
- ✅ Karakter isimleri (Jin-Woo, Cha Hae-In, vb.)
- ✅ Yer adları (Shadow Dungeon, Hunter's Guild, vb.)
- ✅ Yetenekler/Büyüler (Shadow Exchange, Monarch's Domain, vb.)
- ✅ Özel eşyalar (Demon King's Dagger, vb.)
- ✅ Organizasyonlar (Hunter Association, vb.)

**Not**: Otomatik eklenen terimler "Onaylanmamış" olarak işaretlenir. Sözlük sayfasından kontrol edip onaylayabilir veya düzeltebilirsiniz.

#### ✍️ Manuel Terim Ekleme
1. **Sözlük** → Proje seç
2. **Terim Ekle** → Çevirileri tanımla
3. Terimler sonraki çevirilerde otomatik kullanılır

## 💡 Kullanım İpuçları

### 🎯 En İyi Çeviri Kalitesi İçin
1. **İlk bölümü dikkatlice çevirin** - Sözlük temelini oluşturur
2. **Önemli terimleri manuel ekleyin** - Karakter isimleri, yetenekler, vb.
3. **Bölüm bölüm ilerleyin** - Tutarlılık için
4. **Sözlüğü düzenli kontrol edin** - Yanlış çevirileri düzeltin

### 💰 Maliyet Optimizasyonu
- **Önbellek kullanın** - Aynı metinler tekrar çevrilmez
- **Groq veya Gemini** - Ücretsiz/ekonomik seçenekler
- **Dashboard'dan takip** - Harcamaları izleyin
- **Toplu çeviri** - Daha verimli

### 📊 Verimlilik
- **Toplu çeviri** kullanın - 10+ bölümü birden
- **Klavye kısayolları** - Hızlı erişim
- **Düzenli yedekleme** - Güvenli çalışma
- **Export** - İş bittikten sonra dışa aktarın

## 🏗️ Proje Yapısı

```
Novel-Translator/
├── main.py                    # FastAPI backend
├── database.py               # Veritabanı modelleri
├── config.py                 # Ayarlar
├── ai_providers.py           # AI entegrasyonları
├── translation_engine.py     # Çeviri motoru
├── cost_tracking.py          # Maliyet takibi
├── batch_translation.py      # Toplu çeviri
├── export_service.py         # Export işlemleri
├── backup_service.py         # Yedekleme sistemi
├── requirements.txt          # Bağımlılıklar
├── run.py                    # Başlatma scripti
├── static/
│   ├── index.html           # Ana sayfa
│   ├── style.css            # Ana stiller
│   ├── styles_additions.css # Yeni özellik stilleri
│   └── script.js            # Frontend mantığı
├── exports/                 # Export dosyaları
├── backups/                 # Yedek dosyaları
└── README.md               # Bu dosya
```

## 🗄️ Veritabanı

SQLite veritabanı (`novel_translator.db`) otomatik oluşturulur.

### Tablolar:
- **projects** - Proje bilgileri
- **chapters** - Bölüm verileri
- **glossary_entries** - Sözlük terimleri
- **api_configs** - AI yapılandırmaları
- **translation_cache** - Çeviri önbelleği
- **translation_jobs** - Toplu çeviri işleri
- **cost_tracking** - Maliyet kayıtları
- **chapter_revisions** - Bölüm geçmişi
- **project_backups** - Yedek kayıtları
- **user_settings** - Kullanıcı ayarları

## 🎨 Arayüz Özellikleri

### Modern UI
- 🎨 Gradient butonlar ve kartlar
- 💫 Smooth animasyonlar
- 📱 Responsive tasarım
- 🌓 Dark/Light tema
- ⚡ Hızlı yükleme
- 🎭 Font Awesome ikonları

### Dashboard
- 📊 İstatistik kartları
- 💰 Maliyet özeti
- 📈 İlerleme çubukları
- 🤖 AI sağlayıcı analizi

### Çeviri Yönetimi
- ✅ Durum göstergeleri
- 🎯 Toplu işlemler
- 📝 Yan yana görünüm
- ⚡ Hızlı eylemler

## ⚙️ Gelişmiş Ayarlar

### AI Parametreleri
- **Max Tokens**: 100-32000 (varsayılan: 4000)
- **Temperature**: 0.0-2.0 (varsayılan: 0.7)
  - 0.3: Tutarlı, kelimesi kelimesine
  - 0.7: Dengeli
  - 1.0+: Yaratıcı, serbest

### Çeviri Stratejisi
1. Metni paragraflara böl
2. Her parçayı ayrı çevir
3. Sözlük kullan
4. Bağlam ekle
5. Sonuçları birleştir

## 🔒 Güvenlik
- API anahtarları güvenle saklanır
- Veriler yerel veritabanında
- Yedeklemeler ZIP formatında
- Şifreleme desteği (opsiyonel)

## 🐛 Sorun Giderme

### Kurulum Sorunları

#### "ModuleNotFoundError"
```bash
# Çözüm: Paketleri yeniden yükleyin
pip install -r requirements.txt --upgrade
```

#### Port 8000 zaten kullanımda
```bash
# Çözüm: Farklı port kullanın
uvicorn main:app --port 8001
```

#### ImportError veya syntax hatası
```bash
# Python versiyonunu kontrol edin
python --version  # 3.8+ olmalı

# Doğru Python kullanın
python3 run.py
```

### Kullanım Sorunları

#### "AI provider not configured"
✅ **Çözüm**: Ayarlar → AI seç → API key gir → Kaydet
✅ API anahtarının geçerli olduğunu test edin

#### Çeviri çok yavaş
✅ **Çözüm**: Groq veya Gemini kullanın (çok hızlı)
✅ Küçük bölümler halinde çevirin
✅ Temperature düşürün (0.3-0.5)

#### Tutarsız çeviriler
✅ **Çözüm**: Sözlük'ten önemli terimleri ekleyin
✅ İlk bölümde manuel terim ekleyin
✅ Aynı AI sağlayıcıyı kullanın
✅ Temperature 0.5'e çekin

#### Export çalışmıyor
✅ **Çözüm**: 
```bash
pip install reportlab ebooklib python-docx
```
✅ Bölümlerin çevrilmiş olduğunu kontrol edin
✅ `exports/` klasörüne yazma izni olduğundan emin olun

#### Sözlük onaylama hatası
✅ **Çözüm**: Proje seçili olduğundan emin olun
✅ Sayfayı yenileyin (F5)
✅ Tarayıcı console'una bakın (F12)

### Genel Sorunlar

#### Uygulama açılmıyor
```bash
# 1. Python versiyonunu kontrol edin
python --version

# 2. Bağımlılıkları kontrol edin
pip list | grep fastapi

# 3. Hata log'larını görün
python run.py
```

#### Veritabanı hatası
```bash
# Veritabanını sıfırlayın
rm novel_translator.db
python run.py  # Otomatik oluşturulur
```

### 🆘 Hala Çözülmedi mi?

1. **GitHub Issues** açın: Detaylı hata mesajı ile
2. **Log dosyalarını** ekleyin
3. **Python versiyonu** belirtin
4. **İşletim sistemi** belirtin

## 📚 Dokümantasyon

### Kullanıcı Kılavuzları
- 📖 [`README.md`](README.md) - Ana dokümantasyon (bu dosya)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) - 5 dakikada başlangıç kılavuzu
- ⚙️ [`FEATURES.md`](FEATURES.md) - Detaylı özellik listesi
- 🤖 [`API_GUIDE.md`](API_GUIDE.md) - AI sağlayıcı karşılaştırması
- 📋 [`PROVIDERS_QUICKREF.md`](PROVIDERS_QUICKREF.md) - Hızlı API referansı
- 📝 [`CHANGELOG.md`](CHANGELOG.md) - Sürüm geçmişi

### API Dokümantasyonu
Uygulamayı başlattıktan sonra:
- **Swagger UI**: http://localhost:8000/docs (interaktif API testi)
- **ReDoc**: http://localhost:8000/redoc (detaylı dokümantasyon)

### Temel Endpoint'ler:

```
GET  /api/projects                    # Projeleri listele
POST /api/projects                    # Yeni proje
GET  /api/projects/{id}               # Proje detayı

POST /api/projects/{id}/chapters      # Bölüm ekle
POST /api/translate                   # Çevir
POST /api/batch/translate             # Toplu çevir

GET  /api/stats/dashboard             # Dashboard
GET  /api/costs/summary               # Maliyet özeti

GET  /api/export/project/{id}/{format} # Export
POST /api/backup/create/{id}          # Yedekle
POST /api/backup/restore              # Geri yükle

GET  /api/glossary/{id}/export        # Sözlük export
POST /api/glossary/{id}/import        # Sözlük import
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! 🎉

### Nasıl Katkıda Bulunulur?

1. **Fork** edin bu repository'yi
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

### Katkı Alanları
- 🐛 Bug düzeltmeleri
- ✨ Yeni özellikler
- 📚 Dokümantasyon iyileştirmeleri
- 🌍 Yeni dil desteği
- 🤖 Yeni AI sağlayıcı entegrasyonu
- 🎨 UI/UX iyileştirmeleri

### Geliştirme Ortamı
```bash
# Clone repo
git clone https://github.com/yourusername/Novel-Translator.git
cd Novel-Translator

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Geliştirme modunda çalıştır
python run.py
```

## 📄 Lisans

MIT License

## 🙏 Teşekkürler

Bu proje şu teknolojileri kullanmaktadır:

### Backend
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Vali validation
- **Uvicorn** - ASGI server

### Export
- **ReportLab** - PDF oluşturma
- **EbookLib** - EPUB oluşturma
- **python-docx** - Word belgeleri
- **pandas** - CSV/Excel işlemleri

### Frontend
- **Font Awesome** - İkonlar
- **Vanilla JS** - Saf JavaScript
- **CSS3** - Modern stiller

### AI Providers
- Tüm AI sağlayıcıların resmi SDK'ları

## 📈 Yol Haritası

### Yakında Gelecek Özellikler:
- [ ] Çeviri editörü (manuel düzenleme)
- [ ] Multi-AI karşılaştırma
- [ ] Gelişmiş arama ve filtreleme
- [ ] Önbellek yönetim paneli
- [ ] Otomasyon kuralları
- [ ] Webhook entegrasyonu
- [ ] REST API (harici kullanım)
- [ ] Docker desteği
- [ ] Cloud storage entegrasyonu

## 💬 Destek

Sorularınız için:
- GitHub Issues açın
- Dokümantasyonu okuyun
- API Docs'a bakın

## 📊 İstatistikler

**Novel Translator v2.0**
- 📦 10+ yeni özellik
- 🤖 6 AI sağlayıcı desteği
- 📄 4 export formatı
- 🌍 Çoklu dil desteği
- 💾 Otomatik yedekleme
- 📊 Kapsamlı raporlama

---

**Not**: Bu yazılım eğitim ve kişisel kullanım amaçlıdır. Telif hakkı koruması altındaki materyalleri çevirirken yerel yasalara uyun.

## 🌟 Özellik Karşılaştırması

| Özellik | v1.0 | v2.0 |
|---------|------|------|
| Temel Çeviri | ✅ | ✅ |
| AI Sağlayıcı | 6 | **12** 🆕 |
| Sözlük Yönetimi | ✅ | ✅ |
| **Otomatik Terim Tespiti** | ❌ | ✅ 🆕 |
| **Toplu Çeviri** | ❌ | ✅ |
| **Dashboard** | ❌ | ✅ |
| **Maliyet Takibi** | ❌ | ✅ |
| **Export (PDF/EPUB/DOCX)** | ❌ | ✅ |
| **Yedekleme** | ❌ | ✅ |
| **Tema Sistemi** | ❌ | ✅ |
| **Klavye Kısayolları** | ❌ | ✅ |
| **Sözlük Import/Export** | ❌ | ✅ |
| **DeepL & Profesyonel API** | ❌ | ✅ 🆕 |

Mutlu çeviriler! 📚✨🚀

---

## 📜 Copyright & Yasal Bildirim

**Novel Translator v2.0** - Professional Edition
Made with ❤️ for translators

### Copyright © 2025 Novel Translator Project

Bu yazılım MIT Lisansı altında lisanslanmıştır.

#### İzin Verilen Kullanımlar:
✅ Kişisel kullanım için sınırsız erişim
✅ Eğitim amaçlı kullanım
✅ Kaynak kodunu inceleme ve değiştirme
✅ Ticari olmayan projelerde kullanım
✅ Fork ve katkıda bulunma

#### Yasal Sorumluluklar:
⚠️ Bu yazılım telif hakkı koruması altındaki materyallerin çevirisinde kullanılırken, kullanıcılar yerel ve uluslararası telif hakkı yasalarına uymakla yükümlüdür.

⚠️ Yazılımın geliştiricileri, kullanıcıların yasa dışı faaliyetlerinden sorumlu tutulamaz.

⚠️ AI sağlayıcılarının kullanım şartlarına ve gizlilik politikalarına uyulmalıdır.

⚠️ API anahtarlarınızın güvenliğinden siz sorumlusunuz.

#### Feragatname (Disclaimer):
Bu yazılım "OLDUĞU GİBİ" sunulmaktadır ve herhangi bir garanti olmaksızın sağlanmaktadır. Yazılımın kullanımından doğabilecek herhangi bir doğrudan veya dolaylı zarar için geliştiriciler sorumluluk kabul etmez.

#### Etik Kullanım:
🤝 Bu yazılım, çevirmenlere yardımcı olmak ve çeviri sürecini hızlandırmak için tasarlanmıştır.

🤝 Profesyonel çeviri kalitesini artırmayı ve tutarlılığı sağlamayı amaçlar.

🤝 Telif hakkına saygılı ve etik kullanım teşvik edilir.

#### İletişim:
📧 Sorular ve öneriler için GitHub Issues kullanabilirsiniz.
🐛 Bug raporları ve feature request'ler GitHub üzerinden yapılabilir.

#### Katkıda Bulunanlar:
Bu projeye katkıda bulunan herkese teşekkürler! 🙏

#### Lisans Metni:
```
MIT License

Copyright (c) 2024 Novel Translator Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Novel Translator** - Powering the future of multilingual literature 🌍📚
Developed with passion for translators worldwide 💙

*Last Updated: November 2025*
