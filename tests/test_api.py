from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from slaif_fms.api import create_app
from slaif_fms.auth import ApiKeyConfigurationError
from slaif_fms.config import Settings
from slaif_fms.service import ScoringEngine
from tests.test_service import FakeBackend, FakeCropper, image_bytes, settings

EXPECTED_AUTH_ERROR = {
    "error": {
        "code": "invalid_api_key",
        "message": "A valid API key is required.",
    }
}


def configured_settings(api_key_file: Path) -> Settings:
    config = settings()
    config.api_key_file = api_key_file
    return config


def fake_engine(config: Settings) -> ScoringEngine:
    return ScoringEngine(config, cropper=FakeCropper(), backend=FakeBackend())


def score(client: TestClient, *, api_key: str | None = None):
    headers = {"X-API-Key": api_key} if api_key is not None else {}
    return client.post(
        "/v1/score",
        headers=headers,
        files={"image": ("face.png", image_bytes(), "image/png")},
    )


def test_health_readiness_and_score() -> None:
    config = settings()
    engine = fake_engine(config)
    with TestClient(create_app(config, engine=engine)) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.get("/readyz").status_code == 200
        response = score(client)
        openapi = client.get("/openapi.json").json()
    assert response.status_code == 200
    assert response.json()["score"] == 0.625
    assert "security" not in openapi["paths"]["/v1/score"]["post"]
    assert "securitySchemes" not in openapi.get("components", {})


def test_rejects_unsupported_content_type() -> None:
    config = settings()
    engine = fake_engine(config)
    with TestClient(create_app(config, engine=engine)) as client:
        response = client.post(
            "/v1/score",
            files={"image": ("face.gif", b"GIF89a", "image/gif")},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_media_type"


def test_api_key_protects_only_score_endpoint(tmp_path: Path) -> None:
    api_key_file = tmp_path / "api_key"
    api_key_file.write_text("correct-secret\n", encoding="utf-8")
    config = configured_settings(api_key_file)

    with TestClient(create_app(config, engine=fake_engine(config))) as client:
        missing = score(client)
        incorrect = score(client, api_key="incorrect-secret")
        correct = score(client, api_key="correct-secret")

        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200
        assert client.get("/docs").status_code == 200
        openapi_response = client.get("/openapi.json")

    assert missing.status_code == 401
    assert missing.json() == EXPECTED_AUTH_ERROR
    assert incorrect.status_code == 401
    assert incorrect.json() == EXPECTED_AUTH_ERROR
    assert correct.status_code == 200

    openapi = openapi_response.json()
    scheme = openapi["components"]["securitySchemes"]["ApiKeyAuth"]
    assert scheme["type"] == "apiKey"
    assert scheme["in"] == "header"
    assert scheme["name"] == "X-API-Key"
    assert openapi["paths"]["/v1/score"]["post"]["security"] == [{"ApiKeyAuth": []}]
    for path in ("/healthz", "/readyz"):
        assert "security" not in openapi["paths"][path]["get"]


def test_api_key_is_reloaded_only_when_app_is_recreated(tmp_path: Path) -> None:
    api_key_file = tmp_path / "api_key"
    api_key_file.write_text("first-secret", encoding="utf-8")
    config = configured_settings(api_key_file)
    first_app = create_app(config, engine=fake_engine(config))
    api_key_file.write_text("second-secret", encoding="utf-8")

    with TestClient(first_app) as client:
        assert score(client, api_key="first-secret").status_code == 200
        assert score(client, api_key="second-secret").status_code == 401

    with TestClient(create_app(config, engine=fake_engine(config))) as client:
        assert score(client, api_key="first-secret").status_code == 401
        assert score(client, api_key="second-secret").status_code == 200


@pytest.mark.parametrize("invalid_kind", ["empty", "directory"])
def test_invalid_api_key_path_fails_app_creation(tmp_path: Path, invalid_kind: str) -> None:
    api_key_path = tmp_path / "api_key"
    if invalid_kind == "empty":
        api_key_path.write_text(" \n", encoding="utf-8")
    else:
        api_key_path.mkdir()

    config = configured_settings(api_key_path)
    with pytest.raises(ApiKeyConfigurationError):
        create_app(config, engine=fake_engine(config))
