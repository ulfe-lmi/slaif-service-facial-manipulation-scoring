"""Resumable manifest scoring with deterministic process sharding."""

from __future__ import annotations

import csv
from pathlib import Path

from ..service import ScoringEngine
from .adapters import normalized_label
from .records import GROUP_COLUMNS

OUTPUT_FIELDS = [
    "dataset",
    "relative_id",
    "label",
    "path",
    "status",
    "score",
    "reason",
    "split",
    "operation",
    "provider",
    "operation_count",
    "operation_level",
    "method",
    "category",
    "input_preprocessing",
]


def score_manifest(
    manifest_path: Path,
    output_path: Path,
    *,
    dataset: str,
    source_column: str = "source_path",
    preprocessed: bool = False,
    resume: bool = True,
    num_shards: int = 1,
    shard_index: int = 0,
    engine: ScoringEngine | None = None,
) -> dict[str, int]:
    if num_shards < 1 or not 0 <= shard_index < num_shards:
        raise ValueError("Require num_shards >= 1 and 0 <= shard_index < num_shards.")
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows = rows[shard_index::num_shards]
    completed: set[str] = set()
    if resume and output_path.exists():
        with output_path.open(newline="", encoding="utf-8") as handle:
            completed = {row["relative_id"] for row in csv.DictReader(handle)}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not output_path.exists() or output_path.stat().st_size == 0
    scorer = engine or ScoringEngine()
    counts = {"selected": len(rows), "scored": 0, "unscorable": 0, "error": 0, "skipped": 0}
    with output_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        if write_header:
            writer.writeheader()
        for index, row in enumerate(rows):
            source_value = row.get(source_column, "")
            relative_id = (
                row.get("relative_id")
                or row.get("relpath")
                or row.get("virtual_path")
                or f"row-{shard_index}-{index:08d}"
            )
            if relative_id in completed:
                counts["skipped"] += 1
                continue
            result_row: dict[str, object] = {
                "dataset": dataset,
                "relative_id": relative_id,
                "label": normalized_label(dataset, row),
                "path": source_value,
                **{name: row.get(name, "") for name in GROUP_COLUMNS},
                "input_preprocessing": "author_crop" if preprocessed else "raw",
            }
            try:
                path = Path(source_value)
                result = (
                    scorer.score_preprocessed_path(path)
                    if preprocessed
                    else scorer.score_path(path)
                )
                result_row.update(
                    {
                        "status": result.status.value,
                        "score": "" if result.score is None else f"{result.score:.9g}",
                        "reason": result.reason or "",
                    }
                )
                counts[result.status.value] += 1
            except Exception as exc:  # continue long evaluations with an auditable row
                result_row.update(
                    {
                        "status": "error",
                        "score": "",
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
                counts["error"] += 1
            writer.writerow(result_row)
            handle.flush()
    return counts
