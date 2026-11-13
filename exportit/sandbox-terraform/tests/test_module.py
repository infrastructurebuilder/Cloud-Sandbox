"""The module validates, and what does not is known and named."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
from support import (
    FRAGMENTS,
    MODULES,
    TOFU_VERSION,
    UNFORMATTED,
    UNIT,
    directories_with_terraform,
    tofu,
)


def test_the_pinned_tofu_is_the_one_that_runs() -> None:
    done = tofu("version")
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith(f"OpenTofu v{TOFU_VERSION}\n")


def test_every_directory_with_terraform_is_a_module_or_a_known_fragment() -> None:
    assert directories_with_terraform() == set(MODULES) | set(FRAGMENTS)


@pytest.mark.parametrize("directory", MODULES)
def test_a_module_validates(directory: str) -> None:
    where = UNIT / directory
    if not (where / ".terraform").is_dir():
        pytest.fail(f"{directory} is not initialised; run `just init` first")
    done = tofu("validate", "-no-color", cwd=where)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Success! The configuration is valid." in done.stdout


def test_only_the_known_files_are_unformatted() -> None:
    done = tofu("fmt", "-check", "-recursive", "-list=true", "-no-color")
    listed = set(done.stdout.split())
    assert listed == UNFORMATTED, (
        f"newly unformatted: {sorted(listed - UNFORMATTED)}; now formatted: {sorted(UNFORMATTED - listed)}"
    )


@pytest.mark.slow
@pytest.mark.parametrize("directory", sorted(FRAGMENTS))
def test_a_known_fragment_still_does_not_validate(directory: str, tmp_path: Path) -> None:
    copy = tmp_path / directory
    shutil.copytree(UNIT / directory, copy, ignore=shutil.ignore_patterns(".terraform*"))
    init = tofu("init", "-backend=false", "-input=false", "-no-color", cwd=copy)
    assert init.returncode == 0, init.stdout + init.stderr
    done = tofu("validate", "-no-color", cwd=copy)
    assert done.returncode != 0, f"{directory} validates now: move it from FRAGMENTS to MODULES"
    assert "Reference to undeclared" in done.stderr


REQUIRED_VERSION = re.compile(r'^\s*required_version\s*=\s*"(?P<version>[^"]+)"', re.MULTILINE)


@pytest.mark.parametrize("directory", MODULES)
def test_each_module_requires_the_pinned_tofu(directory: str) -> None:
    # In versions.tofu: OpenTofu ignores required_version in .tf files.
    found = REQUIRED_VERSION.findall((UNIT / directory / "versions.tofu").read_text())
    assert found == [TOFU_VERSION], (
        f"{directory}/versions.tofu requires {found}, the Justfile pins {TOFU_VERSION}"
    )


def test_the_justfile_pins_the_same_version_as_the_tests() -> None:
    pinned = re.search(r'^export TOFU_VERSION := "([^"]+)"$', (UNIT / "Justfile").read_text(), re.MULTILINE)
    assert pinned and pinned.group(1) == TOFU_VERSION


def test_another_tofu_version_is_refused(tmp_path: Path) -> None:
    copy = tmp_path / "remote-state"
    shutil.copytree(UNIT / "remote-state", copy, ignore=shutil.ignore_patterns(".terraform*"))
    constraint = copy / "versions.tofu"
    constraint.write_text(constraint.read_text().replace(f'"{TOFU_VERSION}"', '"1.0.0"'))
    done = tofu("init", "-backend=false", "-input=false", "-no-color", cwd=copy)
    assert done.returncode != 0
    assert "Incompatible module" in done.stderr or "Unsupported" in done.stderr, done.stderr
