"""
Room service for API operations.

Handles CRUD operations for rooms.
"""

from typing import Any, Optional

import requests

from core.api_client import APIClient
from core.logger import get_logger
from core.response_validator import ResponseValidator


class RoomService:
    """
    Service for room-related API operations.

    Provides methods for:
    - Getting all rooms
    - Getting room details
    - Creating rooms (requires auth)
    - Updating rooms (requires auth)
    - Deleting rooms (requires auth)
    """

    # API endpoints
    ROOM_ENDPOINT = "/room"

    # Valid room types
    ROOM_TYPES = ["Single", "Twin", "Double", "Family", "Suite"]

    # Valid room features
    ROOM_FEATURES = ["WiFi", "TV", "Radio", "Refreshments", "Safe", "Views"]

    def __init__(self) -> None:
        """Initialize the room service."""
        self.client = APIClient()
        self.logger = get_logger(__name__)

    def get_all_rooms(self) -> tuple[requests.Response, ResponseValidator]:
        """
        Get all rooms.

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info("Getting all rooms")

        response = self.client.get(self.ROOM_ENDPOINT)
        return response, ResponseValidator(response)

    def get_room(self, room_id: int) -> tuple[requests.Response, ResponseValidator]:
        """
        Get details of a specific room.

        Args:
            room_id: ID of the room to retrieve

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Getting room: {room_id}")

        response = self.client.get(f"{self.ROOM_ENDPOINT}/{room_id}")
        return response, ResponseValidator(response)

    def create_room(
        self,
        room_name: str,
        room_type: str = "Single",
        accessible: bool = False,
        price: int = 100,
        features: Optional[list[str]] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Create a new room.

        Requires authentication.

        Args:
            room_name: Room number/name
            room_type: Type (Single, Twin, Double, Family, Suite)
            accessible: Whether room is wheelchair accessible
            price: Price per night
            features: List of features (WiFi, TV, Radio, Refreshments, Safe, Views)
            description: Room description
            image: Image URL for the room

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Creating room: {room_name}")

        room_data: dict[str, Any] = {
            "roomName": room_name,
            "type": room_type,
            "accessible": accessible,
            "roomPrice": price,
            "features": features or [],
        }

        if description:
            room_data["description"] = description
        if image:
            room_data["image"] = image

        response = self.client.post(self.ROOM_ENDPOINT, json=room_data)
        return response, ResponseValidator(response)

    def update_room(
        self,
        room_id: int,
        room_name: str,
        room_type: str = "Single",
        accessible: bool = False,
        price: int = 100,
        features: Optional[list[str]] = None,
        description: Optional[str] = None,
        image: Optional[str] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Update an existing room.

        Requires authentication.

        Args:
            room_id: ID of the room to update
            room_name: Room number/name
            room_type: Type (Single, Twin, Double, Family, Suite)
            accessible: Whether room is wheelchair accessible
            price: Price per night
            features: List of features
            description: Room description
            image: Image URL

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Updating room: {room_id}")

        room_data: dict[str, Any] = {
            "roomName": room_name,
            "type": room_type,
            "accessible": accessible,
            "roomPrice": price,
            "features": features or [],
        }

        if description:
            room_data["description"] = description
        if image:
            room_data["image"] = image

        response = self.client.put(
            f"{self.ROOM_ENDPOINT}/{room_id}",
            json=room_data,
        )
        return response, ResponseValidator(response)

    def delete_room(
        self, room_id: int
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Delete a room.

        Requires authentication.

        Args:
            room_id: ID of the room to delete

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Deleting room: {room_id}")

        response = self.client.delete(f"{self.ROOM_ENDPOINT}/{room_id}")
        return response, ResponseValidator(response)

    # Helper methods

    def get_room_ids(self) -> list[int]:
        """
        Get list of all room IDs.

        Returns:
            List of room IDs
        """
        response, validator = self.get_all_rooms()
        if response.status_code == 200:
            rooms = validator.json.get("rooms", [])
            return [room.get("roomid") for room in rooms if room.get("roomid")]
        return []

    def room_exists(self, room_id: int) -> bool:
        """
        Check if a room exists.

        Args:
            room_id: ID of the room

        Returns:
            True if room exists
        """
        response, _ = self.get_room(room_id)
        return response.status_code == 200

    def create_test_room(
        self, room_type: str = "Double"
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Create a test room with generated data.

        Useful for setting up test scenarios.

        Args:
            room_type: Type of room to create

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        from faker import Faker
        import random

        fake = Faker()

        return self.create_room(
            room_name=str(fake.random_int(min=100, max=999)),
            room_type=room_type,
            accessible=random.choice([True, False]),
            price=random.randint(80, 300),
            features=random.sample(self.ROOM_FEATURES, k=random.randint(2, 5)),
            description=f"A lovely {room_type.lower()} room with great amenities.",
        )

    def get_first_room_id(self) -> Optional[int]:
        """
        Get the ID of the first available room.

        Returns:
            First room ID or None if no rooms exist
        """
        room_ids = self.get_room_ids()
        return room_ids[0] if room_ids else None
