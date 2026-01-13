"""
Response validation utilities for API testing.

Provides a fluent interface for validating HTTP responses with
detailed assertion messages and support for JSON path extraction.
"""

import json
from typing import Any, Optional, Union

import requests
from assertpy import assert_that


class ResponseValidator:
    """
    Fluent validator for HTTP responses.

    Provides chainable assertion methods for validating status codes,
    headers, and JSON body content.

    Usage:
        validator = ResponseValidator(response)
        validator.assert_status_code(200)
        validator.assert_json_field("firstname", "John")
        booking_id = validator.get_field("bookingid")
    """

    def __init__(self, response: requests.Response) -> None:
        """
        Initialize validator with a response object.

        Args:
            response: The requests.Response object to validate
        """
        self.response = response
        self._json_cache: Optional[dict] = None

    @property
    def json(self) -> dict:
        """
        Parse and cache the response JSON.

        Returns:
            Parsed JSON as dictionary

        Raises:
            AssertionError: If response is not valid JSON
        """
        if self._json_cache is None:
            try:
                self._json_cache = self.response.json()
            except json.JSONDecodeError as e:
                raise AssertionError(
                    f"Response is not valid JSON: {e}\n"
                    f"Response body: {self.response.text[:500]}"
                )
        return self._json_cache

    def assert_status_code(self, expected: int) -> "ResponseValidator":
        """
        Assert the response status code.

        Args:
            expected: Expected HTTP status code

        Returns:
            Self for method chaining
        """
        actual = self.response.status_code
        assert_that(actual).described_as(
            f"Expected status {expected}, got {actual}. "
            f"Response: {self.response.text[:500]}"
        ).is_equal_to(expected)
        return self

    def assert_status_in(self, *expected_codes: int) -> "ResponseValidator":
        """
        Assert the response status code is one of the expected values.

        Args:
            *expected_codes: Valid HTTP status codes

        Returns:
            Self for method chaining
        """
        actual = self.response.status_code
        assert_that(actual).described_as(
            f"Expected status in {expected_codes}, got {actual}"
        ).is_in(*expected_codes)
        return self

    def assert_success(self) -> "ResponseValidator":
        """
        Assert the response indicates success (2xx status).

        Returns:
            Self for method chaining
        """
        actual = self.response.status_code
        assert_that(actual).described_as(
            f"Expected success status (2xx), got {actual}. "
            f"Response: {self.response.text[:500]}"
        ).is_between(200, 299)
        return self

    def assert_valid_json(self) -> "ResponseValidator":
        """
        Assert the response body is valid JSON.

        Returns:
            Self for method chaining
        """
        # Accessing self.json will raise AssertionError if not valid
        _ = self.json
        return self

    def assert_content_type(self, expected: str) -> "ResponseValidator":
        """
        Assert the Content-Type header.

        Args:
            expected: Expected content type (e.g., "application/json")

        Returns:
            Self for method chaining
        """
        actual = self.response.headers.get("Content-Type", "")
        assert_that(actual).described_as(
            f"Expected Content-Type '{expected}', got '{actual}'"
        ).contains(expected)
        return self

    def assert_header(self, name: str, expected: str) -> "ResponseValidator":
        """
        Assert a specific header value.

        Args:
            name: Header name
            expected: Expected header value

        Returns:
            Self for method chaining
        """
        actual = self.response.headers.get(name)
        assert_that(actual).described_as(
            f"Expected header '{name}' to be '{expected}', got '{actual}'"
        ).is_equal_to(expected)
        return self

    def assert_header_exists(self, name: str) -> "ResponseValidator":
        """
        Assert a header exists.

        Args:
            name: Header name

        Returns:
            Self for method chaining
        """
        assert_that(name in self.response.headers).described_as(
            f"Expected header '{name}' to exist"
        ).is_true()
        return self

    def assert_json_field(
        self, field_path: str, expected: Any, partial_match: bool = False
    ) -> "ResponseValidator":
        """
        Assert a JSON field has the expected value.

        Args:
            field_path: Dot-notation path to field (e.g., "data.user.name")
            expected: Expected value
            partial_match: If True, check if expected is contained in actual

        Returns:
            Self for method chaining
        """
        actual = self.get_field(field_path)

        if partial_match and isinstance(actual, str) and isinstance(expected, str):
            assert_that(actual).described_as(
                f"Expected field '{field_path}' to contain '{expected}', got '{actual}'"
            ).contains(expected)
        else:
            assert_that(actual).described_as(
                f"Expected field '{field_path}' to be '{expected}', got '{actual}'"
            ).is_equal_to(expected)
        return self

    def assert_json_field_exists(self, field_path: str) -> "ResponseValidator":
        """
        Assert a JSON field exists.

        Args:
            field_path: Dot-notation path to field

        Returns:
            Self for method chaining
        """
        value = self.get_field(field_path, raise_on_missing=False)
        assert_that(value).described_as(
            f"Expected field '{field_path}' to exist in response"
        ).is_not_none()
        return self

    def assert_json_field_not_empty(self, field_path: str) -> "ResponseValidator":
        """
        Assert a JSON field exists and is not empty.

        Args:
            field_path: Dot-notation path to field

        Returns:
            Self for method chaining
        """
        value = self.get_field(field_path)
        message = f"Expected field '{field_path}' to not be empty"
        if isinstance(value, (str, list, dict, tuple, set)):
            assert_that(value).described_as(message).is_not_empty()
        else:
            assert_that(value).described_as(message).is_not_none()
        return self

    def assert_json_array_length(
        self, field_path: str, expected_length: int
    ) -> "ResponseValidator":
        """
        Assert a JSON array field has the expected length.

        Args:
            field_path: Dot-notation path to array field
            expected_length: Expected array length

        Returns:
            Self for method chaining
        """
        value = self.get_field(field_path)
        assert_that(value).described_as(
            f"Expected field '{field_path}' to be an array"
        ).is_instance_of(list)
        assert_that(len(value)).described_as(
            f"Expected array '{field_path}' to have length {expected_length}, "
            f"got {len(value)}"
        ).is_equal_to(expected_length)
        return self

    def assert_json_array_not_empty(self, field_path: str = "") -> "ResponseValidator":
        """
        Assert a JSON array field is not empty.

        Args:
            field_path: Dot-notation path to array field (empty for root)

        Returns:
            Self for method chaining
        """
        if field_path:
            value = self.get_field(field_path)
        else:
            value = self.json

        assert_that(value).described_as(
            f"Expected {'field ' + field_path if field_path else 'response'} to be a non-empty array"
        ).is_instance_of(list).is_not_empty()
        return self

    def get_field(
        self, field_path: str, raise_on_missing: bool = True
    ) -> Optional[Any]:
        """
        Extract a field value from the JSON response.

        Args:
            field_path: Dot-notation path to field (e.g., "data.user.name")
            raise_on_missing: If True, raise AssertionError for missing fields

        Returns:
            Field value or None if not found and raise_on_missing is False
        """
        data: Any = self.json
        parts = field_path.split(".") if field_path else []

        for part in parts:
            if isinstance(data, dict):
                if part not in data:
                    if raise_on_missing:
                        raise AssertionError(
                            f"Field '{field_path}' not found in response. "
                            f"Available keys at '{'.'.join(parts[:parts.index(part)])}': "
                            f"{list(data.keys())}"
                        )
                    return None
                data = data[part]
            elif isinstance(data, list):
                try:
                    index = int(part)
                    data = data[index]
                except (ValueError, IndexError):
                    if raise_on_missing:
                        raise AssertionError(
                            f"Cannot access '{part}' in array at '{field_path}'"
                        )
                    return None
            else:
                if raise_on_missing:
                    raise AssertionError(
                        f"Cannot navigate to '{part}' - current value is {type(data)}"
                    )
                return None

        return data

    def get_cookie(self, name: str) -> Optional[str]:
        """
        Get a cookie value from the response.

        Args:
            name: Cookie name

        Returns:
            Cookie value or None if not found
        """
        return self.response.cookies.get(name)
