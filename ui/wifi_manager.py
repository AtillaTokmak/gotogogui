import subprocess
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon


class WiFiScannerThread(QThread):
    """WiFi ağlarını taramak için thread"""
    networks_found = Signal(list)
    
    def run(self):
        """Mevcut WiFi ağlarını tara"""
        try:
            import platform
            # Farklı işletim sistemleri için komutlar
            if platform.system() == 'Windows':
                # Windows için WMIC veya PowerShell
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 'Get-NetAdapter -Physical | Select-Object Name, Status'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    networks = ['WiFi Bağlantı 1', 'WiFi Bağlantı 2']  # Demo
                except:
                    networks = []
            else:
                # Linux/Raspberry Pi için nmcli
                result = subprocess.run(
                    ['nmcli', 'device', 'wifi', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                networks = []
                lines = result.stdout.strip().split('\n')[1:]  # Başlık satırını atla
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 7:
                            # Ağ adı (SSID) genellikle 7. sütun
                            ssid = ' '.join(parts[6:])
                            if ssid and ssid != '--':
                                networks.append(ssid)
            
            self.networks_found.emit(networks)
        except Exception as e:
            print(f"WiFi tarama hatası: {e}")
            self.networks_found.emit([])


class WiFiManagerDialog(QDialog):
    """WiFi Bağlantı Yönetici Dialogu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📡 WiFi Yönetimi")
        self.setGeometry(100, 100, 500, 400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #00aaff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
            QListWidget {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #00aaff;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📡 Wireless Network Yönetimi")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Bağlı ağ bilgisi
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Bağlı Ağ: Kontrol ediliyor...")
        self.refresh_status()
        status_layout.addWidget(self.status_label)
        
        # Tarama butonu
        self.scan_btn = QPushButton("🔍 Ağları Tara")
        self.scan_btn.clicked.connect(self.scan_networks)
        status_layout.addWidget(self.scan_btn)
        
        layout.addLayout(status_layout)
        
        # Mevcut ağlar listesi
        networks_label = QLabel("Mevcut WiFi Ağları:")
        layout.addWidget(networks_label)
        
        self.networks_list = QListWidget()
        self.networks_list.itemClicked.connect(self.on_network_selected)
        layout.addWidget(self.networks_list)
        
        # Bağlantı seçenekleri
        connection_layout = QHBoxLayout()
        
        # Parola girişi
        connection_layout.addWidget(QLabel("Parola:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        connection_layout.addWidget(self.password_input)
        
        # Bağlan butonu
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.connect_to_network)
        connection_layout.addWidget(self.connect_btn)
        
        layout.addLayout(connection_layout)
        
        # İstatistikler
        stats_label = QLabel("Bağlantı İstatistikleri:")
        layout.addWidget(stats_label)
        
        self.stats_label = QLabel(
            "IP Adresi: -\n"
            "Signal Gücü: -\n"
            "Bağlantı Hızı: -"
        )
        self.stats_label.setStyleSheet("color: #00ff88; font-size: 11px;")
        layout.addWidget(self.stats_label)
        
        # Kapatma butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Thread
        self.scanner_thread = None
        
        # Timer ile durum güncelleme
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_status)
        self.update_timer.start(5000)  # Her 5 saniyede güncelle
    
    def scan_networks(self):
        """WiFi ağlarını tara"""
        self.scan_btn.setEnabled(False)
        self.networks_list.clear()
        self.networks_list.addItem("⏳ Ağlar taranıyor...")
        
        # Thread'de tarama yap
        self.scanner_thread = WiFiScannerThread()
        self.scanner_thread.networks_found.connect(self.display_networks)
        self.scanner_thread.start()
    
    def display_networks(self, networks):
        """Bulunan ağları göster"""
        self.networks_list.clear()
        
        if not networks:
            self.networks_list.addItem("❌ Ağ bulunamadı")
        else:
            for network in networks:
                item = QListWidgetItem(f"📶 {network}")
                self.networks_list.addItem(item)
        
        self.scan_btn.setEnabled(True)
    
    def on_network_selected(self, item):
        """Ağ seçildiğinde"""
        ssid = item.text().replace("📶 ", "")
        self.password_input.clear()
        self.password_input.setFocus()
    
    def connect_to_network(self):
        """Seçilen ağa bağlan"""
        if not self.networks_list.currentItem():
            QMessageBox.warning(self, "Hata", "Lütfen bir WiFi ağı seçin!")
            return
        
        ssid = self.networks_list.currentItem().text().replace("📶 ", "")
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Hata", "Lütfen parola girin!")
            return
        
        # Bağlantı komutunu çalıştır
        try:
            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("Bağlanıyor...")
            
            # nmcli ile bağlan
            cmd = [
                'nmcli', 'device', 'wifi', 'connect', ssid,
                'password', password
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                QMessageBox.information(
                    self, "Başarılı",
                    f"✓ {ssid} ağına bağlanıldı!"
                )
                self.refresh_status()
            else:
                QMessageBox.critical(
                    self, "Bağlantı Hatası",
                    f"Bağlantı başarısız:\n{result.stderr}"
                )
            
        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Hata", "Bağlantı zaman aşımına uğradı")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hata oluştu:\n{str(e)}")
        finally:
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("Bağlan")
    
    def refresh_status(self):
        """Bağlantı durumunu güncelle"""
        try:
            # nmcli ile aktif bağlantı kontrolü
            result = subprocess.run(
                ['nmcli', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            active_networks = []
            for line in result.stdout.split('\n'):
                if 'connection.id' in line:
                    ssid = line.split(':')[1].strip()
                    if ssid:
                        active_networks.append(ssid)
            
            if active_networks:
                self.status_label.setText(f"🟢 Bağlı: {', '.join(active_networks)}")
                self.status_label.setStyleSheet("color: #00ff88;")
                self.update_stats()
            else:
                self.status_label.setText("🔴 Bağlı değil")
                self.status_label.setStyleSheet("color: #ff4444;")
                self.stats_label.setText(
                    "IP Adresi: -\n"
                    "Signal Gücü: -\n"
                    "Bağlantı Hızı: -"
                )
        
        except Exception as e:
            self.status_label.setText("❓ Durum kontrol edilemiyor")
            self.status_label.setStyleSheet("color: #ff8800;")
    
    def update_stats(self):
        """Bağlantı istatistiklerini güncelle"""
        try:
            # IP adresi
            result = subprocess.run(
                ['nmcli', 'device', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            ip_address = "-"
            signal_strength = "-"
            
            for line in result.stdout.split('\n'):
                if 'IP4.ADDRESS' in line:
                    ip_address = line.split()[-1]
                if 'SIGNAL' in line:
                    signal_strength = line.split()[-1] + "%"
            
            stats_text = (
                f"IP Adresi: {ip_address}\n"
                f"Signal Gücü: {signal_strength}\n"
                f"Bağlantı Hızı: Uydu"
            )
            self.stats_label.setText(stats_text)
        
        except Exception as e:
            pass
    
    def closeEvent(self, event):
        """Dialog kapatılırken"""
        self.update_timer.stop()
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.quit()
            self.scanner_thread.wait()
        event.accept()
