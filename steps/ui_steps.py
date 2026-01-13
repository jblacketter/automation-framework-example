"""
UI-specific step definitions.

These steps handle browser-based UI testing scenarios.
"""

from behave import given, when, then

from pages.home_page import HomePage
from pages.admin_page import AdminPage
from pages.booking_page import BookingPage


# Navigation steps


@given("I am on the home page")
def step_on_home_page(context):
    """Navigate to the home page."""
    context.home_page = HomePage(context.page)
    context.home_page.navigate()


@given("I am on the admin page")
def step_on_admin_page(context):
    """Navigate to the admin page."""
    context.admin_page = AdminPage(context.page)
    context.admin_page.navigate()


@when("I navigate to the home page")
def step_navigate_home_page(context):
    """Navigate to the home page."""
    context.home_page = HomePage(context.page)
    context.home_page.navigate()


@when("I navigate to the admin page")
def step_navigate_admin_page(context):
    """Navigate to the admin page."""
    context.admin_page = AdminPage(context.page)
    context.admin_page.navigate()


# Home page steps


@then("I should see the hotel name")
def step_see_hotel_name(context):
    """Verify hotel name is displayed."""
    context.home_page.assert_hotel_name_displayed()


@then("I should see at least {count:d} room(s)")
def step_see_rooms(context, count):
    """Verify rooms are displayed."""
    context.home_page.assert_rooms_displayed(min_count=count)


@then("I should see the contact form")
def step_see_contact_form(context):
    """Verify contact form is visible."""
    context.home_page.assert_contact_form_visible()


@when("I fill in the contact form")
def step_fill_contact_form(context):
    """Fill the contact form with data from table."""
    data = {row["field"]: row["value"] for row in context.table}
    context.home_page.fill_contact_form(
        name=data.get("name", "Test User"),
        email=data.get("email", "test@example.com"),
        phone=data.get("phone", "01onal234567890"),
        subject=data.get("subject", "Test Subject"),
        message=data.get("message", "This is a test message."),
    )


@when("I submit the contact form")
def step_submit_contact_form(context):
    """Submit the contact form."""
    context.home_page.submit_contact_form()


@then("I should see a contact success message")
def step_see_contact_success(context):
    """Verify contact success message is shown."""
    assert context.home_page.is_contact_success_visible(
        timeout=5000
    ), "Contact success message not visible"


@then("I should not see a contact success message")
def step_not_see_contact_success(context):
    """Verify contact success message is NOT shown."""
    assert not context.home_page.is_contact_success_visible(
        timeout=2000
    ), "Contact success message should not be visible"


@when("I click book room for the first room")
def step_click_book_first_room(context):
    """Click the Book button for the first room."""
    context.home_page.wait_for_rooms_to_load()
    context.home_page.click_book_room(room_index=0)
    context.booking_page = BookingPage(context.page)


# Admin page steps


@when("I login as admin")
def step_login_admin(context):
    """Login using admin credentials."""
    context.admin_page.login_as_admin()


@when('I login with username "{username}" and password "{password}"')
def step_login_credentials(context, username, password):
    """Login with specific credentials."""
    context.admin_page.login(username, password)


@then("I should be logged in")
def step_should_be_logged_in(context):
    """Verify user is logged in."""
    context.admin_page.assert_logged_in()


@then("I should not be logged in")
def step_should_not_be_logged_in(context):
    """Verify user is not logged in."""
    context.admin_page.assert_logged_out()


@then("I should see a login error")
def step_see_login_error(context):
    """Verify login error is displayed."""
    context.admin_page.assert_login_error_displayed()


@when("I logout")
def step_logout(context):
    """Logout from the admin panel."""
    context.admin_page.logout()


@when('I create a room "{room_name}" of type "{room_type}"')
def step_create_room_ui(context, room_name, room_type):
    """Create a room via UI."""
    context.admin_page.create_room(
        room_number=room_name,
        room_type=room_type,
        price="150",
        features=["WiFi", "TV"],
    )


@then("I should see at least {count:d} room(s) in the admin list")
def step_see_rooms_admin(context, count):
    """Verify room count in admin."""
    actual = context.admin_page.get_room_count()
    assert actual >= count, f"Expected at least {count} rooms, found {actual}"


@when("I navigate to messages")
def step_navigate_messages(context):
    """Navigate to messages inbox."""
    context.admin_page.navigate_to_messages()


@when("I navigate to branding settings")
def step_navigate_branding(context):
    """Navigate to branding settings."""
    context.admin_page.navigate_to_branding()


# Booking page steps


@then("I should see the booking calendar")
def step_see_booking_calendar(context):
    """Verify booking calendar is visible."""
    context.booking_page.assert_calendar_visible()


@when("I select dates for a {nights:d} night stay")
def step_select_dates(context, nights):
    """Select booking dates."""
    context.booking_page.select_dates_by_drag(
        start_offset_days=7, duration_days=nights
    )


@when("I fill in the guest details")
def step_fill_guest_details(context):
    """Fill guest details from table."""
    data = {row["field"]: row["value"] for row in context.table}
    context.booking_page.fill_guest_details(
        firstname=data.get("firstname", "John"),
        lastname=data.get("lastname", "Doe"),
        email=data.get("email", "john@example.com"),
        phone=data.get("phone", "01234567890"),
    )


@when("I submit the booking")
def step_submit_booking(context):
    """Submit the booking form."""
    context.booking_page.submit_booking()


@then("the booking should be successful")
def step_booking_successful(context):
    """Verify booking was successful."""
    context.booking_page.assert_booking_successful()


@then("I should see a booking error")
def step_see_booking_error(context):
    """Verify booking error is displayed."""
    context.booking_page.assert_booking_error_displayed()


# Generic UI steps


@then('I should see "{text}" on the page')
def step_see_text(context, text):
    """Verify text is visible on page."""
    assert context.page.get_by_text(text).is_visible(), f"Text '{text}' not found on page"


@then('the page title should contain "{text}"')
def step_title_contains(context, text):
    """Verify page title contains text."""
    title = context.page.title()
    assert text in title, f"Expected '{text}' in title, got '{title}'"


@then('the URL should contain "{text}"')
def step_url_contains(context, text):
    """Verify URL contains text."""
    url = context.page.url
    assert text in url, f"Expected '{text}' in URL, got '{url}'"


@when('I click on "{text}"')
def step_click_text(context, text):
    """Click on element with text."""
    context.page.get_by_text(text).click()


@when('I fill "{selector}" with "{value}"')
def step_fill_selector(context, selector, value):
    """Fill an input field."""
    context.page.fill(selector, value)


@when("I take a screenshot")
def step_take_screenshot(context):
    """Take a screenshot."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    context.browser_factory.take_screenshot(f"manual_{timestamp}")
