class RandomEngine:
    def __init__(self, phrase_repo):
        self.phrase_repo = phrase_repo

    def next(self, topic_ids=None):
        return self.phrase_repo.get_next_item(topic_ids)
