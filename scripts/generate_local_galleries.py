#!/usr/bin/env python3
"""Generate rights-restricted low/high image examples outside the repository."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from slaif_fms.evaluation.gallery import exemplar_records, generate_gallery
from slaif_fms.evaluation.records import ScoreRecord, read_score_records, write_csv

DATASETS = {
    "str_ffhq_fm": "str_ffhq_fm/scores/selfmadpp_str_ffhq_fm_author_crop_full_scores.csv",
    "readfake": "readfake/scores/selfmadpp_readfake_author_crop_full_scores.csv",
    "celebhq_fm": "celebhq_fm/scores/selfmadpp_celebhq_fm_author_crop_full_scores.csv",
    "ffhqr": "ffhqr/scores/selfmadpp_ffhqr_author_crop_full_scores.csv",
    "ppr10k": "ppr10k/scores/selfmadpp_ppr10k_author_crop_full_scores.csv",
    "mffi": "mffi/scores/selfmadpp_mffi_author_crop_full_scores.csv",
    "ffhq": "ffhq/scores/selfmadpp_ffhq_author_crop_all_scores.csv",
}
OPERATIONS = {
    "Whitening": "has_whitening",
    "Smoothing": "has_smoothing",
    "FaceLifting": "has_facelifting",
    "EyeEnlarging": "has_eyeenlarging",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def retouch_gallery_records(source_root: Path) -> list[ScoreRecord]:
    retouch_rows = read_rows(
        source_root
        / (
            "retouchingffhq/scores/"
            "selfmadpp_retouchingffhq_author_crop_sample50000_scores.csv"
        )
    )
    ffhq_rows = read_rows(
        source_root / "ffhq/scores/selfmadpp_ffhq_author_crop_all_scores_enriched.csv"
    )
    ffhq_by_id = {row["ffhq_id"].zfill(5): row for row in ffhq_rows}
    records: list[ScoreRecord] = []
    seen_real: set[tuple[str, str]] = set()
    for index, row in enumerate(retouch_rows):
        ffhq_id = row["ffhq_id"].zfill(5)
        for operation, flag in OPERATIONS.items():
            if row.get(flag) != "1":
                continue
            records.append(
                ScoreRecord(
                    relative_id=f"retouched-{index:06d}",
                    label=1,
                    score=float(row["prob_morph"]),
                    dataset="retouchingffhq",
                    path=row["out_path"],
                    groups={"operation": operation},
                )
            )
            real_key = (operation, ffhq_id)
            real = ffhq_by_id.get(ffhq_id)
            if real and real_key not in seen_real:
                seen_real.add(real_key)
                records.append(
                    ScoreRecord(
                        relative_id=f"ffhq-{ffhq_id}",
                        label=0,
                        score=float(real["prob_morph"]),
                        dataset="retouchingffhq",
                        path=real["path"],
                        groups={"operation": operation},
                    )
                )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--summary", type=Path, default=None)
    parser.add_argument("--extremes-summary", type=Path, default=None)
    args = parser.parse_args()
    summary_rows: list[dict[str, object]] = []
    extreme_rows: list[dict[str, object]] = []
    for dataset, relative_path in DATASETS.items():
        records = read_score_records(args.source_root / relative_path, dataset=dataset)
        output = args.output_root / dataset
        count = generate_gallery(records, output, dataset=dataset)
        summary_rows.append(
            {"dataset": dataset, "images": count, "groups": "overall", "public": False}
        )
        extreme_rows.extend(
            {
                "dataset": dataset,
                "group": "overall",
                "role": role,
                "score": record.score,
                "image_published": False,
            }
            for role, record in exemplar_records(records)
        )

    retouch_records = retouch_gallery_records(args.source_root)
    output = args.output_root / "retouchingffhq"
    count = generate_gallery(
        retouch_records,
        output,
        dataset="retouchingffhq",
        group_by="operation",
    )
    summary_rows.append(
        {
            "dataset": "retouchingffhq",
            "images": count,
            "groups": "overall and operation",
            "public": False,
        }
    )
    extreme_rows.extend(
        {
            "dataset": "retouchingffhq",
            "group": group,
            "role": role,
            "score": record.score,
            "image_published": False,
        }
        for group, group_records in [
            ("overall", retouch_records),
            *[
                (
                    f"operation_{operation}",
                    [
                        record
                        for record in retouch_records
                        if record.groups.get("operation") == operation
                    ],
                )
                for operation in OPERATIONS
            ],
        ]
        for role, record in exemplar_records(group_records)
    )
    if args.summary:
        write_csv(args.summary, ["dataset", "images", "groups", "public"], summary_rows)
    if args.extremes_summary:
        write_csv(
            args.extremes_summary,
            ["dataset", "group", "role", "score", "image_published"],
            extreme_rows,
        )
    print(f"Generated {sum(int(row['images']) for row in summary_rows)} local exemplar images")


if __name__ == "__main__":
    main()
