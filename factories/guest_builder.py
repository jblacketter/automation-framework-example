"""
Guest data builder for test scenarios.

Cleanup-signal naming convention (from docs/northstar-patterns.md P10):
generated guest lastnames carry a recognizable prefix — `Automated-<5 digits>` —
so a real backend's cleanup script can sweep automation-created records by
regex (`^Automated-\\d{5}$`, case-insensitive). This pattern is a **signal**,
not a unique ID — pair it with per-run ID tracking (e.g. a
`context.cleanup_<entity>_ids` list on Behave's `context`) when you also
need targeted teardown for the specific records a single run produced.

The two public demo targets this framework points at
(`automationintesting.online`, `restful-booker.herokuapp.com`) don't
actually need cleanup; this pattern is shown for portability to real
backends where test-data accumulation is a real problem. Callers who
need truly realistic names can still override via `.with_lastname(...)`.
"""

import random
from dataclasses import dataclass, field
from typing import Optional

from faker import Faker

_AUTO_LASTNAME_PREFIX = "Automated-"


def _cleanup_signal_lastname() -> str:
    """Generate a cleanup-recognizable lastname: `Automated-<5 digits>`."""
    return f"{_AUTO_LASTNAME_PREFIX}{random.randint(10000, 99999)}"


@dataclass
class Guest:
    """Guest data object."""

    firstname: str
    lastname: str
    email: Optional[str] = None
    phone: Optional[str] = None

    def full_name(self) -> str:
        """Return the guest's full name."""
        return f"{self.firstname} {self.lastname}"


class GuestBuilder:
    """
    Builder for creating Guest test data.

    Usage:
        # Basic guest with random data
        guest = GuestBuilder().build()

        # Customized guest
        guest = (
            GuestBuilder()
            .with_name("John", "Doe")
            .with_email("john@example.com")
            .build()
        )

        # Multiple guests
        guests = GuestBuilder().build_many(5)
    """

    def __init__(self, locale: str = "en_US") -> None:
        """
        Initialize the builder.

        Args:
            locale: Faker locale for generating data (default: en_US)
        """
        self._fake = Faker(locale)
        self._firstname: Optional[str] = None
        self._lastname: Optional[str] = None
        self._email: Optional[str] = None
        self._phone: Optional[str] = None

    def with_name(self, firstname: str, lastname: str) -> "GuestBuilder":
        """Set specific first and last name."""
        self._firstname = firstname
        self._lastname = lastname
        return self

    def with_firstname(self, firstname: str) -> "GuestBuilder":
        """Set specific first name."""
        self._firstname = firstname
        return self

    def with_lastname(self, lastname: str) -> "GuestBuilder":
        """Set specific last name."""
        self._lastname = lastname
        return self

    def with_email(self, email: str) -> "GuestBuilder":
        """Set specific email address."""
        self._email = email
        return self

    def with_phone(self, phone: str) -> "GuestBuilder":
        """Set specific phone number."""
        self._phone = phone
        return self

    def with_contact_info(self) -> "GuestBuilder":
        """Generate random email and phone."""
        self._email = self._fake.email()
        self._phone = self._fake.phone_number()
        return self

    def build(self) -> Guest:
        """Build and return the Guest object.

        When no explicit lastname was set via `with_name` / `with_lastname`,
        the builder produces a cleanup-signal lastname (`Automated-XXXXX`)
        instead of a raw Faker lastname — see the module docstring.
        """
        return Guest(
            firstname=self._firstname or self._fake.first_name(),
            lastname=self._lastname or _cleanup_signal_lastname(),
            email=self._email,
            phone=self._phone,
        )

    def build_many(self, count: int) -> list[Guest]:
        """Build multiple Guest objects with random data."""
        return [GuestBuilder(self._fake.locales[0]).build() for _ in range(count)]

    def reset(self) -> "GuestBuilder":
        """Reset builder to initial state."""
        self._firstname = None
        self._lastname = None
        self._email = None
        self._phone = None
        return self
