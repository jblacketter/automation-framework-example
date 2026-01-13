"""
Home page object for the Restful Booker Platform.

Represents the main landing page with hotel information,
room listings, and contact form.
"""

from typing import Optional

from playwright.sync_api import Page

from pages.base_page import BasePage


class HomePage(BasePage):
    """
    Page object for the Restful Booker Platform home page.

    The home page displays:
    - Hotel branding and description
    - Available rooms with details
    - Contact form for inquiries
    - Map location
    """

    # Selectors
    HOTEL_NAME = ".hotel-name, h1"
    HOTEL_DESCRIPTION = ".hotel-description, .lead"

    # Room selectors
    ROOM_CARD = ".hotel-room-info, .room-card, [data-testid='room']"
    ROOM_NAME = ".room-name, h3"
    ROOM_TYPE = ".room-type"
    ROOM_FEATURES = ".room-features, .roomFeatures"
    ROOM_IMAGE = ".hotel-img, .room-image img"
    BOOK_ROOM_BUTTON = "button.btn-outline-primary, button:has-text('Book this room')"

    # Contact form selectors
    CONTACT_NAME = "#name, input[name='name']"
    CONTACT_EMAIL = "#email, input[name='email']"
    CONTACT_PHONE = "#phone, input[name='phone']"
    CONTACT_SUBJECT = "#subject, input[name='subject']"
    CONTACT_MESSAGE = "#description, textarea[name='description'], textarea[name='message']"
    CONTACT_SUBMIT = "#submitContact, button:has-text('Submit')"
    CONTACT_SUCCESS = ".contact-success, [data-testid='contact-success']"
    CONTACT_ERROR = ".alert-danger, .error-message"

    # Footer/info selectors
    HOTEL_ADDRESS = ".hotel-address, address"
    HOTEL_PHONE = ".hotel-phone"
    HOTEL_EMAIL = ".hotel-email"

    @property
    def url_path(self) -> str:
        """Home page URL path."""
        return "/"

    def get_hotel_name(self) -> str:
        """
        Get the hotel name from the page.

        Returns:
            Hotel name text
        """
        return self.get_text(self.HOTEL_NAME)

    def get_hotel_description(self) -> str:
        """
        Get the hotel description.

        Returns:
            Hotel description text
        """
        return self.get_text(self.HOTEL_DESCRIPTION)

    def get_room_count(self) -> int:
        """
        Get the number of rooms displayed.

        Returns:
            Count of room cards
        """
        return self.get_element_count(self.ROOM_CARD)

    def get_room_names(self) -> list[str]:
        """
        Get names of all displayed rooms.

        Returns:
            List of room names
        """
        rooms = self.page.locator(self.ROOM_CARD).all()
        names = []
        for room in rooms:
            name_element = room.locator(self.ROOM_NAME)
            if name_element.count() > 0:
                names.append(name_element.text_content() or "")
        return names

    def click_book_room(self, room_index: int = 0) -> None:
        """
        Click the Book Room button for a specific room.

        Args:
            room_index: Zero-based index of the room to book
        """
        self.logger.info(f"Clicking Book Room button for room {room_index}")
        rooms = self.page.locator(self.ROOM_CARD).all()
        if room_index < len(rooms):
            book_button = rooms[room_index].locator(self.BOOK_ROOM_BUTTON)
            book_button.click()
        else:
            raise IndexError(f"Room index {room_index} out of range. Found {len(rooms)} rooms.")

    def fill_contact_form(
        self,
        name: str,
        email: str,
        phone: str,
        subject: str,
        message: str,
    ) -> "HomePage":
        """
        Fill out the contact form.

        Args:
            name: Contact name
            email: Contact email
            phone: Contact phone number
            subject: Message subject
            message: Message content

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Filling contact form for: {name}")

        self.scroll_to(self.CONTACT_NAME)
        self.fill(self.CONTACT_NAME, name)
        self.fill(self.CONTACT_EMAIL, email)
        self.fill(self.CONTACT_PHONE, phone)
        self.fill(self.CONTACT_SUBJECT, subject)
        self.fill(self.CONTACT_MESSAGE, message)

        return self

    def submit_contact_form(self) -> "HomePage":
        """
        Submit the contact form.

        Returns:
            Self for method chaining
        """
        self.logger.info("Submitting contact form")
        self.click(self.CONTACT_SUBMIT)
        return self

    def is_contact_success_visible(self, timeout: Optional[int] = None) -> bool:
        """
        Check if the contact success message is visible.

        Args:
            timeout: Optional timeout in milliseconds

        Returns:
            True if success message is visible
        """
        return self.is_visible(self.CONTACT_SUCCESS, timeout=timeout)

    def get_contact_error_message(self) -> str:
        """
        Get the contact form error message if present.

        Returns:
            Error message text or empty string
        """
        if self.is_visible(self.CONTACT_ERROR):
            return self.get_text(self.CONTACT_ERROR)
        return ""

    def wait_for_rooms_to_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for room cards to be visible.

        Args:
            timeout: Optional timeout in milliseconds
        """
        self.wait_for_element(self.ROOM_CARD, state="visible", timeout=timeout)

    def is_room_available(self, room_index: int = 0) -> bool:
        """
        Check if a room has a Book button (indicating availability).

        Args:
            room_index: Zero-based index of the room

        Returns:
            True if room has Book button
        """
        rooms = self.page.locator(self.ROOM_CARD).all()
        if room_index < len(rooms):
            return rooms[room_index].locator(self.BOOK_ROOM_BUTTON).count() > 0
        return False

    # Assertion methods

    def assert_hotel_name_displayed(self) -> None:
        """Assert that the hotel name is visible."""
        self.assert_element_visible(self.HOTEL_NAME)

    def assert_rooms_displayed(self, min_count: int = 1) -> None:
        """
        Assert that rooms are displayed.

        Args:
            min_count: Minimum expected number of rooms
        """
        count = self.get_room_count()
        assert count >= min_count, f"Expected at least {min_count} rooms, found {count}"

    def assert_contact_form_visible(self) -> None:
        """Assert that the contact form is visible."""
        self.assert_element_visible(self.CONTACT_NAME)
        self.assert_element_visible(self.CONTACT_EMAIL)
        self.assert_element_visible(self.CONTACT_SUBMIT)
