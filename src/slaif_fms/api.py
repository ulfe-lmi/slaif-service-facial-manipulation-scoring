"""FastAPI application for stateless facial manipulation scoring."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse

from .config import Settings
from .preprocessing import InvalidImageError
from .schemas import ErrorDetail, ErrorResponse, ScoreResult
from .service import ScoringEngine


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    content = ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump(mode="json")
    return JSONResponse(status_code=status_code, content=content)


def create_app(
    settings: Settings | None = None,
    *,
    engine: ScoringEngine | None = None,
) -> FastAPI:
    app_settings = settings or Settings()
    scoring_engine = engine or ScoringEngine(app_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if app_settings.eager_load and not scoring_engine.ready:
            scoring_engine.load()
        yield

    app = FastAPI(
        title="SLAIF Facial Manipulation Scoring",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.scoring_engine = scoring_engine
    app.state.settings = app_settings

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(request: Request) -> JSONResponse:
        current: ScoringEngine = request.app.state.scoring_engine
        if current.ready:
            return JSONResponse(status_code=200, content={"status": "ok", "model": "loaded"})
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "model": "not_loaded",
                "detail": current.load_error,
            },
        )

    @app.post(
        "/v1/score",
        response_model=ScoreResult,
        responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    )
    async def score_image(request: Request, image: Annotated[UploadFile, File()]):
        allowed = {"image/jpeg", "image/png", "image/webp", "application/octet-stream"}
        if image.content_type not in allowed:
            return error_response(400, "unsupported_media_type", "Use JPEG, PNG, or WebP.")
        settings_: Settings = request.app.state.settings
        data = await image.read(settings_.max_upload_bytes + 1)
        if len(data) > settings_.max_upload_bytes:
            return error_response(413, "image_too_large", "The uploaded image is too large.")
        engine_: ScoringEngine = request.app.state.scoring_engine
        try:
            return engine_.score_bytes(data, filename=image.filename)
        except InvalidImageError as exc:
            return error_response(400, "invalid_image", str(exc))

    return app


app = create_app()
