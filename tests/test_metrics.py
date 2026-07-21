import numpy as np

from slaif_fms.evaluation.metrics import bootstrap_intervals, describe, roc_curve_fixed
from slaif_fms.evaluation.records import read_score_records


def test_perfect_fixed_polarity_metrics() -> None:
    labels = np.asarray([0, 0, 1, 1])
    scores = np.asarray([0.1, 0.2, 0.8, 0.9])
    result = roc_curve_fixed(labels, scores)
    assert result.auc == 1.0
    assert result.eer == 0.0
    assert result.positive_count == 2
    assert result.negative_count == 2


def test_polarity_is_not_reversed_for_bad_scores() -> None:
    labels = np.asarray([0, 0, 1, 1])
    scores = np.asarray([0.8, 0.9, 0.1, 0.2])
    result = roc_curve_fixed(labels, scores)
    assert result.auc == 0.0
    assert result.eer == 1.0


def test_describe_and_bootstrap_are_deterministic() -> None:
    labels = np.asarray([0, 0, 1, 1])
    scores = np.asarray([0.1, 0.2, 0.8, 0.9])
    assert describe(scores)["median"] == 0.5
    first = bootstrap_intervals(labels, scores, iterations=10, seed=42)
    second = bootstrap_intervals(labels, scores, iterations=10, seed=42)
    assert first == second


def test_score_reader_excludes_unscorable_rows(tmp_path) -> None:
    path = tmp_path / "scores.csv"
    path.write_text(
        "relative_id,label,status,score\n"
        "ok,0,scored,0.1\n"
        "missing,1,unscorable,\n",
        encoding="utf-8",
    )
    records = read_score_records(path)
    assert [record.relative_id for record in records] == ["ok"]
