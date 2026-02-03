from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class MediaOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        self.move(300, 100)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30,30,30,230);
                border-radius: 12px;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        title = QLabel("Spotify Player")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px;")

        layout.addWidget(title)
        self.hide()
