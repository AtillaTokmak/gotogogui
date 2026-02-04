"""
Geri Görüş Kamerası Widget'ı
Raspberry Pi'deki USB kameradan video akışı gösterir
"""

import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap


class CameraView(QWidget):
    """USB Kamera görüntüsü widget'ı"""
    
    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        
        self.camera_index = camera_index
        self.capture = None
        self.timer = QTimer()
        self.is_active = False
        
        # UI kurulumu
        self.setup_ui()
        
    def setup_ui(self):
        """UI elemanlarını oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video gösterimi için label
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #ff4444;
            }
        """)
        
        # Geri vites göstergesi
        self.indicator_label = QLabel("⚠️ GERİ VİTES - KAMERA AKTİF ⚠️")
        self.indicator_label.setAlignment(Qt.AlignCenter)
        self.indicator_label.setStyleSheet("""
            QLabel {
                background-color: #ff4444;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(self.indicator_label)
        layout.addWidget(self.video_label, stretch=1)
        
        # Timer bağlantısı
        self.timer.timeout.connect(self.update_frame)
    
    def start_camera(self):
        """Kamerayı başlat"""
        if self.is_active:
            return
        
        try:
            # OpenCV ile kamerayı aç
            self.capture = cv2.VideoCapture(self.camera_index)
            
            # Kamera ayarları
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            if self.capture.isOpened():
                self.is_active = True
                # 30 FPS için ~33ms
                self.timer.start(33)
                print(f"Kamera başlatıldı: /dev/video{self.camera_index}")
            else:
                print(f"Kamera açılamadı: /dev/video{self.camera_index}")
                self.show_error_message("Kamera bağlantısı kurulamadı!")
                
        except Exception as e:
            print(f"Kamera başlatma hatası: {e}")
            self.show_error_message(f"Kamera hatası: {str(e)}")
    
    def stop_camera(self):
        """Kamerayı durdur"""
        if not self.is_active:
            return
        
        self.is_active = False
        self.timer.stop()
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        # Ekranı temizle
        self.video_label.clear()
        print("Kamera durduruldu")
    
    def update_frame(self):
        """Kamera görüntüsünü güncelle"""
        if not self.capture or not self.is_active:
            return
        
        ret, frame = self.capture.read()
        
        if ret:
            # Görüntüyü aynala (geri görüş için)
            frame = cv2.flip(frame, 1)
            
            # Park yardım çizgileri ekle
            frame = self.add_parking_guides(frame)
            
            # BGR'den RGB'ye çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # QImage'e çevir
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Widget boyutuna göre ölçekle
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
        else:
            print("Kameradan frame okunamadı")
            self.show_error_message("Kamera görüntüsü alınamıyor!")
    
    def add_parking_guides(self, frame):
        """Park yardım çizgilerini ekle"""
        h, w = frame.shape[:2]
        
        # Yeşil çizgiler (güvenli bölge)
        cv2.line(frame, (int(w * 0.3), h), (int(w * 0.4), int(h * 0.6)), (0, 255, 0), 3)
        cv2.line(frame, (int(w * 0.7), h), (int(w * 0.6), int(h * 0.6)), (0, 255, 0), 3)
        
        # Sarı çizgiler (dikkat bölgesi)
        cv2.line(frame, (int(w * 0.25), h), (int(w * 0.35), int(h * 0.5)), (0, 255, 255), 3)
        cv2.line(frame, (int(w * 0.75), h), (int(w * 0.65), int(h * 0.5)), (0, 255, 255), 3)
        
        # Kırmızı çizgiler (tehlike bölgesi)
        cv2.line(frame, (int(w * 0.2), h), (int(w * 0.3), int(h * 0.4)), (0, 0, 255), 3)
        cv2.line(frame, (int(w * 0.8), h), (int(w * 0.7), int(h * 0.4)), (0, 0, 255), 3)
        
        # Orta çizgi
        cv2.line(frame, (int(w * 0.5), h), (int(w * 0.5), int(h * 0.3)), (255, 255, 255), 2)
        
        return frame
    
    def show_error_message(self, message):
        """Hata mesajı göster"""
        self.video_label.setText(f"❌ {message}")
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #ff4444;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #ff4444;
            }
        """)
    
    def resizeEvent(self, event):
        """Widget boyutu değiştiğinde"""
        super().resizeEvent(event)
        # Mevcut frame'i yeniden ölçekle
        if self.is_active and self.video_label.pixmap():
            self.update_frame()
