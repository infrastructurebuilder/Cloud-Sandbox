"""The model units of stage 5: their shared harness, and the install contract in MAP.md.

These tests read this repository itself, not a throw-away one: the harness
copies under ``exportit/model-*/tests/``, cloudflow's launchers under
``cloudflow/workflows/``, and the contract table in ``exportit/MAP.md``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "exportit"
HARNESS = "tests/check-scripts.sh"
LAUNCHERS = ROOT / "cloudflow" / "workflows"


def model_units() -> list[Path]:
    return sorted(path for path in EXPORT.glob("model-*") if path.is_dir())


def test_there_are_nine_model_units() -> None:
    names = [unit.name for unit in model_units()]
    assert len(names) == 9, names
    assert "model-common" in names


def test_every_model_unit_carries_the_same_harness() -> None:
    reference = (EXPORT / "model-common" / HARNESS).read_bytes()
    differ = [unit.name for unit in model_units() if (unit / HARNESS).read_bytes() != reference]
    assert not differ, f"{HARNESS} differs from model-common's in: {differ}"


# The harness, run on a small unit made for the purpose.


def run_harness(unit: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(unit / HARNESS), *args], capture_output=True, text=True, check=False, cwd=unit)


@pytest.fixture
def unit(tmp_path: Path) -> Path:
    """Give a unit with one clean script, one with a finding, and one template."""
    (tmp_path / "tests").mkdir()
    shutil.copy2(EXPORT / "model-common" / HARNESS, tmp_path / HARNESS)
    (tmp_path / "clean.sh").write_text('#!/usr/bin/env bash\necho "clean"\n')
    (tmp_path / "noisy").write_text("#!/bin/bash\necho $1\n")  # SC2086: unquoted
    (tmp_path / "notes.txt").write_text("not a script\n")
    (tmp_path / "job.template").write_text("#!/bin/bash -l\nif <Placeholder> ; then\n")
    (tmp_path / "tests" / "templates.txt").write_text("# placeholders\njob.template\n")
    recorded = run_harness(tmp_path, "--record")
    assert recorded.returncode == 0, recorded.stderr
    return tmp_path


def test_the_harness_passes_what_it_recorded(unit: Path) -> None:
    done = run_harness(unit)
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith("3 scripts: syntax as recorded (1 templates);")
    counts = (unit / "tests" / "shellcheck.counts").read_text()
    assert "0\tclean.sh\n" in counts
    assert "1\tnoisy\n" in counts
    assert "notes.txt" not in counts


def test_the_harness_finds_a_syntax_error(unit: Path) -> None:
    (unit / "clean.sh").write_text("#!/usr/bin/env bash\nif true; then\n")
    done = run_harness(unit)
    assert done.returncode == 1
    assert "clean.sh fails bash -n" in done.stderr


def test_the_harness_finds_a_changed_count(unit: Path) -> None:
    (unit / "noisy").write_text('#!/bin/bash\necho "$1"\n')
    done = run_harness(unit)
    assert done.returncode == 1
    assert "noisy: 0 shellcheck findings, 1 recorded" in done.stderr


def test_the_harness_finds_an_unlisted_script(unit: Path) -> None:
    (unit / "more.sh").write_text("echo $HOME\n")
    done = run_harness(unit)
    assert done.returncode == 1
    assert "more.sh is a script that tests/shellcheck.counts does not list" in done.stderr


def test_the_harness_finds_a_template_that_parses(unit: Path) -> None:
    (unit / "job.template").write_text("#!/bin/bash -l\necho fine\n")
    done = run_harness(unit)
    assert done.returncode == 1
    assert "job.template passes bash -n now" in done.stderr


def test_the_harness_refuses_counts_from_another_shellcheck(unit: Path) -> None:
    counts = unit / "tests" / "shellcheck.counts"
    counts.write_text(re.sub(r"version \S+", "version 0.0.1", counts.read_text()))
    done = run_harness(unit)
    assert done.returncode == 1
    assert "recorded with shellcheck 0.0.1" in done.stderr


# The install contract.

# A path a launcher uses that lies in a model's install: one of the
# variables the job configuration fills, with what follows it, or a
# literal path under /save. JOBDIR counts only with something after it,
# since alone it is often the run's output directory.
LAUNCHER_PATH = re.compile(
    r"\$\{?(?P<var>SAVEDIR|PROJHOME|HOMEnos|PHOME|EXEC|MODEL_DIR|JOBDIR)\b[^/\s\"';]*(?P<rest>/[\w./-]*)?"
    r"|(?<![\w/])(?P<literal>/save/[\w./$-]*)"
)


def launcher_paths() -> set[tuple[str, str]]:
    """List (launcher, path) for every install path the launchers use outside comments."""
    found: set[tuple[str, str]] = set()
    for script in sorted(LAUNCHERS.glob("*.sh")):
        for line in script.read_text().splitlines():
            if line.lstrip().startswith("#"):
                continue
            for match in LAUNCHER_PATH.finditer(line.split(" #", 1)[0]):
                if match["literal"]:
                    path = match["literal"]
                elif match["var"] == "JOBDIR" and not match["rest"]:
                    continue
                else:
                    path = f"${match['var']}{match['rest'] or ''}"
                found.add((script.name, path.rstrip("/")))
    return found


def contract_rows() -> set[tuple[str, str]]:
    """Read (launcher, path) from the table under '### The install contract' in MAP.md."""
    text = (EXPORT / "MAP.md").read_text()
    start = text.index("### The install contract")
    end = text.index("\n### ", start + 1)
    rows: set[tuple[str, str]] = set()
    for line in text[start:end].splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0].startswith("`"):
            rows.add((cells[0].strip("`"), cells[1].strip("`")))
    return rows


def test_the_launchers_still_use_install_paths() -> None:
    assert len(launcher_paths()) >= 40


def test_every_launcher_path_has_a_row_in_the_contract() -> None:
    missing = sorted(launcher_paths() - contract_rows())
    assert not missing, f"add these to the install contract in exportit/MAP.md: {missing}"


def test_every_row_of_the_contract_is_a_path_a_launcher_uses() -> None:
    stale = sorted(contract_rows() - launcher_paths())
    assert not stale, f"no launcher uses these any more; remove them from exportit/MAP.md: {stale}"
