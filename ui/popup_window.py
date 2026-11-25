from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout


class PopupWindow(QWidget):
    def __init__(self, audio_service, parent=None):
        super().__init__(parent)
        self.audio_service = audio_service
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(360)

        self.title = QLabel("🇬🇧 DAILY ENGLISH")
        self.title.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.english = QLabel()
        self.english.setWordWrap(True)
        self.english.setStyleSheet("font-size: 24px; font-weight: 700;")

        self.ipa = QLabel()
        self.ipa.setStyleSheet("font-size: 14px; color: #666;")

        self.translation = QLabel()
        self.translation.setWordWrap(True)
        self.translation.setStyleSheet("font-size: 16px;")

        self.topic = QLabel()
        self.topic.setStyleSheet("font-size: 12px; color: #777;")

        self.listen_button = QPushButton("🔊 Listen")
        self.listen_button.clicked.connect(self.play_current)

        buttons = QHBoxLayout()
        buttons.addWidget(self.listen_button)
        buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        layout.addWidget(self.title)
        layout.addWidget(self.english)
        layout.addWidget(self.ipa)
        layout.addWidget(self.translation)
        layout.addWidget(self.topic)
        layout.addLayout(buttons)

        self.setStyleSheet("""
            PopupWindow {
                background: white;
                border: 1px solid #dddddd;
                border-radius: 14px;
            }
            QPushButton {
                padding: 7px 12px;
                border: 1px solid #dddddd;
                border-radius: 8px;
                background: #f7f7f7;
            }
        """)

        self.current_audio = ""
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_item(self, item, duration_seconds=10, play_sound=True):
        self.current_audio = item["item"]["audio_path"] or ""
        data = item["item"]

        self.english.setText(data["sentence"] if item["type"] == "example" else data["expression"])
        self.ipa.setText(data["ipa"] or "")
        self.translation.setText(data["translation"] or "")
        self.topic.setText(f"🏷 {item['phrase']['topic_name']}")

        self.adjustSize()
        screen = self.screen().availableGeometry()
        x = screen.right() - self.width() - 20
        y = screen.bottom() - self.height() - 50
        self.move(QPoint(x, y))
        self.show()
        self.raise_()

        self.hide_timer.start(max(1, int(duration_seconds)) * 1000)

        if play_sound and self.current_audio:
            self.audio_service.play(self.current_audio)

    def play_current(self):
        if self.current_audio:
            self.audio_service.play(self.current_audio)
