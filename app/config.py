"""
Application configuration.

Reads settings from environment variables (populated via a .env file using
python-dotenv).  Never hard-code credentials here.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repository root (if present)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env", override=False)


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class Settings:
    """Central settings object; instantiated once as a module-level singleton."""

    # Oracle Fusion
    fusion_base_url: str = _get("FUSION_BASE_URL", "https://your-tenant.oraclecloud.com")

    # Local storage
    db_path: str = _get("DB_PATH", str(_ROOT / "fusion_tool.db"))

    # Logging
    log_level: str = _get("LOG_LEVEL", "INFO")

    @classmethod
    def reload(cls) -> None:
        """Re-read environment variables (useful in tests)."""
        load_dotenv(_ROOT / ".env", override=True)
        cls.fusion_base_url = _get("FUSION_BASE_URL", "https://your-tenant.oraclecloud.com")
        cls.db_path = _get("DB_PATH", str(_ROOT / "fusion_tool.db"))
        cls.log_level = _get("LOG_LEVEL", "INFO")


settings = Settings()


def configure_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
