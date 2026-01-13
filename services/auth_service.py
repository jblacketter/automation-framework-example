"""
Authentication service for API operations.

Handles login, token management, and session validation.
"""

from typing import Optional

import requests

from core.api_client import APIClient
from core.config import Config
from core.logger import get_logger
from core.response_validator import ResponseValidator


class AuthService:
    """
    Service for authentication-related API operations.

    Provides methods for:
    - Creating authentication tokens
    - Validating tokens
    - Managing admin sessions

    The Restful Booker Platform uses cookie-based auth with a token.
    """

    # API endpoints (Restful Booker API)
    AUTH_ENDPOINT = "/auth"
    VALIDATE_ENDPOINT = "/auth/validate"
    LOGOUT_ENDPOINT = "/auth/logout"

    def __init__(self) -> None:
        """Initialize the auth service."""
        self.client = APIClient()
        self.config = Config()
        self.logger = get_logger(__name__)

    def login(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate and get a session token.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            Authentication token or None if login failed
        """
        self.logger.info(f"Attempting login for user: {username}")

        response = self.client.post(
            self.AUTH_ENDPOINT,
            json={
                "username": username,
                "password": password,
            },
        )

        if response.status_code == 200:
            # Token is returned in body for Restful Booker
            try:
                data = response.json()
                token = data.get("token")
                if token:
                    self.client.set_token(token)
                    self.logger.info("Login successful, token acquired")
                    return token
            except Exception:
                pass

            # Fallback: check cookie
            token = response.cookies.get("token")
            if token:
                self.client.set_token(token)
                self.logger.info("Login successful, token acquired from cookie")
                return token

        self.logger.warning(f"Login failed with status: {response.status_code}")
        return None

    def login_as_admin(self) -> Optional[str]:
        """
        Login using default admin credentials from configuration.

        Returns:
            Authentication token or None if login failed
        """
        return self.login(self.config.admin_username, self.config.admin_password)

    def validate_token(self, token: Optional[str] = None) -> bool:
        """
        Validate an authentication token.

        Args:
            token: Token to validate (uses current token if not provided)

        Returns:
            True if token is valid
        """
        self.logger.debug("Validating authentication token")

        # Use provided token or get from client
        headers = {}
        if token:
            headers["Cookie"] = f"token={token}"

        response = self.client.post(
            self.VALIDATE_ENDPOINT,
            headers=headers,
            json={"token": token} if token else {},
        )

        is_valid = response.status_code == 200
        self.logger.debug(f"Token validation result: {is_valid}")
        return is_valid

    def logout(self) -> bool:
        """
        Log out and invalidate the current session.

        Returns:
            True if logout was successful
        """
        self.logger.info("Logging out")

        response = self.client.post(self.LOGOUT_ENDPOINT)

        # Clear token regardless of response
        self.client.clear_token()
        self.client.clear_cookies()

        success = response.status_code in (200, 204)
        if success:
            self.logger.info("Logout successful")
        else:
            self.logger.warning(f"Logout returned status: {response.status_code}")

        return success

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with a valid token.

        Returns:
            True if authenticated
        """
        return self.validate_token()

    def get_auth_response(
        self, username: str, password: str
    ) -> tuple[requests.Response, ResponseValidator]:
        """
        Perform login and return response with validator for assertions.

        Useful for testing login scenarios without automatically setting token.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            Tuple of (Response, ResponseValidator)
        """
        response = self.client.post(
            self.AUTH_ENDPOINT,
            json={
                "username": username,
                "password": password,
            },
        )
        return response, ResponseValidator(response)
