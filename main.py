"""
Oracle Fusion User Administration Tool
Entry point.
"""

from app.config import load_config
from app.utils.logger import configure_logging


def main() -> None:
    config = load_config()
    configure_logging(config.app.log_level)

    # Import here so CustomTkinter initialises after config/logging are ready
    from app.ui.app_window import AppWindow

    app = AppWindow(config)
    app.mainloop()


if __name__ == "__main__":
    main()
