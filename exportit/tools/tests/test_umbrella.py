"""The umbrella's units.toml names every unit of exportit/, at the unit's own version."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "exportit"
UMBRELLA = "cloud-sandbox"
# The export tool itself is how the copies are made; it is not relocated.
NOT_UNITS = {UMBRELLA, "tools"}


def manifest() -> dict[str, dict[str, object]]:
    units = tomllib.loads((EXPORT / UMBRELLA / "units.toml").read_text())["unit"]
    return {unit["name"]: unit for unit in units}


def test_the_manifest_names_every_mapped_unit() -> None:
    mapped = {path.stem for path in EXPORT.glob("*.map")} - NOT_UNITS
    assert set(manifest()) == mapped


def test_a_unit_with_a_pyproject_has_that_version_in_the_manifest() -> None:
    differ: list[str] = []
    for name, unit in manifest().items():
        pyproject = EXPORT / name / "pyproject.toml"
        if pyproject.is_file():
            version = tomllib.loads(pyproject.read_text())["project"]["version"]
            if version != unit["version"]:
                differ.append(f"{name}: {unit['version']} in units.toml, {version} in pyproject.toml")
    assert not differ, differ


def test_every_unit_has_a_justfile_with_the_five_targets() -> None:
    missing: list[str] = []
    for name in [*manifest(), UMBRELLA]:
        text = (EXPORT / name / "Justfile").read_text()
        missing += [
            f"{name}: {target}"
            for target in ("init", "build", "test", "full-test", "release")
            if f"\n{target}:" not in text and f"\n{target} " not in text
        ]
    assert not missing, missing
