#!/usr/bin/env python3
"""Import existing SelfMAD++ scores without invoking the model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

from slaif_fms.evaluation.metrics import describe
from slaif_fms.evaluation.records import ScoreRecord, read_score_records, write_csv
from slaif_fms.evaluation.report import evaluate_records

DATASETS = {
    "str_ffhq_fm": "str_ffhq_fm/scores/selfmadpp_str_ffhq_fm_author_crop_full_scores.csv",
    "readfake": "readfake/scores/selfmadpp_readfake_author_crop_full_scores.csv",
    "celebhq_fm": "celebhq_fm/scores/selfmadpp_celebhq_fm_author_crop_full_scores.csv",
    "ffhqr": "ffhqr/scores/selfmadpp_ffhqr_author_crop_full_scores.csv",
    "ppr10k": "ppr10k/scores/selfmadpp_ppr10k_author_crop_full_scores.csv",
    "mffi": "mffi/scores/selfmadpp_mffi_author_crop_full_scores.csv",
    "ffhq": "ffhq/scores/selfmadpp_ffhq_author_crop_all_scores.csv",
}

DISPLAY_NAMES = {
    "str_ffhq_fm": "STR-FFHQ-FM",
    "readfake": "READFake",
    "celebhq_fm": "CelebHQ-FM",
    "ffhqr": "FFHQR",
    "ppr10k": "PPR10K",
    "mffi": "MFFI",
    "ffhq": "FFHQ control",
    "retouchingffhq": "RetouchingFFHQ",
}

EXPECTED = {
    "str_ffhq_fm": (3288, 0.900410248, 0.180046437),
    "readfake": (2135, 0.688332920, 0.372851386),
    "celebhq_fm": (14454, 0.944284623, 0.133543728),
    "ffhqr": (3991, 0.597943053, 0.428714662),
    "ppr10k": (25910, 0.466837940, 0.522061243),
    "mffi": (42374, 0.782433277, 0.287322455),
    "retouchingffhq": (84003, 0.686089604, 0.366665043),
}

COVERAGE = [
    {
        "dataset": "STR-FFHQ-FM",
        "official_or_reference_total": 3311,
        "locally_available": 3310,
        "selected": 3310,
        "scored": 3288,
        "selection_percent_reference": 99.969798,
        "scored_percent_reference": 99.305346,
        "scored_percent_selected": 99.335347,
        "selection": "all locally available metadata rows",
    },
    {
        "dataset": "READFake",
        "official_or_reference_total": 2136,
        "locally_available": 2136,
        "selected": 2136,
        "scored": 2135,
        "selection_percent_reference": 100.0,
        "scored_percent_reference": 99.953184,
        "scored_percent_selected": 99.953184,
        "selection": "all annotated archive rows",
    },
    {
        "dataset": "CelebHQ-FM",
        "official_or_reference_total": 14490,
        "locally_available": 14490,
        "selected": 14490,
        "scored": 14454,
        "selection_percent_reference": 100.0,
        "scored_percent_reference": 99.751553,
        "scored_percent_selected": 99.751553,
        "selection": "all rows; original _orig images define bona fide",
    },
    {
        "dataset": "FFHQR",
        "official_or_reference_total": 140000,
        "locally_available": 20000,
        "selected": 4000,
        "scored": 3991,
        "selection_percent_reference": 2.857143,
        "scored_percent_reference": 2.850714,
        "scored_percent_selected": 99.775,
        "selection": "balanced 20% of local ID slice 60000-69999",
    },
    {
        "dataset": "PPR10K",
        "official_or_reference_total": 44644,
        "locally_available": 44644,
        "selected": 44644,
        "scored": 25910,
        "selection_percent_reference": 100.0,
        "scored_percent_reference": 58.037810,
        "scored_percent_selected": 58.037810,
        "selection": "all 11161 sources and three retouched targets per source",
    },
    {
        "dataset": "MFFI",
        "official_or_reference_total": 1024000,
        "locally_available": 853739,
        "selected": 42688,
        "scored": 42374,
        "selection_percent_reference": 4.168750,
        "scored_percent_reference": 4.138086,
        "scored_percent_selected": 99.264196,
        "selection": "5% of local pool, uniformly random and class-balanced",
    },
    {
        "dataset": "RetouchingFFHQ",
        "official_or_reference_total": 739317,
        "locally_available": 729281,
        "selected": 50000,
        "scored": 49939,
        "selection_percent_reference": 6.763001,
        "scored_percent_reference": 6.754749,
        "scored_percent_selected": 99.878,
        "selection": "proportional stratified sample of pairable archive rows",
    },
    {
        "dataset": "FFHQ control",
        "official_or_reference_total": 70000,
        "locally_available": 69343,
        "selected": 69343,
        "scored": 69098,
        "selection_percent_reference": 99.061429,
        "scored_percent_reference": 98.711429,
        "scored_percent_selected": 99.646684,
        "selection": "all locally available official FFHQ images",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def public_rows(records: list[ScoreRecord], output_path: Path, dataset: str) -> None:
    rows = []
    for record in records:
        subset = record.groups.get("subset", "")
        relative_id = "/".join(part for part in (subset, record.relative_id) if part)
        if Path(relative_id).is_absolute() or ".." in Path(relative_id).parts:
            raise ValueError(f"Unsafe identifier: {relative_id}")
        rows.append(
            {
                "dataset": dataset,
                "relative_id": relative_id,
                "label": record.label,
                "score": f"{record.score:.9g}",
                "status": "scored",
            }
        )
    write_csv(output_path, ["dataset", "relative_id", "label", "score", "status"], rows)


def retouch_records(source_root: Path) -> tuple[list[ScoreRecord], list[dict[str, str]]]:
    retouch_path = source_root / (
        "retouchingffhq/scores/"
        "selfmadpp_retouchingffhq_author_crop_sample50000_scores.csv"
    )
    ffhq_path = source_root / "ffhq/scores/selfmadpp_ffhq_author_crop_all_scores_enriched.csv"
    retouch_rows = read_rows(retouch_path)
    ffhq_rows = read_rows(ffhq_path)
    ffhq_by_id = {row["ffhq_id"].zfill(5): row for row in ffhq_rows}
    selected_ids = {row["ffhq_id"].zfill(5) for row in retouch_rows}

    records = [
        ScoreRecord(
            relative_id=f"retouched-{index:06d}",
            label=1,
            score=float(row["prob_morph"]),
            dataset="retouchingffhq",
            path=row["out_path"],
        )
        for index, row in enumerate(retouch_rows)
    ]
    for ffhq_id in sorted(selected_ids):
        row = ffhq_by_id.get(ffhq_id)
        if row:
            records.append(
                ScoreRecord(
                    relative_id=f"ffhq-{ffhq_id}",
                    label=0,
                    score=float(row["prob_morph"]),
                    dataset="retouchingffhq",
                    path=row["path"],
                )
            )
    return records, retouch_rows


def copy_retouch_tables(source_root: Path, destination: Path) -> None:
    metrics_root = source_root / (
        "retouchingffhq/scores/"
        "selfmadpp_retouchingffhq_author_crop_sample50000_with_ffhq_baseline_metrics"
    )
    summaries_root = source_root / (
        "retouchingffhq/scores/"
        "selfmadpp_retouchingffhq_author_crop_sample50000_operation_summaries"
    )
    destination.mkdir(parents=True, exist_ok=True)
    for path in sorted(metrics_root.glob("*.csv")):
        shutil.copy2(path, destination / path.name)
    for path in sorted(summaries_root.glob("*.csv")):
        shutil.copy2(path, destination / f"retouched_{path.name}")


def operation_category_rows(source_root: Path) -> list[dict[str, object]]:
    path = source_root / (
        "retouchingffhq/scores/"
        "selfmadpp_retouchingffhq_author_crop_sample50000_with_ffhq_baseline_metrics/"
        "metrics_by_operation.csv"
    )
    rows: list[dict[str, object]] = []
    for row in read_rows(path):
        for label, name, prefix in ((0, "bona_fide", "neg"), (1, "retouched", "pos")):
            rows.append(
                {
                    "dataset": "RetouchingFFHQ",
                    "category_kind": "operation",
                    "category": row["operation"],
                    "label": label,
                    "label_name": name,
                    "n": int(row[f"n_{prefix}"]),
                    "mean": float(row[f"{prefix}_mean"]),
                }
            )
    return rows


def assert_expected(dataset: str, metrics: dict[str, object]) -> None:
    expected_n, expected_auc, expected_eer = EXPECTED[dataset]
    if metrics["n"] != expected_n:
        raise RuntimeError(f"{dataset} count changed: {metrics['n']} != {expected_n}")
    for name, expected in (("auc", expected_auc), ("eer", expected_eer)):
        actual = float(metrics[name])
        if abs(actual - expected) > 1e-8:
            raise RuntimeError(f"{dataset} {name} changed: {actual} != {expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("results"))
    parser.add_argument("--bootstrap-iterations", type=int, default=1000)
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    frozen_root = output_root / "frozen"
    provenance_rows = []
    headline_rows: list[dict[str, object]] = []
    category_rows: list[dict[str, object]] = []

    for dataset, relative_path in DATASETS.items():
        source = args.source_root / relative_path
        records = read_score_records(source, dataset=dataset)
        metrics = evaluate_records(
            records,
            frozen_root / dataset,
            dataset=dataset,
            bootstrap_iterations=args.bootstrap_iterations,
            display_name=DISPLAY_NAMES[dataset],
        )
        if dataset != "ffhq":
            assert_expected(dataset, metrics)
            headline_rows.append(metrics)
        for label, name in ((0, "bona_fide"), (1, "manipulated")):
            values = [record.score for record in records if record.label == label]
            if values:
                summary = describe(np.asarray(values))
                category_rows.append(
                    {
                        "dataset": dataset,
                        "category_kind": "class",
                        "category": "overall",
                        "label": label,
                        "label_name": name,
                        "n": summary["n"],
                        "mean": summary["mean"],
                    }
                )
        if dataset in {"ffhq", "ffhqr"}:
            public_rows(records, frozen_root / dataset / "scores.csv", dataset)
        provenance_rows.append(
            {
                "artifact": source.name,
                "dataset": dataset,
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )

    retouch, _ = retouch_records(args.source_root)
    retouch_metrics = evaluate_records(
        retouch,
        frozen_root / "retouchingffhq",
        dataset="retouchingffhq",
        bootstrap_iterations=args.bootstrap_iterations,
        display_name=DISPLAY_NAMES["retouchingffhq"],
    )
    assert_expected("retouchingffhq", retouch_metrics)
    headline_rows.append(retouch_metrics)
    labels = {0: "bona_fide", 1: "retouched"}
    for label, name in labels.items():
        values = np.asarray([record.score for record in retouch if record.label == label])
        category_rows.append(
            {
                "dataset": "RetouchingFFHQ",
                "category_kind": "class",
                "category": "overall",
                "label": label,
                "label_name": name,
                "n": len(values),
                "mean": float(values.mean()),
            }
        )
    category_rows.extend(operation_category_rows(args.source_root))
    copy_retouch_tables(args.source_root, frozen_root / "retouchingffhq" / "categories")

    retouch_source = args.source_root / (
        "retouchingffhq/scores/"
        "selfmadpp_retouchingffhq_author_crop_sample50000_scores.csv"
    )
    provenance_rows.append(
        {
            "artifact": retouch_source.name,
            "dataset": "retouchingffhq",
            "bytes": retouch_source.stat().st_size,
            "sha256": sha256(retouch_source),
        }
    )
    extra_sources = [
        args.source_root / "ffhq/scores/selfmadpp_ffhq_author_crop_all_scores_enriched.csv",
        *sorted(
            (
                args.source_root
                / (
                    "retouchingffhq/scores/"
                    "selfmadpp_retouchingffhq_author_crop_sample50000_with_ffhq_baseline_metrics"
                )
            ).glob("*.csv")
        ),
    ]
    for source in extra_sources:
        provenance_rows.append(
            {
                "artifact": source.name,
                "dataset": "ffhq" if "ffhq_author_crop_all" in source.name else "retouchingffhq",
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )

    headline_fields = [
        "dataset",
        "n",
        "n_bona_fide",
        "n_manipulated",
        "auc",
        "auc_ci95_low",
        "auc_ci95_high",
        "eer",
        "eer_ci95_low",
        "eer_ci95_high",
        "eer_threshold",
    ]
    write_csv(output_root / "headline_metrics.csv", headline_fields, headline_rows)
    write_csv(
        output_root / "category_means.csv",
        ["dataset", "category_kind", "category", "label", "label_name", "n", "mean"],
        category_rows,
    )
    write_csv(output_root / "coverage.csv", list(COVERAGE[0]), COVERAGE)
    write_csv(
        output_root / "provenance" / "source_artifacts.csv",
        ["artifact", "dataset", "bytes", "sha256"],
        provenance_rows,
    )
    (output_root / "provenance" / "import.json").write_text(
        json.dumps(
            {
                "source_root_not_published": True,
                "model_inference_run": False,
                "importer": "scripts/import_frozen_results.py",
                "bootstrap_iterations": args.bootstrap_iterations,
                "positive_label": 1,
                "eer_definition": "nearest_discrete_fpr_fnr_crossing",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
