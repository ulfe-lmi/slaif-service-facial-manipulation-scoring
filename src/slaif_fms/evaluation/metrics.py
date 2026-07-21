"""Fixed-polarity binary metrics and descriptive statistics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .records import ScoreRecord


@dataclass(frozen=True)
class RocResult:
    fpr: np.ndarray
    tpr: np.ndarray
    thresholds: np.ndarray
    auc: float
    eer: float
    eer_threshold: float
    negative_count: int
    positive_count: int


def roc_curve_fixed(labels: np.ndarray, scores: np.ndarray) -> RocResult:
    """Compute ROC with immutable `1 = manipulated` polarity."""
    positive = labels == 1
    positive_count = int(positive.sum())
    negative_count = int((~positive).sum())
    if positive_count == 0 or negative_count == 0:
        raise ValueError("ROC requires both label 0 and label 1.")

    order = np.argsort(-scores, kind="mergesort")
    sorted_positive = positive[order]
    sorted_scores = scores[order]
    tpr = [0.0]
    fpr = [0.0]
    thresholds = [float("inf")]
    true_positive = 0
    false_positive = 0
    for index, is_positive in enumerate(sorted_positive):
        true_positive += int(is_positive)
        false_positive += int(not is_positive)
        if index == len(sorted_positive) - 1 or sorted_scores[index + 1] != sorted_scores[index]:
            tpr.append(true_positive / positive_count)
            fpr.append(false_positive / negative_count)
            thresholds.append(float(sorted_scores[index]))

    fpr_array = np.asarray(fpr, dtype=np.float64)
    tpr_array = np.asarray(tpr, dtype=np.float64)
    threshold_array = np.asarray(thresholds, dtype=np.float64)
    false_negative_rate = 1.0 - tpr_array
    eer_index = int(np.argmin(np.abs(fpr_array - false_negative_rate)))
    return RocResult(
        fpr=fpr_array,
        tpr=tpr_array,
        thresholds=threshold_array,
        auc=float(np.trapz(tpr_array, fpr_array)),
        eer=float((fpr_array[eer_index] + false_negative_rate[eer_index]) / 2.0),
        eer_threshold=float(threshold_array[eer_index]),
        negative_count=negative_count,
        positive_count=positive_count,
    )


def describe(values: np.ndarray) -> dict[str, float | int]:
    if len(values) == 0:
        raise ValueError("Cannot describe an empty score collection.")
    return {
        "n": len(values),
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "min": float(values.min()),
        "p01": float(np.quantile(values, 0.01)),
        "p05": float(np.quantile(values, 0.05)),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.quantile(values, 0.50)),
        "p75": float(np.quantile(values, 0.75)),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
        "max": float(values.max()),
    }


def bootstrap_intervals(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    iterations: int = 1000,
    seed: int = 20260718,
) -> dict[str, float]:
    if iterations < 1:
        return {}
    rng = np.random.default_rng(seed)
    label_indices = {label: np.flatnonzero(labels == label) for label in (0, 1)}
    aucs: list[float] = []
    eers: list[float] = []
    for _ in range(iterations):
        sample_indices = np.concatenate(
            [
                rng.choice(indices, size=len(indices), replace=True)
                for indices in label_indices.values()
            ]
        )
        result = roc_curve_fixed(labels[sample_indices], scores[sample_indices])
        aucs.append(result.auc)
        eers.append(result.eer)
    return {
        "auc_ci95_low": float(np.quantile(aucs, 0.025)),
        "auc_ci95_high": float(np.quantile(aucs, 0.975)),
        "eer_ci95_low": float(np.quantile(eers, 0.025)),
        "eer_ci95_high": float(np.quantile(eers, 0.975)),
        "bootstrap_iterations": iterations,
        "bootstrap_seed": seed,
    }


def records_arrays(records: list[ScoreRecord]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray([record.label for record in records], dtype=np.int64),
        np.asarray([record.score for record in records], dtype=np.float64),
    )
