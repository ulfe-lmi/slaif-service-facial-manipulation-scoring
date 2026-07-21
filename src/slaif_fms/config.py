"""Runtime configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import DEFAULT_MAX_IMAGE_PIXELS, DEFAULT_MAX_UPLOAD_BYTES


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SLAIF_FMS_", case_sensitive=False)

    selfmadpp_root: Path = Path("vendor/SelfMADpp")
    checkpoint_path: Path = Path("models/SelfMADpp_SMDD.tar")
    landmark_model_path: Path = Path("models/shape_predictor_81_face_landmarks.dat")
    api_key_file: Path = Path("secrets/api_key")
    max_upload_bytes: int = Field(default=DEFAULT_MAX_UPLOAD_BYTES, ge=1)
    max_image_pixels: int = Field(default=DEFAULT_MAX_IMAGE_PIXELS, ge=1)
    verify_artifact_checksums: bool = True
    eager_load: bool = True
