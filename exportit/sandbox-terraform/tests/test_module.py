"""The module validates, and what does not is known and named."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from support import (
    FRAGMENTS,
    MODULES,
    TERRAFORM_VERSION,
    UNFORMATTED,
    UNIT,
    directories_with_terraform,
    terraform,
)


def test_the_pinned_terraform_is_the_one_that_runs() -> None:
    done = terraform("version")
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith(f"Terraform v{TERRAFORM_VERSION}\n")


def test_every_directory_with_terraform_is_a_module_or_a_known_fragment() -> None:
    assert directories_with_terraform() == set(MODULES) | set(FRAGMENTS)


@pytest.mark.parametrize("directory", MODULES)
def test_a_module_validates(directory: str) -> None:
    where = UNIT / directory
    if not (where / ".terraform").is_dir():
        pytest.fail(f"{directory} is not initialised; run `just init` first")
    done = terraform("validate", "-no-color", cwd=where)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Success! The configuration is valid." in done.stdout


def test_only_the_known_files_are_unformatted() -> None:
    done = terraform("fmt", "-check", "-recursive", "-list=true", "-no-color")
    listed = set(done.stdout.split())
    assert listed == UNFORMATTED, (
        f"newly unformatted: {sorted(listed - UNFORMATTED)}; now formatted: {sorted(UNFORMATTED - listed)}"
    )


@pytest.mark.slow
@pytest.mark.parametrize("directory", sorted(FRAGMENTS))
def test_a_known_fragment_still_does_not_validate(directory: str, tmp_path: Path) -> None:
    copy = tmp_path / directory
    shutil.copytree(UNIT / directory, copy, ignore=shutil.ignore_patterns(".terraform*"))
    init = terraform("init", "-backend=false", "-input=false", "-no-color", cwd=copy)
    assert init.returncode == 0, init.stdout + init.stderr
    done = terraform("validate", "-no-color", cwd=copy)
    assert done.returncode != 0, f"{directory} validates now: move it from FRAGMENTS to MODULES"
    assert "Reference to undeclared" in done.stderr
