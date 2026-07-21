from fastapi.testclient import TestClient

from slaif_fms.api import create_app
from slaif_fms.service import ScoringEngine
from tests.test_service import FakeBackend, FakeCropper, image_bytes, settings


def test_health_readiness_and_score() -> None:
    config = settings()
    engine = ScoringEngine(config, cropper=FakeCropper(), backend=FakeBackend())
    with TestClient(create_app(config, engine=engine)) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.get("/readyz").status_code == 200
        response = client.post(
            "/v1/score",
            files={"image": ("face.png", image_bytes(), "image/png")},
        )
    assert response.status_code == 200
    assert response.json()["score"] == 0.625


def test_rejects_unsupported_content_type() -> None:
    config = settings()
    engine = ScoringEngine(config, cropper=FakeCropper(), backend=FakeBackend())
    with TestClient(create_app(config, engine=engine)) as client:
        response = client.post(
            "/v1/score",
            files={"image": ("face.gif", b"GIF89a", "image/gif")},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_media_type"
