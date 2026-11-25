from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


class TrayIcon(QSystemTrayIcon):
    def __init__(self, window):
        super().__init__(window)
        self.setToolTip("English Reminder")

        menu = QMenu()
        show_action = QAction("Show Manager", self)
        show_action.triggered.connect(window.show)
        menu.addAction(show_action)

        next_action = QAction("Show Next Phrase", self)
        next_action.triggered.connect(window.show_next_phrase)
        menu.addAction(next_action)

        pause_action = QAction("Pause / Resume", self)
        pause_action.triggered.connect(window.toggle_reminder)
        menu.addAction(pause_action)

        menu.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(window.show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(window.exit_app)
        menu.addAction(exit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._activated)

    def _activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.parent().show()
            self.parent().raise_()
