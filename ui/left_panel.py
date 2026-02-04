from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QPainter, QColor


class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Hız göstergesi
        self.speed_label = QLabel("0")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 72px; font-weight: bold; color: #00ff88;")
        
        speed_unit = QLabel("km/h")
        speed_unit.setAlignment(Qt.AlignCenter)
        speed_unit.setStyleSheet("font-size: 18px; color: #888;")
        
        # Mod göstergesi
        self.mode_label = QLabel("NORMAL")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white;
            background-color: #333;
            padding: 10px;
            border-radius: 8px;
        """)
        
        # Vites göstergesi
        gear_container = QHBoxLayout()
        gear_label = QLabel("Vites:")
        gear_label.setStyleSheet("font-size: 16px; color: #aaa;")
        
        self.gear_label = QLabel("N")
        self.gear_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold;
            color: white;
            background-color: #444;
            padding: 5px 20px;
            border-radius: 5px;
        """)
        
        gear_container.addWidget(gear_label)
        gear_container.addWidget(self.gear_label)
        gear_container.addStretch()
        
        # EDS göstergesi (küçük)
        self.eds_label = QLabel("EDS: KAPALI")
        self.eds_label.setAlignment(Qt.AlignCenter)
        self.eds_label.setStyleSheet("""
            font-size: 10px;
            color: #666;
            padding: 3px;
            border: 1px solid #444;
            border-radius: 3px;
        """)
        
        # Gaz, Sol Motor, Sağ Motor (mini göstergeler)
        stats_container = QHBoxLayout()
        
        # Ortalama Gaz Yüzdesi
        throttle_label = QLabel("Gaz:")
        throttle_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.throttle_value = QLabel("0%")
        self.throttle_value.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffaa00;")
        
        # Sol Motor Gaz
        left_throttle_label = QLabel("Sol:")
        left_throttle_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.left_throttle_value = QLabel("0%")
        self.left_throttle_value.setStyleSheet("font-size: 12px; font-weight: bold; color: #00aaff;")
        
        # Sağ Motor Gaz
        right_throttle_label = QLabel("Sağ:")
        right_throttle_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.right_throttle_value = QLabel("0%")
        self.right_throttle_value.setStyleSheet("font-size: 12px; font-weight: bold; color: #00aaff;")
        
        stats_container.addWidget(throttle_label)
        stats_container.addWidget(self.throttle_value)
        stats_container.addSpacing(10)
        stats_container.addWidget(left_throttle_label)
        stats_container.addWidget(self.left_throttle_value)
        stats_container.addSpacing(10)
        stats_container.addWidget(right_throttle_label)
        stats_container.addWidget(self.right_throttle_value)
        stats_container.addStretch()
        
        # Direksiyon açısı
        steering_container = QHBoxLayout()
        steering_text = QLabel("Direksiyon:")
        steering_text.setStyleSheet("font-size: 14px; color: #aaa;")
        
        self.steering_label = QLabel("0.0°")
        self.steering_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        steering_container.addWidget(steering_text)
        steering_container.addWidget(self.steering_label)
        steering_container.addStretch()
        
        # Motor gaz göstergeleri
        motor_frame = QFrame()
        motor_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        motor_layout = QVBoxLayout(motor_frame)
        
        motor_title = QLabel("Motor Gücü")
        motor_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00aaff;")
        motor_title.setAlignment(Qt.AlignCenter)
        
        # Sol motor
        left_motor_layout = QHBoxLayout()
        left_motor_label = QLabel("Sol:")
        left_motor_label.setStyleSheet("font-size: 14px; color: #aaa;")
        self.left_motor_bar = PowerBar()
        left_motor_layout.addWidget(left_motor_label)
        left_motor_layout.addWidget(self.left_motor_bar, 1)
        self.left_motor_value = QLabel("0%")
        self.left_motor_value.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 40px;")
        left_motor_layout.addWidget(self.left_motor_value)
        
        # Sağ motor
        right_motor_layout = QHBoxLayout()
        right_motor_label = QLabel("Sağ:")
        right_motor_label.setStyleSheet("font-size: 14px; color: #aaa;")
        self.right_motor_bar = PowerBar()
        right_motor_layout.addWidget(right_motor_label)
        right_motor_layout.addWidget(self.right_motor_bar, 1)
        self.right_motor_value = QLabel("0%")
        self.right_motor_value.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 40px;")
        right_motor_layout.addWidget(self.right_motor_value)
        
        motor_layout.addWidget(motor_title)
        motor_layout.addLayout(left_motor_layout)
        motor_layout.addLayout(right_motor_layout)
        
        # Sinyaller (Sol, Dörtlü, Sağ)
        signals_container = QHBoxLayout()
        
        self.left_signal_light = QLabel("◄")
        self.left_signal_light.setAlignment(Qt.AlignCenter)
        self.left_signal_light.setStyleSheet("""
            font-size: 32px;
            color: #444;
            min-width: 50px;
        """)
        
        self.hazard_light = QLabel("◆")
        self.hazard_light.setAlignment(Qt.AlignCenter)
        self.hazard_light.setStyleSheet("""
            font-size: 28px;
            color: #444;
            min-width: 50px;
        """)
        
        self.right_signal_light = QLabel("►")
        self.right_signal_light.setAlignment(Qt.AlignCenter)
        self.right_signal_light.setStyleSheet("""
            font-size: 32px;
            color: #444;
            min-width: 50px;
        """)
        
        signals_container.addWidget(self.left_signal_light)
        signals_container.addStretch()
        signals_container.addWidget(self.hazard_light)
        signals_container.addStretch()
        signals_container.addWidget(self.right_signal_light)
        
        # Araç göstergesi (basit SVG)
        self.car_indicator = CarIndicator()
        
        # Layout'a ekle
        layout.addWidget(self.speed_label)
        layout.addWidget(speed_unit)
        layout.addWidget(self.mode_label)
        layout.addLayout(gear_container)
        layout.addWidget(self.eds_label)
        layout.addLayout(stats_container)
        layout.addLayout(steering_container)
        layout.addWidget(motor_frame)
        layout.addLayout(signals_container)
        layout.addWidget(self.car_indicator)
        layout.addStretch()
    
    def update_data(self, data: dict):
        """Arduino'dan gelen veriyi güncelle"""
        # Hız
        if 'avg_speed' in data:
            self.speed_label.setText(f"{int(data['avg_speed'])}")
        
        # Mod (0=Eco, 1=Normal, 2=Sport)
        if 'mode' in data:
            mode_names = ["ECO", "NORMAL", "SPORT"]
            mode_colors = ["#00ff44", "#00aaff", "#ff4444"]
            mode = data['mode']
            
            if 0 <= mode < len(mode_names):
                self.mode_label.setText(mode_names[mode])
                self.mode_label.setStyleSheet(f"""
                    font-size: 24px; 
                    font-weight: bold; 
                    color: white;
                    background-color: {mode_colors[mode]};
                    padding: 10px;
                    border-radius: 8px;
                """)
        
        # Vites (0=Neutral, 1=İleri, 2=Geri)
        if 'vites' in data:
            vites_symbols = ["N", "D", "R"]
            vites_colors = ["#666", "#00ff44", "#ff4444"]
            vites = data['vites']
            
            if 0 <= vites < len(vites_symbols):
                self.gear_label.setText(vites_symbols[vites])
                self.gear_label.setStyleSheet(f"""
                    font-size: 32px; 
                    font-weight: bold;
                    color: white;
                    background-color: {vites_colors[vites]};
                    padding: 5px 20px;
                    border-radius: 5px;
                """)
        
        # EDS durumu
        if 'EDS_AKTIF' in data:
            if data['EDS_AKTIF'] == 1:
                self.eds_label.setText("EDS: AKTİF ✓")
                self.eds_label.setStyleSheet("""
                    font-size: 10px;
                    color: #00ff44;
                    font-weight: bold;
                    padding: 3px;
                    border: 1px solid #00ff44;
                    border-radius: 3px;
                """)
            else:
                self.eds_label.setText("EDS: KAPALI")
                self.eds_label.setStyleSheet("""
                    font-size: 10px;
                    color: #666;
                    padding: 3px;
                    border: 1px solid #444;
                    border-radius: 3px;
                """)
        
        # Ortalama gaz yüzdesi (sol + sağ / 2)
        if 'solGazYuzdesi' in data and 'sagGazYuzdesi' in data:
            avg_throttle = (data['solGazYuzdesi'] + data['sagGazYuzdesi']) / 2.0
            self.throttle_value.setText(f"{int(avg_throttle)}%")
        
        # Sol motor gaz yüzdesi
        if 'solGazYuzdesi' in data:
            self.left_throttle_value.setText(f"{data['solGazYuzdesi']}%")
        
        # Sağ motor gaz yüzdesi
        if 'sagGazYuzdesi' in data:
            self.right_throttle_value.setText(f"{data['sagGazYuzdesi']}%")
        
        # Direksiyon açısı
        if 'direksiyonaci' in data:
            angle = data['direksiyonaci']
            self.steering_label.setText(f"{angle:.1f}°")
            
            # Renk değişimi
            if abs(angle) > 90:
                color = "#ff4444"
            elif abs(angle) > 45:
                color = "#ffaa00"
            else:
                color = "#00ff44"
            
            self.steering_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        
        # Motor güçleri
        if 'solGazYuzdesi' in data:
            self.left_motor_value.setText(f"{data['solGazYuzdesi']}%")
            self.left_motor_bar.set_value(data['solGazYuzdesi'])
        
        if 'sagGazYuzdesi' in data:
            self.right_motor_value.setText(f"{data['sagGazYuzdesi']}%")
            self.right_motor_bar.set_value(data['sagGazYuzdesi'])
        
        # Araç göstergesi güncelle
        self.car_indicator.update_indicators(
            left_signal=data.get('sinyalsol', 0),
            right_signal=data.get('sinyalsag', 0),
            hazard=data.get('dortlu', 0),
            headlight=data.get('far', 0),
            high_beam=data.get('far2', 0)
        )
        
        # Sinyalleri güncelle (yanıp sönme)
        left_active = data.get('sinyalsol', 0) == 1 or data.get('dortlu', 0) == 1
        right_active = data.get('sinyalsag', 0) == 1 or data.get('dortlu', 0) == 1
        hazard_active = data.get('dortlu', 0) == 1
        
        # Sol sinyal
        if left_active and self.car_indicator.blink_state:
            self.left_signal_light.setStyleSheet("""
                font-size: 32px;
                color: #ffaa00;
                font-weight: bold;
                min-width: 50px;
            """)
        else:
            self.left_signal_light.setStyleSheet("""
                font-size: 32px;
                color: #444;
                min-width: 50px;
            """)
        
        # Sağ sinyal
        if right_active and self.car_indicator.blink_state:
            self.right_signal_light.setStyleSheet("""
                font-size: 32px;
                color: #ffaa00;
                font-weight: bold;
                min-width: 50px;
            """)
        else:
            self.right_signal_light.setStyleSheet("""
                font-size: 32px;
                color: #444;
                min-width: 50px;
            """)
        
        # Dörtlü sinyal (hazard)
        if hazard_active and self.car_indicator.blink_state:
            self.hazard_light.setStyleSheet("""
                font-size: 28px;
                color: #ff4444;
                font-weight: bold;
                min-width: 50px;
            """)
        else:
            self.hazard_light.setStyleSheet("""
                font-size: 28px;
                color: #444;
                min-width: 50px;
            """)


