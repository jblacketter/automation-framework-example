"""
API-specific step definitions.

These steps handle API testing scenarios for bookings, rooms, and authentication.
"""

from datetime import date, timedelta

from behave import given, when, then

from core.api_client import APIClient
from core.response_validator import ResponseValidator
from services.auth_service import AuthService
from services.booking_service import BookingService
from services.room_service import RoomService


# Authentication steps


@when("I attempt to login with invalid credentials")
def step_login_invalid_credentials(context):
    """Attempt login with invalid username/password."""
    auth_service = AuthService()
    context.response, context.validator = auth_service.get_auth_response(
        "invalid_user", "wrong_password"
    )


# Booking steps


@given("bookings exist in the system")
def step_bookings_exist(context):
    """Ensure bookings exist in the system (Restful Booker always has bookings)."""
    # Restful Booker API always has pre-loaded bookings
    booking_service = BookingService()
    response, validator = booking_service.get_all_bookings()
    assert response.status_code == 200, "Could not fetch bookings"
    bookings = validator.json
    assert len(bookings) > 0, "No bookings found in system"
    context.existing_booking_id = bookings[0].get("bookingid")


@when("I request all bookings")
def step_request_all_bookings(context):
    """Get all bookings from the API."""
    booking_service = BookingService()
    context.response, context.validator = booking_service.get_all_bookings()


@when('I request bookings filtered by firstname "{firstname}"')
def step_request_bookings_by_firstname(context, firstname):
    """Get all bookings filtered by firstname."""
    booking_service = BookingService()
    context.response, context.validator = booking_service.get_all_bookings(firstname=firstname)


@when("I request booking with ID {booking_id:d}")
def step_request_booking_by_id(context, booking_id):
    """Get a specific booking by ID."""
    booking_service = BookingService()
    context.response, context.validator = booking_service.get_booking(booking_id)


@when('I create a booking for "{firstname}" "{lastname}"')
def step_create_booking(context, firstname, lastname):
    """Create a new booking."""
    booking_service = BookingService()

    check_in = date.today() + timedelta(days=7)
    check_out = check_in + timedelta(days=2)

    context.response, context.validator = booking_service.create_booking(
        firstname=firstname,
        lastname=lastname,
        check_in=check_in,
        check_out=check_out,
        total_price=150,
        deposit_paid=True,
    )

    # Track for cleanup if created successfully
    if context.response.status_code == 200:
        booking_id = context.validator.get_field("bookingid", raise_on_missing=False)
        if booking_id:
            context.bookings_to_cleanup.append(booking_id)
            context.created_booking_id = booking_id


@when("I create a test booking")
def step_create_test_booking(context):
    """Create a test booking with generated data."""
    booking_service = BookingService()

    context.response, context.validator = booking_service.create_test_booking()

    if context.response.status_code == 200:
        booking_id = context.validator.get_field("bookingid", raise_on_missing=False)
        if booking_id:
            context.bookings_to_cleanup.append(booking_id)
            context.created_booking_id = booking_id


@when("I create a weekend booking with breakfast")
def step_create_weekend_booking(context):
    """Create a weekend booking using the builder pattern."""
    from factories import BookingBuilder

    booking = BookingBuilder().for_weekend().with_breakfast().with_deposit().build()
    booking_service = BookingService()

    context.response, context.validator = booking_service.create_from_builder(booking)

    if context.response.status_code == 200:
        booking_id = context.validator.get_field("bookingid", raise_on_missing=False)
        if booking_id:
            context.bookings_to_cleanup.append(booking_id)
            context.created_booking_id = booking_id


@when("I create a long stay booking for {nights:d} nights")
def step_create_long_stay_booking(context, nights):
    """Create a long stay booking using the builder pattern."""
    from factories import BookingBuilder

    booking = (
        BookingBuilder()
        .for_nights(nights)
        .starting_in_days(14)
        .with_deposit()
        .with_late_checkout()
        .build()
    )
    booking_service = BookingService()

    context.response, context.validator = booking_service.create_from_builder(booking)

    if context.response.status_code == 200:
        booking_id = context.validator.get_field("bookingid", raise_on_missing=False)
        if booking_id:
            context.bookings_to_cleanup.append(booking_id)
            context.created_booking_id = booking_id


@when("I delete the created booking")
def step_delete_created_booking(context):
    """Delete the most recently created booking."""
    assert hasattr(context, "created_booking_id"), "No booking was created"

    booking_service = BookingService()
    context.response, context.validator = booking_service.delete_booking(
        context.created_booking_id
    )

    # Remove from cleanup list if deleted
    if context.response.status_code in (200, 202, 204):
        if context.created_booking_id in context.bookings_to_cleanup:
            context.bookings_to_cleanup.remove(context.created_booking_id)


@when("I delete booking {booking_id:d}")
def step_delete_booking(context, booking_id):
    """Delete a specific booking."""
    booking_service = BookingService()
    context.response, context.validator = booking_service.delete_booking(booking_id)


@then("the booking should have firstname {firstname}")
def step_booking_has_firstname(context, firstname):
    """Assert booking has specific firstname."""
    context.validator.assert_json_field("firstname", firstname)


@then("the booking should have lastname {lastname}")
def step_booking_has_lastname(context, lastname):
    """Assert booking has specific lastname."""
    context.validator.assert_json_field("lastname", lastname)


# Generic API request steps


@when('I make a GET request to "{endpoint}"')
def step_get_request(context, endpoint):
    """Make a GET request to any endpoint."""
    client = APIClient()
    context.response = client.get(endpoint)
    context.validator = ResponseValidator(context.response)


@when('I make a POST request to "{endpoint}"')
def step_post_request(context, endpoint):
    """Make a POST request to any endpoint."""
    client = APIClient()

    # Use table data if provided
    json_data = None
    if context.table:
        json_data = {row["field"]: row["value"] for row in context.table}

    context.response = client.post(endpoint, json=json_data)
    context.validator = ResponseValidator(context.response)


@when('I make a DELETE request to "{endpoint}"')
def step_delete_request(context, endpoint):
    """Make a DELETE request to any endpoint."""
    client = APIClient()
    context.response = client.delete(endpoint)
    context.validator = ResponseValidator(context.response)
