"""
Behave environment hooks.

This module contains hooks that run at various points during test execution:
- before_all/after_all: Run once per test session
- before_feature/after_feature: Run once per feature file
- before_scenario/after_scenario: Run once per scenario
- before_step/after_step: Run once per step

These hooks handle:
- Browser lifecycle management for UI tests
- API client initialization and cleanup
- Screenshot capture on failure
- Test data cleanup
"""

import os
import re
from datetime import datetime

from behave import fixture, use_fixture
from behave.model import Feature, Scenario, Step
from behave.runner import Context

from core.api_client import APIClient
from core.browser_factory import BrowserFactory
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


def before_all(context: Context) -> None:
    """
    Run once before all tests.

    Initializes:
    - Configuration
    - Logger
    - Report directories
    """
    logger.info("=" * 60)
    logger.info("STARTING TEST SUITE")
    logger.info("=" * 60)

    # Store config in context for access in tests
    context.config_obj = Config()

    # Create report directories
    context.config_obj.screenshot_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Base URL: {context.config_obj.base_url}")
    logger.info(f"Browser: {context.config_obj.browser}")
    logger.info(f"Headless: {context.config_obj.headless}")


def after_all(context: Context) -> None:
    """
    Run once after all tests.

    Cleans up any remaining resources.
    """
    logger.info("=" * 60)
    logger.info("TEST SUITE COMPLETE")
    logger.info("=" * 60)


def before_feature(context: Context, feature: Feature) -> None:
    """
    Run before each feature.

    For UI features:
    - Initializes browser (one browser per feature for efficiency)

    For API features:
    - Initializes API client
    """
    logger.info("-" * 60)
    logger.info(f"FEATURE: {feature.name}")
    logger.info("-" * 60)

    # Check if this is a UI feature
    if _is_ui_feature(feature):
        logger.info("Initializing browser for UI feature")
        browser_factory = BrowserFactory()
        browser_factory.initialize()
        context.browser_factory = browser_factory


def after_feature(context: Context, feature: Feature) -> None:
    """
    Run after each feature.

    Cleans up browser if it was initialized.
    """
    if hasattr(context, "browser_factory") and context.browser_factory:
        logger.info("Closing browser")
        context.browser_factory.close()
        context.browser_factory = None

    logger.info(f"Feature '{feature.name}' complete")


def before_scenario(context: Context, scenario: Scenario) -> None:
    """
    Run before each scenario.

    Initializes:
    - Fresh browser context/page for UI tests
    - Fresh API client state
    - Clean context attributes
    """
    logger.info(f"  SCENARIO: {scenario.name}")

    # Reset API client state
    client = APIClient()
    client.clear_token()
    client.clear_cookies()

    # Clear any previous response/validator
    context.response = None
    context.validator = None

    # Initialize test data cleanup list
    context.bookings_to_cleanup = []
    context.rooms_to_cleanup = []

    # For UI tests, create a new page
    if hasattr(context, "browser_factory") and context.browser_factory:
        context.page = context.browser_factory.new_page()


def after_scenario(context: Context, scenario: Scenario) -> None:
    """
    Run after each scenario.

    Handles:
    - Screenshot on failure
    - Test data cleanup
    - Page/context cleanup
    """
    # Capture screenshot on failure
    if scenario.status == "failed":
        _capture_failure_screenshot(context, scenario)
        _log_failure_details(context, scenario)

    # Cleanup test data (bookings, rooms, etc.)
    _cleanup_test_data(context)

    # Close page but keep browser for next scenario
    if hasattr(context, "browser_factory") and context.browser_factory:
        context.browser_factory.close_context()

    status_icon = "PASSED" if scenario.status == "passed" else "FAILED"
    logger.info(f"  Scenario {status_icon}: {scenario.name}")


def before_step(context: Context, step: Step) -> None:
    """
    Run before each step.

    Optional: Add step-level logging or timing.
    """
    pass  # Minimal overhead - logging happens in step implementations


def after_step(context: Context, step: Step) -> None:
    """
    Run after each step.

    Logs step failures with additional context.
    """
    if step.status == "failed":
        logger.error(f"    STEP FAILED: {step.keyword} {step.name}")
        if step.error_message:
            # Truncate long error messages
            error_msg = step.error_message[:500]
            logger.error(f"    Error: {error_msg}")


# Helper functions


def _is_ui_feature(feature: Feature) -> bool:
    """
    Determine if a feature requires browser automation.

    Checks for @ui tag or feature file location.
    """
    # Check for @ui tag
    if "ui" in feature.tags:
        return True

    # Check if feature file is in ui directory
    if feature.filename and "/ui/" in feature.filename:
        return True

    return False


def _capture_failure_screenshot(context: Context, scenario: Scenario) -> None:
    """Capture a screenshot on scenario failure."""
    if not hasattr(context, "browser_factory") or not context.browser_factory:
        return

    if not context.config_obj.screenshot_on_failure:
        return

    try:
        # Create a safe filename from scenario name
        safe_name = re.sub(r"[^\w\-]", "_", scenario.name)[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"failure_{safe_name}_{timestamp}"

        path = context.browser_factory.take_screenshot(screenshot_name)
        logger.info(f"Failure screenshot saved: {path}")
    except Exception as e:
        logger.warning(f"Failed to capture screenshot: {e}")


def _log_failure_details(context: Context, scenario: Scenario) -> None:
    """Log additional details on scenario failure for debugging."""
    logger.error(f"Scenario failed: {scenario.name}")

    # Log API response details if available
    if hasattr(context, "response") and context.response:
        logger.error(f"Last API response status: {context.response.status_code}")
        try:
            body = context.response.text[:500]
            logger.error(f"Response body: {body}")
        except Exception:
            pass

    # Log current URL for UI tests
    if hasattr(context, "page") and context.page:
        try:
            logger.error(f"Current URL: {context.page.url}")
        except Exception:
            pass


def _cleanup_test_data(context: Context) -> None:
    """Clean up any test data created during the scenario."""
    from services.auth_service import AuthService
    from services.booking_service import BookingService
    from services.room_service import RoomService

    # Clean up bookings
    if hasattr(context, "bookings_to_cleanup") and context.bookings_to_cleanup:
        logger.debug(f"Cleaning up {len(context.bookings_to_cleanup)} bookings")
        auth_service = AuthService()
        auth_service.login_as_admin()

        booking_service = BookingService()
        for booking_id in context.bookings_to_cleanup:
            try:
                booking_service.delete_booking(booking_id)
                logger.debug(f"Deleted booking: {booking_id}")
            except Exception as e:
                logger.warning(f"Failed to delete booking {booking_id}: {e}")

        context.bookings_to_cleanup = []

    # Clean up rooms
    if hasattr(context, "rooms_to_cleanup") and context.rooms_to_cleanup:
        logger.debug(f"Cleaning up {len(context.rooms_to_cleanup)} rooms")
        auth_service = AuthService()
        auth_service.login_as_admin()

        room_service = RoomService()
        for room_id in context.rooms_to_cleanup:
            try:
                room_service.delete_room(room_id)
                logger.debug(f"Deleted room: {room_id}")
            except Exception as e:
                logger.warning(f"Failed to delete room {room_id}: {e}")

        context.rooms_to_cleanup = []