class PowerBar(QWidget):
    """Motor gücü gösterge çubuğu"""
    def __init__(self):
        super().__init__()
        self.value = 0
        self.setFixedHeight(20)
        self.setMinimumWidth(100)
    
    def set_value(self, value):
        self.value = max(0, min(100, value))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        # Değer çubuğu
        width = int((self.width() * self.value) / 100)
        
        # Renk gradient (yeşil -> sarı -> kırmızı)
        if self.value < 50:
            color = QColor("#00ff44")
        elif self.value < 80:
            color = QColor("#ffaa00")
        else:
            color = QColor("#ff4444")
        
        painter.fillRect(0, 0, width, self.height(), color)


class CarIndicator(QWidget):
    """Araç gösterge paneli (sinyaller, farlar vb.)"""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(150)
        
        self.left_signal = False
        self.right_signal = False
        self.hazard = False
        self.headlight = False
        self.high_beam = False
        
        # Yanıp sönme için timer
        self.blink_state = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_blink)
        self.timer.start(500)
    
    def toggle_blink(self):
        self.blink_state = not self.blink_state
        self.update()
    
    def update_indicators(self, left_signal, right_signal, hazard, headlight, high_beam):
        self.left_signal = left_signal == 1
        self.right_signal = right_signal == 1
        self.hazard = hazard == 1
        self.headlight = headlight > 0
        self.high_beam = high_beam == 1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        
        # Araç gövdesi (basit dikdörtgen)
        car_width = 80
        car_height = 40
        car_x = center_x - car_width // 2
        car_y = height // 2 - car_height // 2
        
        painter.fillRect(car_x, car_y, car_width, car_height, QColor("#555"))
        
        # Sol sinyal
        if (self.left_signal or self.hazard) and self.blink_state:
            painter.fillRect(car_x - 30, car_y + 10, 20, 20, QColor("#ffaa00"))
        
        # Sağ sinyal
        if (self.right_signal or self.hazard) and self.blink_state:
            painter.fillRect(car_x + car_width + 10, car_y + 10, 20, 20, QColor("#ffaa00"))
        
        # Farlar
        if self.headlight:
            color = QColor("#ffff44") if self.high_beam else QColor("#ffffff")
            painter.fillRect(car_x - 5, car_y - 15, 10, 10, color)
            painter.fillRect(car_x + car_width - 5, car_y - 15, 10, 10, color)
