# 🎥 Geri Görüş Kamerası Kurulum Kılavuzu

Bu kılavuz, GoToGo Dashboard'a USB kamera entegrasyonu için gerekli adımları açıklar.

## 📋 Gereksinimler

### Donanım
- Raspberry Pi (3/4/5)
- USB Webcam (720p veya üzeri önerilir)
- USB kablosu
- Araç kadranı ekranı

### Yazılım
- Raspberry Pi OS (Bullseye veya üzeri)
- Python 3.8+
- OpenCV
- v4l-utils (Video4Linux araçları)

## 🔧 Kurulum Adımları

### 1. Sistem Paketlerini Güncelle
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Video4Linux Araçlarını Yükle
```bash
sudo apt install v4l-utils -y
```

### 3. Python Kütüphanelerini Yükle
```bash
# OpenCV ve NumPy
pip3 install opencv-python numpy

# Veya requirements.txt üzerinden
pip3 install -r requirements.txt
```

### 4. USB Kamerayı Bağla
1. USB kamerayı Raspberry Pi'ye takın
2. Kameranın algılandığını kontrol edin:
```bash
ls -l /dev/video*
```
Çıktı şu şekilde olmalı:
```
crw-rw---- 1 root video 81, 0 Feb  4 10:30 /dev/video0
```

### 5. Kamera Bilgilerini Görüntüle
```bash
v4l2-ctl --list-devices
```

Örnek çıktı:
```
USB Camera (usb-0000:01:00.0-1.2):
    /dev/video0
    /dev/video1
```

### 6. Kullanıcı İzinlerini Ayarla
```bash
# Kullanıcınızı video grubuna ekleyin
sudo usermod -a -G video $USER

# Değişikliklerin geçerli olması için yeniden giriş yapın
# veya bilgisayarı yeniden başlatın
```

### 7. Kamera Testini Yap
```bash
# Kamerayı test et
v4l2-ctl --device=/dev/video0 --all

# Desteklenen formatları listele
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

## ⚙️ Yapılandırma

### Kamera Cihaz Numarasını Değiştirme

Eğer kameranız `/dev/video1` veya farklı bir cihaz numarasındaysa:

**main.py** dosyasında (satır ~54):
```python
# Varsayılan: /dev/video0
self.camera_view = CameraView(camera_index=0)

# /dev/video1 için:
self.camera_view = CameraView(camera_index=1)
```

### Kamera Çözünürlüğünü Değiştirme

**ui/camera_view.py** dosyasında (satır ~45-47):
```python
# Varsayılan ayarlar
self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
self.capture.set(cv2.CAP_PROP_FPS, 30)

# 1080p için:
self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

### Park Yardım Çizgilerini Özelleştirme

**ui/camera_view.py** dosyasında `add_parking_guides` metodunu düzenleyin:

```python
def add_parking_guides(self, frame):
    h, w = frame.shape[:2]
    
    # Çizgilerin konumlarını ayarlayın
    # Yeşil çizgiler (güvenli bölge)
    cv2.line(frame, (int(w * 0.3), h), (int(w * 0.4), int(h * 0.6)), (0, 255, 0), 3)
    
    # Renkleri değiştirin: (B, G, R) formatında
    # Kırmızı: (0, 0, 255)
    # Yeşil: (0, 255, 0)
    # Mavi: (255, 0, 0)
    # Sarı: (0, 255, 255)
```

## 🧪 Test Etme

### 1. Basit Kamera Testi
```bash
# Terminal üzerinden kamera testini çalıştır
python3 test_connection.py
```

### 2. Dashboard'u Başlat
```bash
python3 main.py
```

