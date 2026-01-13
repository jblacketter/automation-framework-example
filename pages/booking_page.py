"""
Booking page object for the Restful Booker Platform.

Represents the booking calendar and form for making room reservations.
"""

from datetime import date, timedelta
from typing import Optional

from playwright.sync_api import Page

from pages.base_page import BasePage


class BookingPage(BasePage):
    """
    Page object for the room booking flow.

    Handles the booking calendar, date selection, and
    guest information form.
    """

    # Calendar selectors
    CALENDAR_CONTAINER = ".rbc-calendar, [data-testid='calendar']"
    CALENDAR_CELL = ".rbc-day-bg, .calendar-cell"
    CALENDAR_NEXT = ".rbc-btn-group button:last-child, button:has-text('>')"
    CALENDAR_PREV = ".rbc-btn-group button:first-child, button:has-text('<')"
    CALENDAR_TODAY = "button:has-text('Today')"
    CALENDAR_MONTH_LABEL = ".rbc-toolbar-label"

    # Booking form selectors
    BOOKING_FORM = ".booking-form, [data-testid='booking-form']"
    FIRSTNAME_INPUT = "input[name='firstname'], #firstname"
    LASTNAME_INPUT = "input[name='lastname'], #lastname"
    EMAIL_INPUT = "input[name='email'], #email"
    PHONE_INPUT = "input[name='phone'], #phone"
    BOOK_BUTTON = "button:has-text('Book'), .book-room"
    CANCEL_BUTTON = "button:has-text('Cancel')"

    # Confirmation selectors
    BOOKING_CONFIRMATION = ".confirmation, [data-testid='booking-confirmation']"
    BOOKING_SUCCESS = ".alert-success, .booking-success"
    BOOKING_ERROR = ".alert-danger, .booking-error"

    # Room info in booking context
    ROOM_NAME = ".room-name, h2"
    ROOM_PRICE = ".room-price"
    TOTAL_PRICE = ".total-price"

    @property
    def url_path(self) -> str:
        """Booking page doesn't have a direct URL - accessed via room booking."""
        return "/"

    def select_dates_by_drag(
        self,
        start_offset_days: int = 1,
        duration_days: int = 2,
    ) -> "BookingPage":
        """
        Select booking dates by dragging on the calendar.

        This simulates clicking and dragging to select a date range.

        Args:
            start_offset_days: Days from today for check-in
            duration_days: Number of nights

        Returns:
            Self for method chaining
        """
        self.logger.info(
            f"Selecting dates: {start_offset_days} days from now, {duration_days} nights"
        )

        # Wait for calendar to be visible
        self.wait_for_element(self.CALENDAR_CONTAINER, state="visible")

        # Calculate target dates
        check_in = date.today() + timedelta(days=start_offset_days)
        check_out = check_in + timedelta(days=duration_days)

        self.logger.debug(f"Check-in: {check_in}, Check-out: {check_out}")

        # Find and interact with calendar cells
        # The specific implementation depends on the calendar widget used
        calendar = self.page.locator(self.CALENDAR_CONTAINER)

        # Try to find date cells and drag between them
        cells = calendar.locator(self.CALENDAR_CELL).all()

        if len(cells) >= start_offset_days + duration_days:
            # Get the start and end cells
            start_cell = cells[start_offset_days]
            end_cell = cells[start_offset_days + duration_days - 1]

            # Perform drag operation
            start_cell.drag_to(end_cell)

        return self

    def navigate_to_next_month(self) -> "BookingPage":
        """
        Navigate to the next month in the calendar.

        Returns:
            Self for method chaining
        """
        self.click(self.CALENDAR_NEXT)
        self.page.wait_for_timeout(500)  # Wait for calendar animation
        return self

    def navigate_to_previous_month(self) -> "BookingPage":
        """
        Navigate to the previous month in the calendar.

        Returns:
            Self for method chaining
        """
        self.click(self.CALENDAR_PREV)
        self.page.wait_for_timeout(500)
        return self

    def get_current_month_label(self) -> str:
        """
        Get the current month label from the calendar.

        Returns:
            Month label text (e.g., "January 2024")
        """
        return self.get_text(self.CALENDAR_MONTH_LABEL)

    def fill_guest_details(
        self,
        firstname: str,
        lastname: str,
        email: str,
        phone: str,
    ) -> "BookingPage":
        """
        Fill in the guest details form.

        Args:
            firstname: Guest first name
            lastname: Guest last name
            email: Guest email
            phone: Guest phone number

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Filling guest details for: {firstname} {lastname}")

        self.wait_for_element(self.FIRSTNAME_INPUT, state="visible")
        self.fill(self.FIRSTNAME_INPUT, firstname)
        self.fill(self.LASTNAME_INPUT, lastname)
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.PHONE_INPUT, phone)

        return self

    def submit_booking(self) -> "BookingPage":
        """
        Submit the booking form.

        Returns:
            Self for method chaining
        """
        self.logger.info("Submitting booking")
        self.click(self.BOOK_BUTTON)
        return self

    def cancel_booking(self) -> "BookingPage":
        """
        Cancel the booking form.

        Returns:
            Self for method chaining
        """
        self.logger.info("Cancelling booking")
        self.click(self.CANCEL_BUTTON)
        return self

    def is_booking_successful(self, timeout: Optional[int] = None) -> bool:
        """
        Check if booking was successful.

        Args:
            timeout: Optional timeout in milliseconds

        Returns:
            True if success message is visible
        """
        return self.is_visible(self.BOOKING_SUCCESS, timeout=timeout)

    def get_booking_error(self) -> str:
        """
        Get the booking error message if present.

        Returns:
            Error message text or empty string
        """
        if self.is_visible(self.BOOKING_ERROR):
            return self.get_text(self.BOOKING_ERROR)
        return ""

    def get_room_name(self) -> str:
        """
        Get the name of the room being booked.

        Returns:
            Room name text
        """
        return self.get_text(self.ROOM_NAME)

    def get_total_price(self) -> str:
        """
        Get the total price for the booking.

        Returns:
            Total price text
        """
        if self.is_visible(self.TOTAL_PRICE):
            return self.get_text(self.TOTAL_PRICE)
        return ""

    def is_calendar_visible(self) -> bool:
        """
        Check if the booking calendar is visible.

        Returns:
            True if calendar is visible
        """
        return self.is_visible(self.CALENDAR_CONTAINER)

    def is_booking_form_visible(self) -> bool:
        """
        Check if the booking form is visible.

        Returns:
            True if booking form is visible
        """
        return self.is_visible(self.FIRSTNAME_INPUT)

    def wait_for_calendar(self, timeout: Optional[int] = None) -> None:
        """
        Wait for the calendar to be visible.

        Args:
            timeout: Optional timeout in milliseconds
        """
        self.wait_for_element(self.CALENDAR_CONTAINER, state="visible", timeout=timeout)

    def wait_for_booking_form(self, timeout: Optional[int] = None) -> None:
        """
        Wait for the booking form to be visible.

        Args:
            timeout: Optional timeout in milliseconds
        """
        self.wait_for_element(self.FIRSTNAME_INPUT, state="visible", timeout=timeout)

    # Assertion methods

    def assert_calendar_visible(self) -> None:
        """Assert that the booking calendar is visible."""
        self.assert_element_visible(self.CALENDAR_CONTAINER)

    def assert_booking_form_visible(self) -> None:
        """Assert that the booking form is visible."""
        self.assert_element_visible(self.FIRSTNAME_INPUT)

    def assert_booking_successful(self) -> None:
        """Assert that the booking was successful."""
        assert self.is_booking_successful(timeout=5000), "Booking was not successful"

    def assert_booking_error_displayed(self) -> None:
        """Assert that a booking error is displayed."""
        self.assert_element_visible(self.BOOKING_ERROR)
