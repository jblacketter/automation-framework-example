"""
Logging configuration for the test framework.

Provides a centralized logger with consistent formatting and
support for sensitive data masking.
"""

import logging
import re
import sys
from typing import Any, Optional

# Patterns for sensitive data that should be masked in logs
SENSITIVE_PATTERNS = [
    (re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE), '"password": "***"'),
    (re.compile(r'"token"\s*:\s*"[^"]*"', re.IGNORECASE), '"token": "***"'),
    (re.compile(r'"authorization"\s*:\s*"[^"]*"', re.IGNORECASE), '"authorization": "***"'),
    (re.compile(r'"cookie"\s*:\s*"[^"]*"', re.IGNORECASE), '"cookie": "***"'),
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***"),
]


class SensitiveDataFilter(logging.Filter):
    """Filter that masks sensitive data in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = mask_sensitive_data(record.msg)
        return True


def mask_sensitive_data(data: Any) -> str:
    """
    Mask sensitive data in strings for safe logging.

    Args:
        data: The data to mask (will be converted to string)

    Returns:
        String with sensitive values replaced with '***'
    """
    text = str(data)
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Uses a module-level logger to prevent duplicate handlers when
    the same module requests a logger multiple times.

    Args:
        name: Logger name (typically __name__)
        level: Log level override (default: from config or INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if none exist (prevents duplicates)
    if not logger.handlers:
        # Import here to avoid circular dependency
        from core.config import Config

        config = Config()
        log_level = level or config.log_level

        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Add sensitive data filter
        handler.addFilter(SensitiveDataFilter())

        logger.addHandler(handler)

        # Prevent propagation to root logger (avoids duplicate logs)
        logger.propagate = False

    return logger


# Module-level logger for this file
logger = get_logger(__name__)
