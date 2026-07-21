"""Evaluation command group."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .gallery import generate_gallery
from .profile import profile_reference
from .publication import sanitize_score_rows
from .records import read_score_records
from .report import evaluate_records
from .sampling import balanced_sample
from .scoring import score_manifest

app = typer.Typer(no_args_is_help=True, help="Evaluate frozen scores and profile reference data.")


@app.command("report")
def report(
    scores_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")],
    dataset: Annotated[str, typer.Option("--dataset")],
    bootstrap_iterations: Annotated[int, typer.Option("--bootstrap-iterations")] = 1000,
) -> None:
    """Generate metrics and plots from an existing score CSV."""
    records = read_score_records(scores_csv, dataset=dataset)
    result = evaluate_records(
        records,
        output_dir,
        dataset=dataset,
        bootstrap_iterations=bootstrap_iterations,
    )
    typer.echo(json.dumps(result, indent=2, sort_keys=True))


@app.command("profile-reference")
def reference_profile(
    scores_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")],
    name: Annotated[str, typer.Option("--name")] = "customer",
    percentiles: Annotated[str, typer.Option("--percentiles")] = "0.95,0.99,0.999",
) -> None:
    """Describe an untouched label-0 reference score distribution."""
    values = tuple(float(value) for value in percentiles.split(","))
    result = profile_reference(
        read_score_records(scores_csv),
        output_dir,
        name=name,
        percentiles=values,
    )
    typer.echo(json.dumps(result, indent=2, sort_keys=True))


@app.command("sample-balanced")
def sample_balanced(
    manifest_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_csv: Annotated[Path, typer.Option("--output", "-o")],
    fraction: Annotated[float, typer.Option("--fraction")],
    seed: Annotated[int, typer.Option("--seed")] = 20260718,
    label_column: Annotated[str, typer.Option("--label-column")] = "label",
) -> None:
    """Create a deterministic class-balanced manifest sample."""
    result = balanced_sample(
        manifest_csv,
        output_csv,
        fraction=fraction,
        seed=seed,
        label_column=label_column,
    )
    typer.echo(json.dumps(result, indent=2, sort_keys=True))


@app.command("gallery")
def gallery(
    scores_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")],
    dataset: Annotated[str, typer.Option("--dataset")],
    public: Annotated[bool, typer.Option("--public/--local-only")] = False,
    permissions: Annotated[Path | None, typer.Option("--permissions")] = None,
    group_by: Annotated[str | None, typer.Option("--group-by")] = None,
) -> None:
    """Copy exact low/high exemplars into a local rights-aware gallery."""
    count = generate_gallery(
        read_score_records(scores_csv, dataset=dataset),
        output_dir,
        dataset=dataset,
        public=public,
        permissions_path=permissions,
        group_by=group_by,
    )
    typer.echo(f"Wrote {count} exemplars to {output_dir}")


@app.command("sanitize-public-rows")
def sanitize_public_rows(
    scores_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_csv: Annotated[Path, typer.Option("--output", "-o")],
    dataset: Annotated[str, typer.Option("--dataset")],
) -> None:
    """Strip local paths and enforce the dataset publication policy."""
    count = sanitize_score_rows(scores_csv, output_csv, dataset=dataset)
    typer.echo(f"Wrote {count} sanitized rows to {output_csv}")


@app.command("score-manifest")
def manifest_score(
    manifest_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_csv: Annotated[Path, typer.Option("--output", "-o")],
    dataset: Annotated[str, typer.Option("--dataset")],
    source_column: Annotated[str, typer.Option("--source-column")] = "source_path",
    preprocessed: Annotated[bool, typer.Option("--preprocessed/--raw")] = False,
    resume: Annotated[bool, typer.Option("--resume/--no-resume")] = True,
    num_shards: Annotated[int, typer.Option("--num-shards")] = 1,
    shard_index: Annotated[int, typer.Option("--shard-index")] = 0,
) -> None:
    """Score a normalized manifest with deterministic sharding and resume."""
    result = score_manifest(
        manifest_csv,
        output_csv,
        dataset=dataset,
        source_column=source_column,
        preprocessed=preprocessed,
        resume=resume,
        num_shards=num_shards,
        shard_index=shard_index,
    )
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
