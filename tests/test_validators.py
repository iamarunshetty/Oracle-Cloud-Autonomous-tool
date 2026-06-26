"""
Tests for form-field validation helpers.
"""

import pytest
from app.utils.validators import (
    validate_required,
    validate_email,
    validate_username,
    validate_min_length,
    validate_not_empty_list,
    run_all,
)


class TestValidateRequired:
    def test_valid_string(self):
        ok, msg = validate_required("hello")
        assert ok is True
        assert msg == ""

    def test_empty_string(self):
        ok, msg = validate_required("")
        assert ok is False
        assert "required" in msg.lower()

    def test_whitespace_only(self):
        ok, msg = validate_required("   ")
        assert ok is False

    def test_none_value(self):
        ok, msg = validate_required(None)  # type: ignore[arg-type]
        assert ok is False

    def test_custom_field_name(self):
        ok, msg = validate_required("", "My Field")
        assert "My Field" in msg


class TestValidateEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "admin+tag@oracle.co.uk",
        "u@x.io",
    ])
    def test_valid_emails(self, email):
        ok, msg = validate_email(email)
        assert ok is True, f"Expected valid, got: {msg}"

    @pytest.mark.parametrize("email", [
        "",
        "notanemail",
        "@missing-local.com",
        "missing-at-sign.com",
        "user@",
        "user@.com",
        "user@domain",
    ])
    def test_invalid_emails(self, email):
        ok, msg = validate_email(email)
        assert ok is False, f"Expected invalid for: {email!r}"

    def test_strips_whitespace(self):
        ok, _ = validate_email("  user@example.com  ")
        assert ok is True


class TestValidateUsername:
    def test_valid_username(self):
        ok, _ = validate_username("john.doe_01")
        assert ok is True

    def test_too_short(self):
        ok, msg = validate_username("ab")
        assert ok is False
        assert "3" in msg

    def test_too_long(self):
        ok, msg = validate_username("a" * 81)
        assert ok is False
        assert "80" in msg

    def test_invalid_characters(self):
        ok, _ = validate_username("user name!")
        assert ok is False

    def test_email_style_username(self):
        ok, _ = validate_username("user@domain.com")
        assert ok is True

    def test_empty(self):
        ok, _ = validate_username("")
        assert ok is False


class TestValidateMinLength:
    def test_sufficient_length(self):
        ok, _ = validate_min_length("abcde", 5)
        assert ok is True

    def test_too_short(self):
        ok, msg = validate_min_length("ab", 5, "Password")
        assert ok is False
        assert "5" in msg
        assert "Password" in msg

    def test_empty_string(self):
        ok, _ = validate_min_length("", 1)
        assert ok is False


class TestValidateNotEmptyList:
    def test_non_empty(self):
        ok, _ = validate_not_empty_list(["role1"])
        assert ok is True

    def test_empty_list(self):
        ok, msg = validate_not_empty_list([])
        assert ok is False
        assert "empty" in msg.lower()


class TestRunAll:
    def test_all_pass(self):
        ok, errors = run_all(
            validate_required("hello"),
            validate_email("a@b.com"),
        )
        assert ok is True
        assert errors == []

    def test_one_fails(self):
        ok, errors = run_all(
            validate_required("hello"),
            validate_email("bad-email"),
        )
        assert ok is False
        assert len(errors) == 1

    def test_multiple_fail(self):
        ok, errors = run_all(
            validate_required(""),
            validate_email(""),
            validate_username(""),
        )
        assert ok is False
        assert len(errors) == 3
