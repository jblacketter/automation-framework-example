"""
Common step definitions shared across UI and API tests.

These steps provide reusable functionality for both test types.
"""

from behave import given, when, then, step

from core.api_client import APIClient
from core.config import Config
from services.auth_service import AuthService


# Authentication steps (shared between UI and API)
# Using @step decorator allows these to be used with Given/When/Then


@step("I am authenticated as admin")
def step_authenticated_as_admin(context):
    """Authenticate using admin credentials."""
    auth_service = AuthService()
    token = auth_service.login_as_admin()
    assert token, "Failed to authenticate as admin"
    context.auth_token = token


@step('I am authenticated as "{username}" with password "{password}"')
def step_authenticated_with_credentials(context, username, password):
    """Authenticate using specific credentials."""
    auth_service = AuthService()
    token = auth_service.login(username, password)
    context.auth_token = token


@step("I am not authenticated")
def step_not_authenticated(context):
    """Ensure no authentication token is set."""
    client = APIClient()
    client.clear_token()
    client.clear_cookies()
    context.auth_token = None


@then("the token should be valid")
def step_token_is_valid(context):
    """Assert that a valid token was obtained."""
    assert hasattr(context, "auth_token") and context.auth_token, "No valid token was obtained"


@then("the token should be invalid")
def step_token_is_invalid(context):
    """Assert that no valid token was obtained."""
    token = getattr(context, "auth_token", None)
    assert not token, "Expected no token but got one"


# Response validation steps (API)


@then("the response status code should be {status_code:d}")
def step_response_status_code(context, status_code):
    """Assert the response has the expected status code."""
    assert context.response is not None, "No response available"
    context.validator.assert_status_code(status_code)


@then("the response should be successful")
def step_response_successful(context):
    """Assert the response indicates success (2xx)."""
    assert context.response is not None, "No response available"
    context.validator.assert_success()


@then("the response should be valid JSON")
def step_response_valid_json(context):
    """Assert the response is valid JSON."""
    assert context.response is not None, "No response available"
    context.validator.assert_valid_json()


@then('the response should contain "{field}"')
def step_response_contains_field(context, field):
    """Assert the response JSON contains a field."""
    assert context.response is not None, "No response available"
    context.validator.assert_json_field_exists(field)


@then('the response field "{field}" should be "{value}"')
def step_response_field_value(context, field, value):
    """Assert a response field has a specific value."""
    assert context.response is not None, "No response available"
    context.validator.assert_json_field(field, value)


@then('the response field "{field}" should not be empty')
def step_response_field_not_empty(context, field):
    """Assert a response field is not empty."""
    assert context.response is not None, "No response available"
    context.validator.assert_json_field_not_empty(field)


@then("the response should be an array")
def step_response_is_array(context):
    """Assert the response is a JSON array."""
    assert context.response is not None, "No response available"
    data = context.validator.json
    assert isinstance(data, list), f"Expected array, got {type(data)}"


@then("the response array should not be empty")
def step_response_array_not_empty(context):
    """Assert the response array is not empty."""
    assert context.response is not None, "No response available"
    context.validator.assert_json_array_not_empty()


@then("the response array should have {count:d} items")
def step_response_array_count(context, count):
    """Assert the response array has a specific length."""
    assert context.response is not None, "No response available"
    data = context.validator.json
    assert len(data) == count, f"Expected {count} items, got {len(data)}"


# Configuration steps


@given("the base URL is configured")
def step_base_url_configured(context):
    """Verify base URL is configured."""
    config = Config()
    assert config.base_url, "Base URL is not configured"


# Wait/timing steps


@when("I wait for {seconds:d} seconds")
def step_wait_seconds(context, seconds):
    """Wait for a specified number of seconds."""
    import time

    time.sleep(seconds)
