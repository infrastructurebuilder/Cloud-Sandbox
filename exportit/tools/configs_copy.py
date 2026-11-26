"""Copy cloudflow's schema of descriptions into csis-sandbox-configs, and check the copies (spec 005).

The schema lives in one place: cloudflow, beside the code that reads the
descriptions (its ``tools/configs_schema.py`` writes ``schema/``), with the
rules that read a description by it (``tools/schema_check.py``).
csis-sandbox-configs holds the site's own descriptions to the same schema and
rules, so it keeps copies, byte for byte; this writes them and says when one
has drifted (Cloud-Sandbox's constitution, principle I).

Commands::

    configs_copy.py write   copy cloudflow's files into csis-sandbox-configs
    configs_copy.py check   exit 1 if a copy differs from cloudflow's
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COPIES = {
    "schema/jobs.json": "schema/jobs.json",
    "schema/clusters.json": "schema/clusters.json",
    "tools/schema_check.py": "tests/schema_check.py",
}
"""cloudflow's file -> its copy in csis-sandbox-configs"""


def pairs(export: Path) -> list[tuple[Path, Path]]:
    """Give each of cloudflow's files with the path of its copy."""
    return [
        (export / "cloudflow" / source, export / "sandbox-configs" / copy) for source, copy in COPIES.items()
    ]


def problems(export: Path) -> list[str]:
    """Say which copies differ from cloudflow's files, or are missing."""
    found: list[str] = []
    for source, copy in pairs(export):
        if not source.is_file():
            found.append(f"cloudflow has no {source.relative_to(export / 'cloudflow')}")
        elif not copy.is_file() or copy.read_bytes() != source.read_bytes():
            found.append(
                f"sandbox-configs: {copy.relative_to(export / 'sandbox-configs')} differs from cloudflow's"
            )
    return found


def write(export: Path) -> list[str]:
    """Write every copy that differs; give what was written."""
    written: list[str] = []
    for source, copy in pairs(export):
        if not copy.is_file() or copy.read_bytes() != source.read_bytes():
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(source.read_bytes())
            written.append(str(copy.relative_to(export)))
    return written


def main(argv: list[str] | None = None) -> int:
    """Run one command; see the module docstring."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", maxsplit=1)[0])
    parser.add_argument("--export", type=Path, default=HERE.parent, help="the exportit/ directory")
    parser.add_argument("command", choices=["write", "check"])
    args = parser.parse_args(argv)
    export: Path = args.export
    if args.command == "write":
        for line in write(export):
            print(f"wrote {line}")
        return 0
    found = problems(export)
    for problem in found:
        print(f"PROBLEM {problem}", file=sys.stderr)
    if not found:
        print("configs: csis-sandbox-configs' schema and rules are cloudflow's")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
