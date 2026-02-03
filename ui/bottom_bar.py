from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt


class BottomBar(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #222222;
            }
            QPushButton {
                background: transparent;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border: 2px solid transparent;
                border-radius: 5px;
            }
            QPushButton:hover {
                color: #00aaff;
                border: 2px solid #00aaff;
            }
            QPushButton:pressed {
                background-color: rgba(0, 170, 255, 0.2);
            }
            QLabel {
                color: #888;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 20, 5)
        layout.setSpacing(10)
        
        # Media butonları
        self.spotify_btn = QPushButton("🎵 Spotify")
        self.youtube_btn = QPushButton("📺 YouTube")
        self.messages_btn = QPushButton("💬 Mesajlar")
        
        # Harita butonu (Google Maps'e dön)
        self.maps_btn = QPushButton("🗺️ Harita")
        
        # Bağlantı durumu göstergesi
        self.connection_status = QLabel("● Bağlantı: Bekliyor...")
        self.connection_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Layout'a ekle
        layout.addWidget(self.spotify_btn)
        layout.addWidget(self.youtube_btn)
        layout.addWidget(self.messages_btn)
        layout.addWidget(self.maps_btn)
        layout.addStretch()
        layout.addWidget(self.connection_status)
    
    def update_connection_status(self, status: str, connection_type: str = ""):
        """Bağlantı durumunu güncelle"""
        status_map = {
            'connected': ('🟢', '#00ff44', 'Bağlı'),
            'disconnected': ('⚪', '#666', 'Bağlantı Yok'),
            'error': ('🔴', '#ff4444', 'Hata')
        }
        
        icon, color, text = status_map.get(status, ('⚪', '#666', 'Bilinmiyor'))
        
        if connection_type:
            type_names = {
                'usb': 'USB',
                'wifi': 'WiFi',
                'bluetooth': 'Bluetooth'
            }
            conn_text = type_names.get(connection_type, connection_type.upper())
            text = f"{text} ({conn_text})"
        
        self.connection_status.setText(f"{icon} {text}")
        self.connection_status.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px;")
