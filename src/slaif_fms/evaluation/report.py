"""Generate complete machine-readable evidence from score records."""

from __future__ import annotations

import json
import math
from pathlib import Path

from .metrics import bootstrap_intervals, describe, records_arrays, roc_curve_fixed
from .plots import write_distribution_plots, write_roc_plot
from .records import ScoreRecord, write_csv


def evaluate_records(
    records: list[ScoreRecord],
    output_dir: Path,
    *,
    dataset: str,
    bootstrap_iterations: int = 1000,
) -> dict[str, object]:
    if not records:
        raise ValueError("No score records supplied.")
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = output_dir / dataset
    labels, scores = records_arrays(records)

    summaries = []
    for label, label_name in ((0, "bona_fide"), (1, "manipulated")):
        values = scores[labels == label]
        if len(values):
            summaries.append({"label": label, "label_name": label_name, **describe(values)})
    write_csv(
        prefix.with_name(f"{prefix.name}_summary_by_label.csv"),
        list(summaries[0]),
        summaries,
    )
    write_distribution_plots(records, prefix, f"{dataset}: SelfMAD++ score distributions")

    metrics: dict[str, object] = {
        "dataset": dataset,
        "n": len(records),
        "positive_label": 1,
        "positive_name": "manipulated",
        "score": "SelfMAD++ class-1 softmax",
        "score_direction": "higher_means_stronger_manipulation_indication",
    }
    if set(labels) == {0, 1}:
        roc = roc_curve_fixed(labels, scores)
        metrics.update(
            {
                "n_bona_fide": roc.negative_count,
                "n_manipulated": roc.positive_count,
                "auc": roc.auc,
                "eer": roc.eer,
                "eer_threshold": roc.eer_threshold,
                **bootstrap_intervals(
                    labels,
                    scores,
                    iterations=bootstrap_iterations,
                ),
            }
        )
        point_rows = [
            {
                "fpr": float(fpr),
                "tpr": float(tpr),
                "threshold": "inf" if math.isinf(threshold) else float(threshold),
            }
            for fpr, tpr, threshold in zip(roc.fpr, roc.tpr, roc.thresholds, strict=True)
        ]
        write_csv(
            prefix.with_name(f"{prefix.name}_roc_points.csv"),
            ["fpr", "tpr", "threshold"],
            point_rows,
        )
        write_roc_plot(roc, prefix, f"{dataset}: manipulated versus bona fide")

    (output_dir / f"{dataset}_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_group_metrics(records, output_dir, dataset)
    return metrics


def _write_group_metrics(records: list[ScoreRecord], output_dir: Path, dataset: str) -> None:
    group_names = (
        "operation",
        "provider",
        "operation_count",
        "operation_level",
        "method",
        "category",
    )
    for group_name in group_names:
        values = sorted(
            {record.groups[group_name] for record in records if group_name in record.groups}
        )
        rows = []
        for value in values:
            group_records = [record for record in records if record.groups.get(group_name) == value]
            labels, scores = records_arrays(group_records)
            row: dict[str, object] = {group_name: value, "n": len(group_records)}
            for label, name in ((0, "bona_fide"), (1, "manipulated")):
                class_scores = scores[labels == label]
                row[f"{name}_n"] = len(class_scores)
                row[f"{name}_mean"] = float(class_scores.mean()) if len(class_scores) else ""
            if set(labels) == {0, 1}:
                result = roc_curve_fixed(labels, scores)
                row.update({"auc": result.auc, "eer": result.eer})
            rows.append(row)
        if rows:
            write_csv(
                output_dir / f"{dataset}_metrics_by_{group_name}.csv",
                list(rows[0]),
                rows,
            )
