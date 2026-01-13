"""
Admin page object for the Restful Booker Platform.

Represents the admin login and dashboard pages for managing
rooms, bookings, and messages.
"""

from typing import Optional

from playwright.sync_api import Page

from pages.base_page import BasePage


class AdminPage(BasePage):
    """
    Page object for the Restful Booker Platform admin section.

    The admin section includes:
    - Login form
    - Room management
    - Booking management
    - Message inbox
    - Branding settings
    """

    # Login selectors
    LOGIN_USERNAME = "#username, input[name='username']"
    LOGIN_PASSWORD = "#password, input[name='password']"
    LOGIN_BUTTON = "#doLogin, button:has-text('Login')"
    LOGIN_ERROR = ".alert-danger, [data-testid='login-error']"
    LOGOUT_BUTTON = "a:has-text('Logout'), button:has-text('Logout')"

    # Navigation selectors
    NAV_ROOMS = "a:has-text('Rooms'), [data-testid='nav-rooms']"
    NAV_REPORT = "a:has-text('Report'), [data-testid='nav-report']"
    NAV_BRANDING = "a:has-text('Branding'), [data-testid='nav-branding']"
    NAV_MESSAGES = ".fa-inbox, [data-testid='nav-messages']"

    # Room management selectors
    ROOM_LISTING = ".room-details, [data-testid='roomlisting']"
    ROOM_NUMBER_INPUT = "#roomNumber, input[name='roomNumber']"
    ROOM_TYPE_SELECT = "#type, select[name='type']"
    ROOM_ACCESSIBLE_CHECKBOX = "#accessible, input[name='accessible']"
    ROOM_PRICE_INPUT = "#roomPrice, input[name='roomPrice']"
    ROOM_WIFI_CHECKBOX = "#wifiCheckbox, input[value='WiFi']"
    ROOM_TV_CHECKBOX = "#tvCheckbox, input[value='TV']"
    ROOM_RADIO_CHECKBOX = "#radioCheckbox, input[value='Radio']"
    ROOM_REFRESHMENTS_CHECKBOX = "#refreshCheckbox, input[value='Refreshments']"
    ROOM_SAFE_CHECKBOX = "#safeCheckbox, input[value='Safe']"
    ROOM_VIEWS_CHECKBOX = "#viewsCheckbox, input[value='Views']"
    CREATE_ROOM_BUTTON = "#createRoom, button:has-text('Create')"
    ROOM_DELETE_BUTTON = ".roomDelete, button[data-testid='roomDelete']"

    # Booking selectors
    BOOKING_ROW = ".booking-row, [data-testid='booking']"
    BOOKING_NAME = ".booking-name"
    BOOKING_DATES = ".booking-dates"
    BOOKING_DELETE = ".booking-delete, button:has-text('Delete')"

    # Message selectors
    MESSAGE_ROW = ".message-row, [data-testid='message']"
    MESSAGE_UNREAD_COUNT = ".badge, .notification-count"

    # Branding selectors
    BRANDING_NAME = "#name, input[name='name']"
    BRANDING_MAP = "#map, textarea[name='map']"
    BRANDING_LOGO = "#logoUrl, input[name='logoUrl']"
    BRANDING_DESCRIPTION = "#description, textarea[name='description']"
    BRANDING_CONTACT_NAME = "#contactName, input[name='contactName']"
    BRANDING_CONTACT_ADDRESS = "#contactAddress, input[name='contactAddress']"
    BRANDING_CONTACT_PHONE = "#contactPhone, input[name='contactPhone']"
    BRANDING_CONTACT_EMAIL = "#contactEmail, input[name='contactEmail']"
    BRANDING_SUBMIT = "#updateBranding, button:has-text('Submit')"

    @property
    def url_path(self) -> str:
        """Admin page URL path."""
        return "/#/admin"

    def login(self, username: str, password: str) -> "AdminPage":
        """
        Log in to the admin panel.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Logging in as: {username}")

        self.wait_for_element(self.LOGIN_USERNAME, state="visible")
        self.fill(self.LOGIN_USERNAME, username)
        self.fill(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

        # Wait for navigation or error
        self.page.wait_for_timeout(1000)  # Brief wait for response

        return self

    def login_as_admin(self) -> "AdminPage":
        """
        Log in using default admin credentials from config.

        Returns:
            Self for method chaining
        """
        return self.login(self.config.admin_username, self.config.admin_password)

    def logout(self) -> "AdminPage":
        """
        Log out from the admin panel.

        Returns:
            Self for method chaining
        """
        self.logger.info("Logging out")
        self.click(self.LOGOUT_BUTTON)
        return self

    def is_logged_in(self) -> bool:
        """
        Check if currently logged in to admin panel.

        Returns:
            True if logged in (logout button visible)
        """
        return self.is_visible(self.LOGOUT_BUTTON)

    def get_login_error(self) -> str:
        """
        Get the login error message if present.

        Returns:
            Error message text or empty string
        """
        if self.is_visible(self.LOGIN_ERROR):
            return self.get_text(self.LOGIN_ERROR)
        return ""

    # Room management methods

    def create_room(
        self,
        room_number: str,
        room_type: str = "Single",
        accessible: bool = False,
        price: str = "100",
        features: Optional[list[str]] = None,
    ) -> "AdminPage":
        """
        Create a new room.

        Args:
            room_number: Room number/name
            room_type: Type (Single, Twin, Double, Family, Suite)
            accessible: Whether room is accessible
            price: Price per night
            features: List of features (WiFi, TV, Radio, Refreshments, Safe, Views)

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Creating room: {room_number}")

        self.fill(self.ROOM_NUMBER_INPUT, room_number)
        self.select_option(self.ROOM_TYPE_SELECT, room_type)

        if accessible:
            self.check(self.ROOM_ACCESSIBLE_CHECKBOX)

        self.fill(self.ROOM_PRICE_INPUT, price)

        # Check feature checkboxes
        if features:
            feature_map = {
                "WiFi": self.ROOM_WIFI_CHECKBOX,
                "TV": self.ROOM_TV_CHECKBOX,
                "Radio": self.ROOM_RADIO_CHECKBOX,
                "Refreshments": self.ROOM_REFRESHMENTS_CHECKBOX,
                "Safe": self.ROOM_SAFE_CHECKBOX,
                "Views": self.ROOM_VIEWS_CHECKBOX,
            }
            for feature in features:
                if feature in feature_map:
                    self.check(feature_map[feature])

        self.click(self.CREATE_ROOM_BUTTON)
        return self

    def get_room_count(self) -> int:
        """
        Get the number of rooms in the listing.

        Returns:
            Count of room rows
        """
        return self.get_element_count(self.ROOM_LISTING)

    def delete_room(self, index: int = 0) -> "AdminPage":
        """
        Delete a room by index.

        Args:
            index: Zero-based index of room to delete

        Returns:
            Self for method chaining
        """
        self.logger.info(f"Deleting room at index: {index}")
        rooms = self.page.locator(self.ROOM_LISTING).all()
        if index < len(rooms):
            delete_button = rooms[index].locator(self.ROOM_DELETE_BUTTON)
            delete_button.click()
        return self

    # Navigation methods

    def navigate_to_rooms(self) -> "AdminPage":
        """Navigate to room management."""
        self.click(self.NAV_ROOMS)
        return self

    def navigate_to_report(self) -> "AdminPage":
        """Navigate to report page."""
        self.click(self.NAV_REPORT)
        return self

    def navigate_to_branding(self) -> "AdminPage":
        """Navigate to branding settings."""
        self.click(self.NAV_BRANDING)
        return self

    def navigate_to_messages(self) -> "AdminPage":
        """Navigate to message inbox."""
        self.click(self.NAV_MESSAGES)
        return self

    def get_unread_message_count(self) -> int:
        """
        Get the count of unread messages.

        Returns:
            Number of unread messages or 0
        """
        if self.is_visible(self.MESSAGE_UNREAD_COUNT):
            try:
                return int(self.get_text(self.MESSAGE_UNREAD_COUNT))
            except ValueError:
                return 0
        return 0

    # Branding methods

    def update_branding(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
    ) -> "AdminPage":
        """
        Update hotel branding settings.

        Args:
            name: Hotel name
            description: Hotel description
            contact_name: Contact name
            contact_phone: Contact phone
            contact_email: Contact email

        Returns:
            Self for method chaining
        """
        self.logger.info("Updating branding settings")

        if name:
            self.clear_and_fill(self.BRANDING_NAME, name)
        if description:
            self.clear_and_fill(self.BRANDING_DESCRIPTION, description)
        if contact_name:
            self.clear_and_fill(self.BRANDING_CONTACT_NAME, contact_name)
        if contact_phone:
            self.clear_and_fill(self.BRANDING_CONTACT_PHONE, contact_phone)
        if contact_email:
            self.clear_and_fill(self.BRANDING_CONTACT_EMAIL, contact_email)

        self.click(self.BRANDING_SUBMIT)
        return self

    # Assertion methods

    def assert_logged_in(self) -> None:
        """Assert that user is logged in."""
        assert self.is_logged_in(), "Expected to be logged in but logout button not visible"

    def assert_logged_out(self) -> None:
        """Assert that user is logged out."""
        assert not self.is_logged_in(), "Expected to be logged out but logout button is visible"

    def assert_login_error_displayed(self) -> None:
        """Assert that a login error is displayed."""
        self.assert_element_visible(self.LOGIN_ERROR)

    def assert_room_count(self, expected: int) -> None:
        """Assert the number of rooms displayed."""
        actual = self.get_room_count()
        assert actual == expected, f"Expected {expected} rooms, found {actual}"
