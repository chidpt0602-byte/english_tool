import random
from datetime import datetime


class PhraseRepository:
    def __init__(self, db):
        self.db = db

    def add_phrase(self, topic_id, expression, ipa="", translation=""):
        with self.db.connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO phrases
                (topic_id, expression, ipa, translation)
                VALUES (?, ?, ?, ?)
            """, (topic_id, expression.strip(), ipa.strip(), translation.strip()))
            row = conn.execute("""
                SELECT * FROM phrases
                WHERE topic_id=? AND expression=?
            """, (topic_id, expression.strip())).fetchone()
            conn.commit()
            return row

    def add_example(self, phrase_id, sentence, ipa="", translation=""):
        with self.db.connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO phrase_examples
                (phrase_id, sentence, ipa, translation)
                VALUES (?, ?, ?, ?)
            """, (phrase_id, sentence.strip(), ipa.strip(), translation.strip()))
            row = conn.execute("""
                SELECT * FROM phrase_examples
                WHERE phrase_id=? AND sentence=?
            """, (phrase_id, sentence.strip())).fetchone()
            conn.commit()
            return row

    def list_phrases(self, topic_id=None, search=""):
        sql = """
            SELECT p.*, t.name AS topic_name
            FROM phrases p
            JOIN topics t ON t.id=p.topic_id
            WHERE 1=1
        """
        params = []
        if topic_id:
            sql += " AND p.topic_id=?"
            params.append(topic_id)
        if search:
            sql += " AND (p.expression LIKE ? OR p.translation LIKE ?)"
            q = f"%{search}%"
            params.extend([q, q])
        sql += " ORDER BY p.id DESC"
        with self.db.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def get_examples(self, phrase_id):
        with self.db.connect() as conn:
            return conn.execute(
                "SELECT * FROM phrase_examples WHERE phrase_id=? ORDER BY id",
                (phrase_id,)
            ).fetchall()

    def update_phrase(self, phrase_id, expression, ipa, translation):
        with self.db.connect() as conn:
            conn.execute("""
                UPDATE phrases
                SET expression=?, ipa=?, translation=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (expression.strip(), ipa.strip(), translation.strip(), phrase_id))
            conn.commit()

    def delete_phrase(self, phrase_id):
        with self.db.connect() as conn:
            conn.execute("DELETE FROM phrases WHERE id=?", (phrase_id,))
            conn.commit()

    def get_next_item(self, topic_ids=None):
        with self.db.connect() as conn:
            params = []
            where = "p.enabled=1"
            if topic_ids:
                marks = ",".join("?" * len(topic_ids))
                where += f" AND p.topic_id IN ({marks})"
                params.extend(topic_ids)

            rows = conn.execute(f"""
                SELECT p.*, t.name AS topic_name
                FROM phrases p
                JOIN topics t ON t.id=p.topic_id
                WHERE {where}
            """, params).fetchall()

            if not rows:
                return None

            # Prefer phrases not shown recently / never shown.
            unseen = [r for r in rows if r["show_count"] == 0]
            candidates = unseen if unseen else sorted(
                rows,
                key=lambda r: r["last_shown_at"] or ""
            )[:max(1, min(10, len(rows)))]

            phrase = random.choice(candidates)
            examples = conn.execute("""
                SELECT * FROM phrase_examples
                WHERE phrase_id=? AND enabled=1
                ORDER BY show_count ASC, COALESCE(last_shown_at, '')
            """, (phrase["id"],)).fetchall()

            # 50% chance to show an example when examples exist.
            if examples and random.random() < 0.5:
                example = random.choice(list(examples[:min(5, len(examples))]))
                return {"type": "example", "phrase": phrase, "item": example}

            return {"type": "phrase", "phrase": phrase, "item": phrase}

    def mark_shown(self, item):
        now = datetime.now().isoformat(timespec="seconds")
        phrase = item["phrase"]
        selected = item["item"]

        with self.db.connect() as conn:
            conn.execute("""
                UPDATE phrases
                SET show_count=show_count+1, last_shown_at=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (now, phrase["id"]))

            if item["type"] == "example":
                conn.execute("""
                    UPDATE phrase_examples
                    SET show_count=show_count+1, last_shown_at=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (now, selected["id"]))

            conn.execute("""
                INSERT INTO phrase_history(phrase_id, example_id, shown_at)
                VALUES (?, ?, ?)
            """, (
                phrase["id"],
                selected["id"] if item["type"] == "example" else None,
                now
            ))
            conn.commit()
