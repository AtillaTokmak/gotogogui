# 🚀 Hızlı Başlangıç Kılavuzu

## 5 Dakikada Dashboard Kurulumu

### 1️⃣ Gerekli Araçları Yükleyin

**Python 3.8+ gerekli!**

```bash
# Python versiyonunu kontrol edin
python3 --version
```

### 2️⃣ Projeyi İndirin ve Kurun

**Linux / macOS:**
```bash
cd dashbqoard_v2
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
cd dashbqoard_v2
install.bat
```

### 3️⃣ Arduino'yu Bağlayın

1. Arduino'nuzu USB ile bilgisayara bağlayın
2. Arduino IDE'de `ARDUINO_INTEGRATION.ino` dosyasını açın
3. Kartınızı ve portu seçin
4. Yükle butonuna basın

### 4️⃣ Uygulamayı Başlatın

**Linux / macOS:**
```bash
source venv/bin/activate
python main.py
```

**Windows:**
```cmd
venv\Scripts\activate.bat
python main.py
```

### 5️⃣ İlk Bağlantı

Uygulama başladığında:

1. **Otomatik Bağlantı**: Uygulama otomatik olarak USB portunu bulmaya çalışır
2. **Manuel Bağlantı**: Alt paneldeki ⚙️ Ayarlar butonuna tıklayın
   - Port seçin (otomatik tespit edilir)
   - Bağlan'a tıklayın

### ✅ Başarılı Bağlantı

Bağlantı başarılı olduğunda:
- Sol panel: Hız, mod ve vites bilgileri görünür
- Sağ alt köşe: 🟢 Bağlı (USB) yazısı çıkar
- Veriler gerçek zamanlı güncellenir

---

## 🐛 Sorun mu yaşıyorsunuz?

### Port bulunamadı
```bash
# Linux için
sudo usermod -a -G dialout $USER
# Yeniden giriş yapın

# Portları manuel kontrol
python test_connection.py
```

### Modül bulunamadı hatası
```bash
# Virtual environment aktif mi kontrol edin
which python  # Linux/macOS
where python  # Windows

# Paketleri yeniden yükleyin
pip install -r requirements.txt
```

### Arduino'dan veri gelmiyor
1. Arduino'da Serial.begin(115200) olduğundan emin olun
2. Arduino Serial Monitor'de veri geldiğini kontrol edin
3. Baud rate'in 115200 olduğunu kontrol edin

---

## 📱 Telefon Ekran Yansıtma (Opsiyonel)

### Gereksinimler
- Android telefon
- USB kablosu
- ADB ve scrcpy yüklü

### Kurulum

**Linux:**
```bash
sudo apt install adb scrcpy
```

**macOS:**
```bash
brew install android-platform-tools scrcpy
```

**Windows:**
```powershell
scoop install adb scrcpy
# veya
choco install adb scrcpy
```

### Kullanım

1. Telefonu USB ile bağlayın
2. Telefonda **Geliştirici Seçenekleri** > **USB Hata Ayıklama** açık olmalı
3. Dashboard'da **📱 Telefon** butonuna tıklayın
4. **Ekranı Yansıt** butonuna basın

---

## 🎮 Temel Kullanım

### Klavye Kısayolları
- `F11`: Tam ekran aç/kapat
- `Esc`: Tam ekrandan çık
- `Ctrl+Q`: Uygulamadan çık

### Butonlar
- **🎵 Spotify**: Media player'ı aç
- **📺 YouTube**: Media player'ı aç
- **📱 Telefon**: Telefon kontrol panelini aç
- **⚙️ Ayarlar**: Bağlantı ayarları

### Göstergeler
- **Hız**: Ana ekranda büyük rakamlarla
- **Mod**: ECO (yeşil) / NORMAL (mavi) / SPORT (kırmızı)
- **Vites**: N (nötr) / D (ileri) / R (geri)
- **EDS**: Aktif olduğunda yeşil ✓
- **Motor Güçleri**: Progress bar'larda yüzde olarak
- **Bağlantı**: Sağ altta durum göstergesi

---

## 🔧 İleri Düzey

### WiFi Bağlantı

Arduino'ya ESP8266/ESP32 ekleyin:

```cpp
// Arduino kodunda
Serial1.begin(115200);  // ESP modülü için
// Serial print'leri Serial1'e yönlendirin
```

Dashboard'da:
1. Ayarlar > WiFi seçin
2. ESP'nin IP adresini girin
3. Port girin (varsayılan: 8888)
4. Bağlan

### Bluetooth Bağlantı

HC-05/HC-06 modülü ekleyin:

```cpp
// Arduino baudrate ayarı (AT modunda)
AT+BAUD8  // 115200 için
```

Dashboard'da:
1. Ayarlar > Bluetooth seçin
2. Cihazları Ara
3. Arduino modülünü seçin
4. Bağlan

### Veri Test Aracı

```bash
python test_connection.py
```

Bu araç ile:
- Mevcut portları listele
- Bluetooth cihazlarını tara
- Veri akışını gerçek zamanlı izle
- Bağlantı sorunlarını teşhis et

---

## 📚 Daha Fazla Bilgi

- Detaylı dokümantasyon: `README.md`
- Versiyon geçmişi: `CHANGELOG.md`
- Arduino entegrasyonu: `ARDUINO_INTEGRATION.ino`

## 💬 Destek

Sorun yaşarsanız:
1. `test_connection.py` ile bağlantıyı test edin
2. README.md'deki sorun giderme bölümüne bakın
3. GitHub'da issue açın

---

**Başarılar! İyi sürüşler! 🚗💨**
