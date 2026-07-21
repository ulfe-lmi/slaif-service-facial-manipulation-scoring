"""Create local low/high score galleries from exact evaluated images."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from .publication import dataset_registry
from .records import ScoreRecord


def exemplar_records(records: list[ScoreRecord]) -> list[tuple[str, ScoreRecord]]:
    selected: list[tuple[str, ScoreRecord]] = []
    for label, class_name in ((0, "bona_fide"), (1, "manipulated")):
        class_records = sorted(
            (record for record in records if record.label == label),
            key=lambda item: item.score,
        )
        if class_records:
            selected.append((f"{class_name}_lowest", class_records[0]))
            selected.append((f"{class_name}_highest", class_records[-1]))
    return selected


def generate_gallery(
    records: list[ScoreRecord],
    output_dir: Path,
    *,
    dataset: str,
    public: bool = False,
    permissions_path: Path | None = None,
    group_by: str | None = None,
) -> int:
    policy = dataset_registry().get(dataset)
    if policy is None:
        raise ValueError(f"Unknown dataset policy: {dataset}")
    permissions: dict[str, dict[str, str]] = {}
    if permissions_path:
        permissions = json.loads(permissions_path.read_text(encoding="utf-8"))
    grouped_records: list[tuple[str, list[ScoreRecord]]] = [("overall", records)]
    if group_by:
        values = sorted(
            {record.groups[group_by] for record in records if group_by in record.groups}
        )
        grouped_records.extend(
            (
                f"{group_by}_{value}",
                [record for record in records if record.groups.get(group_by) == value],
            )
            for value in values
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for group, group_records in grouped_records:
        for role, record in exemplar_records(group_records):
            source = Path(record.path)
            if not source.is_file():
                raise FileNotFoundError(f"Gallery source does not exist: {source}")
            permission = permissions.get(record.relative_id)
            if public:
                if policy.get("images_public") is not True and not permission:
                    raise PermissionError(
                        f"Public image requires verified per-asset permission: {record.relative_id}"
                    )
                required = {"source_url", "author", "license", "license_url"}
                if not permission or not required.issubset(permission):
                    raise PermissionError(f"Incomplete attribution for {record.relative_id}")
            destination = output_dir / f"{group}_{role}_{record.score:.6f}{source.suffix.lower()}"
            shutil.copy2(source, destination)
            manifest_rows.append(
                {
                    "group": group,
                    "role": role,
                    "relative_id": record.relative_id,
                    "label": record.label,
                    "score": record.score,
                    "file": destination.name,
                    "source_url": (permission or {}).get("source_url", "local-only"),
                    "author": (permission or {}).get("author", "local-only"),
                    "license": (permission or {}).get("license", "not-for-redistribution"),
                    "license_url": (permission or {}).get("license_url", ""),
                }
            )
    with (output_dir / "gallery.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    return len(manifest_rows)
