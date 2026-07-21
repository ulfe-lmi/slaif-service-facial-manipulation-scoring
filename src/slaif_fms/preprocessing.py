"""Faithful implementation of the pinned SelfMAD++ author crop."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class InvalidImageError(ValueError):
    """Raised when bytes cannot be decoded as a supported image."""


@dataclass(frozen=True)
class CropOutcome:
    image_rgb: np.ndarray | None
    source_width: int
    source_height: int
    detected_faces: int
    box_xyxy: tuple[int, int, int, int] | None


def decode_image(data: bytes, *, max_pixels: int) -> np.ndarray:
    encoded = np.frombuffer(data, dtype=np.uint8)
    frame_bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if frame_bgr is None:
        raise InvalidImageError("The upload is not a decodable JPEG, PNG, or WebP image.")
    height, width = frame_bgr.shape[:2]
    if height * width > max_pixels:
        raise InvalidImageError(f"Decoded image exceeds the {max_pixels} pixel limit.")
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)


def landmark_crop_box(
    landmarks: np.ndarray,
    *,
    frame_width: int,
    frame_height: int,
    margin_percent: float = 12.5,
) -> tuple[int, int, int, int]:
    """Return the exact unpadded box used by the pinned author script."""
    points = np.asarray(landmarks)
    if points.size == 0 or points.shape[-1] != 2:
        raise ValueError("Expected non-empty landmarks with final dimension (x, y).")
    if points.ndim > 2:
        points = points.reshape(-1, points.shape[-1])

    min_xy = np.min(points, axis=0)
    max_xy = np.max(points, axis=0)
    left, top = min_xy.astype(int)
    right, bottom = max_xy.astype(int)
    margin_percent = max(margin_percent, 0.0)
    pad_h = int(round((bottom - top) * (margin_percent / 100.0)))
    pad_w = int(round((right - left) * (margin_percent / 100.0)))
    return (
        max(left - pad_w, 0),
        max(top - pad_h, 0),
        min(right + pad_w, frame_width),
        min(bottom + pad_h, frame_height),
    )


def shape_to_array(shape: Any) -> np.ndarray:
    return np.asarray([(shape.part(i).x, shape.part(i).y) for i in range(shape.num_parts)])


class AuthorCropper:
    """Detect and crop the largest face exactly as upstream `crop.py` does."""

    def __init__(self, predictor_path: Path, *, detector: Any = None, predictor: Any = None):
        if detector is None or predictor is None:
            try:
                import dlib
            except ImportError as exc:  # pragma: no cover - depends on model environment
                raise RuntimeError("dlib is required for author-crop preprocessing.") from exc
            detector = detector or dlib.get_frontal_face_detector()
            predictor = predictor or dlib.shape_predictor(str(predictor_path))
        self.detector = detector
        self.predictor = predictor

    def crop(self, frame_rgb: np.ndarray) -> CropOutcome:
        height, width = frame_rgb.shape[:2]
        faces = self.detector(frame_rgb, 1)
        largest_area = 0
        largest_landmarks: np.ndarray | None = None
        for rectangle in faces:
            landmarks = shape_to_array(self.predictor(frame_rgb, rectangle))
            x0, y0 = landmarks[:, 0].min(), landmarks[:, 1].min()
            x1, y1 = landmarks[:, 0].max(), landmarks[:, 1].max()
            area = int((x1 - x0) * (y1 - y0))
            if area > largest_area:
                largest_area = area
                largest_landmarks = landmarks

        if largest_landmarks is None:
            return CropOutcome(None, width, height, len(faces), None)

        box = landmark_crop_box(
            largest_landmarks,
            frame_width=width,
            frame_height=height,
        )
        left, top, right, bottom = box
        if left >= right or top >= bottom:
            return CropOutcome(None, width, height, len(faces), None)
        return CropOutcome(frame_rgb[top:bottom, left:right], width, height, len(faces), box)
