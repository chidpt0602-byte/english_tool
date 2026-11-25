import os
import sys
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None


class StartupService:
    APP_NAME = "EnglishReminder"

    @staticmethod
    def set_enabled(enabled):
        if winreg is None or os.name != "nt":
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            if getattr(sys, "frozen", False):
                command = f'"{sys.executable}"'
            else:
                project_dir = Path(__file__).resolve().parent.parent
                command = f'"{sys.executable}" "{project_dir / "app.py"}"'

            if enabled:
                winreg.SetValueEx(key, StartupService.APP_NAME, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, StartupService.APP_NAME)
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
            return True
        except OSError:
            return False
