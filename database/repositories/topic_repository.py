class TopicRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self, enabled_only=False):
        sql = "SELECT * FROM topics"
        if enabled_only:
            sql += " WHERE enabled = 1"
        sql += " ORDER BY name"
        with self.db.connect() as conn:
            return conn.execute(sql).fetchall()

    def get_or_create(self, name):
        name = name.strip()
        if not name:
            raise ValueError("Topic name cannot be empty.")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO topics(name) VALUES (?)", (name,)
            )
            row = conn.execute(
                "SELECT * FROM topics WHERE name = ?", (name,)
            ).fetchone()
            conn.commit()
            return row

    def set_enabled(self, topic_id, enabled):
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE topics SET enabled=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (1 if enabled else 0, topic_id)
            )
            conn.commit()
