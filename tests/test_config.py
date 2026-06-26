"""Tests for configuration loading."""
from __future__ import annotations

import os

import pytest

from app.config import Settings, settings


class TestSettings:
    def test_default_fusion_url(self) -> None:
        """Default URL placeholder is present when env var is not set."""
        s = Settings()
        # Verify the default is a well-formed Fusion cloud URL placeholder
        assert s.fusion_base_url.startswith("https://") and s.fusion_base_url.endswith(".oraclecloud.com")

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """FUSION_BASE_URL env var overrides the default."""
        monkeypatch.setenv("FUSION_BASE_URL", "https://test.example.com")
        Settings.reload()
        assert settings.fusion_base_url == "https://test.example.com"
        # Cleanup
        monkeypatch.delenv("FUSION_BASE_URL", raising=False)
        Settings.reload()

    def test_log_level_default(self) -> None:
        assert settings.log_level.upper() in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def test_db_path_non_empty(self) -> None:
        assert settings.db_path
        assert "fusion_tool" in settings.db_path

    def test_reload_picks_up_new_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        Settings.reload()
        assert settings.log_level == "DEBUG"
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        Settings.reload()
