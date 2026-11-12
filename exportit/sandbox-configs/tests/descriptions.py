"""Read every file of the unit and say what it is, what role it plays, and whether cloudflow can use it.

Run as a script to write the catalogue again::

    uv run python tests/descriptions.py --record

The tests compare what this module finds with ``tests/catalogue.json``, so a
change in any description, or in the schema, shows up as a difference to
review rather than passing unnoticed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

UNIT = Path(__file__).resolve().parents[1]
DIRECTORIES = ["job.configs", "cluster.configs"]
SCHEMA = UNIT / "schema"
CATALOGUE = UNIT / "tests" / "catalogue.json"

# One site's AWS resources, by the shape of their identifiers.
AWS_IDENTIFIER = re.compile(r"\b(ami|sg|subnet|vpc)-[0-9a-f]{8,17}\b")
# Paths in one person's directory. /save/ec2-user is the default user of the
# image, not a person, so it does not count.
PERSONAL_PATH = re.compile(r"(/save|/home|/com|/ptmp)/(?!ec2-user\b|\$)[a-z][a-z0-9_.-]*/")
PLACEHOLDER = re.compile(r"/pathway/to/|<[A-Za-z_ ]+>|__[A-Z_]+__")


def files() -> list[str]:
    """List the copied files, relative to the unit, in a fixed order."""
    return sorted(
        path.relative_to(UNIT).as_posix()
        for directory in DIRECTORIES
        for path in (UNIT / directory).rglob("*")
        if path.is_file()
    )


def schema(name: str) -> dict[str, Any]:
    """Read one of the two schema files."""
    return json.loads((SCHEMA / name).read_text())


def strings_in(value: Any) -> list[str]:
    """Give every string inside a JSON value."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings_in(item)]  # type: ignore[union-attr]
    if isinstance(value, list):
        return [text for item in value for text in strings_in(item)]  # type: ignore[union-attr]
    return []


def missing_keys(description: dict[str, Any], entry: dict[str, Any], common: dict[str, Any]) -> list[str]:
    """List the required keys a description lacks."""
    required = {**common["required"], **entry["required"]}
    return sorted(key for key in required if key not in description)


def check_job(description: dict[str, Any]) -> str:
    """Say whether cloudflow can read a job description."""
    jobs = schema("jobs.json")
    jobtype = description.get("JOBTYPE")
    entry = jobs["jobtypes"].get(jobtype)
    if entry is None:
        return f"unknown JOBTYPE {jobtype!r}"
    if description.get("MODEL") != entry["MODEL"]:
        return f"JOBTYPE {jobtype} needs MODEL {entry['MODEL']}, not {description.get('MODEL')!r}"
    missing = missing_keys(description, entry, jobs["common"])
    return f"missing {', '.join(missing)}" if missing else "ok"


def check_cluster(description: dict[str, Any]) -> str:
    """Say whether cloudflow can read a cluster description."""
    clusters = schema("clusters.json")
    platform = description.get("platform")
    entry = clusters["platforms"].get(platform)
    if entry is None:
        return f"unknown platform {platform!r}"
    missing = missing_keys(description, entry, clusters["common"])
    return f"missing {', '.join(missing)}" if missing else "ok"


def role_of(path: str, texts: list[str]) -> str:
    """Say whether a description is a template, one site's data, or an example."""
    if "template" in Path(path).name or any(PLACEHOLDER.search(text) for text in texts):
        return "template"
    if any(AWS_IDENTIFIER.search(text) or PERSONAL_PATH.search(text) for text in texts):
        return "site"
    return "example"


def examine(path: str) -> dict[str, str]:
    """Describe one file: its kind, its role, and whether cloudflow can use it."""
    full = UNIT / path
    text = full.read_text(errors="replace")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        return examine_other(path, text, error)
    if not isinstance(value, dict):
        return {"kind": "other", "role": "note", "status": "JSON, but not an object"}
    description: dict[str, Any] = value  # type: ignore[assignment]
    texts = strings_in(description)
    if "platform" in description:
        return {"kind": "cluster", "role": role_of(path, texts), "status": check_cluster(description)}
    if "JOBTYPE" in description or "MODEL" in description:
        return {"kind": "job", "role": role_of(path, texts), "status": check_job(description)}
    return {"kind": "other", "role": role_of(path, texts), "status": "JSON, but neither a job nor a cluster"}


def examine_other(path: str, text: str, error: json.JSONDecodeError) -> dict[str, str]:
    """Describe a file that is not JSON."""
    lines = text.splitlines()
    if text.startswith("#!"):
        return {"kind": "other", "role": "helper", "status": "a script"}
    if path.endswith(".py"):
        return {"kind": "other", "role": "helper", "status": "a Python script"}
    if len(lines) == 1 and lines[0].strip() and " " not in lines[0].strip():
        # A file holding the name of another, like a symbolic link would.
        named = lines[0].strip()
        top = UNIT / Path(path).parts[0]
        exists = (UNIT / Path(path).parent / named).is_file() or (top / named).is_file()
        status = f"names {named}" if exists else f"names {named}, which is not here"
        return {"kind": "other", "role": "pointer", "status": status}
    if text.lstrip().startswith(("{", '"')):
        kind = "cluster" if path.startswith("cluster.configs/") else "job"
        texts = re.findall(r'"([^"]*)"', text)
        return {
            "kind": kind,
            "role": role_of(path, texts),
            "status": f"not JSON: {error.msg} at line {error.lineno}",
        }
    return {"kind": "other", "role": "note", "status": "text"}


def catalogue() -> dict[str, dict[str, str]]:
    """Examine every file."""
    return {path: examine(path) for path in files()}


def record() -> None:
    """Write the catalogue file from what is here now."""
    CATALOGUE.write_text(json.dumps(catalogue(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {CATALOGUE.relative_to(UNIT)}")


if __name__ == "__main__":
    if sys.argv[1:] != ["--record"]:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    record()
