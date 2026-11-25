from pathlib import Path


class ImportService:
    def __init__(self, topic_repo, phrase_repo):
        self.topic_repo = topic_repo
        self.phrase_repo = phrase_repo

    def import_txt(self, file_path):
        current_topic = None
        imported = 0
        skipped = 0
        invalid = 0

        lines = Path(file_path).read_text(encoding="utf-8-sig").splitlines()

        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current_topic = self.topic_repo.get_or_create(
                    line[1:-1].strip()
                )
                continue

            if current_topic is None:
                invalid += 1
                continue

            is_example = line.startswith(">")
            if is_example:
                line = line[1:].strip()

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                invalid += 1
                continue

            english, ipa, vietnamese = parts[:3]

            if is_example:
                # The example belongs to the most recently imported phrase.
                if "phrase_row" not in locals():
                    invalid += 1
                    continue
                before = self.phrase_repo.get_examples(phrase_row["id"])
                self.phrase_repo.add_example(
                    phrase_row["id"], english, ipa, vietnamese
                )
                after = self.phrase_repo.get_examples(phrase_row["id"])
                if len(after) > len(before):
                    imported += 1
                else:
                    skipped += 1
            else:
                before = self.phrase_repo.list_phrases(
                    topic_id=current_topic["id"], search=english
                )
                phrase_row = self.phrase_repo.add_phrase(
                    current_topic["id"], english, ipa, vietnamese
                )
                if len(before) == 0:
                    imported += 1
                else:
                    skipped += 1

        return {
            "imported": imported,
            "skipped": skipped,
            "invalid": invalid,
        }
