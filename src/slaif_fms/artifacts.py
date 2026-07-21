"""Artifact integrity checks."""

import hashlib
from pathlib import Path

from .constants import CHECKPOINT_SHA256, LANDMARK_MODEL_SHA256


def sha256_file(path: Path, *, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"Required artifact does not exist: {path}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise RuntimeError(f"SHA-256 mismatch for {path}: expected {expected_sha256}, got {actual}")


def verify_model_artifacts(checkpoint_path: Path, landmark_model_path: Path) -> None:
    verify_file(checkpoint_path, CHECKPOINT_SHA256)
    verify_file(landmark_model_path, LANDMARK_MODEL_SHA256)
