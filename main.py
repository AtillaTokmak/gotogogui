import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import QTimer

from arduino.arduino_reader import ArduinoReader, ConnectionType
from ui.connection_dialog import ConnectionSettingsDialog
from ui.wifi_manager import WiFiManagerDialog
from ui.phone_mirror import PhoneMirrorDialog
from ui.left_panel import LeftPanel
from ui.map_view import MapView
from ui.bottom_bar import BottomBar
from ui.media_overlay import MediaOverlay
from ui.clock_widget import ClockWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # -------- Arduino Reader --------
        self.arduino_reader = None
        self.connection_type = ConnectionType.USB
        self.connection_params = {}
        
        # -------- Window --------
        self.setWindowTitle("GoToGo Dashboard - Tesla Style")
        self.showFullScreen()
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        
        central = QWidget(self)
        self.setCentralWidget(central)
        
        main_v = QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)
        
        # -------- TOP (Left + Map) --------
        top_h = QHBoxLayout()
        top_h.setContentsMargins(0, 0, 0, 0)
        
        self.left_panel = LeftPanel()
        self.map_view = MapView()
        
        top_h.addWidget(self.left_panel)
        top_h.addWidget(self.map_view)
        top_h.setStretch(0, 3)
        top_h.setStretch(1, 7)
        
        # -------- BOTTOM --------
        bottom_h = QHBoxLayout()
        bottom_h.setContentsMargins(0, 0, 0, 0)
        
        self.bottom_bar = BottomBar()
        self.clock = ClockWidget()
        
        bottom_h.addWidget(self.bottom_bar)
        bottom_h.addWidget(self.clock)
        bottom_h.setStretch(0, 8)
        bottom_h.setStretch(1, 2)
        
        # -------- Media Overlay --------
        self.overlay = MediaOverlay(self.map_view)
        
        # Buton bağlantıları - Webview'ları değiştir
        self.bottom_bar.spotify_btn.clicked.connect(
            lambda: self.map_view.switch_view('spotify')
        )
        self.bottom_bar.youtube_btn.clicked.connect(
            lambda: self.map_view.switch_view('youtube')
        )
        self.bottom_bar.maps_btn.clicked.connect(
            lambda: self.map_view.switch_view('maps')
        )
        
        # -------- WiFi Butonu --------
        self.bottom_bar.wifi_btn.clicked.connect(self.show_wifi_manager)
        
        # -------- RACE MODE Butonu --------
        self.bottom_bar.race_mode_btn.clicked.connect(self.toggle_race_mode)
        
        # -------- Phone Mirror Butonu --------
        self.bottom_bar.phone_mirror_btn.clicked.connect(self.show_phone_mirror)
        
        # -------- Layout attach --------
        main_v.addLayout(top_h)
        main_v.addLayout(bottom_h)
        main_v.setStretch(0, 9)
        main_v.setStretch(1, 1)
        
        # -------- Otomatik Bağlantı Denemesi --------
        QTimer.singleShot(1000, self.auto_connect)
    
    def auto_connect(self):
        """Otomatik bağlantı başlat (USB)"""
        try:
            # Varsayılan USB bağlantı
            self.start_arduino_connection(
                ConnectionType.USB,
                {'baud': 115200}
            )
        except Exception as e:
            print(f"Otomatik bağlantı başarısız: {e}")
            self.bottom_bar.update_connection_status('disconnected')
    
    def show_connection_settings(self):
        """Bağlantı ayarları dialogunu göster"""
        dialog = ConnectionSettingsDialog(self)
        dialog.connection_changed.connect(self.start_arduino_connection)
        dialog.exec()
    
    def show_wifi_manager(self):
        """WiFi Yönetimi dialogunu göster"""
        dialog = WiFiManagerDialog(self)
        dialog.exec()
    
    def toggle_race_mode(self):
        """RACE MODE'u aç/kapat"""
        self.map_view.toggle_race_mode()
        
        if self.map_view.race_mode:
            # RACE MODE açık
            self.bottom_bar.race_mode_btn.setText("🏁 EXIT RACE MODE")
            self.bottom_bar.race_mode_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 68, 68, 0.3);
                    color: #ff4444;
                    font-size: 16px;
                    padding: 10px 20px;
                    border: 2px solid #ff4444;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(255, 68, 68, 0.5);
                }
            """)
            # Diğer butonları devre dışı bırak
            self.bottom_bar.spotify_btn.setEnabled(False)
            self.bottom_bar.youtube_btn.setEnabled(False)
            self.bottom_bar.maps_btn.setEnabled(False)
            self.bottom_bar.wifi_btn.setEnabled(False)
        else:
            # RACE MODE kapalı
            self.bottom_bar.race_mode_btn.setText("🏁 RACE MODE")
            self.bottom_bar.race_mode_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    font-size: 16px;
                    padding: 10px 20px;
                    border: 2px solid transparent;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    color: #ff4444;
                    border: 2px solid #ff4444;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 68, 68, 0.2);
                }
            """)
            # Diğer butonları etkinleştir
            self.bottom_bar.spotify_btn.setEnabled(True)
            self.bottom_bar.youtube_btn.setEnabled(True)
            self.bottom_bar.maps_btn.setEnabled(True)
            self.bottom_bar.wifi_btn.setEnabled(True)
    
    def show_phone_mirror(self):
        """Telefon yansıtma dialogunu göster"""
        dialog = PhoneMirrorDialog(self)
        dialog.exec()
    
    def start_arduino_connection(self, connection_type: str, params: dict):
        """Arduino bağlantısını başlat"""
        # Eski bağlantıyı kapat
        if self.arduino_reader:
            self.arduino_reader.stop()
            self.arduino_reader = None
        
        # Yeni bağlantı
        self.connection_type = connection_type
        self.connection_params = params
        
        try:
            self.arduino_reader = ArduinoReader(
                connection_type=connection_type,
                **params
            )
            
            # Signal bağlantıları
            self.arduino_reader.data_received.connect(self.update_data)
            self.arduino_reader.connection_status.connect(self.on_connection_status)
            self.arduino_reader.error_message.connect(self.on_error_message)
            
            # Thread'i başlat
            self.arduino_reader.start()
            
            # Bağlantı tipini göster
            self.bottom_bar.update_connection_status('connected', connection_type)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Bağlantı Hatası",
                f"Arduino bağlantısı başlatılamadı:\n{str(e)}"
            )
            self.bottom_bar.update_connection_status('error')
    
    def on_connection_status(self, status: str):
        """Bağlantı durumu değiştiğinde"""
        self.bottom_bar.update_connection_status(status, self.connection_type)
        
        if status == 'error' or status == 'disconnected':
            # Yeniden bağlanma denemesi (5 saniye sonra)
            QTimer.singleShot(5000, self.reconnect_arduino)
    
    def reconnect_arduino(self):
        """Arduino'ya yeniden bağlanmayı dene"""
        if self.connection_params:
            print("Yeniden bağlanma denemesi...")
            self.start_arduino_connection(
                self.connection_type,
                self.connection_params
            )
    
    def on_error_message(self, message: str):
        """Hata mesajı geldiğinde"""
        print(f"Arduino Hatası: {message}")
        # Kullanıcıya gösterme (çok fazla popup olmasın)
        # İsterseniz status bar'da gösterebilirsiniz
    
    def update_data(self, data: dict):
        """Arduino'dan gelen veriyi güncelle"""
        # Sol panel güncelle
        self.left_panel.update_data(data)
        
        # Geri viteste farklı görünüm
        if data.get('vites') == 2:  # 2 = Geri vites
            # Harita yerine geri görüş kamerası göster
            # Veya haritayı arka görünüme çevir
            self.show_reverse_view()
        else:
            self.show_normal_view()
    
    def show_reverse_view(self):
        """Geri vites görünümü"""
        # TODO: Kamera entegrasyonu
        # Şimdilik sadece map'i gizle veya overlay göster
        pass
    
    def show_normal_view(self):
        """Normal görünüm"""
        pass
    
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik"""
        if self.arduino_reader:
            self.arduino_reader.stop()
        
        # Telefon ekran yansıtmayı durdur
        if self.map_view.scrcpy_process:
            self.map_view.stop_screen_mirror()
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # QtWebEngine crash fix
    QWebEngineProfile.defaultProfile()
    
    # Uygulama stili
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
