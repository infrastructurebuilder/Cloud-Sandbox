"""Check that attic/CATALOGUE.tsv and the files of the attic agree.

The attic holds the files of Cloud-Sandbox's scripts/ and misc/ that were read
and found superseded or dead (stage 7). They stay with the original repository
rather than travel with sandbox-ops (the operator's decision of 2026-11-13).

Every file in attic/ has exactly one row, every row names a file that is here,
each file sits at attic/<status>/<its original path>, every row gives its
evidence and its group, and a superseded file says what superseded it.

Run with any Python 3.11 or later; it needs nothing but the standard library.
"""

from __future__ import annotations

import sys
from pathlib import Path

UMBRELLA = Path(__file__).resolve().parents[1]
ATTIC = UMBRELLA / "attic"
CATALOGUE = ATTIC / "CATALOGUE.tsv"
# The attic's own description, which is not one of the retired files.
OWN = {"attic/CATALOGUE.tsv", "attic/README.md"}
HEADER = ["source", "copy", "status", "group", "superseded_by", "evidence", "sensitive"]
STATUSES = {"superseded", "dead"}


def problems() -> tuple[list[str], dict[str, int]]:
    """List what is wrong with the attic, and count its files by status."""
    lines = CATALOGUE.read_text().splitlines()
    found: list[str] = []
    if lines[0].split("\t") != HEADER:
        found.append(f"{CATALOGUE.name}: the header is not: {' '.join(HEADER)}")
    listed: dict[str, str] = {}
    for number, line in enumerate(lines[1:], start=2):
        fields = line.split("\t")
        if len(fields) != len(HEADER):
            found.append(f"line {number}: {len(fields)} fields, not {len(HEADER)}")
            continue
        row = dict(zip(HEADER, fields, strict=True))
        copy, status = row["copy"], row["status"]
        if copy in listed:
            found.append(f"{copy} is listed twice")
        listed[copy] = status
        if not (UMBRELLA / copy).is_file():
            found.append(f"{copy} (from {row['source']}) is listed but not here")
        if status not in STATUSES:
            found.append(f"{copy}: status {status!r} does not belong in the attic")
        elif copy != f"attic/{status}/{row['source']}":
            found.append(f"{copy} is not at attic/{status}/{row['source']}")
        if not row["evidence"]:
            found.append(f"{copy} has no evidence")
        if not row["group"]:
            found.append(f"{copy} has no group")
        if status == "superseded" and not row["superseded_by"]:
            found.append(f"{copy} is superseded but does not say by what")
    for path in sorted(ATTIC.rglob("*")):
        relative = path.relative_to(UMBRELLA).as_posix()
        if path.is_file() and relative not in OWN and relative not in listed:
            found.append(f"{relative} is here but not in {CATALOGUE.name}")
    count = {status: list(listed.values()).count(status) for status in sorted(STATUSES)}
    return found, count


def main() -> int:
    found, count = problems()
    for problem in found:
        print(f"PROBLEM {problem}", file=sys.stderr)
    if found:
        print(f"{len(found)} problems", file=sys.stderr)
        return 1
    total = sum(count.values())
    print(f"attic: {total} files catalogued: {count['superseded']} superseded, {count['dead']} dead")
    return 0


if __name__ == "__main__":
    sys.exit(main())
