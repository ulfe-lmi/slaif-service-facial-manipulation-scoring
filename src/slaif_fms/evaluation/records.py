"""Canonical score-table records and CSV I/O."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ScoreRecord:
    relative_id: str
    label: int
    score: float
    dataset: str = ""
    path: str = ""
    groups: dict[str, str] = field(default_factory=dict)


LABEL_COLUMNS = ("label", "label_id", "target_label")
SCORE_COLUMNS = ("score", "prob_morph")
ID_COLUMNS = ("relative_id", "relpath", "manifest_relpath", "virtual_path", "path")
GROUP_COLUMNS = (
    "split",
    "subset",
    "operation",
    "provider",
    "operation_count",
    "operation_level",
    "method",
    "category",
)


def first_value(row: dict[str, str], candidates: tuple[str, ...]) -> str:
    for name in candidates:
        value = row.get(name, "").strip()
        if value:
            return value
    return ""


def read_score_records(path: Path, *, dataset: str = "") -> list[ScoreRecord]:
    records: list[ScoreRecord] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for index, row in enumerate(csv.DictReader(handle), start=2):
            status = row.get("status", "").strip().lower()
            if status and status not in {"scored", "ok"}:
                continue
            label_value = first_value(row, LABEL_COLUMNS)
            score_value = first_value(row, SCORE_COLUMNS)
            if score_value == "":
                continue
            if label_value == "" or score_value == "":
                raise ValueError(f"Missing label or score in {path}:{index}")
            label = int(label_value)
            score = float(score_value)
            if label not in {0, 1}:
                raise ValueError(f"Label must be 0 or 1 in {path}:{index}")
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Score must be in [0, 1] in {path}:{index}")
            relative_id = first_value(row, ID_COLUMNS) or f"row-{index - 1:08d}"
            groups = {name: row[name] for name in GROUP_COLUMNS if row.get(name, "") != ""}
            records.append(
                ScoreRecord(
                    relative_id=relative_id,
                    label=label,
                    score=score,
                    dataset=row.get("dataset", dataset) or dataset,
                    path=row.get("path", ""),
                    groups=groups,
                )
            )
    return records


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
