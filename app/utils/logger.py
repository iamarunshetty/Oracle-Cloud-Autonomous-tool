"""
Structured logger with secret masking.
"""

import logging
import re
import sys

_SENSITIVE_PATTERNS = [
    (re.compile(r'("password"\s*:\s*")([^"]+)(")', re.IGNORECASE), r"\1***\3"),
    (re.compile(r'("token"\s*:\s*")([^"]+)(")', re.IGNORECASE), r"\1***\3"),
    (re.compile(r'(Authorization:\s*\S+\s+)\S+', re.IGNORECASE), r"\1***"),
    (re.compile(r'("username"\s*:\s*")([^"]+)(")', re.IGNORECASE), r"\1***\3"),
]


class _MaskingFormatter(logging.Formatter):
    """Formatter that masks sensitive values before writing."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in _SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        return message


def get_logger(name: str = "oracle_fusion_tool") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            _MaskingFormatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    return logger


def configure_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger("oracle_fusion_tool").setLevel(numeric)
