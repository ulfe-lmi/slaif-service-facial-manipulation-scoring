"""Empirical profiling for a user's untouched reference scores."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .metrics import describe, records_arrays
from .plots import write_distribution_plots
from .records import ScoreRecord


def profile_reference(
    records: list[ScoreRecord],
    output_dir: Path,
    *,
    name: str,
    percentiles: tuple[float, ...],
) -> dict[str, object]:
    if not records:
        raise ValueError("Reference profile is empty.")
    labels, scores = records_arrays(records)
    if np.any(labels != 0):
        raise ValueError("Reference profiling accepts untouched label-0 rows only.")
    if any(not 0.0 < percentile < 1.0 for percentile in percentiles):
        raise ValueError("Percentiles must be strictly between 0 and 1.")
    profile: dict[str, object] = {
        "name": name,
        "interpretation": "empirical_reference_distribution_not_probability_calibration",
        "score_direction": "higher_means_stronger_manipulation_indication",
        "summary": describe(scores),
        "percentiles": {
            f"p{percentile * 100:g}": float(np.quantile(scores, percentile))
            for percentile in percentiles
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{name}_reference_profile.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_distribution_plots(records, output_dir / f"{name}_reference", f"{name}: reference scores")
    return profile
