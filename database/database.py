import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path="data/english_reminder.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                expression TEXT NOT NULL,
                ipa TEXT DEFAULT '',
                translation TEXT DEFAULT '',
                audio_path TEXT DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                show_count INTEGER NOT NULL DEFAULT 0,
                last_shown_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(topic_id, expression),
                FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS phrase_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase_id INTEGER NOT NULL,
                sentence TEXT NOT NULL,
                ipa TEXT DEFAULT '',
                translation TEXT DEFAULT '',
                audio_path TEXT DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                show_count INTEGER NOT NULL DEFAULT 0,
                last_shown_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(phrase_id, sentence),
                FOREIGN KEY(phrase_id) REFERENCES phrases(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS phrase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase_id INTEGER,
                example_id INTEGER,
                shown_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(phrase_id) REFERENCES phrases(id) ON DELETE CASCADE,
                FOREIGN KEY(example_id) REFERENCES phrase_examples(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """)

            defaults = {
                "reminder_interval_seconds": "60",
                "popup_duration_seconds": "10",
                "tts_voice": "en-US-JennyNeural",
                "tts_rate": "+0%",
                "sound_enabled": "1",
                "startup_enabled": "0",
                "selected_topics": ""
            }
            for key, value in defaults.items():
                conn.execute(
                    "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                    (key, value)
                )
            conn.commit()
