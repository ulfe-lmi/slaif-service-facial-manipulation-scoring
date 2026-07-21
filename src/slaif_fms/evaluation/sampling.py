"""Deterministic balanced sampling for manifest rows."""

from __future__ import annotations

import csv
import random
from pathlib import Path


def balanced_sample(
    input_path: Path,
    output_path: Path,
    *,
    fraction: float,
    seed: int,
    label_column: str = "label",
) -> dict[str, int | float]:
    if not 0.0 < fraction <= 1.0:
        raise ValueError("fraction must be in (0, 1].")
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if label_column not in fieldnames:
        raise ValueError(f"Manifest does not contain {label_column!r}.")
    classes = {label: [row for row in rows if row[label_column] == str(label)] for label in (0, 1)}
    if any(not class_rows for class_rows in classes.values()):
        raise ValueError("Balanced sampling requires both labels.")
    target_total = int(round(len(rows) * fraction))
    target_total += target_total % 2
    per_class = min(target_total // 2, *(len(class_rows) for class_rows in classes.values()))
    if per_class < 1:
        raise ValueError("Requested fraction produces an empty class.")
    rng = random.Random(seed)
    sample = rng.sample(classes[0], per_class) + rng.sample(classes[1], per_class)
    rng.shuffle(sample)
    extra_fields = ["sample_seed", "sample_fraction", "sample_per_class"]
    for field in extra_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    for row in sample:
        row.update(
            {
                "sample_seed": str(seed),
                "sample_fraction": f"{fraction:.9g}",
                "sample_per_class": str(per_class),
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample)
    return {
        "source_rows": len(rows),
        "selected_rows": len(sample),
        "selected_per_class": per_class,
        "fraction_requested": fraction,
        "seed": seed,
    }
