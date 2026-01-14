"""
Room data builder for test scenarios.
"""

import random
from dataclasses import dataclass, field
from typing import Any, Optional

from faker import Faker


@dataclass
class Room:
    """Room data object."""

    room_name: str
    room_type: str
    accessible: bool
    price: int
    features: list[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to API request payload format."""
        payload: dict[str, Any] = {
            "roomName": self.room_name,
            "type": self.room_type,
            "accessible": self.accessible,
            "roomPrice": self.price,
            "features": self.features,
        }
        if self.description:
            payload["description"] = self.description
        return payload


class RoomBuilder:
    """
    Builder for creating Room test data.

    Usage:
        # Basic room with defaults
        room = RoomBuilder().build()

        # Luxury suite
        room = (
            RoomBuilder()
            .as_suite()
            .with_price(350)
            .accessible()
            .with_all_features()
            .build()
        )

        # Budget single room
        room = (
            RoomBuilder()
            .as_single()
            .with_price(75)
            .with_features(["WiFi", "TV"])
            .build()
        )

        # Family room
        room = (
            RoomBuilder()
            .as_family()
            .accessible()
            .with_description("Spacious room for families")
            .build()
        )
    """

    ROOM_TYPES = ["Single", "Double", "Twin", "Family", "Suite"]

    ALL_FEATURES = [
        "WiFi",
        "TV",
        "Radio",
        "Refreshments",
        "Safe",
        "Views",
    ]

    def __init__(self) -> None:
        """Initialize the builder with sensible defaults."""
        self._fake = Faker()
        self._room_name: Optional[str] = None
        self._room_type: str = "Double"
        self._accessible: bool = False
        self._price: Optional[int] = None
        self._features: Optional[list[str]] = None
        self._description: Optional[str] = None

    # Room name configuration

    def with_name(self, name: str) -> "RoomBuilder":
        """Set specific room name/number."""
        self._room_name = name
        return self

    def with_room_number(self, number: int) -> "RoomBuilder":
        """Set room number."""
        self._room_name = str(number)
        return self

    # Room type configuration

    def of_type(self, room_type: str) -> "RoomBuilder":
        """Set specific room type."""
        self._room_type = room_type
        return self

    def as_single(self) -> "RoomBuilder":
        """Configure as single room."""
        self._room_type = "Single"
        if self._price is None:
            self._price = random.randint(60, 100)
        return self

    def as_double(self) -> "RoomBuilder":
        """Configure as double room."""
        self._room_type = "Double"
        if self._price is None:
            self._price = random.randint(100, 150)
        return self

    def as_twin(self) -> "RoomBuilder":
        """Configure as twin room."""
        self._room_type = "Twin"
        if self._price is None:
            self._price = random.randint(100, 140)
        return self

    def as_family(self) -> "RoomBuilder":
        """Configure as family room."""
        self._room_type = "Family"
        if self._price is None:
            self._price = random.randint(150, 250)
        return self

    def as_suite(self) -> "RoomBuilder":
        """Configure as suite."""
        self._room_type = "Suite"
        if self._price is None:
            self._price = random.randint(250, 500)
        return self

    # Accessibility configuration

    def accessible(self) -> "RoomBuilder":
        """Mark room as accessible."""
        self._accessible = True
        return self

    def not_accessible(self) -> "RoomBuilder":
        """Mark room as not accessible."""
        self._accessible = False
        return self

    # Price configuration

    def with_price(self, price: int) -> "RoomBuilder":
        """Set specific room price."""
        self._price = price
        return self

    def with_random_price(self, min_price: int = 80, max_price: int = 300) -> "RoomBuilder":
        """Set random price within range."""
        self._price = random.randint(min_price, max_price)
        return self

    # Features configuration

    def with_features(self, features: list[str]) -> "RoomBuilder":
        """Set specific features."""
        self._features = features
        return self

    def with_all_features(self) -> "RoomBuilder":
        """Add all available features."""
        self._features = self.ALL_FEATURES.copy()
        return self

    def with_random_features(self, min_count: int = 2, max_count: int = 5) -> "RoomBuilder":
        """Add random selection of features."""
        count = random.randint(min_count, max_count)
        self._features = random.sample(self.ALL_FEATURES, k=min(count, len(self.ALL_FEATURES)))
        return self

    def with_wifi(self) -> "RoomBuilder":
        """Add WiFi to features."""
        if self._features is None:
            self._features = []
        if "WiFi" not in self._features:
            self._features.append("WiFi")
        return self

    def with_tv(self) -> "RoomBuilder":
        """Add TV to features."""
        if self._features is None:
            self._features = []
        if "TV" not in self._features:
            self._features.append("TV")
        return self

    # Description configuration

    def with_description(self, description: str) -> "RoomBuilder":
        """Set specific description."""
        self._description = description
        return self

    def with_generated_description(self) -> "RoomBuilder":
        """Generate a description based on room type."""
        descriptions = {
            "Single": "A cozy single room perfect for solo travelers.",
            "Double": "A comfortable double room with a queen-size bed.",
            "Twin": "A spacious twin room with two single beds.",
            "Family": "A large family room with ample space for everyone.",
            "Suite": "A luxurious suite with premium amenities and stunning views.",
        }
        self._description = descriptions.get(
            self._room_type, f"A lovely {self._room_type.lower()} room with great amenities."
        )
        return self

    # Build methods

    def build(self) -> Room:
        """Build and return the Room object."""
        # Generate room name if not set
        room_name = self._room_name or str(random.randint(100, 999))

        # Determine features
        if self._features is None:
            features = random.sample(self.ALL_FEATURES, k=random.randint(2, 4))
        else:
            features = self._features

        # Determine price based on room type if not set
        if self._price is None:
            price_ranges = {
                "Single": (60, 100),
                "Double": (100, 150),
                "Twin": (100, 140),
                "Family": (150, 250),
                "Suite": (250, 500),
            }
            min_p, max_p = price_ranges.get(self._room_type, (80, 200))
            price = random.randint(min_p, max_p)
        else:
            price = self._price

        return Room(
            room_name=room_name,
            room_type=self._room_type,
            accessible=self._accessible,
            price=price,
            features=features,
            description=self._description,
        )

    def build_many(self, count: int) -> list[Room]:
        """Build multiple Room objects with varied data."""
        rooms = []
        for i in range(count):
            room_type = self.ROOM_TYPES[i % len(self.ROOM_TYPES)]
            room = (
                RoomBuilder()
                .of_type(room_type)
                .with_room_number(100 + i)
                .with_random_features()
                .accessible() if i % 3 == 0 else RoomBuilder()
                .of_type(room_type)
                .with_room_number(100 + i)
                .with_random_features()
            ).build()
            rooms.append(room)
        return rooms

    def reset(self) -> "RoomBuilder":
        """Reset builder to initial state."""
        self._room_name = None
        self._room_type = "Double"
        self._accessible = False
        self._price = None
        self._features = None
        self._description = None
        return self
