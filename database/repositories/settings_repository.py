class SettingsRepository:
    def __init__(self, db):
        self.db = db

    def get(self, key, default=None):
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key=?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set(self, key, value):
        with self.db.connect() as conn:
            conn.execute("""
                INSERT INTO settings(key,value) VALUES(?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))
            conn.commit()
