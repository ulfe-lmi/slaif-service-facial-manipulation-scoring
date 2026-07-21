from slaif_fms.evaluation.profile import profile_reference
from slaif_fms.evaluation.records import ScoreRecord


def test_reference_profile_reports_empirical_percentiles(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "slaif_fms.evaluation.profile.write_distribution_plots",
        lambda *_args, **_kwargs: None,
    )
    records = [ScoreRecord(str(index), 0, score) for index, score in enumerate([0.1, 0.2, 0.3])]
    profile = profile_reference(
        records,
        tmp_path,
        name="reference",
        percentiles=(0.5, 0.99),
    )
    assert profile["percentiles"]["p50"] == 0.2
    assert (
        profile["interpretation"]
        == "empirical_reference_distribution_not_probability_calibration"
    )
