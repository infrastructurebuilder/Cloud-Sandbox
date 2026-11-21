"""Write the shared part of every unit's constitution, and check that none has drifted.

Each unit under ``exportit/`` is a repository of its own (``exportit/MOVINGDAY.md``)
and plans its work with Spec Kit. Its constitution, ``.specify/memory/constitution.md``,
has two parts: its own, which it amends itself, and a shared part, the same in every
unit, which is kept here, in ``constitution/shared.md``. The shared part sits between
two markers::

    <!-- csis-shared: begin, version 1.0.0 ... -->
    ...
    <!-- csis-shared: end -->

Every unit's ``CLAUDE.md`` is shared whole: ``constitution/CLAUDE.md`` with the
repository's and the unit's names put in. Every unit's ``LICENSE`` is
Cloud-Sandbox's own ``LICENSE``, the project's licence (Cloud-Sandbox's
constitution, principle I: a file more than one unit needs lives in one place).

Commands::

    constitution.py write [UNIT ...]   put the shared part and CLAUDE.md into the units
    constitution.py check              exit 1 if any unit's copy differs from the source

A unit's repository name comes from the umbrella's ``units.toml``.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

SHARED_VERSION = "2.1.0"
"""The shared part's version. Raise it with every change to ``shared.md``, as its Governance says."""

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "constitution"
CONSTITUTION = Path(".specify") / "memory" / "constitution.md"
BEGIN = re.compile(r"^<!-- csis-shared: begin.*-->$", re.MULTILINE)
END = "<!-- csis-shared: end -->"


class ConstitutionError(Exception):
    """A unit's constitution cannot be read or written as the markers require."""


def begin_marker() -> str:
    """Give the marker that opens the shared part, with its version."""
    return (
        f"<!-- csis-shared: begin, version {SHARED_VERSION}. Written by Cloud-Sandbox's "
        "`just constitution` from exportit/tools/constitution/shared.md; do not edit here. -->"
    )


def shared_block(source: Path = SOURCE) -> str:
    """Give the shared part as it goes into a constitution, markers included."""
    return f"{begin_marker()}\n\n{(source / 'shared.md').read_text().strip()}\n\n{END}"


def claude_md(repository: str, unit: str, source: Path = SOURCE) -> str:
    """Give a unit's CLAUDE.md."""
    return (source / "CLAUDE.md").read_text().replace("{repository}", repository).replace("{unit}", unit)


def with_shared(text: str, block: str) -> str:
    """Put ``block`` in place of the shared part of a constitution."""
    begins = list(BEGIN.finditer(text))
    if len(begins) != 1 or text.count(END) != 1:
        raise ConstitutionError("needs exactly one begin and one end marker of the shared part")
    start, end = begins[0].start(), text.index(END) + len(END)
    if end < start:
        raise ConstitutionError("the end marker comes before the begin marker")
    return text[:start] + block + text[end:]


def repositories(export: Path) -> dict[str, str]:
    """Map each unit to its repository's name, from the umbrella's units.toml."""
    units = tomllib.loads((export / "cloud-sandbox" / "units.toml").read_text())["unit"]
    return {
        unit["name"]: str(unit["repository"]).rsplit("/", 1)[1] for unit in units if not unit.get("external")
    } | {"cloud-sandbox": "csis-cloud-sandbox"}


def units_of(export: Path) -> list[str]:
    """List the units: one per mapping file."""
    return sorted(path.stem for path in export.glob("*.map"))


def licence(export: Path) -> bytes:
    """Give the licence every unit carries: the one at the root of the repository ``export`` is in."""
    return (export.parent / "LICENSE").read_bytes()


def problems(export: Path, source: Path = SOURCE) -> list[str]:
    """Say where a unit's shared part, CLAUDE.md or LICENSE differs from its source."""
    found: list[str] = []
    block = shared_block(source)
    names = repositories(export)
    for unit in units_of(export):
        constitution = export / unit / CONSTITUTION
        if not constitution.is_file():
            found.append(f"{unit}: no {CONSTITUTION}")
            continue
        text = constitution.read_text()
        try:
            if with_shared(text, block) != text:
                found.append(f"{unit}: the shared part of its constitution differs from shared.md")
        except ConstitutionError as error:
            found.append(f"{unit}: {CONSTITUTION}: {error}")
        guide = export / unit / "CLAUDE.md"
        if not guide.is_file() or guide.read_text() != claude_md(names[unit], unit, source):
            found.append(f"{unit}: CLAUDE.md differs from the shared one")
        copy = export / unit / "LICENSE"
        if not copy.is_file() or copy.read_bytes() != licence(export):
            found.append(f"{unit}: LICENSE differs from Cloud-Sandbox's")
    return found


def write(export: Path, names: list[str], source: Path = SOURCE) -> list[str]:
    """Write the shared part, CLAUDE.md and LICENSE into the named units (all when none is named)."""
    block = shared_block(source)
    repos = repositories(export)
    written: list[str] = []
    for unit in names or units_of(export):
        constitution = export / unit / CONSTITUTION
        text = constitution.read_text()
        new = with_shared(text, block)
        if new != text:
            constitution.write_text(new)
            written.append(f"{unit}: {CONSTITUTION}")
        guide = export / unit / "CLAUDE.md"
        wanted = claude_md(repos[unit], unit, source)
        if not guide.is_file() or guide.read_text() != wanted:
            guide.write_text(wanted)
            written.append(f"{unit}: CLAUDE.md")
        copy = export / unit / "LICENSE"
        if not copy.is_file() or copy.read_bytes() != licence(export):
            copy.write_bytes(licence(export))
            written.append(f"{unit}: LICENSE")
    return written


def main(argv: list[str] | None = None) -> int:
    """Run one command; see the module docstring."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", maxsplit=1)[0])
    parser.add_argument("--export", type=Path, default=HERE.parent, help="the exportit/ directory")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("write").add_argument("units", nargs="*")
    commands.add_parser("check")
    args = parser.parse_args(argv)
    export: Path = args.export
    try:
        if args.command == "write":
            for line in write(export, list(args.units)):
                print(f"wrote {line}")
            return 0
        found = problems(export)
    except (ConstitutionError, OSError) as error:
        print(f"PROBLEM {error}", file=sys.stderr)
        return 1
    for problem in found:
        print(f"PROBLEM {problem}", file=sys.stderr)
    if not found:
        agree = f"the shared part (version {SHARED_VERSION}), CLAUDE.md and LICENSE"
        print(f"constitutions: {agree} agree in every unit")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