### 3. Geri Vitesi Test Et
1. Dashboard çalışırken
2. Aracı **geri vitese** takın (Arduino'dan vites=2 değeri gelecek)
3. Kamera görünümünün otomatik açıldığını kontrol edin
4. İleri vitese alın, harita görünümüne dönmeli

## 🔍 Sorun Giderme

### Kamera Algılanmıyor

**Problem:** `ls /dev/video*` hiçbir şey göstermiyor

**Çözüm:**
```bash
# USB bağlantılarını kontrol edin
lsusb

# Kamera sürücülerini kontrol edin
dmesg | grep -i video

# Kamerayı çıkarıp tekrar takın
```

### "Permission denied" Hatası

**Problem:** `/dev/video0: Permission denied`

**Çözüm:**
```bash
# Video grubuna üye olup olmadığınızı kontrol edin
groups $USER

# Video grubunda değilseniz:
sudo usermod -a -G video $USER

# Oturumu kapatıp açın veya:
sudo reboot
```

### Kamera Görüntüsü Donuyor

**Problem:** Video akışı takılıyor veya donuyor

**Çözüm:**
1. Çözünürlüğü düşürün (720p → 480p)
2. FPS'i azaltın (30 → 15)
3. USB bağlantısını kontrol edin (USB 3.0 portu kullanın)
4. CPU kullanımını kontrol edin (`htop`)

```python
# Düşük performanslı sistemler için:
self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
self.capture.set(cv2.CAP_PROP_FPS, 15)
```

### Görüntü Ters veya Bozuk

**Problem:** Kamera görüntüsü ters veya aynalı değil

**Çözüm:**
`ui/camera_view.py` dosyasında flip parametresini değiştirin:
```python
# Yatay aynalama (varsayılan)
frame = cv2.flip(frame, 1)

# Dikey çevirme
frame = cv2.flip(frame, 0)

# Her iki yönde çevirme
frame = cv2.flip(frame, -1)

# Hiç çevirme
# Bu satırı yoruma alın veya silin
```

### OpenCV Kurulum Sorunu

**Problem:** `ImportError: No module named 'cv2'`

**Çözüm:**
```bash
# Eski sürümü kaldır
pip3 uninstall opencv-python opencv-python-headless

# Yeniden yükle
pip3 install opencv-python

# Raspberry Pi'de headless sürüm gerekiyorsa:
pip3 install opencv-python-headless
```

### Yavaş Performans

**Problem:** Kamera akışı yavaş, gecikme var

**Optimizasyon:**
1. **Çözünürlüğü düşürün:**
   ```python
   self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

2. **FPS'i ayarlayın:**
   ```python
   self.capture.set(cv2.CAP_PROP_FPS, 15)
   self.timer.start(66)  # ~15 FPS için 66ms
   ```

3. **GPU hızlandırmasını etkinleştirin (Raspberry Pi 4/5):**
   ```bash
   sudo raspi-config
   # Advanced Options > GL Driver > GL (Full KMS)
   ```

4. **Overclock yapın (dikkatli olun):**
   ```bash
   sudo nano /boot/config.txt
   # Ekleyin:
   arm_freq=2000
   gpu_freq=750
   ```

## 📊 Performans İpuçları

### Önerilen Kamera Ayarları

| Cihaz | Çözünürlük | FPS | Önerilen |
|-------|------------|-----|----------|
| Raspberry Pi 3 | 640x480 | 15 | ✅ |
| Raspberry Pi 3 | 1280x720 | 15 | ⚠️ |
| Raspberry Pi 4 | 1280x720 | 30 | ✅ |
| Raspberry Pi 4 | 1920x1080 | 30 | ⚠️ |
| Raspberry Pi 5 | 1920x1080 | 30 | ✅ |

### CPU Kullanımını İzleme

```bash
# Terminal'de CPU kullanımını görüntüle
htop

# Python sürecini izle
top -p $(pgrep -f main.py)
```

## 🎯 Gelişmiş Özellikler

### Gece Görüşü Modu

**ui/camera_view.py** dosyasına ekleyin:
```python
def enhance_night_vision(self, frame):
    # Parlaklık ve kontrast artırma
    alpha = 1.5  # Kontrast
    beta = 50    # Parlaklık
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

# update_frame metodunda kullanın:
frame = self.enhance_night_vision(frame)
```

### Mesafe Göstergesi

```python
def add_distance_markers(self, frame):
    h, w = frame.shape[:2]
    
    # 1 metre
    cv2.putText(frame, "1m", (int(w*0.5), int(h*0.7)), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    # 2 metre
    cv2.putText(frame, "2m", (int(w*0.5), int(h*0.5)), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
```

### Kayıt Özelliği

```python
def start_recording(self):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    self.video_writer = cv2.VideoWriter(
        'reverse_camera.mp4', fourcc, 30.0, (1280, 720))

def stop_recording(self):
    if self.video_writer:
        self.video_writer.release()
```

## 📞 Destek

Sorun yaşıyorsanız:
1. GitHub Issues sayfasında arama yapın
2. Yeni bir issue açın
3. Log dosyalarını paylaşın:
   ```bash
   python3 main.py 2>&1 | tee dashboard.log
   ```

---

**İyi sürüşler! 🚗💨**
