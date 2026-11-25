from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QComboBox, QFileDialog, QMessageBox,
    QLineEdit, QCheckBox, QSpinBox, QFormLayout, QGroupBox
)

from database.repositories.topic_repository import TopicRepository
from database.repositories.phrase_repository import PhraseRepository
from database.repositories.settings_repository import SettingsRepository
from services.import_service import ImportService
from services.tts_service import TTSService
from services.audio_service import AudioService
from services.startup_service import StartupService
from core.random_engine import RandomEngine
from core.reminder_manager import ReminderManager
from ui.popup_window import PopupWindow
from ui.tray_icon import TrayIcon


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.topic_repo = TopicRepository(db)
        self.phrase_repo = PhraseRepository(db)
        self.settings_repo = SettingsRepository(db)
        self.import_service = ImportService(self.topic_repo, self.phrase_repo)
        self.tts_service = TTSService(
            voice=self.settings_repo.get("tts_voice", "en-US-JennyNeural"),
            rate=self.settings_repo.get("tts_rate", "+0%")
        )
        self.audio_service = AudioService()
        self.random_engine = RandomEngine(self.phrase_repo)
        self.reminder = ReminderManager(self.random_engine, self.phrase_repo)
        self.reminder.phrase_ready.connect(self.on_phrase_ready)

        self.popup = PopupWindow(self.audio_service)
        self.tray = TrayIcon(self)
        self.tray.show()

        self.setWindowTitle("English Reminder")
        self.resize(950, 620)

        self._build_ui()
        self.refresh_topics()
        self.refresh_phrases()

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)

        title = QLabel("🇬🇧 English Reminder")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root.addWidget(title)

        subtitle = QLabel("Manage phrases and let the app remind you while you work.")
        subtitle.setStyleSheet("color: #666;")
        root.addWidget(subtitle)

        controls = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search phrase...")
        self.search.textChanged.connect(self.refresh_phrases)
        controls.addWidget(self.search)

        self.topic_combo = QComboBox()
        self.topic_combo.currentIndexChanged.connect(self.refresh_phrases)
        controls.addWidget(self.topic_combo)

        import_btn = QPushButton("Import TXT")
        import_btn.clicked.connect(self.import_txt)
        controls.addWidget(import_btn)

        next_btn = QPushButton("Show Next")
        next_btn.clicked.connect(self.show_next_phrase)
        controls.addWidget(next_btn)

        root.addLayout(controls)

        self.phrase_list = QListWidget()
        root.addWidget(self.phrase_list)

        settings_box = QGroupBox("Reminder Settings")
        form = QFormLayout(settings_box)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 3600)
        self.interval_spin.setValue(int(self.settings_repo.get("reminder_interval_seconds", "60")))
        form.addRow("Interval (seconds):", self.interval_spin)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(3, 120)
        self.duration_spin.setValue(int(self.settings_repo.get("popup_duration_seconds", "10")))
        form.addRow("Popup duration:", self.duration_spin)

        self.sound_check = QCheckBox("Play audio automatically")
        self.sound_check.setChecked(self.settings_repo.get("sound_enabled", "1") == "1")
        form.addRow("", self.sound_check)

        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self.settings_repo.get("startup_enabled", "0") == "1")
        form.addRow("", self.startup_check)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        form.addRow("", save_btn)

        root.addWidget(settings_box)

        self.status = QLabel("Ready.")
        root.addWidget(self.status)

        self.setCentralWidget(central)

    def refresh_topics(self):
        current = self.topic_combo.currentData()
        self.topic_combo.blockSignals(True)
        self.topic_combo.clear()
        self.topic_combo.addItem("All Topics", None)
        for topic in self.topic_repo.get_all():
            self.topic_combo.addItem(topic["name"], topic["id"])
        if current is not None:
            idx = self.topic_combo.findData(current)
            if idx >= 0:
                self.topic_combo.setCurrentIndex(idx)
        self.topic_combo.blockSignals(False)

    def refresh_phrases(self):
        self.phrase_list.clear()
        topic_id = self.topic_combo.currentData()
        rows = self.phrase_repo.list_phrases(
            topic_id=topic_id,
            search=self.search.text().strip()
        )
        for row in rows:
            examples = self.phrase_repo.get_examples(row["id"])
            text = f"{row['expression']}  |  {row['translation']}  |  {row['topic_name']}"
            if examples:
                text += f"  ({len(examples)} examples)"
            self.phrase_list.addItem(text)
        self.status.setText(f"{len(rows)} phrases.")

    def import_txt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import TXT", "", "Text files (*.txt)"
        )
        if not path:
            return
        try:
            result = self.import_service.import_txt(path)
            self.refresh_topics()
            self.refresh_phrases()
            QMessageBox.information(
                self,
                "Import completed",
                f"Imported: {result['imported']}\n"
                f"Skipped duplicate: {result['skipped']}\n"
                f"Invalid: {result['invalid']}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Import error", str(exc))

    def save_settings(self):
        interval = self.interval_spin.value()
        duration = self.duration_spin.value()
        sound = self.sound_check.isChecked()
        startup = self.startup_check.isChecked()

        self.settings_repo.set("reminder_interval_seconds", interval)
        self.settings_repo.set("popup_duration_seconds", duration)
        self.settings_repo.set("sound_enabled", 1 if sound else 0)
        self.settings_repo.set("startup_enabled", 1 if startup else 0)

        StartupService.set_enabled(startup)
        self.start_reminder()
        self.status.setText("Settings saved.")

    def start_reminder(self):
        interval = int(self.settings_repo.get("reminder_interval_seconds", "60"))
        selected = self.topic_combo.currentData()
        topic_ids = [selected] if selected else []
        self.reminder.start(interval, topic_ids, immediate=False)

    def start_background_services(self):
        self.start_reminder()

    def on_phrase_ready(self, item):
        duration = int(self.settings_repo.get("popup_duration_seconds", "10"))
        sound = self.settings_repo.get("sound_enabled", "1") == "1"

        data = item["item"]
        item_id = data["id"]

        # Generate audio lazily. Existing audio is always reused.
        if item["type"] == "phrase":
            text = data["expression"]
        else:
            text = data["sentence"]

        audio_path = self.tts_service.generate_for_id(text, item_id)
        with self.db.connect() as conn:
            table = "phrases" if item["type"] == "phrase" else "phrase_examples"
            conn.execute(
                f"UPDATE {table} SET audio_path=? WHERE id=?",
                (audio_path, item_id)
            )
            conn.commit()

        data = dict(data)
        data["audio_path"] = audio_path
        item = dict(item)
        item["item"] = data

        self.popup.show_item(item, duration, sound)

    def show_next_phrase(self):
        selected = self.topic_combo.currentData()
        item = self.random_engine.next([selected] if selected else [])
        if item:
            self.phrase_repo.mark_shown(item)
            self.on_phrase_ready(item)

    def toggle_reminder(self):
        if self.reminder.timer.isActive():
            self.reminder.stop()
            self.status.setText("Reminder paused.")
        else:
            self.start_reminder()
            self.status.setText("Reminder resumed.")

    def show_settings(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        # Closing the window keeps the tray app running.
        self.hide()
        event.ignore()

    def exit_app(self):
        self.reminder.stop()
        self.tray.hide()
        self.popup.close()
        self.close()
        self.destroy()
