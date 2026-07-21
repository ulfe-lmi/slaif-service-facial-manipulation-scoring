"""Command-line interface."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Annotated

import typer

from .artifacts import verify_model_artifacts
from .config import Settings
from .evaluation.cli import app as evaluation_app
from .service import ScoringEngine

app = typer.Typer(no_args_is_help=True, help="Score facial images with SelfMAD++.")
app.add_typer(evaluation_app, name="evaluation")


@app.command()
def score(
    image: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[str, typer.Option("--output", help="Output format: json or text.")] = "json",
) -> None:
    """Apply author cropping and score one image."""
    result = ScoringEngine().score_path(image)
    if output == "json":
        typer.echo(result.model_dump_json(indent=2))
    elif output == "text":
        value = "unscorable" if result.score is None else f"{result.score:.9f}"
        typer.echo(f"status: {result.status.value}\nscore: {value}\nreason: {result.reason or ''}")
    else:
        raise typer.BadParameter("--output must be json or text")


@app.command("score-batch")
def score_batch(
    input_path: Annotated[Path, typer.Argument(exists=True, readable=True)],
    output_path: Annotated[Path, typer.Option("--output-path", "-o")],
    output_format: Annotated[str, typer.Option("--format")] = "jsonl",
    recursive: Annotated[bool, typer.Option("--recursive/--no-recursive")] = True,
) -> None:
    """Score an image or every supported image below a directory."""
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if input_path.is_file():
        paths = [input_path]
    else:
        iterator = input_path.rglob("*") if recursive else input_path.glob("*")
        paths = sorted(
            path for path in iterator if path.is_file() and path.suffix.lower() in extensions
        )
    if not paths:
        raise typer.BadParameter("No supported images found.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = ScoringEngine()
    rows = []
    for path in paths:
        result = engine.score_path(path)
        row = {"path": str(path), **result.model_dump(mode="json")}
        rows.append(row)

    if output_format == "jsonl":
        with output_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    elif output_format == "csv":
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["path", "status", "score", "reason"])
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key) for key in writer.fieldnames})
    else:
        raise typer.BadParameter("--format must be jsonl or csv")
    typer.echo(f"Wrote {len(rows)} results to {output_path}")


@app.command("verify-artifacts")
def verify_artifacts() -> None:
    """Verify the configured checkpoint and landmark-model checksums."""
    settings = Settings()
    verify_model_artifacts(settings.checkpoint_path, settings.landmark_model_path)
    typer.echo("Model artifacts match the pinned SHA-256 checksums.")
