"""
Centralised Oracle Fusion API client.

Features:
- Base URL + auth configuration (basic auth or bearer token)
- Request timeout and retry handling (exponential back-off for transient errors)
- Structured error mapping to UI-friendly messages
- Secret-safe logging (credentials never appear in log output)
"""

from __future__ import annotations

import time
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, HTTPError, Timeout

from app.utils.logger import get_logger

logger = get_logger("oracle_fusion_tool.api")

# HTTP status codes that are considered transient and worth retrying
_TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}


class APIError(Exception):
    """Raised when an API call fails after all retries."""

    def __init__(self, message: str, status_code: int | None = None, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail

    def __str__(self) -> str:  # pragma: no cover
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class OracleAPIClient:
    """
    HTTP client for Oracle Fusion REST APIs.

    Parameters
    ----------
    base_url:
        Root URL of the Oracle Fusion instance, e.g.
        ``https://your-instance.oraclecloud.com``.
    username / password:
        Basic-auth credentials (used when ``token`` is not provided).
    token:
        Bearer token for Authorization header (takes precedence over basic auth).
    timeout:
        Per-request timeout in seconds.
    retry_count:
        Maximum number of attempts for transient failures (default 3).
    """

    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        token: str = "",
        timeout: int = 30,
        retry_count: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._token = token
        self._timeout = timeout
        self._retry_count = max(1, retry_count)
        self._session = requests.Session()
        self._session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )
        logger.debug("OracleAPIClient initialised for base_url=%s", self._base_url)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, json=payload)

    def patch(self, path: str, payload: dict[str, Any] | None = None) -> Any:
        return self._request("PATCH", path, json=payload)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _auth(self) -> HTTPBasicAuth | None:
        if self._token:
            return None  # auth header set directly
        if self._username and self._password:
            return HTTPBasicAuth(self._username, self._password)
        return None

    def _headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        logger.debug("%s %s", method, url)

        last_exception: Exception | None = None

        for attempt in range(1, self._retry_count + 1):
            try:
                response = self._session.request(
                    method,
                    url,
                    auth=self._auth(),
                    headers=self._headers(),
                    timeout=self._timeout,
                    **kwargs,
                )
                response.raise_for_status()
                if response.content:
                    return response.json()
                return {}

            except HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else None
                detail = ""
                if exc.response is not None:
                    try:
                        detail = exc.response.json().get("detail", exc.response.text[:200])
                    except Exception:
                        detail = exc.response.text[:200]
                msg = self._friendly_http_error(status, detail)
                logger.warning("HTTP %s on attempt %d/%d: %s", status, attempt, self._retry_count, msg)

                if status in _TRANSIENT_STATUS_CODES and attempt < self._retry_count:
                    self._backoff(attempt)
                    last_exception = APIError(msg, status_code=status, detail=detail)
                    continue
                raise APIError(msg, status_code=status, detail=detail) from exc

            except Timeout as exc:
                msg = f"Request timed out after {self._timeout}s."
                logger.warning("Timeout on attempt %d/%d: %s", attempt, self._retry_count, msg)
                last_exception = APIError(msg)
                if attempt < self._retry_count:
                    self._backoff(attempt)
                    continue
                raise APIError(msg) from exc

            except ConnectionError as exc:
                msg = "Unable to connect to Oracle Fusion. Check your network and Base URL."
                logger.warning("Connection error on attempt %d/%d", attempt, self._retry_count)
                last_exception = APIError(msg)
                if attempt < self._retry_count:
                    self._backoff(attempt)
                    continue
                raise APIError(msg) from exc

            except Exception as exc:
                msg = f"Unexpected error: {exc}"
                logger.error("Unexpected error: %s", exc)
                raise APIError(msg) from exc

        raise last_exception  # type: ignore[misc]

    @staticmethod
    def _backoff(attempt: int) -> None:
        delay = 2 ** (attempt - 1)  # 1s, 2s, 4s …
        logger.debug("Backing off for %ds before retry.", delay)
        time.sleep(delay)

    @staticmethod
    def _friendly_http_error(status: int | None, detail: str) -> str:
        mapping = {
            400: "Bad request – check the data you submitted.",
            401: "Authentication failed – verify your credentials.",
            403: "Permission denied – your account lacks the required privilege.",
            404: "Resource not found.",
            409: "Conflict – the resource may already exist.",
            422: "Validation error from the server.",
            429: "Too many requests – please wait before retrying.",
            500: "Internal server error – Oracle Fusion returned an unexpected error.",
            502: "Bad gateway – upstream server is unavailable.",
            503: "Service unavailable – Oracle Fusion may be down for maintenance.",
            504: "Gateway timeout – the server did not respond in time.",
        }
        base = mapping.get(status, f"HTTP error {status}.")
        if detail:
            return f"{base} Detail: {detail}"
        return base
