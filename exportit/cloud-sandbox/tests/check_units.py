"""Check that units.toml is consistent: names, versions, and the two orders.

Run with any Python 3.11 or later; it needs nothing but the standard library.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

UMBRELLA = Path(__file__).resolve().parents[1]
FIELDS = {"name", "version", "kind", "step", "relocate", "needs", "what"}
# A unit that already lives in a repository of its own, and is not copied
# into exportit/, says so with external = true and has relocate = 0.
OPTIONAL = {"external"}
KINDS = {"python", "ansible", "terraform", "scripts", "data"}
VERSION = re.compile(r"^\d+\.\d+\.\d+([ab]\d+)?$")


def problems() -> list[str]:
    """List what is wrong with units.toml."""
    units = tomllib.loads((UMBRELLA / "units.toml").read_text())["unit"]
    found: list[str] = []
    names = [unit.get("name") for unit in units]
    if len(names) != len(set(names)):
        found.append(f"a name is used twice: {sorted(n for n in names if names.count(n) > 1)}")
    by_name = {unit["name"]: unit for unit in units}
    for unit in units:
        name = unit.get("name", "?")
        if set(unit) - OPTIONAL != FIELDS:
            found.append(f"{name}: fields {sorted((set(unit) - OPTIONAL) ^ FIELDS)} are missing or unknown")
            continue
        if unit.get("external", False) is True:
            if unit["relocate"] != 0:
                found.append(f"{name} is external, so it is not relocated: relocate must be 0")
        elif "external" in unit:
            found.append(f"{name}: external must be true, or left out")
        elif unit["relocate"] < 1:
            found.append(f"{name}: relocate must be 1 or more; only an external unit has 0")
        if not VERSION.match(unit["version"]):
            found.append(f"{name}: {unit['version']!r} is not a version")
        if unit["kind"] not in KINDS:
            found.append(f"{name}: unknown kind {unit['kind']!r}")
        for other in unit["needs"]:
            if other not in by_name:
                found.append(f"{name} needs {other}, which is not a unit")
            elif by_name[other]["relocate"] >= unit["relocate"]:
                found.append(f"{name} is relocated before {other}, which it needs")
    steps = sorted({unit["step"] for unit in units})
    if steps != list(range(1, len(steps) + 1)):
        found.append(f"the steps are not 1, 2, 3...: {steps}")
    return found


def main() -> int:
    """Print the problems; exit 1 if there are any."""
    found = problems()
    for problem in found:
        print(f"PROBLEM {problem}", file=sys.stderr)
    if not found:
        count = len(tomllib.loads((UMBRELLA / "units.toml").read_text())["unit"])
        print(f"units.toml: {count} units, consistent")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
