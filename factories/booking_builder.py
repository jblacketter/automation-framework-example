"""
Booking data builder for test scenarios.
"""

import random
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

from faker import Faker

from factories.guest_builder import Guest, GuestBuilder


@dataclass
class Booking:
    """Booking data object."""

    guest: Guest
    check_in: date
    check_out: date
    total_price: int
    deposit_paid: bool
    additional_needs: Optional[str] = None

    @property
    def nights(self) -> int:
        """Calculate number of nights."""
        return (self.check_out - self.check_in).days

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload format."""
        payload: dict[str, Any] = {
            "firstname": self.guest.firstname,
            "lastname": self.guest.lastname,
            "totalprice": self.total_price,
            "depositpaid": self.deposit_paid,
            "bookingdates": {
                "checkin": self.check_in.isoformat(),
                "checkout": self.check_out.isoformat(),
            },
        }
        if self.additional_needs:
            payload["additionalneeds"] = self.additional_needs
        return payload


class BookingBuilder:
    """
    Builder for creating Booking test data.

    Usage:
        # Basic booking with defaults (7 days from now, 2 nights)
        booking = BookingBuilder().build()

        # Weekend getaway booking
        booking = (
            BookingBuilder()
            .for_guest(GuestBuilder().with_name("John", "Doe").build())
            .for_weekend()
            .with_breakfast()
            .build()
        )

        # Specific dates
        booking = (
            BookingBuilder()
            .checking_in(date(2024, 6, 15))
            .checking_out(date(2024, 6, 18))
            .with_price(450)
            .build()
        )

        # Long stay with deposit
        booking = (
            BookingBuilder()
            .for_nights(14)
            .starting_in_days(30)
            .with_deposit()
            .build()
        )
    """

    ADDITIONAL_NEEDS_OPTIONS = [
        "Breakfast",
        "Late checkout",
        "Airport pickup",
        "Extra towels",
        "Crib for baby",
        "Pet-friendly room",
        None,
    ]

    def __init__(self) -> None:
        """Initialize the builder with sensible defaults."""
        self._fake = Faker()
        self._guest: Optional[Guest] = None
        self._check_in: Optional[date] = None
        self._check_out: Optional[date] = None
        self._days_from_now: int = 7
        self._nights: int = 2
        self._total_price: Optional[int] = None
        self._deposit_paid: bool = False
        self._additional_needs: Optional[str] = None

    # Guest configuration

    def for_guest(self, guest: Guest) -> "BookingBuilder":
        """Set a specific guest for the booking."""
        self._guest = guest
        return self

    def with_random_guest(self) -> "BookingBuilder":
        """Generate a random guest (this is the default behavior)."""
        self._guest = None
        return self

    # Date configuration

    def checking_in(self, check_in: date) -> "BookingBuilder":
        """Set specific check-in date."""
        self._check_in = check_in
        return self

    def checking_out(self, check_out: date) -> "BookingBuilder":
        """Set specific check-out date."""
        self._check_out = check_out
        return self

    def starting_in_days(self, days: int) -> "BookingBuilder":
        """Set check-in to N days from today."""
        self._days_from_now = days
        self._check_in = None  # Clear explicit date
        return self

    def for_nights(self, nights: int) -> "BookingBuilder":
        """Set duration in nights."""
        self._nights = nights
        self._check_out = None  # Clear explicit date
        return self

    def for_weekend(self) -> "BookingBuilder":
        """Configure a weekend stay (Friday to Sunday)."""
        # Find next Friday
        today = date.today()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        self._check_in = today + timedelta(days=days_until_friday)
        self._check_out = self._check_in + timedelta(days=2)
        return self

    def for_next_week(self) -> "BookingBuilder":
        """Configure a week-long stay starting next Monday."""
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        self._check_in = today + timedelta(days=days_until_monday)
        self._check_out = self._check_in + timedelta(days=7)
        return self

    # Price configuration

    def with_price(self, price: int) -> "BookingBuilder":
        """Set specific total price."""
        self._total_price = price
        return self

    def with_random_price(self, min_price: int = 100, max_price: int = 500) -> "BookingBuilder":
        """Set random price within range."""
        self._total_price = random.randint(min_price, max_price)
        return self

    # Deposit configuration

    def with_deposit(self) -> "BookingBuilder":
        """Mark deposit as paid."""
        self._deposit_paid = True
        return self

    def without_deposit(self) -> "BookingBuilder":
        """Mark deposit as not paid."""
        self._deposit_paid = False
        return self

    # Additional needs configuration

    def with_additional_needs(self, needs: str) -> "BookingBuilder":
        """Set specific additional needs."""
        self._additional_needs = needs
        return self

    def with_breakfast(self) -> "BookingBuilder":
        """Add breakfast to booking."""
        self._additional_needs = "Breakfast"
        return self

    def with_late_checkout(self) -> "BookingBuilder":
        """Add late checkout to booking."""
        self._additional_needs = "Late checkout"
        return self

    def with_random_extras(self) -> "BookingBuilder":
        """Add random additional needs."""
        self._additional_needs = random.choice(self.ADDITIONAL_NEEDS_OPTIONS)
        return self

    # Build methods

    def build(self) -> Booking:
        """Build and return the Booking object."""
        # Determine guest
        guest = self._guest or GuestBuilder().build()

        # Determine dates
        if self._check_in:
            check_in = self._check_in
        else:
            check_in = date.today() + timedelta(days=self._days_from_now)

        if self._check_out:
            check_out = self._check_out
        else:
            check_out = check_in + timedelta(days=self._nights)

        # Determine price
        if self._total_price is not None:
            total_price = self._total_price
        else:
            nights = (check_out - check_in).days
            total_price = nights * random.randint(80, 150)

        return Booking(
            guest=guest,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            deposit_paid=self._deposit_paid,
            additional_needs=self._additional_needs,
        )

    def build_many(self, count: int) -> list[Booking]:
        """Build multiple Booking objects with varied data."""
        bookings = []
        for i in range(count):
            # Stagger check-in dates to avoid conflicts
            booking = (
                BookingBuilder()
                .starting_in_days(self._days_from_now + (i * 3))
                .for_nights(self._nights)
                .with_random_extras()
                .build()
            )
            bookings.append(booking)
        return bookings

    def reset(self) -> "BookingBuilder":
        """Reset builder to initial state."""
        self._guest = None
        self._check_in = None
        self._check_out = None
        self._days_from_now = 7
        self._nights = 2
        self._total_price = None
        self._deposit_paid = False
        self._additional_needs = None
        return self
