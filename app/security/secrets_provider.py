"""
Secrets-handling abstraction.

The default provider reads credentials from environment variables only –
credentials are NEVER hard-coded here.

How to swap for Windows Credential Manager:
    1. Install ``pywin32`` (``pip install pywin32``).
    2. Implement ``WindowsCredentialProvider`` below (see TODO).
    3. Set ``secrets = WindowsCredentialProvider()`` at the bottom of this file.

The rest of the application only calls ``secrets.get_credential(service)``
and never accesses raw env-vars for passwords.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional


class SecretsProvider(ABC):
    """Abstract interface for a secrets provider."""

    @abstractmethod
    def get_credential(self, service: str) -> Optional[str]:
        """Return the credential/token for *service*, or None if not found."""

    @abstractmethod
    def set_credential(self, service: str, value: str) -> None:
        """Persist *value* for *service* (implementation-specific storage)."""


class EnvSecretsProvider(SecretsProvider):
    """
    Read-only provider that resolves secrets from environment variables.

    The environment variable name is derived by upper-casing the service
    name and replacing hyphens/spaces with underscores.

    Example:
        service="fusion-password"  →  env var ``FUSION_PASSWORD``
    """

    def get_credential(self, service: str) -> Optional[str]:
        key = service.upper().replace("-", "_").replace(" ", "_")
        value = os.environ.get(key)
        return value if value else None

    def set_credential(self, service: str, value: str) -> None:
        # Environment variables are process-scoped; writing here only
        # affects the current process.
        key = service.upper().replace("-", "_").replace(" ", "_")
        os.environ[key] = value


# ---------------------------------------------------------------------------
# TODO: Windows Credential Manager provider
# ---------------------------------------------------------------------------
# class WindowsCredentialProvider(SecretsProvider):
#     """Store/retrieve credentials via Windows Credential Manager."""
#
#     def get_credential(self, service: str) -> Optional[str]:
#         import win32cred  # pip install pywin32
#         try:
#             cred = win32cred.CredRead(service, win32cred.CRED_TYPE_GENERIC)
#             return cred["CredentialBlob"].decode()
#         except Exception:
#             return None
#
#     def set_credential(self, service: str, value: str) -> None:
#         import win32cred
#         win32cred.CredWrite({
#             "Type": win32cred.CRED_TYPE_GENERIC,
#             "TargetName": service,
#             "CredentialBlob": value.encode(),
#             "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE,
#         })
# ---------------------------------------------------------------------------

# Active provider – swap to WindowsCredentialProvider() when ready
secrets: SecretsProvider = EnvSecretsProvider()
