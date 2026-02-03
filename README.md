**Rahman Ve Rahim Olan Allah'ın Adıyla (başlarım)**

# GoToGo Dashboard v2.0 🚗

Tesla tarzı, modern araç kontrol paneli uygulaması. Arduino tabanlı elektronik diferansiyel sistemi (EDS) ile entegre.

## ✨ Özellikler

### Bağlantı Desteği
- ✅ **USB Serial** - Otomatik port algılama (Windows/Linux/macOS)
- ✅ **WiFi (TCP/IP)** - Kablosuz bağlantı
- ✅ **Bluetooth** - Bluetooth seri port profili

### Görsel Arayüz
- 🚀 Tesla tarzı modern tasarım
- 📊 Gerçek zamanlı hız, mod, vites göstergeleri
- 🎯 EDS (Elektronik Diferansiyel Sistemi) durumu
- 🔄 Direksiyon açısı ve motor güçleri
- 💡 Araç sinyal ve far göstergeleri
- 🗺️ Google Maps entegrasyonu
- 🕐 Saat ve tarih widget'ı

### Yeni Özellikler (v2.0)
- 📱 **USB Telefon Ekran Yansıtma** (scrcpy ile)
- 🔌 **Otomatik Port Algılama** (İşletim sistemine göre)
- 🌐 **Multi-Platform Destek** (Windows, Linux, macOS)
- 🔄 **Otomatik Yeniden Bağlanma**
- ⚙️ **Grafik Arayüzlü Ayarlar Paneli**

### Arduino Entegrasyonu
- 🎮 Mod seçimi (Eco / Normal / Sport)
- 🚦 Vites kontrolü (N / D / R)
- 💡 Far ve sinyal takibi
- 🎯 Elektronik Diferansiyel Sistemi (EDS) desteği
- 📐 Direksiyon açısı sensörü
- ⚡ Çift motor gaz kontrolü

## 📋 Gereksinimler

### Yazılım
- Python 3.8+
- PySide6 (Qt6)
- pyserial
- pybluez (Bluetooth desteği için)

### Donanım
- Arduino (GoToGo 7.5 Alpha yazılımı yüklü)
- USB/WiFi/Bluetooth bağlantı
- Enkoder (direksiyon açısı için)
- Motor sürücüleri

### Opsiyonel
- Android telefon (ekran yansıtma için)
- ADB (Android Debug Bridge)
- scrcpy (ekran yansıtma aracı)

## 🚀 Kurulum

### 1. Python Paketlerini Yükle
```bash
pip install -r requirements.txt
```

### 2. Telefon Ekran Yansıtma (Opsiyonel)

**Linux:**
```bash
sudo apt install adb scrcpy
```

**Windows:**
```bash
scoop install adb scrcpy
# veya chocolatey: choco install adb scrcpy
```

**macOS:**
```bash
brew install android-platform-tools scrcpy
```

### 3. Bluetooth Desteği (Opsiyonel)

**Linux:**
```bash
sudo apt install bluetooth libbluetooth-dev
pip install pybluez
```

**Windows:**
```bash
pip install pybluez
```

**macOS:**
```bash
pip install pyobjc-framework-CoreBluetooth
```

## 🎮 Kullanım

### Hızlı Başlangıç
```bash
python main.py
```

Uygulama otomatik olarak USB portunu algılamaya çalışacaktır.

### Bağlantı Ayarları

1. Uygulamayı başlatın
2. Alt paneldeki **⚙️ Ayarlar** butonuna tıklayın
3. Bağlantı tipini seçin:
   - **USB Serial**: Port seçin ve baud rate'i ayarlayın (varsayılan: 115200)
   - **WiFi**: Arduino'nun IP adresi ve port numarasını girin
   - **Bluetooth**: Cihazları arayın ve Arduino'yu seçin
4. **Bağlan** butonuna tıklayın

### Telefon Ekran Yansıtma

1. Android telefonunuzu USB ile bilgisayara bağlayın
2. Telefonda **Geliştirici Seçenekleri** > **USB Hata Ayıklama** açık olmalı
3. Alt paneldeki **📱 Telefon** butonuna tıklayın
4. Açılan panelden **Ekranı Yansıt** butonuna basın

## 📊 Arduino Serial Protokolü

Uygulama aşağıdaki formatta veri bekler:

```
mode/far/durum/far2/vites/sinyallambasi/dortlu/sinyalsol/sinyalsag/speed1/speed2/direksiyonaci/solGaz/sagGaz/EDS_AKTIF
```

**Örnek:**
```
1/2/1/0/1/0/0/0/1/45.5/46.2/12.5/75/80/1
```

### Veri Alanları

| Alan | Açıklama | Değerler |
|------|----------|----------|
| mode | Sürüş modu | 0=Eco, 1=Normal, 2=Sport |
| far | Ön far | 0=Kapalı, 1=Otomatik, 2=Açık |
| durum | Araç durumu | 0=Kapalı, 1=Açık, 2=Aksesuvar |
| far2 | Uzun/Sis far | 0=Kapalı, 1=Uzun, 2=Sis |
| vites | Vites | 0=Nötr, 1=İleri, 2=Geri |
| sinyallambasi | Sinyal lambası | 0/1 |
| dortlu | Dörtlü flaşör | 0/1 |
| sinyalsol | Sol sinyal | 0/1 |
| sinyalsag | Sağ sinyal | 0/1 |
| speed1 | Sol motor hızı | km/h |
| speed2 | Sağ motor hızı | km/h |
| direksiyonaci | Direksiyon açısı | Derece (-180 ile +180) |
| solGaz | Sol motor gaz | % (0-100) |
| sagGaz | Sağ motor gaz | % (0-100) |
| EDS_AKTIF | EDS durumu | 0=Kapalı, 1=Aktif |

## 🔧 Sorun Giderme

### Port Bulunamıyor
- Arduino'nun USB ile bağlı olduğundan emin olun
- Gerekli sürücülerin yüklü olduğunu kontrol edin
- Linux'ta kullanıcınızın `dialout` grubunda olması gerekir:
  ```bash
  sudo usermod -a -G dialout $USER
  # Yeniden giriş yapın
  ```

### Bluetooth Bağlanamıyor
- Bluetooth'un açık olduğundan emin olun
- Arduino Bluetooth modülü ile eşleştirilmiş olmalı
- Linux'ta bluetooth servisi çalışıyor olmalı:
  ```bash
  sudo systemctl start bluetooth
  ```

### Telefon Ekranı Yansıtılamıyor
- ADB ve scrcpy kurulu olmalı
- Telefonda USB Hata Ayıklama açık olmalı
- İlk bağlantıda telefonda izin vermeniz gerekebilir

### Veri Gelmiyor
- Serial ayarlarını kontrol edin (Baud rate: 115200)
- Arduino'da doğru firmware yüklü olduğundan emin olun
- Serial monitörde veri geldiğini kontrol edin

## 🎨 Özelleştirme

### Tema Renkleri
`ui/left_panel.py` dosyasındaki stil kodlarını düzenleyerek renkleri değiştirebilirsiniz.

### Mod İsimleri
```python
mode_names = ["ECO", "NORMAL", "SPORT"]
mode_colors = ["#00ff44", "#00aaff", "#ff4444"]
```

### Bağlantı Varsayılanları
`main.py` içinde `auto_connect` metodunu düzenleyin.

## 📝 Lisans

Bu proje GoToGo projesi kapsamında geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---


