"""
HTTP API client using singleton pattern.

Provides a centralized HTTP client with session pooling, automatic
token management, request/response logging, and retry capabilities.
"""

import json
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import Config
from core.logger import get_logger, mask_sensitive_data


class APIClient:
    """
    Singleton HTTP API client.

    Features:
    - Connection pooling via requests.Session
    - Automatic token injection in headers
    - Request/response logging with sensitive data masking
    - Configurable retry strategy
    - Cookie management for session-based auth

    Usage:
        client = APIClient()
        client.set_token("your-token")
        response = client.get("/booking/1")
    """

    _instance: Optional["APIClient"] = None
    _initialized: bool = False

    def __new__(cls) -> "APIClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.config = Config()
        self.logger = get_logger(__name__)
        self.base_url = self.config.api_base_url

        # Initialize session with connection pooling
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Token storage
        self._token: Optional[str] = None

        self._initialized = True
        self.logger.info(f"APIClient initialized with base URL: {self.base_url}")

    def set_token(self, token: str) -> None:
        """Set the authentication token for subsequent requests."""
        self._token = token
        self.logger.debug("Authentication token set")

    def clear_token(self) -> None:
        """Clear the authentication token."""
        self._token = None
        self.logger.debug("Authentication token cleared")

    def set_cookie(self, name: str, value: str) -> None:
        """Set a cookie for subsequent requests."""
        self.session.cookies.set(name, value)
        self.logger.debug(f"Cookie '{name}' set")

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self.session.cookies.clear()
        self.logger.debug("All cookies cleared")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        return urljoin(self.base_url, endpoint)

    def _build_headers(self, additional_headers: Optional[dict] = None) -> dict:
        """Build request headers with optional token."""
        headers = {}
        if self._token:
            headers["Cookie"] = f"token={self._token}"
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Log request details with sensitive data masked."""
        if not self.config.log_api_requests:
            return

        log_parts = [f"Request: {method} {url}"]

        if "headers" in kwargs and kwargs["headers"]:
            log_parts.append(f"Headers: {mask_sensitive_data(kwargs['headers'])}")

        if "json" in kwargs and kwargs["json"]:
            log_parts.append(f"Body: {mask_sensitive_data(json.dumps(kwargs['json']))}")

        if "data" in kwargs and kwargs["data"]:
            log_parts.append(f"Data: {mask_sensitive_data(kwargs['data'])}")

        if "params" in kwargs and kwargs["params"]:
            log_parts.append(f"Params: {kwargs['params']}")

        self.logger.info(" | ".join(log_parts))

    def _log_response(self, response: requests.Response) -> None:
        """Log response details with sensitive data masked."""
        if not self.config.log_api_responses:
            return

        log_parts = [f"Response: {response.status_code} {response.reason}"]

        try:
            body = response.json()
            # Truncate large responses
            body_str = json.dumps(body)
            if len(body_str) > 1000:
                body_str = body_str[:1000] + "... (truncated)"
            log_parts.append(f"Body: {mask_sensitive_data(body_str)}")
        except (json.JSONDecodeError, ValueError):
            if response.text:
                text = response.text[:500] if len(response.text) > 500 else response.text
                log_parts.append(f"Body: {text}")

        self.logger.info(" | ".join(log_parts))

    def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (will be joined with base_url)
            headers: Additional headers to include
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response object
        """
        url = self._build_url(endpoint)
        request_headers = self._build_headers(headers)
        timeout = timeout or (self.config.default_timeout // 1000)

        self._log_request(method, url, headers=request_headers, **kwargs)

        response = self.session.request(
            method=method,
            url=url,
            headers=request_headers,
            timeout=timeout,
            **kwargs,
        )

        self._log_response(response)

        return response

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make a GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make a POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make a PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        if cls._instance:
            cls._instance.session.close()
        cls._instance = None
        cls._initialized = False
