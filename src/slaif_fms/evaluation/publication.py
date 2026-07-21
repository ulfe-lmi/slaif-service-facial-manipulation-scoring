"""Fail-closed controls for publishing score rows and dataset assets."""

from __future__ import annotations

import csv
import json
from importlib.resources import files
from pathlib import Path


def dataset_registry() -> dict[str, dict[str, object]]:
    path = files("slaif_fms.resources").joinpath("datasets.json")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_identified_rows_publishable(dataset: str) -> None:
    policy = dataset_registry().get(dataset)
    if policy is None:
        raise ValueError(f"Unknown dataset policy: {dataset}")
    if policy.get("identified_rows_public") is not True:
        raise PermissionError(f"Identified score rows are not approved for publication: {dataset}")


def sanitize_score_rows(input_path: Path, output_path: Path, *, dataset: str) -> int:
    assert_identified_rows_publishable(dataset)
    with input_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fieldnames = [
        "dataset",
        "relative_id",
        "label",
        "score",
        "status",
        "split",
        "operation",
        "provider",
        "operation_count",
        "operation_level",
    ]
    sanitized = []
    for index, row in enumerate(rows, start=1):
        relative_id = row.get("relative_id") or row.get("relpath") or f"row-{index:08d}"
        if Path(relative_id).is_absolute() or ".." in Path(relative_id).parts:
            raise ValueError(f"Unsafe relative identifier: {relative_id}")
        sanitized.append(
            {
                **{field: row.get(field, "") for field in fieldnames},
                "dataset": dataset,
                "relative_id": relative_id,
                "label": row.get("label") or row.get("label_id") or row.get("target_label"),
                "score": row.get("score") or row.get("prob_morph"),
                "status": row.get("status", "scored"),
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sanitized)
    return len(sanitized)
