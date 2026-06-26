"""
Tests for the Oracle API client – error handling and retry behaviour.
Uses the `responses` library to mock HTTP calls without network access.
"""

import pytest
import responses as resp_lib
import requests

from app.api.client import OracleAPIClient, APIError


BASE = "https://test-instance.oraclecloud.com"


def _make_client(**kwargs) -> OracleAPIClient:
    defaults = dict(
        base_url=BASE,
        username="admin",
        password="secret",
        timeout=5,
        retry_count=1,
    )
    defaults.update(kwargs)
    return OracleAPIClient(**defaults)


# ---------------------------------------------------------------------------
# Friendly error messages
# ---------------------------------------------------------------------------

class TestFriendlyHttpError:
    def test_401_message(self):
        msg = OracleAPIClient._friendly_http_error(401, "")
        assert "authentication" in msg.lower()

    def test_403_message(self):
        msg = OracleAPIClient._friendly_http_error(403, "")
        assert "permission" in msg.lower()

    def test_404_message(self):
        msg = OracleAPIClient._friendly_http_error(404, "")
        assert "not found" in msg.lower()

    def test_unknown_status(self):
        msg = OracleAPIClient._friendly_http_error(418, "")
        assert "418" in msg

    def test_detail_appended(self):
        msg = OracleAPIClient._friendly_http_error(400, "field X is invalid")
        assert "field X is invalid" in msg


# ---------------------------------------------------------------------------
# HTTP-level error handling
# ---------------------------------------------------------------------------

class TestHTTPErrorHandling:
    @resp_lib.activate
    def test_404_raises_api_error(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/some/path", status=404)
        client = _make_client(retry_count=1)
        with pytest.raises(APIError) as exc_info:
            client.get("/some/path")
        assert exc_info.value.status_code == 404

    @resp_lib.activate
    def test_401_raises_api_error(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/users", status=401)
        client = _make_client(retry_count=1)
        with pytest.raises(APIError) as exc_info:
            client.get("/users")
        assert exc_info.value.status_code == 401
        assert "authentication" in str(exc_info.value).lower()

    @resp_lib.activate
    def test_successful_get_returns_json(self):
        resp_lib.add(
            resp_lib.GET,
            f"{BASE}/users",
            json={"items": [{"id": "1", "userName": "jdoe"}]},
            status=200,
        )
        client = _make_client()
        result = client.get("/users")
        assert result["items"][0]["userName"] == "jdoe"

    @resp_lib.activate
    def test_empty_response_returns_empty_dict(self):
        resp_lib.add(resp_lib.DELETE, f"{BASE}/users/1", status=204, body="")
        client = _make_client()
        result = client.delete("/users/1")
        assert result == {}

    @resp_lib.activate
    def test_post_sends_payload(self):
        resp_lib.add(
            resp_lib.POST,
            f"{BASE}/users",
            json={"id": "new-user-id"},
            status=201,
        )
        client = _make_client()
        result = client.post("/users", {"userName": "newuser"})
        assert result["id"] == "new-user-id"
        assert resp_lib.calls[0].request.body is not None


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------

class TestRetryBehavior:
    @resp_lib.activate
    def test_retries_on_503(self):
        # First call returns 503; second call succeeds
        resp_lib.add(resp_lib.GET, f"{BASE}/users", status=503)
        resp_lib.add(resp_lib.GET, f"{BASE}/users", json={"items": []}, status=200)
        # Patch sleep to speed up test
        import unittest.mock as mock
        client = _make_client(retry_count=2)
        with mock.patch("app.api.client.time.sleep"):
            result = client.get("/users")
        assert result == {"items": []}
        assert len(resp_lib.calls) == 2

    @resp_lib.activate
    def test_exhausted_retries_raises_api_error(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/users", status=503)
        resp_lib.add(resp_lib.GET, f"{BASE}/users", status=503)
        import unittest.mock as mock
        client = _make_client(retry_count=2)
        with mock.patch("app.api.client.time.sleep"):
            with pytest.raises(APIError) as exc_info:
                client.get("/users")
        assert exc_info.value.status_code == 503

    @resp_lib.activate
    def test_non_transient_error_not_retried(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/users", status=403)
        client = _make_client(retry_count=3)
        with pytest.raises(APIError):
            client.get("/users")
        # Should only be called once – 403 is not transient
        assert len(resp_lib.calls) == 1


# ---------------------------------------------------------------------------
# Auth header behaviour
# ---------------------------------------------------------------------------

class TestAuthHeaders:
    @resp_lib.activate
    def test_bearer_token_takes_precedence(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/users", json={}, status=200)
        client = OracleAPIClient(
            base_url=BASE,
            username="admin",
            password="secret",
            token="my-token-xyz",
        )
        client.get("/users")
        auth_header = resp_lib.calls[0].request.headers.get("Authorization", "")
        assert "my-token-xyz" in auth_header
        assert auth_header.startswith("Bearer ")

    @resp_lib.activate
    def test_basic_auth_used_when_no_token(self):
        resp_lib.add(resp_lib.GET, f"{BASE}/users", json={}, status=200)
        client = OracleAPIClient(
            base_url=BASE,
            username="admin",
            password="secret",
        )
        client.get("/users")
        # Basic auth is set via HTTPBasicAuth, which sets the Authorization header
        auth_header = resp_lib.calls[0].request.headers.get("Authorization", "")
        assert auth_header.startswith("Basic ")
