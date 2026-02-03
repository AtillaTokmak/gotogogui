from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QGroupBox,
    QRadioButton, QButtonGroup, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from arduino.arduino_reader import ArduinoReader, ConnectionType


class ConnectionSettingsDialog(QDialog):
    """Bağlantı ayarları dialog penceresi"""
    
    connection_changed = Signal(str, dict)  # connection_type, params
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Bağlantı Ayarları")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QComboBox {
                background-color: #1a1a1a;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                color: white;
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
            QRadioButton {
                color: white;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Bağlantı tipi seçimi
        type_group = QGroupBox("Bağlantı Tipi")
        type_layout = QVBoxLayout()
        
        self.connection_type_group = QButtonGroup()
        
        self.usb_radio = QRadioButton("USB Serial")
        self.wifi_radio = QRadioButton("WiFi (TCP/IP)")
        self.bluetooth_radio = QRadioButton("Bluetooth")
        
        self.usb_radio.setChecked(True)
        
        self.connection_type_group.addButton(self.usb_radio, 0)
        self.connection_type_group.addButton(self.wifi_radio, 1)
        self.connection_type_group.addButton(self.bluetooth_radio, 2)
        
        type_layout.addWidget(self.usb_radio)
        type_layout.addWidget(self.wifi_radio)
        type_layout.addWidget(self.bluetooth_radio)
        type_group.setLayout(type_layout)
        
        # USB ayarları
        self.usb_group = QGroupBox("USB Ayarları")
        usb_layout = QVBoxLayout()
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.refresh_ports_btn = QPushButton("🔄")
        self.refresh_ports_btn.setMaximumWidth(40)
        self.refresh_ports_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.port_combo, 1)
        port_layout.addWidget(self.refresh_ports_btn)
        
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("Baud Rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("115200")
        baud_layout.addWidget(self.baud_combo, 1)
        
        usb_layout.addLayout(port_layout)
        usb_layout.addLayout(baud_layout)
        self.usb_group.setLayout(usb_layout)
        
        # WiFi ayarları
        self.wifi_group = QGroupBox("WiFi Ayarları")
        wifi_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("IP Adresi:"))
        self.host_input = QLineEdit("192.168.1.100")
        host_layout.addWidget(self.host_input, 1)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.tcp_port_input = QLineEdit("8888")
        port_layout.addWidget(self.tcp_port_input, 1)
        
        wifi_layout.addLayout(host_layout)
        wifi_layout.addLayout(port_layout)
        self.wifi_group.setLayout(wifi_layout)
        self.wifi_group.setVisible(False)
        
        # Bluetooth ayarları
        self.bluetooth_group = QGroupBox("Bluetooth Ayarları")
        bt_layout = QVBoxLayout()
        
        bt_search_layout = QHBoxLayout()
        self.bt_search_btn = QPushButton("Cihazları Ara")
        self.bt_search_btn.clicked.connect(self.search_bluetooth)
        bt_search_layout.addWidget(self.bt_search_btn)
        
        self.bt_devices_list = QListWidget()
        
        bt_layout.addLayout(bt_search_layout)
        bt_layout.addWidget(QLabel("Bulunan Cihazlar:"))
        bt_layout.addWidget(self.bt_devices_list)
        
        self.bluetooth_group.setLayout(bt_layout)
        self.bluetooth_group.setVisible(False)
        
        # Radio button değişikliklerini dinle
        self.usb_radio.toggled.connect(lambda: self.toggle_groups())
        self.wifi_radio.toggled.connect(lambda: self.toggle_groups())
        self.bluetooth_radio.toggled.connect(lambda: self.toggle_groups())
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Bağlan")
        self.cancel_btn = QPushButton("İptal")
        
        self.connect_btn.clicked.connect(self.apply_settings)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.connect_btn)
        
        # Ana layout'a ekle
        layout.addWidget(type_group)
        layout.addWidget(self.usb_group)
        layout.addWidget(self.wifi_group)
        layout.addWidget(self.bluetooth_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # İlk yükleme
        self.refresh_ports()
    
    def toggle_groups(self):
        """Seçilen bağlantı tipine göre grupları göster/gizle"""
        self.usb_group.setVisible(self.usb_radio.isChecked())
        self.wifi_group.setVisible(self.wifi_radio.isChecked())
        self.bluetooth_group.setVisible(self.bluetooth_radio.isChecked())
    
    def refresh_ports(self):
        """Mevcut portları yenile"""
        self.port_combo.clear()
        
        ports = ArduinoReader.list_available_ports()
        
        if ports:
            for port in ports:
                self.port_combo.addItem(
                    f"{port['device']} - {port['description']}",
                    port['device']
                )
        else:
            self.port_combo.addItem("Port bulunamadı", None)
    
    def search_bluetooth(self):
        """Bluetooth cihazlarını ara"""
        self.bt_devices_list.clear()
        self.bt_search_btn.setEnabled(False)
        self.bt_search_btn.setText("Aranıyor...")
        
        # Arka planda arama yapılacak (thread kullanarak)
        devices = ArduinoReader.list_bluetooth_devices()
        
        if devices:
            for device in devices:
                self.bt_devices_list.addItem(
                    f"{device['name']} ({device['address']})"
                )
        else:
            self.bt_devices_list.addItem("Cihaz bulunamadı")
        
        self.bt_search_btn.setEnabled(True)
        self.bt_search_btn.setText("Cihazları Ara")
    
    def apply_settings(self):
        """Ayarları uygula ve bağlan"""
        if self.usb_radio.isChecked():
            port = self.port_combo.currentData()
            if not port:
                QMessageBox.warning(self, "Hata", "Geçerli bir port seçin!")
                return
            
            params = {
                'port': port,
                'baud': int(self.baud_combo.currentText())
            }
            self.connection_changed.emit(ConnectionType.USB, params)
        
        elif self.wifi_radio.isChecked():
            params = {
                'host': self.host_input.text(),
                'tcp_port': int(self.tcp_port_input.text())
            }
            self.connection_changed.emit(ConnectionType.WIFI, params)
        
        elif self.bluetooth_radio.isChecked():
            selected_item = self.bt_devices_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Hata", "Bir Bluetooth cihazı seçin!")
                return
            
            # Address'i parse et
            text = selected_item.text()
            address = text.split('(')[1].split(')')[0]
            
            params = {
                'bt_address': address,
                'bt_port': 1
            }
            self.connection_changed.emit(ConnectionType.BLUETOOTH, params)
        
        self.accept()
