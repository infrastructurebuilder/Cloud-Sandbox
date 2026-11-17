"""The umbrella's units.toml names every unit of exportit/, at the unit's own version."""

from __future__ import annotations

import configparser
import re
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
    copied = {name for name, unit in manifest().items() if not unit.get("external")}
    assert copied == mapped


def submodules() -> dict[str, str]:
    """The units kept here as submodules: directory under exportit/ -> the URL .gitmodules gives."""
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules")
    found = {parser[section]["path"]: parser[section]["url"] for section in parser.sections()}
    return {path.removeprefix("exportit/"): url for path, url in found.items()}


def test_a_submodule_is_the_repository_the_manifest_names() -> None:
    """A submodule's URL is relative, following this repository's remote; its name is the manifest's."""
    units = manifest()
    differ: list[str] = []
    for name, url in submodules().items():
        if name == UMBRELLA:
            continue
        repository = str(units[name]["repository"]).rsplit("/", 1)[1]
        if url != f"../{repository}.git":
            differ.append(f"{name}: .gitmodules says {url}, units.toml says {repository}")
    assert not differ, differ


def test_every_submodule_is_a_mapped_unit() -> None:
    mapped = {path.stem for path in EXPORT.glob("*.map")}
    assert set(submodules()) <= mapped


def test_an_external_unit_is_not_copied_here() -> None:
    for name, unit in manifest().items():
        if unit.get("external"):
            assert not (EXPORT / f"{name}.map").exists(), name
            assert not (EXPORT / name).exists(), name


def test_the_collection_is_pinned_where_it_is_used_at_its_manifest_version() -> None:
    requirements = (EXPORT / "sandbox-provisioning" / "requirements.yml").read_text()
    pinned = re.search(
        r"ansible-collection-csis-spack\.git\n\s+type: git\n\s+version: \"([^\"]+)\"", requirements
    )
    assert pinned, "sandbox-provisioning/requirements.yml does not pin the collection"
    assert pinned.group(1) == manifest()["ansible-collection-csis-spack"]["version"]


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
    for name in [*(name for name, unit in manifest().items() if not unit.get("external")), UMBRELLA]:
        text = (EXPORT / name / "Justfile").read_text()
        missing += [
            f"{name}: {target}"
            for target in ("init", "build", "test", "full-test", "release")
            if f"\n{target}:" not in text and f"\n{target} " not in text
        ]
    assert not missing, missing


def test_the_site_mirror_keys_fingerprint_is_the_key_sandbox_ops_keeps() -> None:
    """sandbox-provisioning trusts the site mirror's key by a fingerprint; it is this key's."""
    variables = (EXPORT / "sandbox-provisioning" / "group_vars" / "all.yml").read_text()
    (fingerprint,) = re.findall(r"^spack_key_fingerprint: ([0-9A-F]{40})$", variables, re.MULTILINE)
    assert (EXPORT / "sandbox-ops" / "keys" / f"{fingerprint}.pub").is_file()
