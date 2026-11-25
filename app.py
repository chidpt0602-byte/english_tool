import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from database.database import Database
from services.startup_service import StartupService
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("English Reminder")
    app.setQuitOnLastWindowClosed(False)

    db = Database()
    db.initialize()

    window = MainWindow(db)
    window.show()

    # Keep the app responsive and allow tray/background operation.
    QTimer.singleShot(0, window.start_background_services)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
