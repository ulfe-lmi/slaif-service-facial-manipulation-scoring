"""Canonical image-to-score orchestration."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from .artifacts import verify_model_artifacts
from .backend import ScoreBackend, SelfMADBackend
from .config import Settings
from .preprocessing import AuthorCropper, InvalidImageError, decode_image
from .schemas import ImageMetadata, ScoreResult, ScoreStatus


class ScoringEngine:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        cropper: AuthorCropper | None = None,
        backend: ScoreBackend | None = None,
    ):
        self.settings = settings or Settings()
        self._cropper = cropper
        self._backend = backend
        self._lock = Lock()
        self._ready = cropper is not None and backend is not None
        self._load_error: str | None = None

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def load(self) -> None:
        if self._ready:
            return
        try:
            if self.settings.verify_artifact_checksums:
                verify_model_artifacts(
                    self.settings.checkpoint_path,
                    self.settings.landmark_model_path,
                )
            self._cropper = AuthorCropper(self.settings.landmark_model_path)
            self._backend = SelfMADBackend(
                self.settings.selfmadpp_root,
                self.settings.checkpoint_path,
            )
            self._backend.load()
        except Exception as exc:
            self._load_error = str(exc)
            self._ready = False
            raise
        self._load_error = None
        self._ready = True

    def score_path(self, path: Path) -> ScoreResult:
        if not path.is_file():
            raise FileNotFoundError(path)
        data = path.read_bytes()
        return self.score_bytes(data, filename=path.name)

    def score_preprocessed_path(self, path: Path) -> ScoreResult:
        """Score a crop already produced by the pinned author preprocessing."""
        if not path.is_file():
            raise FileNotFoundError(path)
        return self.score_preprocessed_bytes(path.read_bytes(), filename=path.name)

    def score_bytes(self, data: bytes, *, filename: str | None = None) -> ScoreResult:
        if len(data) > self.settings.max_upload_bytes:
            raise InvalidImageError(
                f"Image exceeds the {self.settings.max_upload_bytes} byte upload limit."
            )
        if not self._ready:
            self.load()
        assert self._cropper is not None
        assert self._backend is not None

        frame = decode_image(data, max_pixels=self.settings.max_image_pixels)
        outcome = self._cropper.crop(frame)
        if outcome.image_rgb is None:
            return ScoreResult(
                status=ScoreStatus.UNSCORABLE,
                reason="no_face_detected",
                image=ImageMetadata(
                    filename=filename,
                    width=outcome.source_width,
                    height=outcome.source_height,
                    detected_faces=outcome.detected_faces,
                ),
            )

        crop_height, crop_width = outcome.image_rgb.shape[:2]
        with self._lock:
            score = self._backend.score(outcome.image_rgb)
        return ScoreResult(
            status=ScoreStatus.SCORED,
            score=score,
            image=ImageMetadata(
                filename=filename,
                width=outcome.source_width,
                height=outcome.source_height,
                detected_faces=outcome.detected_faces,
                crop_box_xyxy=outcome.box_xyxy,
                crop_width=crop_width,
                crop_height=crop_height,
            ),
        )

    def score_preprocessed_bytes(self, data: bytes, *, filename: str | None = None) -> ScoreResult:
        if len(data) > self.settings.max_upload_bytes:
            raise InvalidImageError(
                f"Image exceeds the {self.settings.max_upload_bytes} byte upload limit."
            )
        if not self._ready:
            self.load()
        assert self._backend is not None
        frame = decode_image(data, max_pixels=self.settings.max_image_pixels)
        height, width = frame.shape[:2]
        with self._lock:
            score = self._backend.score(frame)
        return ScoreResult(
            status=ScoreStatus.SCORED,
            score=score,
            image=ImageMetadata(
                filename=filename,
                width=width,
                height=height,
                detected_faces=1,
                crop_box_xyxy=(0, 0, width, height),
                crop_width=width,
                crop_height=height,
            ),
        )
