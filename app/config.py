"""
Configuration management.
Reads from environment variables (and an optional .env file) or config.json.
Sensitive values are never logged.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent

# Load .env if present (does NOT override existing env vars)
load_dotenv(_ROOT / ".env", override=False)


@dataclass
class OracleConfig:
    base_url: str = ""
    username: str = ""
    password: str = ""
    token: str = ""
    timeout: int = 30
    retry_count: int = 3


@dataclass
class AppConfig:
    log_level: str = "INFO"
    audit_file: str = str(_ROOT / "audit_log.csv")


@dataclass
class Config:
    oracle: OracleConfig = field(default_factory=OracleConfig)
    app: AppConfig = field(default_factory=AppConfig)


def _load_json_config() -> dict:
    """Load optional config.json from repository root."""
    config_path = _ROOT / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def load_config() -> Config:
    """Build Config from environment variables, falling back to config.json."""
    json_cfg = _load_json_config()
    oracle_json = json_cfg.get("oracle", {})
    app_json = json_cfg.get("app", {})

    oracle = OracleConfig(
        base_url=os.getenv("ORACLE_BASE_URL", oracle_json.get("base_url", "")),
        username=os.getenv("ORACLE_USERNAME", oracle_json.get("username", "")),
        password=os.getenv("ORACLE_PASSWORD", oracle_json.get("password", "")),
        token=os.getenv("ORACLE_TOKEN", oracle_json.get("token", "")),
        timeout=int(os.getenv("ORACLE_REQUEST_TIMEOUT", oracle_json.get("timeout", 30))),
        retry_count=int(os.getenv("ORACLE_RETRY_COUNT", oracle_json.get("retry_count", 3))),
    )

    app = AppConfig(
        log_level=os.getenv("APP_LOG_LEVEL", app_json.get("log_level", "INFO")),
        audit_file=os.getenv(
            "APP_AUDIT_FILE",
            app_json.get("audit_file", str(_ROOT / "audit_log.csv")),
        ),
    )

    return Config(oracle=oracle, app=app)
