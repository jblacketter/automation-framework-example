"""
Configuration management using singleton pattern.

Provides centralized access to environment variables with type-safe getters
and validation for required configuration values.
"""

import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


class Config:
    """
    Singleton configuration manager.

    Loads environment variables from .env file and provides type-safe
    access methods with support for defaults and required values.

    Usage:
        config = Config()
        base_url = config.get_required("BASE_URL")
        timeout = config.get_int("TIMEOUT", default=30000)
    """

    _instance: Optional["Config"] = None
    _initialized: bool = False

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        # Load .env file from project root
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Try .env.example as fallback for CI/CD or first-time setup
            example_path = Path(__file__).parent.parent / ".env.example"
            if example_path.exists():
                load_dotenv(example_path)

        self._initialized = True

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value with optional default."""
        return os.getenv(key, default)

    def get_required(self, key: str) -> str:
        """
        Get a required configuration value.

        Raises:
            ConfigurationError: If the key is not set or empty.
        """
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(
                f"Required configuration '{key}' is not set. "
                f"Please add it to your .env file."
            )
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get a configuration value as integer."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a configuration value as boolean."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def get_list(self, key: str, separator: str = ",") -> list[str]:
        """Get a configuration value as a list of strings."""
        value = os.getenv(key)
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]

    # Convenience properties for common configuration values
    @property
    def base_url(self) -> str:
        """Base URL for the application under test."""
        return self.get("BASE_URL", "https://automationintesting.online")

    @property
    def api_base_url(self) -> str:
        """Base URL for API endpoints (Restful Booker API)."""
        return self.get("API_BASE_URL", "https://restful-booker.herokuapp.com")

    @property
    def browser(self) -> str:
        """Browser to use for UI tests (chromium, firefox, webkit)."""
        return self.get("BROWSER", "chromium")

    @property
    def headless(self) -> bool:
        """Whether to run browser in headless mode."""
        return self.get_bool("HEADLESS", default=True)

    @property
    def slow_mo(self) -> int:
        """Slow down browser actions by this many milliseconds."""
        return self.get_int("SLOW_MO", default=0)

    @property
    def default_timeout(self) -> int:
        """Default timeout for operations in milliseconds."""
        return self.get_int("DEFAULT_TIMEOUT", default=30000)

    @property
    def navigation_timeout(self) -> int:
        """Timeout for page navigation in milliseconds."""
        return self.get_int("NAVIGATION_TIMEOUT", default=60000)

    @property
    def viewport_width(self) -> int:
        """Browser viewport width."""
        return self.get_int("VIEWPORT_WIDTH", default=1920)

    @property
    def viewport_height(self) -> int:
        """Browser viewport height."""
        return self.get_int("VIEWPORT_HEIGHT", default=1080)

    @property
    def admin_username(self) -> str:
        """Admin username for authenticated tests."""
        return self.get("ADMIN_USERNAME", "admin")

    @property
    def admin_password(self) -> str:
        """Admin password for authenticated tests."""
        return self.get("ADMIN_PASSWORD", "password123")

    @property
    def screenshot_on_failure(self) -> bool:
        """Whether to capture screenshots on test failure."""
        return self.get_bool("SCREENSHOT_ON_FAILURE", default=True)

    @property
    def screenshot_dir(self) -> Path:
        """Directory for storing screenshots."""
        dir_path = Path(self.get("SCREENSHOT_DIR", "reports/screenshots"))
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @property
    def log_level(self) -> str:
        """Logging level."""
        return self.get("LOG_LEVEL", "INFO")

    @property
    def log_api_requests(self) -> bool:
        """Whether to log API requests."""
        return self.get_bool("LOG_API_REQUESTS", default=True)

    @property
    def log_api_responses(self) -> bool:
        """Whether to log API responses."""
        return self.get_bool("LOG_API_RESPONSES", default=True)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._initialized = False
