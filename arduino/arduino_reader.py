import serial
import serial.tools.list_ports
import platform
import socket
#import bluetooth
from PySide6.QtCore import QThread, Signal
from typing import Optional, Dict, List


class ConnectionType:
    """Bağlantı tipi enum"""
    USB = "usb"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"


class ArduinoReader(QThread):
    """
    Arduino'dan veri okuma sınıfı
    - Otomatik port algılama (Windows/Linux/macOS)
    - USB Serial bağlantı
    - WiFi TCP/IP bağlantı
    - Bluetooth bağlantı
    """
    
    data_received = Signal(dict)
    connection_status = Signal(str)  # "connected", "disconnected", "error"
    error_message = Signal(str)
    
    def __init__(self, connection_type=ConnectionType.USB, **kwargs):
        super().__init__()
        self.connection_type = connection_type
        self.running = True
        self.connection = None
        
        # USB parametreleri
        self.port = kwargs.get('port', None)
        self.baud = kwargs.get('baud', 115200)
        
        # WiFi parametreleri
        self.host = kwargs.get('host', '192.168.1.100')
        self.tcp_port = kwargs.get('tcp_port', 8888)
        
        # Bluetooth parametreleri
        self.bt_address = kwargs.get('bt_address', None)
        self.bt_port = kwargs.get('bt_port', 1)
        
        # Otomatik port algılama
        if self.connection_type == ConnectionType.USB and not self.port:
            self.port = self.auto_detect_port()
    
    def auto_detect_port(self) -> Optional[str]:
        """İşletim sistemine göre Arduino portunu otomatik algılar"""
        system = platform.system()
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            self.error_message.emit("Hiçbir seri port bulunamadı!")
            return None
        
        # Platform bazlı port seçimi
        if system == "Windows":
            # Windows'ta COM portlarını ara
            for port in ports:
                if 'Arduino' in port.description or 'USB' in port.description:
                    return port.device
            # Bulunamazsa ilk COM portunu kullan
            return ports[0].device
            
        elif system == "Linux":
            # Linux'ta /dev/ttyUSB* veya /dev/ttyACM* ara
            for port in ports:
                if '/dev/ttyUSB' in port.device or '/dev/ttyACM' in port.device:
                    return port.device
            return ports[0].device
            
        elif system == "Darwin":  # macOS
            # macOS'ta /dev/cu.* veya /dev/tty.* ara
            for port in ports:
                if '/dev/cu.' in port.device or '/dev/tty.' in port.device:
                    if 'usb' in port.device.lower() or 'serial' in port.device.lower():
                        return port.device
            return ports[0].device
        
        return None
    
    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """Mevcut tüm portları listeler"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
        return ports
    
    @staticmethod
    def list_bluetooth_devices() -> List[Dict[str, str]]:
        """Yakındaki Bluetooth cihazlarını listeler"""
        try:
            devices = []
 #           nearby = bluetooth.discover_devices(duration=8, lookup_names=True)
#          for addr, name in nearby:
 #               devices.append({
 #                   'address': addr,
 #                   'name': name
  #              })
            return devices
        except Exception as e:
            print(f"Bluetooth arama hatası: {e}")
            return []
    
    def connect_usb(self) -> bool:
        """USB Serial bağlantı"""
        try:
            if not self.port:
                self.error_message.emit("Port belirtilmedi!")
                return False
            
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=1
            )
            self.connection_status.emit("connected")
            return True
            
        except serial.SerialException as e:
            self.error_message.emit(f"USB bağlantı hatası: {str(e)}")
            self.connection_status.emit("error")
            return False
    
    def connect_wifi(self) -> bool:
        """WiFi TCP/IP bağlantı"""
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(5)
            self.connection.connect((self.host, self.tcp_port))
            self.connection.settimeout(1)
            self.connection_status.emit("connected")
            return True
            
        except socket.error as e:
            self.error_message.emit(f"WiFi bağlantı hatası: {str(e)}")
            self.connection_status.emit("error")
            return False
    
 #   def connect_bluetooth(self) -> bool:
        """Bluetooth bağlantı"""
        #try:
         #   if not self.bt_address:
         #       self.error_message.emit("Bluetooth adresi belirtilmedi!")
          #      return False
            
         #   self.connection = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
           # self.connection.connect((self.bt_address, self.bt_port))
            #self.connection_status.emit("connected")
            #return True
            
        #except bluetooth.BluetoothError as e:
           # self.error_message.emit(f"Bluetooth bağlantı hatası: {str(e)}")
            #self.connection_status.emit("error")
            #return False
    
    def read_line(self) -> str:
        """Bağlantı tipine göre veri okuma"""
        try:
            if self.connection_type == ConnectionType.USB:
                return self.connection.readline().decode('utf-8', errors='ignore').strip()
            
            elif self.connection_type == ConnectionType.WIFI:
                data = self.connection.recv(1024).decode('utf-8', errors='ignore')
                return data.strip()
            
            elif self.connection_type == ConnectionType.BLUETOOTH:
                data = self.connection.recv(1024).decode('utf-8', errors='ignore')
                return data.strip()
            
        except Exception as e:
            return ""
        
        return ""
    
    def parse_arduino_data(self, line: str) -> Optional[Dict]:
        """
        Arduino'dan gelen yeni serial formatı parse eder
        Format: mode/far/durum/far2/vites/sinyallambasi/dortlu/sinyalsol/sinyalsag/
                speed1/speed2/direksiyonaci/solGaz/sagGaz/EDS_AKTIF
        """
        if not line:
            return None
        
        try:
            parts = line.split('/')
            
            if len(parts) < 15:
                return None
            
            data = {
                'mode': int(parts[0]),              # 0=Eco, 1=Normal, 2=Sport
                'far': int(parts[1]),               # 0=Off, 1=Auto, 2=On
                'durum': int(parts[2]),             # 0=Off, 1=On, 2=Acc
                'far2': int(parts[3]),              # 0=Off, 1=Uzun, 2=Sis
                'vites': int(parts[4]),             # 0=Neutral, 1=İleri, 2=Geri
                'sinyallambasi': int(parts[5]),     # 0=Off, 1=On
                'dortlu': int(parts[6]),            # 0=Off, 1=On
                'sinyalsol': int(parts[7]),         # 0=Off, 1=On
                'sinyalsag': int(parts[8]),         # 0=Off, 1=On
                'speed_kmh_1': float(parts[9]),     # Sol motor hızı
                'speed_kmh_2': float(parts[10]),    # Sağ motor hızı
                'direksiyonaci': float(parts[11]),  # Direksiyon açısı
                'solGazYuzdesi': int(parts[12]),    # Sol motor gaz %
                'sagGazYuzdesi': int(parts[13]),    # Sağ motor gaz %
                'EDS_AKTIF': int(parts[14])         # EDS aktif mi? 0/1
            }
            
            # Ortalama hız hesapla
            data['avg_speed'] = (data['speed_kmh_1'] + data['speed_kmh_2']) / 2.0
            
            return data
            
        except (ValueError, IndexError) as e:
            self.error_message.emit(f"Veri parse hatası: {str(e)} - Line: {line}")
            return None
    
    def run(self):
        """Ana thread döngüsü"""
        # Bağlantı kur
        connected = False
        
        if self.connection_type == ConnectionType.USB:
            connected = self.connect_usb()
        elif self.connection_type == ConnectionType.WIFI:
            connected = self.connect_wifi()
        elif self.connection_type == ConnectionType.BLUETOOTH:
            connected = self.connect_bluetooth()
        
        if not connected:
            self.running = False
            return
        
        # Veri okuma döngüsü
        while self.running:
            try:
                line = self.read_line()
                
                if line:
                    data = self.parse_arduino_data(line)
                    
                    if data:
                        self.data_received.emit(data)
                
            except Exception as e:
                self.error_message.emit(f"Okuma hatası: {str(e)}")
                break
        
        self.close_connection()
    
    def close_connection(self):
        """Bağlantıyı kapat"""
        try:
            if self.connection:
                if self.connection_type == ConnectionType.USB:
                    self.connection.close()
                elif self.connection_type in [ConnectionType.WIFI, ConnectionType.BLUETOOTH]:
                    self.connection.close()
                
                self.connection_status.emit("disconnected")
                
        except Exception as e:
            self.error_message.emit(f"Bağlantı kapatma hatası: {str(e)}")
    
    def stop(self):
        """Thread'i durdur"""
        self.running = False
        self.close_connection()
        self.wait()
