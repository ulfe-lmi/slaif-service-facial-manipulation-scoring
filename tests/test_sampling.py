import csv

from slaif_fms.evaluation.sampling import balanced_sample


def test_balanced_sample_is_deterministic(tmp_path) -> None:
    source = tmp_path / "source.csv"
    with source.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_id", "label"])
        writer.writeheader()
        writer.writerows(
            [{"relative_id": f"real-{index}", "label": 0} for index in range(6)]
            + [{"relative_id": f"fake-{index}", "label": 1} for index in range(14)]
        )
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    result = balanced_sample(source, first, fraction=0.5, seed=7)
    balanced_sample(source, second, fraction=0.5, seed=7)
    assert result["selected_rows"] == 10
    assert result["selected_per_class"] == 5
    assert first.read_bytes() == second.read_bytes()
