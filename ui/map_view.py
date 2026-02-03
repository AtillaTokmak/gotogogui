from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtCore import QUrl, Qt, QTimer, QProcess
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
import subprocess
import os
import platform


class MapView(QWebEngineView):
    """
    Harita görünümü + USB Telefon ekran yansıtma (scrcpy)
    YouTube, Spotify, Google Maps gibi farklı webview'ları gösterebilir
    """
    def __init__(self):
        super().__init__()
        
        # WebEngine profili - cookies ve permissions
        self.setup_web_engine()
        
        # Mevcut görünüm tipini takip et
        self.current_view = 'maps'  # 'maps', 'youtube', 'spotify'
        self.race_mode = False  # RACE MODE açık mı
        
        # Google Maps'i varsayılan olarak yükle (konum izni ile)
        self.load_maps()
        
        # Scrcpy process
        self.scrcpy_process = None
        self.phone_connected = False
        
        # Telefon kontrol widget'ı (overlay)
        self.phone_overlay = PhoneControlOverlay(self)
        self.phone_overlay.hide()
        
        # Telefon bağlantı kontrolü
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_phone_connection)
        self.check_timer.start(5000)  # Her 5 saniyede kontrol
    
    def setup_web_engine(self):
        """WebEngine profilini ayarla - cookies, permissions, vs"""
        profile = QWebEngineProfile.defaultProfile()
        
        # Cookies'i etkinleştir ve kaydet
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        
        # Web sitelerinin çerezlerini kalıcı olarak sakla
        cookies_path = os.path.expanduser('~/.goatogo/cookies')
        os.makedirs(cookies_path, exist_ok=True)
        
        # Geçici depolama (localStorage, sessionStorage)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        
        # Settings
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # JavaScript hataları tolerate et (Google Messages vs için)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    
    def load_maps(self):
        """Google Maps'i konum izni ile yükle"""
        # Google Maps URL'i - konum izni parametreleri ile
        maps_url = "https://www.google.com/maps"
        self.setUrl(QUrl(maps_url))
        self.current_view = 'maps'
    
    def load_youtube(self):
        """YouTube'u yükle"""
        youtube_url = "https://www.youtube.com"
        self.setUrl(QUrl(youtube_url))
        self.current_view = 'youtube'
    
    def load_spotify(self):
        """Spotify Web Player'ı yükle"""
        spotify_url = "https://open.spotify.com"
        self.setUrl(QUrl(spotify_url))
        self.current_view = 'spotify'
    
    def switch_view(self, view_type: str):
        """Görünümü değiştir (maps, youtube, spotify)"""
        if view_type == 'maps':
            self.load_maps()
        elif view_type == 'youtube':
            self.load_youtube()
        elif view_type == 'spotify':
            self.load_spotify()
    
    def toggle_race_mode(self):
        """RACE MODE'u aç/kapat"""
        self.race_mode = not self.race_mode
        
        if self.race_mode:
            # RACE MODE açık - webview gizle
            self.hide()
        else:
            # RACE MODE kapalı - webview göster
            self.show()
            self.load_maps()  # Haritaya dön
    
    def on_page_loaded(self, success):
        """Sayfa yüklendikten sonra"""
        pass
    
    def check_phone_connection(self):
        """USB ile bağlı telefon kontrolü (ADB)"""
        try:
            # ADB devices kontrolü
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            lines = result.stdout.strip().split('\n')
            
            # En az 2 satır olmalı (başlık + cihaz)
            if len(lines) > 1 and 'device' in lines[1]:
                if not self.phone_connected:
                    self.phone_connected = True
                    self.phone_overlay.show_notification("Telefon bağlandı!")
            else:
                if self.phone_connected:
                    self.phone_connected = False
                    self.stop_screen_mirror()
                    self.phone_overlay.show_notification("Telefon bağlantısı kesildi!")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # ADB yüklü değil veya zaman aşımı
            pass
    
    def start_screen_mirror(self):
        """Telefon ekranını yansıtmaya başla (scrcpy)"""
        if not self.phone_connected:
            self.phone_overlay.show_notification("Telefon bağlı değil!")
            return
        
        if self.scrcpy_process:
            self.stop_screen_mirror()
        
        try:
            # Scrcpy başlat
            self.scrcpy_process = QProcess()
            
            # Scrcpy parametreleri
            # --window-title: Pencere başlığı
            # --window-x, --window-y: Pencere konumu
            # --window-width, --window-height: Pencere boyutu
            # --always-on-top: Her zaman üstte
            # --turn-screen-off: Telefon ekranını kapat
            # --stay-awake: Telefonu uyanık tut
            
            args = [
                'scrcpy',
                '--window-title', 'Phone Mirror',
                '--window-x', '100',
                '--window-y', '100',
                '--window-width', '400',
                '--window-height', '800',
                '--always-on-top',
                '--stay-awake'
            ]
            
            self.scrcpy_process.start('scrcpy', args[1:])
            self.phone_overlay.show_notification("Ekran yansıtma başladı!")
            self.phone_overlay.mirror_active = True
            
        except Exception as e:
            self.phone_overlay.show_notification(f"Hata: {str(e)}")
    
    def stop_screen_mirror(self):
        """Ekran yansıtmayı durdur"""
        if self.scrcpy_process:
            self.scrcpy_process.kill()
            self.scrcpy_process = None
            self.phone_overlay.mirror_active = False
            self.phone_overlay.show_notification("Ekran yansıtma durduruldu!")
    
    def toggle_screen_mirror(self):
        """Ekran yansıtmayı aç/kapat"""
        if self.phone_overlay.mirror_active:
            self.stop_screen_mirror()
        else:
            self.start_screen_mirror()


class PhoneControlOverlay(QWidget):
    """Telefon kontrol overlay widget'ı"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.mirror_active = False
        
        # Widget özellikleri
        self.setFixedSize(300, 150)
        self.move(parent.width() - 320, 20)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 230);
                border-radius: 12px;
                color: white;
            }
            QPushButton {
                background-color: #00aaff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("📱 Telefon Kontrolü")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        # Durum
        self.status_label = QLabel("Telefon aranıyor...")
        self.status_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.mirror_btn = QPushButton("Ekranı Yansıt")
        self.mirror_btn.clicked.connect(parent.toggle_screen_mirror)
        
        self.notification_label = QLabel("")
        self.notification_label.setStyleSheet("font-size: 11px; color: #00ff88;")
        self.notification_label.setAlignment(Qt.AlignCenter)
        
        btn_layout.addWidget(self.mirror_btn)
        
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)
        layout.addWidget(self.notification_label)
        
        # Bildirim timer
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.clear_notification)
    
    def show_notification(self, text):
        """Bildirim göster"""
        self.notification_label.setText(text)
        self.notification_timer.stop()
        self.notification_timer.start(3000)
    
    def clear_notification(self):
        """Bildirimi temizle"""
        self.notification_label.setText("")
    
    def update_status(self, connected):
        """Durum güncelle"""
        if connected:
            self.status_label.setText("✓ Telefon bağlı")
            self.status_label.setStyleSheet("font-size: 12px; color: #00ff88;")
            self.mirror_btn.setEnabled(True)
        else:
            self.status_label.setText("✗ Telefon bağlı değil")
            self.status_label.setStyleSheet("font-size: 12px; color: #ff4444;")
            self.mirror_btn.setEnabled(False)
