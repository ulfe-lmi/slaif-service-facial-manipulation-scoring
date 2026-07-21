import csv
import json
from pathlib import Path, PurePosixPath

import pytest

ROOT = Path(__file__).parents[1]
RESULTS = ROOT / "results"

EXPECTED_METRICS = {
    "str_ffhq_fm": (3288, 0.9004102481331155, 0.18004643703827652),
    "readfake": (2135, 0.6883329199491341, 0.3728513864118645),
    "celebhq_fm": (14454, 0.9442846232690145, 0.13354372805879666),
    "ffhqr": (3991, 0.5979430529947378, 0.42871466176195083),
    "ppr10k": (25910, 0.46683793967837006, 0.5220612426319836),
    "mffi": (42374, 0.7824332766718405, 0.2873224548694049),
    "retouchingffhq": (84003, 0.6860896041761837, 0.3666650433068033),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_frozen_headline_metrics_match_import_contract() -> None:
    rows = {row["dataset"]: row for row in read_csv(RESULTS / "headline_metrics.csv")}
    assert set(rows) == set(EXPECTED_METRICS)

    for dataset, (count, auc, eer) in EXPECTED_METRICS.items():
        row = rows[dataset]
        assert int(row["n"]) == count
        assert float(row["auc"]) == pytest.approx(auc, abs=1e-12)
        assert float(row["eer"]) == pytest.approx(eer, abs=1e-12)
        assert 0 <= float(row["auc_ci95_low"]) <= auc <= float(row["auc_ci95_high"]) <= 1
        assert 0 <= float(row["eer_ci95_low"]) <= eer <= float(row["eer_ci95_high"]) <= 1


def test_coverage_counts_are_consistent() -> None:
    for row in read_csv(RESULTS / "coverage.csv"):
        reference = int(row["official_or_reference_total"])
        available = int(row["locally_available"])
        selected = int(row["selected"])
        scored = int(row["scored"])
        assert 0 < scored <= selected <= available <= reference


@pytest.mark.parametrize("dataset", ["ffhq", "ffhqr"])
def test_publishable_score_rows_are_relative_and_complete(dataset: str) -> None:
    path = RESULTS / "frozen" / dataset / "scores.csv"
    expected = 69098 if dataset == "ffhq" else 3991
    rows = read_csv(path)
    assert len(rows) == expected

    for row in rows:
        relative_id = PurePosixPath(row["relative_id"])
        assert not relative_id.is_absolute()
        assert ".." not in relative_id.parts
        assert row["dataset"] == dataset
        assert row["status"] == "scored"
        assert 0 <= float(row["score"]) <= 1


def test_public_results_contain_no_local_filesystem_paths() -> None:
    forbidden = ("/synology/", "/data-nvme/", "C:\\Users\\")
    text_suffixes = {".csv", ".json", ".md", ".svg"}
    for path in RESULTS.rglob("*"):
        if path.is_file() and path.suffix.lower() in text_suffixes:
            text = path.read_text(errors="replace")
            assert not any(prefix in text for prefix in forbidden), path


def test_import_provenance_declares_no_new_model_inference() -> None:
    provenance = json.loads((RESULTS / "provenance" / "import.json").read_text())
    assert provenance["model_inference_run"] is False
    assert provenance["positive_label"] == 1
    assert provenance["source_root_not_published"] is True
