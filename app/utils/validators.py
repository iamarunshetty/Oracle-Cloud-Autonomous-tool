"""
Form-field validation helpers.
All validators return (is_valid: bool, error_message: str).
"""

import re


def validate_required(value: str, field_name: str = "Field") -> tuple[bool, str]:
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    pattern = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{1,}$")
    if not email or not email.strip():
        return False, "Email is required."
    if not pattern.match(email.strip()):
        return False, "Enter a valid email address."
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    if not username or not username.strip():
        return False, "Username is required."
    stripped = username.strip()
    if len(stripped) < 3:
        return False, "Username must be at least 3 characters."
    if len(stripped) > 80:
        return False, "Username must be at most 80 characters."
    pattern = re.compile(r"^[a-zA-Z0-9._@\-]+$")
    if not pattern.match(stripped):
        return False, "Username may only contain letters, digits, '.', '_', '@', '-'."
    return True, ""


def validate_min_length(value: str, min_len: int, field_name: str = "Field") -> tuple[bool, str]:
    if not value or len(value.strip()) < min_len:
        return False, f"{field_name} must be at least {min_len} characters."
    return True, ""


def validate_not_empty_list(items: list, field_name: str = "Selection") -> tuple[bool, str]:
    if not items:
        return False, f"{field_name} cannot be empty."
    return True, ""


def run_all(*checks: tuple[bool, str]) -> tuple[bool, list[str]]:
    """Run multiple validation checks and collect all error messages."""
    errors = [msg for ok, msg in checks if not ok]
    return len(errors) == 0, errors
