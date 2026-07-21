"""Public CLI and HTTP response schemas."""

from enum import Enum

from pydantic import BaseModel, Field

from .constants import (
    CHECKPOINT_SHA256,
    CROP_SCRIPT_SHA256,
    MODEL_VERSION,
    PREPROCESSING_VERSION,
    SCORE_DIRECTION,
    SCORE_TYPE,
    SELFMADPP_COMMIT,
)


class ScoreStatus(str, Enum):
    SCORED = "scored"
    UNSCORABLE = "unscorable"


class ModelIdentity(BaseModel):
    name: str = "SelfMAD++"
    version: str = MODEL_VERSION
    upstream_commit: str = SELFMADPP_COMMIT
    checkpoint_sha256: str = CHECKPOINT_SHA256


class PreprocessingIdentity(BaseModel):
    name: str = "SelfMAD++ author crop"
    version: str = PREPROCESSING_VERSION
    upstream_crop_sha256: str = CROP_SCRIPT_SHA256
    face_selection: str = "largest_landmark_bounding_box"
    landmark_margin_percent: float = 12.5
    model_input_size: int = 512


class ImageMetadata(BaseModel):
    filename: str | None = None
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    detected_faces: int = Field(ge=0)
    crop_box_xyxy: tuple[int, int, int, int] | None = None
    crop_width: int | None = Field(default=None, ge=1)
    crop_height: int | None = Field(default=None, ge=1)


class ScoreResult(BaseModel):
    status: ScoreStatus
    score: float | None = Field(default=None, ge=0, le=1)
    score_type: str = SCORE_TYPE
    higher_means: str = SCORE_DIRECTION
    reason: str | None = None
    image: ImageMetadata
    model: ModelIdentity = Field(default_factory=ModelIdentity)
    preprocessing: PreprocessingIdentity = Field(default_factory=PreprocessingIdentity)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
