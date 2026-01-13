"""Page Object Model for UI testing."""

from pages.base_page import BasePage
from pages.home_page import HomePage
from pages.admin_page import AdminPage
from pages.booking_page import BookingPage

__all__ = [
    "BasePage",
    "HomePage",
    "AdminPage",
    "BookingPage",
]
