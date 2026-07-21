"""Dataset-specific label normalization rules."""

from __future__ import annotations


def normalized_label(dataset: str, row: dict[str, str]) -> int:
    explicit = row.get("label") or row.get("label_id") or row.get("target_label")
    label_name = (row.get("label_name") or row.get("subset") or "").lower()
    group = (row.get("group_name") or "").lower()

    if dataset == "ffhq":
        return 0
    if dataset == "retouchingffhq":
        return 1
    if dataset == "celebhq_fm":
        filename = (row.get("filename") or row.get("source_path") or "").lower()
        if "_orig." in filename or label_name in {"orig", "original", "real"}:
            return 0
        if "_none." in filename or (row.get("EDIT_NAME") or row.get("edit_name")) == "none":
            raise ValueError(
                "CelebHQ-FM EDIT_NAME=none output is not accepted as bona fide; use _orig."
            )
        return 1
    if dataset == "readfake":
        return 0 if label_name in {"real", "bona_fide"} else 1
    if dataset == "ffhqr":
        return 0 if label_name in {"unretouched", "real", "source"} or group == "source" else 1
    if dataset == "ppr10k":
        return 0 if group == "source" or label_name in {"source", "real"} else 1
    if explicit != "":
        label = int(explicit)
        if label in {0, 1}:
            return label
    raise ValueError(f"Cannot normalize label for {dataset}: {row}")
