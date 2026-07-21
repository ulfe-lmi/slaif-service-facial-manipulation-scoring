"""Evidence plot generation using class-normalized distributions."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .metrics import RocResult
from .records import ScoreRecord, write_csv

REAL_COLOR = "#007C91"
MANIPULATED_COLOR = "#C64242"
NEUTRAL_COLOR = "#667085"


def _plt():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the evaluation extra to generate plots.") from exc
    return plt


def write_roc_plot(result: RocResult, output_prefix: Path, title: str) -> None:
    plt = _plt()
    fig, axis = plt.subplots(figsize=(7, 6))
    axis.plot(result.fpr, result.tpr, color=MANIPULATED_COLOR, linewidth=2.2)
    axis.plot([0, 1], [0, 1], color=NEUTRAL_COLOR, linestyle="--", linewidth=1)
    axis.set(xlabel="False positive rate", ylabel="True positive rate", title=title)
    axis.grid(True, alpha=0.22)
    axis.text(
        0.58,
        0.08,
        f"AUC = {result.auc:.4f}\nEER = {result.eer:.4f}",
        transform=axis.transAxes,
        bbox={"facecolor": "white", "edgecolor": "#D0D5DD", "alpha": 0.95},
    )
    fig.tight_layout()
    for suffix in ("png", "svg"):
        fig.savefig(output_prefix.with_name(f"{output_prefix.name}_roc.{suffix}"), dpi=180)
    plt.close(fig)


def write_distribution_plots(records: list[ScoreRecord], output_prefix: Path, title: str) -> None:
    plt = _plt()
    bins = np.linspace(0.0, 1.0, 101)
    centers = (bins[:-1] + bins[1:]) / 2.0
    bin_rows: list[dict[str, object]] = []
    fig_hist, hist_axis = plt.subplots(figsize=(8, 5))
    fig_ecdf, ecdf_axis = plt.subplots(figsize=(8, 5))
    for label, name, color in ((0, "bona fide", REAL_COLOR), (1, "manipulated", MANIPULATED_COLOR)):
        values = np.asarray([record.score for record in records if record.label == label])
        if len(values) == 0:
            continue
        counts, _ = np.histogram(values, bins=bins)
        fractions = counts / counts.sum()
        hist_axis.plot(
            centers,
            fractions,
            color=color,
            linewidth=2.2,
            label=f"{name} (n={len(values)})",
        )
        sorted_values = np.sort(values)
        ecdf_axis.step(
            sorted_values,
            np.arange(1, len(values) + 1) / len(values),
            color=color,
            linewidth=2.2,
            label=f"{name} (n={len(values)})",
        )
        for left, right, center, count, fraction in zip(
            bins[:-1], bins[1:], centers, counts, fractions, strict=True
        ):
            bin_rows.append(
                {
                    "label": label,
                    "label_name": name,
                    "bin_left": left,
                    "bin_right": right,
                    "bin_center": center,
                    "count": int(count),
                    "fraction": float(fraction),
                }
            )

    for axis, ylabel in ((hist_axis, "Fraction within class"), (ecdf_axis, "Cumulative fraction")):
        axis.set(xlabel="SelfMAD++ score", ylabel=ylabel, title=title)
        axis.set_xlim(0, 1)
        axis.grid(True, alpha=0.22)
        axis.legend()
    fig_hist.tight_layout()
    fig_ecdf.tight_layout()
    for suffix in ("png", "svg"):
        histogram_path = output_prefix.with_name(f"{output_prefix.name}_histogram.{suffix}")
        fig_hist.savefig(histogram_path, dpi=180)
        fig_ecdf.savefig(output_prefix.with_name(f"{output_prefix.name}_ecdf.{suffix}"), dpi=180)
    plt.close(fig_hist)
    plt.close(fig_ecdf)
    write_csv(
        output_prefix.with_name(f"{output_prefix.name}_histogram_bins.csv"),
        ["label", "label_name", "bin_left", "bin_right", "bin_center", "count", "fraction"],
        bin_rows,
    )
