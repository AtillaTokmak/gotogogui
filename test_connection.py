#!/usr/bin/env python3
"""
GoToGo Dashboard - Test Uygulaması
Arduino bağlantısını ve veri akışını test eder
"""

import sys
from arduino.arduino_reader import ArduinoReader, ConnectionType


def test_port_detection():
    """Mevcut portları listele"""
    print("=" * 60)
    print("PORT ALGILAMA TESTİ")
    print("=" * 60)
    
    ports = ArduinoReader.list_available_ports()
    
    if ports:
        print(f"\n{len(ports)} port bulundu:\n")
        for i, port in enumerate(ports, 1):
            print(f"{i}. {port['device']}")
            print(f"   Açıklama: {port['description']}")
            print(f"   HWID: {port['hwid']}")
            print()
    else:
        print("\nHiçbir port bulunamadı!")
    
    return ports


def test_bluetooth_scan():
    """Bluetooth cihazlarını tara"""
    print("=" * 60)
    print("BLUETOOTH TARAMA TESTİ")
    print("=" * 60)
    print("\nBluetooth cihazları aranıyor (bu 8-10 saniye sürebilir)...\n")
    
    devices = ArduinoReader.list_bluetooth_devices()
    
    if devices:
        print(f"{len(devices)} Bluetooth cihazı bulundu:\n")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['name']}")
            print(f"   Adres: {device['address']}")
            print()
    else:
        print("Hiçbir Bluetooth cihazı bulunamadı!")
    
    return devices


def test_data_reading(connection_type=ConnectionType.USB, **kwargs):
    """Veri okuma testi"""
    print("=" * 60)
    print("VERİ OKUMA TESTİ")
    print("=" * 60)
    
    # Bağlantı tipi bilgisi
    type_names = {
        ConnectionType.USB: "USB Serial",
        ConnectionType.WIFI: "WiFi",
        ConnectionType.BLUETOOTH: "Bluetooth"
    }
    print(f"\nBağlantı Tipi: {type_names.get(connection_type, 'Bilinmiyor')}")
    
    if connection_type == ConnectionType.USB and 'port' in kwargs:
        print(f"Port: {kwargs['port']}")
        print(f"Baud Rate: {kwargs.get('baud', 115200)}")
    elif connection_type == ConnectionType.WIFI:
        print(f"Host: {kwargs.get('host', 'N/A')}")
        print(f"Port: {kwargs.get('tcp_port', 'N/A')}")
    elif connection_type == ConnectionType.BLUETOOTH:
        print(f"Adres: {kwargs.get('bt_address', 'N/A')}")
    
    print("\nBağlanıyor...\n")
    
    try:
        reader = ArduinoReader(connection_type=connection_type, **kwargs)
        
        # Callback fonksiyonları
        def on_data(data):
            print("\n" + "=" * 60)
            print("YENİ VERİ GELDİ:")
            print("=" * 60)
            for key, value in data.items():
                print(f"{key:20s}: {value}")
        
        def on_status(status):
            status_icons = {
                'connected': '✓',
                'disconnected': '✗',
                'error': '⚠'
            }
            icon = status_icons.get(status, '?')
            print(f"\n{icon} Bağlantı Durumu: {status.upper()}")
        
        def on_error(message):
            print(f"\n⚠ HATA: {message}")
        
        # Signal bağlantıları
        reader.data_received.connect(on_data)
        reader.connection_status.connect(on_status)
        reader.error_message.connect(on_error)
        
        # Thread'i başlat
        reader.start()
        
        print("Veri okunuyor... (Çıkmak için Ctrl+C)")
        print("-" * 60)
        
        # Sonsuz döngü (Ctrl+C ile çık)
        reader.wait()
        
    except KeyboardInterrupt:
        print("\n\nTest kullanıcı tarafından durduruldu.")
        reader.stop()
    except Exception as e:
        print(f"\n\n⚠ HATA: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Ana menü"""
    print("\n" + "=" * 60)
    print(" GoToGo Dashboard - Test Uygulaması")
    print("=" * 60)
    
    while True:
        print("\n1. Port Algılama Testi")
        print("2. Bluetooth Tarama Testi")
        print("3. USB Serial Veri Okuma Testi")
        print("4. WiFi Veri Okuma Testi")
        print("5. Bluetooth Veri Okuma Testi")
        print("0. Çıkış")
        print()
        
        choice = input("Seçiminiz: ").strip()
        
        if choice == '1':
            test_port_detection()
        
        elif choice == '2':
            test_bluetooth_scan()
        
        elif choice == '3':
            ports = test_port_detection()
            if ports:
                print("\nBir port seçin:")
                for i, port in enumerate(ports, 1):
                    print(f"{i}. {port['device']}")
                
                try:
                    port_idx = int(input("\nPort numarası: ")) - 1
                    if 0 <= port_idx < len(ports):
                        selected_port = ports[port_idx]['device']
                        baud = input("Baud rate (varsayılan: 115200): ").strip()
                        baud = int(baud) if baud else 115200
                        
                        test_data_reading(
                            ConnectionType.USB,
                            port=selected_port,
                            baud=baud
                        )
                except (ValueError, IndexError):
                    print("Geçersiz seçim!")
        
        elif choice == '4':
            host = input("Arduino IP Adresi (varsayılan: 192.168.1.100): ").strip()
            host = host if host else "192.168.1.100"
            
            port = input("Port (varsayılan: 8888): ").strip()
            port = int(port) if port else 8888
            
            test_data_reading(
                ConnectionType.WIFI,
                host=host,
                tcp_port=port
            )
        
        elif choice == '5':
            devices = test_bluetooth_scan()
            if devices:
                print("\nBir cihaz seçin:")
                for i, device in enumerate(devices, 1):
                    print(f"{i}. {device['name']} ({device['address']})")
                
                try:
                    device_idx = int(input("\nCihaz numarası: ")) - 1
                    if 0 <= device_idx < len(devices):
                        selected_device = devices[device_idx]['address']
                        
                        test_data_reading(
                            ConnectionType.BLUETOOTH,
                            bt_address=selected_device,
                            bt_port=1
                        )
                except (ValueError, IndexError):
                    print("Geçersiz seçim!")
        
        elif choice == '0':
            print("\nÇıkılıyor...")
            break
        
        else:
            print("\nGeçersiz seçim!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram sonlandırıldı.")
        sys.exit(0)
