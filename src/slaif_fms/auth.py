"""Optional API-key authentication for scoring requests."""

from __future__ import annotations

import secrets
import stat
from pathlib import Path

API_KEY_HEADER = "X-API-Key"
INVALID_API_KEY_CODE = "invalid_api_key"
INVALID_API_KEY_MESSAGE = "A valid API key is required."


class ApiKeyConfigurationError(RuntimeError):
    """Raised when a configured API-key file is unsafe or unreadable."""


class InvalidApiKeyError(Exception):
    """Raised when a protected request does not provide the configured key."""


def load_api_key(path: Path) -> str | None:
    """Read an optional API key, failing closed when an existing path is invalid."""
    try:
        file_stat = path.stat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ApiKeyConfigurationError(f"Cannot access API key file: {path}") from exc

    if not stat.S_ISREG(file_stat.st_mode):
        raise ApiKeyConfigurationError(f"API key path is not a regular file: {path}")

    try:
        api_key = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ApiKeyConfigurationError(f"API key file is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise ApiKeyConfigurationError(f"Cannot read API key file: {path}") from exc

    if not api_key:
        raise ApiKeyConfigurationError(f"API key file is empty: {path}")
    return api_key


def api_keys_match(provided: str | None, expected: str) -> bool:
    """Compare keys without leaking their matching prefix through timing."""
    if provided is None:
        return False
    return secrets.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))
