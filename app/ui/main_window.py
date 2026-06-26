"""
Main application window.

Layout:
  - MenuBar (File / Help)
  - QTabWidget with 7 tabs
  - Operation-log panel
  - Status bar
"""
from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.tabs.audit_reporting import AuditReportingTab
from app.ui.tabs.data_access import DataAccessTab
from app.ui.tabs.job_monitor import JobMonitorTab
from app.ui.tabs.password_management import PasswordManagementTab
from app.ui.tabs.role_management import RoleManagementTab
from app.ui.tabs.security_analysis import SecurityAnalysisTab
from app.ui.tabs.user_management import UserManagementTab
from app.ui.widgets.operation_log import OperationLogPanel

logger = logging.getLogger(__name__)

APP_TITLE = "Oracle Fusion Access Manager"
APP_VERSION = "0.1.0"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE}  v{APP_VERSION}")
        self.resize(1280, 800)
        self._build_ui()
        self._build_menu()
        self._status("Ready")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(4)

        # Operation-log panel (shared by all tabs)
        self._log_panel = OperationLogPanel()

        def _log(msg: str) -> None:
            ts = datetime.now().strftime("%H:%M:%S")
            self._log_panel.append(f"[{ts}] {msg}")
            self._status(msg)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.addTab(UserManagementTab(log_fn=_log), "👤  User Management")
        self._tabs.addTab(RoleManagementTab(log_fn=_log), "🔑  Role Management")
        self._tabs.addTab(DataAccessTab(log_fn=_log), "🔒  Data Access")
        self._tabs.addTab(PasswordManagementTab(log_fn=_log), "🔐  Password")
        self._tabs.addTab(SecurityAnalysisTab(log_fn=_log), "🛡  Security Analysis")
        self._tabs.addTab(AuditReportingTab(log_fn=_log), "📊  Audit & Reporting")
        self._tabs.addTab(JobMonitorTab(log_fn=_log), "⚙  Job Monitor")

        root_layout.addWidget(self._tabs, stretch=1)
        root_layout.addWidget(self._log_panel)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _status(self, message: str) -> None:
        self._status_bar.showMessage(message, 8000)

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_TITLE}",
            f"<b>{APP_TITLE}</b><br>Version {APP_VERSION}<br><br>"
            "A Windows desktop tool for Oracle Fusion access administration.<br><br>"
            "<i>External API integration points are currently stubbed.</i>",
        )
