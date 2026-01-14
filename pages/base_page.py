"""
Base page object with common functionality.

All page objects should inherit from this class to gain access to
common methods and ensure consistent patterns across the framework.
"""

from abc import ABC, abstractmethod
import time
from typing import Callable, Optional, TypeVar

from playwright.sync_api import Page, Locator, expect

from core.config import Config
from core.logger import get_logger

T = TypeVar("T")


class BasePage(ABC):
    """
    Abstract base class for all page objects.

    Provides common methods for navigation, element interaction,
    and assertions that all page objects can use.

    Attributes:
        page: Playwright Page instance
        config: Configuration singleton
        logger: Logger instance
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the page object.

        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.config = Config()
        self.logger = get_logger(self.__class__.__name__)

    @property
    @abstractmethod
    def url_path(self) -> str:
        """
        URL path for this page (relative to base URL).

        Must be implemented by subclasses.
        """
        pass

    @property
    def full_url(self) -> str:
        """Full URL for this page."""
        base = self.config.base_url.rstrip("/")
        path = self.url_path.lstrip("/")
        return f"{base}/{path}" if path else base

    def navigate(self) -> "BasePage":
        """
        Navigate to this page.

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Navigating to {self.full_url}")
        self.page.goto(self.full_url)
        self.wait_for_page_load()
        return self

    def wait_for_page_load(self) -> None:
        """Wait for the page to fully load."""
        self.page.wait_for_load_state("networkidle")

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.page.url

    # Element interaction methods

    def click(self, selector: str) -> None:
        """
        Click an element.

        Args:
            selector: CSS selector or text selector
        """
        self.logger.debug(f"Clicking: {selector}")
        self.page.click(selector)

    # Retry helpers for flaky interactions

    def retry_action(
        self,
        action: Callable[[], T],
        retries: int = 3,
        delay: float = 0.5,
        description: str = "action",
    ) -> T:
        """
        Execute an action with retry logic for transient failures.

        Useful for handling flaky UI interactions caused by timing issues,
        animations, or temporary element states.

        Args:
            action: Callable to execute (should raise on failure)
            retries: Maximum number of attempts (default: 3)
            delay: Delay between retries in seconds (default: 0.5)
            description: Description for logging purposes

        Returns:
            The result of the action if successful

        Raises:
            The last exception if all retries fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(retries):
            try:
                return action()
            except Exception as e:
                last_exception = e
                if attempt < retries - 1:
                    self.logger.warning(
                        f"{description} failed (attempt {attempt + 1}/{retries}): {e}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"{description} failed after {retries} attempts: {e}"
                    )

        raise last_exception  # type: ignore[misc]

    def retry_click(self, selector: str, retries: int = 3, delay: float = 0.5) -> None:
        """
        Click an element with retry logic for transient failures.

        Args:
            selector: CSS selector or text selector
            retries: Maximum number of attempts (default: 3)
            delay: Delay between retries in seconds (default: 0.5)
        """
        self.retry_action(
            action=lambda: self.page.click(selector),
            retries=retries,
            delay=delay,
            description=f"Click '{selector}'",
        )

    def retry_fill(
        self, selector: str, value: str, retries: int = 3, delay: float = 0.5
    ) -> None:
        """
        Fill an input with retry logic for transient failures.

        Args:
            selector: CSS selector
            value: Value to enter
            retries: Maximum number of attempts (default: 3)
            delay: Delay between retries in seconds (default: 0.5)
        """
        self.retry_action(
            action=lambda: self.page.fill(selector, value),
            retries=retries,
            delay=delay,
            description=f"Fill '{selector}'",
        )

    def fill(self, selector: str, value: str) -> None:
        """
        Fill a text input.

        Args:
            selector: CSS selector
            value: Value to enter
        """
        self.logger.debug(f"Filling '{selector}' with value")
        self.page.fill(selector, value)

    def clear_and_fill(self, selector: str, value: str) -> None:
        """
        Clear a field and fill with new value.

        Args:
            selector: CSS selector
            value: Value to enter
        """
        self.page.locator(selector).clear()
        self.page.fill(selector, value)

    def select_option(self, selector: str, value: str) -> None:
        """
        Select an option from a dropdown.

        Args:
            selector: CSS selector for select element
            value: Option value to select
        """
        self.logger.debug(f"Selecting '{value}' from '{selector}'")
        self.page.select_option(selector, value)

    def check(self, selector: str) -> None:
        """
        Check a checkbox.

        Args:
            selector: CSS selector
        """
        self.page.check(selector)

    def uncheck(self, selector: str) -> None:
        """
        Uncheck a checkbox.

        Args:
            selector: CSS selector
        """
        self.page.uncheck(selector)

    def get_text(self, selector: str) -> str:
        """
        Get text content of an element.

        Args:
            selector: CSS selector

        Returns:
            Element's text content
        """
        return self.page.text_content(selector) or ""

    def get_input_value(self, selector: str) -> str:
        """
        Get value of an input element.

        Args:
            selector: CSS selector

        Returns:
            Input element's value
        """
        return self.page.input_value(selector)

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get an attribute value from an element.

        Args:
            selector: CSS selector
            attribute: Attribute name

        Returns:
            Attribute value or None
        """
        return self.page.get_attribute(selector, attribute)

    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible.

        Args:
            selector: CSS selector
            timeout: Optional timeout in milliseconds

        Returns:
            True if element is visible
        """
        try:
            locator = self.page.locator(selector)
            if timeout:
                locator.wait_for(state="visible", timeout=timeout)
            return locator.is_visible()
        except Exception:
            return False

    def is_enabled(self, selector: str) -> bool:
        """
        Check if an element is enabled.

        Args:
            selector: CSS selector

        Returns:
            True if element is enabled
        """
        return self.page.is_enabled(selector)

    def wait_for_element(
        self, selector: str, state: str = "visible", timeout: Optional[int] = None
    ) -> Locator:
        """
        Wait for an element to reach a specific state.

        Args:
            selector: CSS selector
            state: State to wait for (visible, hidden, attached, detached)
            timeout: Optional timeout in milliseconds

        Returns:
            Locator for the element
        """
        locator = self.page.locator(selector)
        locator.wait_for(state=state, timeout=timeout)
        return locator

    def wait_for_text(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """
        Wait for an element to contain specific text.

        Args:
            selector: CSS selector
            text: Text to wait for
            timeout: Optional timeout in milliseconds
        """
        locator = self.page.locator(selector)
        expect(locator).to_contain_text(text, timeout=timeout)

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> None:
        """
        Wait for the URL to match a pattern.

        Args:
            url_pattern: URL pattern (can include wildcards)
            timeout: Optional timeout in milliseconds
        """
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def hover(self, selector: str) -> None:
        """
        Hover over an element.

        Args:
            selector: CSS selector
        """
        self.page.hover(selector)

    def scroll_to(self, selector: str) -> None:
        """
        Scroll an element into view.

        Args:
            selector: CSS selector
        """
        self.page.locator(selector).scroll_into_view_if_needed()

    def get_element_count(self, selector: str) -> int:
        """
        Get the count of elements matching a selector.

        Args:
            selector: CSS selector

        Returns:
            Number of matching elements
        """
        return self.page.locator(selector).count()

    def press_key(self, key: str) -> None:
        """
        Press a keyboard key.

        Args:
            key: Key to press (e.g., 'Enter', 'Tab', 'Escape')
        """
        self.page.keyboard.press(key)

    def take_screenshot(self, name: str) -> str:
        """
        Take a screenshot.

        Args:
            name: Screenshot filename (without extension)

        Returns:
            Path to saved screenshot
        """
        screenshot_path = self.config.screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        self.logger.info(f"Screenshot saved: {screenshot_path}")
        return str(screenshot_path)

    # Assertion helper methods

    def assert_url_contains(self, text: str) -> None:
        """Assert the current URL contains text."""
        expect(self.page).to_have_url(f"*{text}*")

    def assert_title_contains(self, text: str) -> None:
        """Assert the page title contains text."""
        expect(self.page).to_have_title(f"*{text}*")

    def assert_element_visible(self, selector: str) -> None:
        """Assert an element is visible."""
        expect(self.page.locator(selector)).to_be_visible()

    def assert_element_hidden(self, selector: str) -> None:
        """Assert an element is hidden."""
        expect(self.page.locator(selector)).to_be_hidden()

    def assert_element_text(self, selector: str, text: str) -> None:
        """Assert an element has specific text."""
        expect(self.page.locator(selector)).to_have_text(text)

    def assert_element_contains_text(self, selector: str, text: str) -> None:
        """Assert an element contains specific text."""
        expect(self.page.locator(selector)).to_contain_text(text)

    def assert_input_value(self, selector: str, value: str) -> None:
        """Assert an input has a specific value."""
        expect(self.page.locator(selector)).to_have_value(value)
