import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox
)
from PySide6.QtCore import QTimer, Signal, QThread


# ==================================================
# WiFi Tarama Thread
# ==================================================
class WiFiScannerThread(QThread):
    networks_found = Signal(list)

    def run(self):
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'IN-USE,SSID', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )

            networks = []
            for line in result.stdout.splitlines():
                if not line:
                    continue
                _, ssid = line.split(':', 1)
                ssid = ssid.strip()
                if ssid and ssid != '--':
                    networks.append(ssid)

            self.networks_found.emit(sorted(set(networks)))

        except Exception as e:
            print("WiFi tarama hatası:", e)
            self.networks_found.emit([])


# ==================================================
# WiFi Manager Dialog
# ==================================================
class WiFiManagerDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📡 WiFi Yönetimi")
        self.setGeometry(100, 100, 520, 420)

        self.setStyleSheet("""
            QDialog { background-color: #1a1a1a; color: white; }
            QLabel { color: white; font-size: 12px; }
            QPushButton {
                background-color: #00aaff;
                color: white;
                border-radius: 5px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0088cc; }
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
        """)

        layout = QVBoxLayout(self)

        title = QLabel("📡 Wireless Network Yönetimi")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # ---------- Status ----------
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Durum kontrol ediliyor...")
        status_layout.addWidget(self.status_label)

        self.scan_btn = QPushButton("🔍 Ağları Tara")
        self.scan_btn.clicked.connect(self.scan_networks)
        status_layout.addWidget(self.scan_btn)

        layout.addLayout(status_layout)

        # ---------- WiFi List ----------
        layout.addWidget(QLabel("Mevcut WiFi Ağları:"))
        self.networks_list = QListWidget()
        layout.addWidget(self.networks_list)

        # ---------- Connect ----------
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Parola:"))

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        conn_layout.addWidget(self.password_input)

        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.connect_to_network)
        conn_layout.addWidget(self.connect_btn)

        layout.addLayout(conn_layout)

        # ---------- Stats ----------
        layout.addWidget(QLabel("Bağlantı İstatistikleri:"))
        self.stats_label = QLabel(
            "IP Adresi: -\n"
            "Signal Gücü: -\n"
            "Bağlantı Hızı: -"
        )
        self.stats_label.setStyleSheet("color: #00ff88; font-size: 11px;")
        layout.addWidget(self.stats_label)

        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # ---------- Timer ----------
        self.scanner_thread = None
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_status)
        self.update_timer.start(5000)

        self.refresh_status()

    # ==================================================
    # WiFi Scan
    # ==================================================
    def scan_networks(self):
        self.scan_btn.setEnabled(False)
        self.networks_list.clear()
        self.networks_list.addItem("⏳ Ağlar taranıyor...")

        self.scanner_thread = WiFiScannerThread()
        self.scanner_thread.networks_found.connect(self.display_networks)
        self.scanner_thread.start()

    def display_networks(self, networks):
        self.networks_list.clear()
        if not networks:
            self.networks_list.addItem("❌ Ağ bulunamadı")
        else:
            for ssid in networks:
                self.networks_list.addItem(QListWidgetItem(f"📶 {ssid}"))
        self.scan_btn.setEnabled(True)

    # ==================================================
    # Connect
    # ==================================================
    def connect_to_network(self):
        item = self.networks_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Hata", "Bir ağ seçin")
            return

        ssid = item.text().replace("📶", "").strip()
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "Hata", "Parola girin")
            return

        try:
            self.connect_btn.setEnabled(False)
            self.connect_btn.setText("Bağlanıyor...")

            result = subprocess.run(
                ['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                capture_output=True,
                text=True,
                timeout=20
            )

            if result.returncode == 0:
                QMessageBox.information(self, "Başarılı", f"{ssid} ağına bağlanıldı")
                self.refresh_status()
            else:
                QMessageBox.critical(self, "Bağlantı Hatası", result.stderr)

        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Hata", "Bağlantı zaman aşımı")

        finally:
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("Bağlan")

    # ==================================================
    # Status (GERÇEK BAĞLANTI KONTROLÜ)
    # ==================================================
    def refresh_status(self):
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'device'],
                capture_output=True,
                text=True,
                timeout=5
            )

            wifi_name = None

            for line in result.stdout.splitlines():
                if not line:
                    continue

                device, dtype, state, connection = line.split(':', 3)

                if dtype == 'wifi' and state == 'connected':
                    wifi_name = connection
                    break

            if wifi_name:
                self.status_label.setText(f"🟢 Bağlı: {wifi_name}")
                self.status_label.setStyleSheet("color: #00ff88;")
                self.update_stats()
            else:
                self.status_label.setText("🔴 Bağlı değil")
                self.status_label.setStyleSheet("color: #ff4444;")
                self.stats_label.setText(
                    "IP Adresi: -\nSignal Gücü: -\nBağlantı Hızı: -"
                )

        except Exception as e:
            print("Durum hatası:", e)
            self.status_label.setText("❓ Durum okunamadı")

    # ==================================================
    # Stats
    # ==================================================
    def update_stats(self):
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'DEVICE,TYPE,IP4.ADDRESS,SIGNAL', 'device'],
                capture_output=True,
                text=True,
                timeout=5
            )

            ip = "-"
            signal = "-"

            for line in result.stdout.splitlines():
                if not line:
                    continue

                device, dtype, ip_addr, sig = line.split(':', 3)

                if dtype == 'wifi' and ip_addr:
                    ip = ip_addr
                    signal = sig + "%"
                    break

            self.stats_label.setText(
                f"IP Adresi: {ip}\n"
                f"Signal Gücü: {signal}\n"
                f"Bağlantı Hızı: WiFi"
            )

        except Exception as e:
            print("Stats hatası:", e)

    def closeEvent(self, event):
        self.update_timer.stop()
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.quit()
            self.scanner_thread.wait()
        event.accept()
