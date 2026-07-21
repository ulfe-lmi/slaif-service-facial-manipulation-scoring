import pytest

from slaif_fms.evaluation.adapters import normalized_label


def test_celebhq_orig_is_bona_fide() -> None:
    assert normalized_label("celebhq_fm", {"source_path": "identity_orig.jpg"}) == 0


def test_celebhq_none_is_not_accepted_as_bona_fide() -> None:
    with pytest.raises(ValueError, match="EDIT_NAME=none"):
        normalized_label("celebhq_fm", {"source_path": "identity_none.jpg"})


def test_dataset_specific_source_labels() -> None:
    assert normalized_label("ppr10k", {"group_name": "source"}) == 0
    assert normalized_label("ffhqr", {"label_name": "retouched"}) == 1
    assert normalized_label("ffhq", {}) == 0
    assert normalized_label("retouchingffhq", {}) == 1
