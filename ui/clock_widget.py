from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, QDateTime, Qt

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.time = QLabel()
        self.date = QLabel()

        self.time.setStyleSheet("font-size: 28px;")
        self.date.setStyleSheet("font-size: 14px; color:#aaa;")

        v.addWidget(self.time)
        v.addWidget(self.date)

        t = QTimer(self)
        t.timeout.connect(self.update)
        t.start(1000)
        self.update()

    def update(self):
        now = QDateTime.currentDateTime()
        self.time.setText(now.toString("HH:mm"))
        self.date.setText(now.toString("dd.MM.yyyy"))
