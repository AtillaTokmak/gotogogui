# Değişiklik Geçmişi

## [2.1.0] - 2025-02-04

### Yeni Özellikler ✨
- **🎥 Geri Görüş Kamerası**: USB kamera desteği eklendi
  - Geri vitese takılınca otomatik kamera görünümüne geçiş
  - Park yardım çizgileri (yeşil, sarı, kırmızı bölgeler)
  - 1280x720 çözünürlük, 30 FPS görüntü akışı
  - Aynalama özelliği (daha kolay park için)
  - İleri vitese geçince otomatik harita görünümüne dönüş
  - Gerçek zamanlı video akışı (<100ms gecikme)

### Teknik İyileştirmeler 🔧
- OpenCV-Python entegrasyonu
- NumPy görüntü işleme
- Kaynak yönetimi (kamera başlat/durdur)
- Thread-safe kamera operasyonları
- Otomatik kamera cihaz algılama (/dev/video0)

### Dokümantasyon 📚
- Geri görüş kamerası kullanım kılavuzu
- Raspberry Pi kamera kurulum talimatları
- Sorun giderme bölümü güncellendi

## [2.0.0] - 2025-02-03

### Yeni Özellikler ✨
- **Multi-platform Serial Port Desteği**: Windows, Linux ve macOS için otomatik port algılama
- **WiFi Bağlantı Desteği**: TCP/IP üzerinden kablosuz Arduino bağlantısı
- **Bluetooth Desteği**: Bluetooth Serial Port Profile ile bağlantı
- **USB Telefon Ekran Yansıtma**: scrcpy ile Android telefon ekranını dashboard'a yansıtma
- **Grafik Ayarlar Paneli**: Bağlantı ayarları için kullanıcı dostu dialog
- **Otomatik Yeniden Bağlanma**: Bağlantı kopunca otomatik yeniden deneme
- **Gelişmiş Veri Gösterimi**: Motor güçleri için progress bar'lar
- **Araç Görsel Göstergesi**: Sinyal, far ve diğer göstergeler için animasyonlu widget

### İyileştirmeler 🔧
- Yeni Arduino serial protokolüne tam uyumluluk (15 alan)
- Vites değişimlerinde gerçek zamanlı görsel geri bildirim
- EDS (Elektronik Diferansiyel Sistemi) durumu göstergesi
- Direksiyon açısı görselleştirmesi
- Mod (Eco/Normal/Sport) renk kodlaması
- Bağlantı durumu göstergesi
- Hata mesajları ve bildirimler

### Hata Düzeltmeleri 🐛
- Serial port okuma hataları düzeltildi
- Frontend veri güncelleme sorunları giderildi
- Geri vites sahnesi eklendi (placeholder)
- Buton tepkisizlik sorunları çözüldü

### Teknik Değişiklikler 🔨
- ArduinoReader sınıfı tamamen yeniden yazıldı
- Thread-safe veri okuma implementasyonu
- Signal/Slot mekanizması ile güvenli GUI güncellemeleri
- Platform bağımsız serial port algılama
- Bluetooth cihaz tarama özelliği
- WiFi socket bağlantı yönetimi

### Dokümantasyon 📚
- Kapsamlı README.md eklendi
- Kurulum betikleri (Linux/macOS/Windows)
- Requirements.txt düzenlendi
- Kullanım kılavuzu ve sorun giderme bölümleri

## [1.0.0] - İlk Sürüm

### Temel Özellikler
- Tesla tarzı dashboard arayüzü
- Basit serial port okuma
- Hız göstergesi
- Harita entegrasyonu
- Media overlay
- Saat widget'ı

---

## Gelecek Sürümler için Planlanan Özellikler 🚀

### [2.2.0] - Planlanan
- [ ] CAN Bus desteği
- [ ] Navigasyon entegrasyonu (turn-by-turn)
- [ ] Spotify/YouTube media kontrolleri
- [ ] Mesajlaşma özellikleri
- [ ] Sesli asistan entegrasyonu
- [ ] Tema özelleştirme paneli
- [ ] Çoklu kamera desteği (ön, arka, yan)

### [3.0.0] - Uzun Vadeli
- [ ] Bulut senkronizasyonu
- [ ] Sürüş istatistikleri ve analitik
- [ ] Uzaktan araç kontrolü
- [ ] OTA (Over-The-Air) güncellemeler
- [ ] Çoklu dil desteği
- [ ] Kullanıcı profilleri
