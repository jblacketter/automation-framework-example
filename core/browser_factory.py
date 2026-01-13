"""
Browser factory for Playwright-based UI testing.

Provides centralized browser lifecycle management with support for
different browsers, headless mode, and viewport configuration.
"""

from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from core.config import Config
from core.logger import get_logger


class BrowserFactory:
    """
    Factory for creating and managing Playwright browser instances.

    Manages browser lifecycle at the feature level for efficiency,
    creating new contexts and pages for each scenario.

    Usage:
        factory = BrowserFactory()
        factory.initialize()  # Called in before_feature
        page = factory.new_page()  # Called in before_scenario
        factory.close()  # Called in after_feature
    """

    _instance: Optional["BrowserFactory"] = None

    def __new__(cls) -> "BrowserFactory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.config = Config()
        self.logger = get_logger(__name__)

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

        self._initialized = True

    @property
    def page(self) -> Optional[Page]:
        """Get the current page instance."""
        return self._page

    @property
    def context(self) -> Optional[BrowserContext]:
        """Get the current browser context."""
        return self._context

    def initialize(self) -> None:
        """
        Initialize Playwright and launch browser.

        Should be called in before_feature hook for efficiency.
        """
        if self._browser is not None:
            self.logger.debug("Browser already initialized")
            return

        self.logger.info(f"Initializing {self.config.browser} browser")

        self._playwright = sync_playwright().start()

        # Get the browser type based on configuration
        browser_type = getattr(self._playwright, self.config.browser)

        # Launch browser with configuration
        self._browser = browser_type.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo,
        )

        self.logger.info(
            f"Browser launched: {self.config.browser} "
            f"(headless={self.config.headless})"
        )

    def new_context(self) -> BrowserContext:
        """
        Create a new browser context.

        Each context has isolated cookies, localStorage, and session storage.

        Returns:
            New BrowserContext instance
        """
        if self._browser is None:
            raise RuntimeError("Browser not initialized. Call initialize() first.")

        # Close existing context if any
        if self._context:
            self._context.close()

        self._context = self._browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            ignore_https_errors=True,
        )

        # Set default timeout
        self._context.set_default_timeout(self.config.default_timeout)
        self._context.set_default_navigation_timeout(self.config.navigation_timeout)

        self.logger.debug("New browser context created")
        return self._context

    def new_page(self) -> Page:
        """
        Create a new page in the current context.

        Creates a new context if one doesn't exist.

        Returns:
            New Page instance
        """
        if self._context is None:
            self.new_context()

        # Close existing page if any
        if self._page:
            self._page.close()

        self._page = self._context.new_page()
        self.logger.debug("New page created")
        return self._page

    def take_screenshot(self, name: str) -> str:
        """
        Capture a screenshot of the current page.

        Args:
            name: Screenshot filename (without extension)

        Returns:
            Path to the saved screenshot
        """
        if self._page is None:
            self.logger.warning("Cannot take screenshot: no page available")
            return ""

        screenshot_path = self.config.screenshot_dir / f"{name}.png"
        self._page.screenshot(path=str(screenshot_path), full_page=True)
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    def close_page(self) -> None:
        """Close the current page."""
        if self._page:
            self._page.close()
            self._page = None
            self.logger.debug("Page closed")

    def close_context(self) -> None:
        """Close the current browser context."""
        if self._context:
            self._context.close()
            self._context = None
            self._page = None
            self.logger.debug("Browser context closed")

    def close(self) -> None:
        """
        Close browser and cleanup Playwright resources.

        Should be called in after_feature hook.
        """
        if self._context:
            self._context.close()
            self._context = None

        if self._browser:
            self._browser.close()
            self._browser = None
            self.logger.info("Browser closed")

        if self._playwright:
            self._playwright.stop()
            self._playwright = None
            self.logger.debug("Playwright stopped")

        self._page = None

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None
