from pathlib import Path

import cv2
import numpy as np

from slaif_fms.config import Settings
from slaif_fms.preprocessing import CropOutcome
from slaif_fms.schemas import ScoreStatus
from slaif_fms.service import ScoringEngine


class FakeCropper:
    def __init__(self, *, face: bool = True):
        self.face = face

    def crop(self, frame_rgb: np.ndarray) -> CropOutcome:
        height, width = frame_rgb.shape[:2]
        if not self.face:
            return CropOutcome(None, width, height, 0, None)
        return CropOutcome(frame_rgb[1:3, 1:4], width, height, 1, (1, 1, 4, 3))


class FakeBackend:
    def load(self) -> None:
        pass

    def score(self, image_rgb: np.ndarray) -> float:
        assert image_rgb.shape == (2, 3, 3)
        return 0.625


def image_bytes() -> bytes:
    ok, encoded = cv2.imencode(".png", np.zeros((5, 6, 3), dtype=np.uint8))
    assert ok
    return encoded.tobytes()


def settings() -> Settings:
    return Settings(
        selfmadpp_root=Path("vendor/SelfMADpp"),
        checkpoint_path=Path("unused"),
        landmark_model_path=Path("unused"),
        verify_artifact_checksums=False,
        eager_load=False,
    )


def test_score_result_has_stable_semantics() -> None:
    engine = ScoringEngine(settings(), cropper=FakeCropper(), backend=FakeBackend())
    result = engine.score_bytes(image_bytes(), filename="face.png")
    assert result.status is ScoreStatus.SCORED
    assert result.score == 0.625
    assert result.higher_means == "higher_means_stronger_manipulation_indication"
    assert result.image.crop_box_xyxy == (1, 1, 4, 3)


def test_no_face_is_unscorable_not_low_score() -> None:
    engine = ScoringEngine(settings(), cropper=FakeCropper(face=False), backend=FakeBackend())
    result = engine.score_bytes(image_bytes())
    assert result.status is ScoreStatus.UNSCORABLE
    assert result.score is None
    assert result.reason == "no_face_detected"


def test_preprocessed_scoring_does_not_apply_cropper() -> None:
    class FailingCropper(FakeCropper):
        def crop(self, frame_rgb: np.ndarray) -> CropOutcome:
            raise AssertionError("cropper must not run")

    class FullFrameBackend(FakeBackend):
        def score(self, image_rgb: np.ndarray) -> float:
            assert image_rgb.shape == (5, 6, 3)
            return 0.25

    engine = ScoringEngine(
        settings(),
        cropper=FailingCropper(),
        backend=FullFrameBackend(),
    )
    result = engine.score_preprocessed_bytes(image_bytes())
    assert result.score == 0.25
