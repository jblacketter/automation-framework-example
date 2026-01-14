"""
Booking service for API operations.

Handles CRUD operations for bookings.
"""

from datetime import date, datetime
from typing import Any, Optional

import requests

from core.api_client import APIClient
from core.logger import get_logger
from core.response_validator import ResponseValidator


class BookingService:
    """
    Service for booking-related API operations.

    Provides methods for:
    - Getting all bookings
    - Getting booking details
    - Creating bookings
    - Updating bookings
    - Deleting bookings

    Note: Some operations require authentication.
    """

    # API endpoints
    BOOKING_ENDPOINT = "/booking"

    def __init__(self) -> None:
        """Initialize the booking service."""
        self.client = APIClient()
        self.logger = get_logger(__name__)

    def get_all_bookings(
        self,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        checkin: Optional[date] = None,
        checkout: Optional[date] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Get all bookings, optionally filtered by name or dates.

        Args:
            firstname: Filter by guest first name
            lastname: Filter by guest last name
            checkin: Filter by check-in date
            checkout: Filter by check-out date

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info("Getting all bookings")

        params = {}
        if firstname:
            params["firstname"] = firstname
        if lastname:
            params["lastname"] = lastname
        if checkin:
            params["checkin"] = checkin.isoformat()
        if checkout:
            params["checkout"] = checkout.isoformat()

        response = self.client.get(self.BOOKING_ENDPOINT, params=params)
        return response, ResponseValidator(response)

    def get_booking(
        self, booking_id: int
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Get details of a specific booking.

        Args:
            booking_id: ID of the booking to retrieve

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Getting booking: {booking_id}")

        response = self.client.get(f"{self.BOOKING_ENDPOINT}/{booking_id}")
        return response, ResponseValidator(response)

    def create_booking(
        self,
        firstname: str,
        lastname: str,
        check_in: date,
        check_out: date,
        total_price: int = 100,
        deposit_paid: bool = False,
        additional_needs: Optional[str] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Create a new booking.

        Args:
            firstname: Guest first name
            lastname: Guest last name
            check_in: Check-in date
            check_out: Check-out date
            total_price: Total price for the stay
            deposit_paid: Whether deposit has been paid
            additional_needs: Any additional requirements

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Creating booking for {firstname} {lastname}")

        booking_data: dict[str, Any] = {
            "firstname": firstname,
            "lastname": lastname,
            "totalprice": total_price,
            "depositpaid": deposit_paid,
            "bookingdates": {
                "checkin": check_in.isoformat(),
                "checkout": check_out.isoformat(),
            },
        }

        if additional_needs:
            booking_data["additionalneeds"] = additional_needs

        response = self.client.post(self.BOOKING_ENDPOINT, json=booking_data)
        return response, ResponseValidator(response)

    def update_booking(
        self,
        booking_id: int,
        firstname: str,
        lastname: str,
        check_in: date,
        check_out: date,
        total_price: int = 100,
        deposit_paid: bool = False,
        additional_needs: Optional[str] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Update an existing booking (full update).

        Requires authentication.

        Args:
            booking_id: ID of the booking to update
            firstname: Guest first name
            lastname: Guest last name
            check_in: Check-in date
            check_out: Check-out date
            total_price: Total price for the stay
            deposit_paid: Whether deposit has been paid
            additional_needs: Any additional requirements

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Updating booking: {booking_id}")

        booking_data: dict[str, Any] = {
            "firstname": firstname,
            "lastname": lastname,
            "totalprice": total_price,
            "depositpaid": deposit_paid,
            "bookingdates": {
                "checkin": check_in.isoformat(),
                "checkout": check_out.isoformat(),
            },
        }

        if additional_needs:
            booking_data["additionalneeds"] = additional_needs

        response = self.client.put(
            f"{self.BOOKING_ENDPOINT}/{booking_id}",
            json=booking_data,
        )
        return response, ResponseValidator(response)

    def delete_booking(
        self, booking_id: int
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Delete a booking.

        Requires authentication.

        Args:
            booking_id: ID of the booking to delete

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Deleting booking: {booking_id}")

        response = self.client.delete(f"{self.BOOKING_ENDPOINT}/{booking_id}")
        return response, ResponseValidator(response)

    def partial_update_booking(
        self,
        booking_id: int,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        total_price: Optional[int] = None,
        deposit_paid: Optional[bool] = None,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        additional_needs: Optional[str] = None,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Partially update a booking (PATCH).

        Requires authentication.

        Args:
            booking_id: ID of the booking to update
            firstname: Guest first name (optional)
            lastname: Guest last name (optional)
            total_price: Total price (optional)
            deposit_paid: Deposit status (optional)
            check_in: Check-in date (optional)
            check_out: Check-out date (optional)
            additional_needs: Additional requirements (optional)

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        self.logger.info(f"Partially updating booking: {booking_id}")

        booking_data: dict[str, Any] = {}
        if firstname:
            booking_data["firstname"] = firstname
        if lastname:
            booking_data["lastname"] = lastname
        if total_price is not None:
            booking_data["totalprice"] = total_price
        if deposit_paid is not None:
            booking_data["depositpaid"] = deposit_paid
        if check_in or check_out:
            booking_data["bookingdates"] = {}
            if check_in:
                booking_data["bookingdates"]["checkin"] = check_in.isoformat()
            if check_out:
                booking_data["bookingdates"]["checkout"] = check_out.isoformat()
        if additional_needs:
            booking_data["additionalneeds"] = additional_needs

        response = self.client.patch(
            f"{self.BOOKING_ENDPOINT}/{booking_id}",
            json=booking_data,
        )
        return response, ResponseValidator(response)

    # Helper methods for common scenarios

    def create_test_booking(
        self,
        days_from_now: int = 7,
        duration_nights: int = 2,
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Create a test booking with generated data.

        Useful for setting up test scenarios.

        Args:
            days_from_now: Days from today for check-in
            duration_nights: Number of nights to book

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        from faker import Faker
        from datetime import timedelta
        import random

        fake = Faker()

        check_in = date.today() + timedelta(days=days_from_now)
        check_out = check_in + timedelta(days=duration_nights)

        return self.create_booking(
            firstname=fake.first_name(),
            lastname=fake.last_name(),
            check_in=check_in,
            check_out=check_out,
            total_price=random.randint(100, 500),
            deposit_paid=True,
            additional_needs=random.choice(["Breakfast", "Late checkout", "Airport pickup", None]),
        )

    def booking_exists(self, booking_id: int) -> bool:
        """
        Check if a booking exists.

        Args:
            booking_id: ID of the booking

        Returns:
            True if booking exists
        """
        response, _ = self.get_booking(booking_id)
        return response.status_code == 200

    def create_from_builder(
        self, booking: "Booking"
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Create a booking from a Booking builder object.

        Usage:
            from factories import BookingBuilder

            booking = BookingBuilder().for_weekend().with_breakfast().build()
            response, validator = service.create_from_builder(booking)

        Args:
            booking: Booking object from BookingBuilder

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        from factories.booking_builder import Booking

        return self.create_booking(
            firstname=booking.guest.firstname,
            lastname=booking.guest.lastname,
            check_in=booking.check_in,
            check_out=booking.check_out,
            total_price=booking.total_price,
            deposit_paid=booking.deposit_paid,
            additional_needs=booking.additional_needs,
        )
