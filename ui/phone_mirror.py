import subprocess
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QColor, QPainter, QFont
from PySide6.QtCore import QByteArray, QBuffer, QIODevice
import io
import os
import time
import platform as sys_platform


def get_adb_path():
    """ADB yolunu bul"""
    # Yaygın konumları dene
    if sys_platform.system() == 'Windows':
        possible_paths = [
            r"C:\platform-tools\adb.exe",
            r"C:\Android\sdk\platform-tools\adb.exe",
            os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
            "adb"  # PATH'te ara
        ]
    else:  # Linux/macOS
        possible_paths = [
            "/usr/bin/adb",
            "/usr/local/bin/adb",
            os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
            os.path.expanduser("~/android-sdk/platform-tools/adb"),
            "/opt/android-sdk/platform-tools/adb",
            "adb"  # PATH'te ara
        ]
    
    for path in possible_paths:
        if os.path.exists(path) or path == "adb":
            return path
    
    return None


class PhoneMirrorThread(QThread):
    """Telefon ekranını periyodik olarak çeken thread"""
    image_captured = Signal(QPixmap)
    
    def __init__(self, use_demo=False):
        super().__init__()
        self.running = True
        self.use_demo = use_demo
    
    def run(self):
        """Telefon screenshot'ını al ve gönder"""
        adb_path = get_adb_path()
        
        while self.running:
            try:
                if self.use_demo:
                    # Demo ekranı göster
                    pixmap = self.create_demo_screen()
                    self.image_captured.emit(pixmap)
                else:
                    # ADB ile telefon ekran görüntüsünü al
                    if not adb_path:
                        self.use_demo = True
                        continue
                    
                    result = subprocess.run(
                        [adb_path, 'exec-out', 'screencap', '-p'],
                        capture_output=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        # PNG dosyasını QPixmap'e dönüştür
                        pixmap = QPixmap()
                        pixmap.loadFromData(result.stdout, "PNG")
                        
                        if not pixmap.isNull():
                            self.image_captured.emit(pixmap)
                
                # 62ms bekle (16 FPS)
                self.msleep(62)
            
            except Exception as e:
                print(f"Telefon mirror hatası: {e}")
                self.msleep(1000)
    
    def create_demo_screen(self):
        """Demo telefon ekranı oluştur"""
        pixmap = QPixmap(1080, 1920)
        pixmap.fill(QColor("#1a1a1a"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Status bar
        painter.fillRect(0, 0, 1080, 60, QColor("#222222"))
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(10, 40, "9:41 📶 🔋")
        
        # Başlık
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.setPen(QColor("#00ff88"))
        painter.drawText(100, 150, "📱 DEMO MODE")
        
        # İçerik
        painter.setFont(QFont("Arial", 16))
        painter.setPen(QColor("#aaa"))
        painter.drawText(50, 350, "ADB yüklü değil - Demo ekranı")
        painter.drawText(50, 420, "Gerçek telefon için ADB gerekli")
        
        painter.drawText(50, 550, "Windows'ta ADB Kurmak için:")
        painter.drawText(50, 610, "1. Android SDK Platform Tools indir")
        painter.drawText(50, 670, "2. PATH'e ekle")
        painter.drawText(50, 730, "3. Telefonu USB'ye bağla")
        painter.drawText(50, 790, "4. USB Debug'u aç")
        
        painter.end()
        return pixmap
    
    def stop(self):
        """Thread'i durdur"""
        self.running = False
        self.wait()


class PhoneMirrorDialog(QDialog):
    """Telefon Ekranı Yansıtma Dialogu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📱 Telefon Ekranı Yansıtması")
        self.setGeometry(100, 100, 1000, 600)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #00aaff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📱 Telefon Ekranı Yansıtması")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Ekran görüntüsü label'ı
        self.screen_label = QLabel("Telefon bağlanıyor...")
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.screen_label.setStyleSheet("background-color: #2a2a2a; border-radius: 5px; min-height: 400px;")
        self.screen_label.setScaledContents(False)
        layout.addWidget(self.screen_label)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Başlat")
        self.start_btn.clicked.connect(self.start_mirror)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Durdur")
        self.stop_btn.clicked.connect(self.stop_mirror)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Mirror thread
        self.mirror_thread = None
    
    def start_mirror(self):
        """Telefon yansıtmasını başlat"""
        adb_path = get_adb_path()
        
        # ADB kontrolü
        adb_available = False
        try:
            if adb_path:
                # ADB daemon'u başlat
                subprocess.run(
                    [adb_path, 'start-server'],
                    capture_output=True,
                    timeout=5
                )
                
                # Biraz bekle daemon başlansın
                time.sleep(1)
                
                # Devices kontrol et
                result = subprocess.run(
                    [adb_path, 'devices'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                lines = result.stdout.strip().split('\n')
                # En az bir device olup, "offline" olmadığını kontrol et
                if len(lines) > 1:
                    for line in lines[1:]:
                        if 'device' in line and 'offline' not in line:
                            adb_available = True
                            break
                
                # Telefon ekranını yatay yap (landscape)
                if adb_available:
                    try:
                        subprocess.run(
                            [adb_path, 'shell', 'settings', 'put', 'system', 'user_rotation', '1'],
                            capture_output=True,
                            timeout=3
                        )
                        print("Telefon ekranı landscape'e döndürüldü")
                    except Exception as e:
                        print(f"Ekran rotate hatası: {e}")
        
        except subprocess.TimeoutExpired:
            print("ADB timeout - DEMO MODE'a geçiliyor")
            adb_available = False
        except Exception as e:
            print(f"ADB kontrol hatası: {e}")
            adb_available = False
        
        # Mirror thread'i başlat
        self.mirror_thread = PhoneMirrorThread(use_demo=not adb_available)
        self.mirror_thread.image_captured.connect(self.display_image)
        self.mirror_thread.start()
        
        if adb_available:
            status_text = "📱 Telefon ekranı yansıtılıyor... (Landscape Modu)"
        else:
            status_text = "📱 DEMO MODE (ADB yüklü değil veya telefon bağlı değil)"
        
        self.screen_label.setText(status_text)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def display_image(self, pixmap):
        """Telefon ekran görüntüsünü göster"""
        # Ekrana sığdır
        scaled_pixmap = pixmap.scaledToWidth(
            self.screen_label.width() - 20,
            Qt.SmoothTransformation
        )
        self.screen_label.setPixmap(scaled_pixmap)
    
    def stop_mirror(self):
        """Telefon yansıtmasını durdur"""
        if self.mirror_thread:
            self.mirror_thread.stop()
            self.mirror_thread = None
        
        # Telefon ekranını normal moda geri döndür (portrait)
        adb_path = get_adb_path()
        try:
            if adb_path:
                subprocess.run(
                    [adb_path, 'shell', 'settings', 'put', 'system', 'user_rotation', '0'],
                    capture_output=True,
                    timeout=3
                )
                print("Telefon ekranı portrait'e döndürüldü")
        except Exception as e:
            print(f"Ekran rotate hatası: {e}")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.screen_label.setText("Durduruldu")
    
    def closeEvent(self, event):
        """Dialog kapatılırken"""
        if self.mirror_thread:
            self.mirror_thread.stop()
        event.accept()
