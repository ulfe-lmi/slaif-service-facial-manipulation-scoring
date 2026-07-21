#!/usr/bin/env python3
"""Download external model artifacts and verify their pinned checksums."""

from __future__ import annotations

import argparse
import bz2
import hashlib
import shutil
import urllib.request
from pathlib import Path

CHECKPOINT_URL = "https://unilj-my.sharepoint.com/:u:/g/personal/leon_todorov_fe1_uni-lj_si/EXPI80C7nVJGm8L130BWR2IBhcaUoDusyDMBYtXdJxgnHQ?e=D4OiAr&download=1"
PREDICTOR_URL = "http://dlib.net/files/shape_predictor_81_face_landmarks.dat.bz2"
CHECKPOINT_SHA256 = "642433f4fcd5d88c072c94f9e9fe6765f46875f2fede69a046924ea6c8cb80d4"
PREDICTOR_SHA256 = "8cae4375589dd915d9a0a881101bed1bbb4e9887e35e63b024388f1ca25ff869"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "slaif-fms-artifact-fetch/0.1"})
    with urllib.request.urlopen(request) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def verify(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        path.unlink(missing_ok=True)
        raise RuntimeError(f"Checksum mismatch for {path}: expected {expected}, got {actual}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("models"))
    parser.add_argument("--checkpoint-url", default=CHECKPOINT_URL)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    checkpoint = args.output_dir / "SelfMADpp_SMDD.tar"
    predictor_archive = args.output_dir / "shape_predictor_81_face_landmarks.dat.bz2"
    predictor = args.output_dir / "shape_predictor_81_face_landmarks.dat"
    if not checkpoint.exists():
        download(args.checkpoint_url, checkpoint)
    verify(checkpoint, CHECKPOINT_SHA256)

    if not predictor.exists():
        download(PREDICTOR_URL, predictor_archive)
        with bz2.open(predictor_archive, "rb") as source, predictor.open("wb") as output:
            shutil.copyfileobj(source, output)
        predictor_archive.unlink()
    verify(predictor, PREDICTOR_SHA256)
    print(f"Verified artifacts in {args.output_dir}")


if __name__ == "__main__":
    main()
