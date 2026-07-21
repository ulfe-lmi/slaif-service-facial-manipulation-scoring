#!/usr/bin/env python3
"""Generate the optional API key used by the scoring endpoint."""

from __future__ import annotations

import argparse
import os
import secrets
import tempfile
from pathlib import Path

DEFAULT_OUTPUT = Path("secrets/api_key")


class KeyGenerationError(RuntimeError):
    """Raised when a key cannot be stored safely."""


def _prepare_parent(output: Path) -> None:
    parent_existed = output.parent.exists()
    try:
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not parent_existed or output == DEFAULT_OUTPUT:
            output.parent.chmod(0o700)
    except OSError as exc:
        raise KeyGenerationError(f"Cannot prepare output directory: {output.parent}") from exc


def generate_api_key(output: Path, *, force: bool = False) -> str:
    """Generate and atomically store a 256-bit URL-safe API key."""
    output = output.expanduser()
    _prepare_parent(output)

    if output.is_symlink():
        raise KeyGenerationError(f"Refusing to write through a symbolic link: {output}")
    if output.exists() and not force:
        raise KeyGenerationError(
            f"API key file already exists: {output} (use --force to rotate it)"
        )
    if output.exists() and not output.is_file():
        raise KeyGenerationError(f"API key output is not a regular file: {output}")

    api_key = secrets.token_urlsafe(32)
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=output.parent,
            prefix=f".{output.name}.",
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(f"{api_key}\n")
            handle.flush()
            os.fsync(handle.fileno())

        if force:
            if output.is_symlink():
                raise KeyGenerationError(f"Refusing to replace a symbolic link: {output}")
            os.replace(temporary_path, output)
        else:
            try:
                os.link(temporary_path, output)
            except FileExistsError as exc:
                raise KeyGenerationError(f"API key file already exists: {output}") from exc
            temporary_path.unlink()
        temporary_path = None
        output.chmod(0o600)
    except KeyGenerationError:
        raise
    except OSError as exc:
        raise KeyGenerationError(f"Cannot write API key file: {output}") from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return api_key


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing regular key file to rotate the key",
    )
    args = parser.parse_args()

    try:
        api_key = generate_api_key(args.output, force=args.force)
    except KeyGenerationError as exc:
        parser.exit(1, f"error: {exc}\n")

    print(f"Generated API key: {api_key}")
    print(f"Saved with owner-only permissions at: {args.output.expanduser()}")
    print("Store the displayed key securely; it will not be shown again by this script.")


if __name__ == "__main__":
    main()
