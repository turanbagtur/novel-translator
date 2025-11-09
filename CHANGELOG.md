# Changelog

Tüm önemli değişiklikler bu dosyada belgelenir.

## [2.0.0] - 2025-11-09

### 🎉 Büyük Güncelleme - Professional Edition

#### Eklenenler ✨

##### Çeviri Özellikleri
- 🤖 **Otomatik Terim Tespiti**: AI çeviri yaparken karakter isimleri, yer adları, yetenekler vb. otomatik sözlüğe eklenir
- ⚡ **Toplu Çeviri Sistemi**: Birden fazla bölümü tek seferde çevir
- 📊 **Gerçek Zamanlı İlerleme**: Background task desteği ile canlı ilerleme takibi

##### Export & Import
- 📄 **PDF Export**: Profesyonel e-kitap formatında export
- 📚 **EPUB Export**: E-okuyucu uyumlu format
- 📝 **DOCX Export**: Word belgesi olarak export
- 📃 **TXT Export**: Düz metin export
- 📥 **Sözlük İçe Aktarma**: CSV/Excel'den toplu terim import
- 📤 **Sözlük Dışa Aktarma**: CSV/Excel formatında sözlük export

##### Yönetim & Analiz
- 📊 **Dashboard**: Kapsamlı istatistikler ve görselleştirmeler
- 💰 **Maliyet Takibi**: Token bazlı maliyet hesaplama ve raporlama
- 💾 **Yedekleme Sistemi**: Otomatik ve manuel proje yedekleme
- 🔄 **Geri Yükleme**: Tek tıkla proje restore
- 📜 **Revizyon Geçmişi**: Bölüm düzenleme geçmişi

##### UI/UX İyileştirmeleri
- 🎨 **Modern Tema Sistemi**: Dark/Light/Auto mode
- ⌨️ **Klavye Kısayolları**: Hızlı erişim (Ctrl+N, D, T, S, F)
- 🎭 **Font Awesome Icons**: 1000+ profesyonel ikon
- 💫 **Smooth Animasyonlar**: Akıcı geçişler ve efektler
- 📱 **Responsive Design**: Mobil uyumlu tasarım
- 🎨 **Gradient Design**: Modern renkler ve efektler

##### Veritabanı
- `TranslationJob` - Toplu çeviri işleri tablosu
- `CostTracking` - Maliyet takip tablosu
- `ChapterRevision` - Revizyon geçmişi tablosu
- `ProjectBackup` - Yedek kayıtları tablosu
- `UserSettings` - Kullanıcı ayarları tablosu

##### API Endpoints
- `POST /api/batch/translate` - Toplu çeviri başlat
- `GET /api/batch/status/{job_id}` - İş durumu sorgula
- `GET /api/stats/dashboard` - Dashboard istatistikleri
- `GET /api/costs/summary` - Maliyet özeti
- `GET /api/export/project/{id}/{format}` - Proje export
- `POST /api/backup/create/{id}` - Yedek oluştur
- `POST /api/backup/restore` - Yedek geri yükle
- `POST /api/glossary/{id}/import` - Sözlük import
- `GET /api/glossary/{id}/export` - Sözlük export

#### Değişenler 🔄

- AI provider'lar artık terim çıkarma desteği ile yanıt dönüyor
- Çeviri istatistikleri maliyet bilgisi içeriyor
- Sözlük girişleri artık "confirmed" durumu içeriyor (otomatik/manuel)
- UI tamamen yenilendi - modern ve profesyonel

#### Düzeltilenler 🐛

- API anahtarı formu sıfırlanma sorunu giderildi
- Çeviri hatası detaylı loglama eklendi
- Chunks değişkeni başlatma hatası düzeltildi
- Model adı field çakışması çözüldü
- Responsive tasarım iyileştirildi

---

## [1.0.0] - 2024-11-09

### İlk Sürüm 🎊

#### Temel Özellikler
- ✅ Proje bazlı çeviri sistemi
- ✅ 6 AI sağlayıcı desteği (Gemini, OpenAI, Claude, Groq, DeepSeek, Perplexity)
- ✅ Akıllı sözlük yönetimi
- ✅ Bağlam farkındalığı
- ✅ Önbellek sistemi
- ✅ Modern web arayüzü
- ✅ Durum takibi
- ✅ Çoklu dil desteği

---

**Format**: [Versiyon] - Tarih
**Kategoriler**: Eklenenler, Değişenler, Düzeltilenler, Kaldırılanlar

