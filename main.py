"""
Oracle Fusion Access Manager – desktop entry point.

Usage:
    python main.py

Build exe:
    pyinstaller FusionAccessManager.spec
"""
from __future__ import annotations

import sys

from app.config import configure_logging, settings
from app.storage.database import db


def main() -> None:
    configure_logging()

    # Initialise database
    db.connect()

    # Launch PySide6 application
    try:
        from PySide6.QtWidgets import QApplication

        from app.ui.main_window import MainWindow
    except ImportError as exc:
        sys.exit(
            f"PySide6 is required. Install it with: pip install PySide6\n{exc}"
        )

    app = QApplication(sys.argv)
    app.setApplicationName("Oracle Fusion Access Manager")
    app.setOrganizationName("FusionAccessManager")

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
