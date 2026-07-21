from pathlib import Path

import pytest

from slaif_fms.auth import ApiKeyConfigurationError, load_api_key


def test_missing_api_key_file_disables_authentication(tmp_path: Path) -> None:
    assert load_api_key(tmp_path / "missing") is None


def test_unreadable_api_key_file_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_key_file = tmp_path / "api_key"
    api_key_file.write_text("secret", encoding="utf-8")

    def fail_read(_: Path, *, encoding: str) -> str:
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "read_text", fail_read)
    with pytest.raises(ApiKeyConfigurationError, match="Cannot read API key file"):
        load_api_key(api_key_file)


def test_non_utf8_api_key_file_fails_closed(tmp_path: Path) -> None:
    api_key_file = tmp_path / "api_key"
    api_key_file.write_bytes(b"\xff")

    with pytest.raises(ApiKeyConfigurationError, match="not valid UTF-8"):
        load_api_key(api_key_file)
