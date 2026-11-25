from PySide6.QtCore import QObject, QTimer, Signal


class ReminderManager(QObject):
    phrase_ready = Signal(object)

    def __init__(self, random_engine, phrase_repo):
        super().__init__()
        self.random_engine = random_engine
        self.phrase_repo = phrase_repo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        self.topic_ids = []

    def start(self, interval_seconds=60, topic_ids=None, immediate=False):
        self.topic_ids = topic_ids or []
        self.timer.stop()
        self.timer.start(max(1, int(interval_seconds)) * 1000)
        if immediate:
            self._on_timeout()

    def stop(self):
        self.timer.stop()

    def _on_timeout(self):
        item = self.random_engine.next(self.topic_ids)
        if item:
            self.phrase_repo.mark_shown(item)
            self.phrase_ready.emit(item)
