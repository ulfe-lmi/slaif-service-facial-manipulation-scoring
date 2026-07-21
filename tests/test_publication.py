import csv

import pytest

from slaif_fms.evaluation.publication import sanitize_score_rows


def write_scores(path, relative_id: str = "images/0001.png") -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset", "relpath", "target_label", "prob_morph", "path"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "dataset": "ffhq",
                "relpath": relative_id,
                "target_label": 0,
                "prob_morph": 0.1,
                "path": "/private/dataset/0001.png",
            }
        )


def test_restricted_dataset_cannot_publish_identified_rows(tmp_path) -> None:
    source = tmp_path / "scores.csv"
    write_scores(source)
    with pytest.raises(PermissionError):
        sanitize_score_rows(source, tmp_path / "public.csv", dataset="ppr10k")


def test_sanitized_rows_omit_absolute_paths(tmp_path) -> None:
    source = tmp_path / "scores.csv"
    output = tmp_path / "public.csv"
    write_scores(source)
    assert sanitize_score_rows(source, output, dataset="ffhq") == 1
    text = output.read_text()
    assert "/private/dataset" not in text
    assert "images/0001.png" in text


def test_path_traversal_identifier_is_rejected(tmp_path) -> None:
    source = tmp_path / "scores.csv"
    write_scores(source, "../private.png")
    with pytest.raises(ValueError, match="Unsafe"):
        sanitize_score_rows(source, tmp_path / "public.csv", dataset="ffhq")
