"""The shared part of the units' constitutions is written from one source, and drift is caught."""

from __future__ import annotations

from pathlib import Path

import pytest

import constitution

UNITS_TOML = """\
[[unit]]
name = "alpha"
repository = "https://github.com/infrastructurebuilder/csis-alpha"
[[unit]]
name = "flow"
repository = "https://github.com/infrastructurebuilder/flow"
[[unit]]
name = "outside"
repository = "https://github.com/infrastructurebuilder/outside"
external = true
"""

OWN = """\
# {name} Constitution

## Core Principles

### I. Its Own

Text of its own.

<!-- csis-shared: begin, version 0.0.0 -->
stale shared text
<!-- csis-shared: end -->

## Technical Constraints

Its own constraints.
"""


@pytest.fixture
def export(tmp_path: Path) -> Path:
    root = tmp_path / "exportit"
    for unit in ("alpha", "flow", "cloud-sandbox"):
        (root / f"{unit}.map").parent.mkdir(parents=True, exist_ok=True)
        (root / f"{unit}.map").write_text("")
        memory = root / unit / ".specify" / "memory"
        memory.mkdir(parents=True)
        (memory / "constitution.md").write_text(OWN.format(name=unit))
    (root / "cloud-sandbox" / "units.toml").write_text(UNITS_TOML)
    (tmp_path / "LICENSE").write_text("The project's licence.\n")
    return root


def run(export: Path, *args: str) -> int:
    return constitution.main(["--export", str(export), *args])


def test_writing_puts_the_shared_part_between_the_markers_and_keeps_the_rest(export: Path) -> None:
    assert run(export, "check") == 1
    assert run(export, "write") == 0
    text = (export / "alpha" / constitution.CONSTITUTION).read_text()
    shared = (constitution.SOURCE / "shared.md").read_text().strip()
    assert shared in text
    assert "stale shared text" not in text
    assert text.startswith("# alpha Constitution\n")
    assert text.rstrip().endswith("Its own constraints.")
    assert f"version {constitution.SHARED_VERSION}" in text
    assert run(export, "check") == 0


def test_claude_md_names_the_repository_and_the_unit(export: Path) -> None:
    run(export, "write")
    assert (export / "alpha" / "CLAUDE.md").read_text().startswith("# csis-alpha\n")
    assert (export / "flow" / "CLAUDE.md").read_text().startswith("# flow\n")
    assert (export / "cloud-sandbox" / "CLAUDE.md").read_text().startswith("# csis-cloud-sandbox\n")
    assert "exportit/alpha.map" in (export / "alpha" / "CLAUDE.md").read_text()


def test_an_edit_inside_the_shared_part_is_drift(export: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(export, "write")
    path = export / "flow" / constitution.CONSTITUTION
    path.write_text(path.read_text().replace("### S4.", "### S4 (edited here)."))
    assert run(export, "check") == 1
    assert "flow: the shared part of its constitution differs" in capsys.readouterr().err


def test_an_edit_outside_the_shared_part_is_the_units_own(export: Path) -> None:
    run(export, "write")
    path = export / "flow" / constitution.CONSTITUTION
    path.write_text(path.read_text().replace("Text of its own.", "Amended by the unit."))
    assert run(export, "check") == 0


def test_an_edited_claude_md_is_drift(export: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(export, "write")
    (export / "alpha" / "CLAUDE.md").write_text("# something else\n")
    assert run(export, "check") == 1
    assert "alpha: CLAUDE.md differs" in capsys.readouterr().err


def test_a_unit_without_a_constitution_is_a_problem(export: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(export, "write")
    (export / "alpha" / constitution.CONSTITUTION).unlink()
    assert run(export, "check") == 1
    assert "alpha: no .specify/memory/constitution.md" in capsys.readouterr().err


@pytest.mark.parametrize(
    "broken",
    [
        "no markers at all\n",
        "<!-- csis-shared: end -->\nthen\n<!-- csis-shared: begin, version 1 -->\n",
        "<!-- csis-shared: begin -->\n<!-- csis-shared: begin -->\n<!-- csis-shared: end -->\n",
    ],
)
def test_markers_must_be_one_pair_in_order(export: Path, broken: str) -> None:
    (export / "alpha" / constitution.CONSTITUTION).write_text(broken)
    assert run(export, "check") == 1
    assert run(export, "write") == 1


def test_writing_again_changes_nothing(export: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(export, "write")
    capsys.readouterr()
    assert run(export, "write") == 0
    assert capsys.readouterr().out == ""


def test_the_real_units_agree_with_the_source() -> None:
    """Every unit of this repository carries the shared part and CLAUDE.md as the source has them."""
    assert constitution.problems(constitution.HERE.parent) == []


def test_every_unit_carries_the_projects_licence(export: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(export, "write")
    assert (export / "alpha" / "LICENSE").read_text() == "The project's licence.\n"
    assert run(export, "check") == 0
    (export / "flow" / "LICENSE").write_text("Another licence.\n")
    assert run(export, "check") == 1
    assert "flow: LICENSE differs from Cloud-Sandbox's" in capsys.readouterr().err
    assert run(export, "write") == 0
    assert (export / "flow" / "LICENSE").read_text() == "The project's licence.\n"
