import re
import stat
import subprocess
import sys
from pathlib import Path

GENERATOR = Path(__file__).parents[1] / "scripts" / "generate_api_key.py"
KEY_PATTERN = re.compile(r"Generated API key: ([A-Za-z0-9_-]{43})\n")


def run_generator(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def generated_key(result: subprocess.CompletedProcess[str]) -> str:
    match = KEY_PATTERN.search(result.stdout)
    assert match is not None
    return match.group(1)


def test_generator_creates_private_key_and_prints_it_once(tmp_path: Path) -> None:
    output = tmp_path / "private" / "api_key"
    result = run_generator("--output", str(output))

    assert result.returncode == 0, result.stderr
    api_key = generated_key(result)
    assert result.stdout.count(api_key) == 1
    assert output.read_text(encoding="utf-8").strip() == api_key
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    assert stat.S_IMODE(output.parent.stat().st_mode) == 0o700


def test_generator_refuses_overwrite_unless_forced(tmp_path: Path) -> None:
    output = tmp_path / "api_key"
    first = run_generator("--output", str(output))
    first_key = generated_key(first)

    refused = run_generator("--output", str(output))
    assert refused.returncode == 1
    assert refused.stdout == ""
    assert "already exists" in refused.stderr
    assert output.read_text(encoding="utf-8").strip() == first_key

    replaced = run_generator("--output", str(output), "--force")
    replacement_key = generated_key(replaced)
    assert replaced.returncode == 0, replaced.stderr
    assert replacement_key != first_key
    assert output.read_text(encoding="utf-8").strip() == replacement_key
    assert stat.S_IMODE(output.stat().st_mode) == 0o600


def test_generator_refuses_symbolic_link_even_when_forced(tmp_path: Path) -> None:
    destination = tmp_path / "destination"
    destination.write_text("unchanged", encoding="utf-8")
    output = tmp_path / "api_key"
    output.symlink_to(destination)

    result = run_generator("--output", str(output), "--force")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "symbolic link" in result.stderr
    assert destination.read_text(encoding="utf-8") == "unchanged"
