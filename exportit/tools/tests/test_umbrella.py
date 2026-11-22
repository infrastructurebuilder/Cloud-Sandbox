"""The umbrella's units.toml names every unit of exportit/, at the unit's own version."""

from __future__ import annotations

import configparser
import operator
import re
import tomllib
from collections.abc import Callable
from pathlib import Path

import pytest

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


COLLECTION = "infrastructurebuilder.csis_spack"
REPOSITORY = "https://github.com/infrastructurebuilder/ansible-collection-csis-spack.git"
Release = tuple[int, ...]
COMPARISONS: dict[str, Callable[[Release, Release], bool]] = {
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
}


def release(text: str) -> Release:
    return tuple(int(part) for part in text.split("."))


def satisfies(version: str, spec: str) -> bool:
    """Say whether a version is inside a range as ansible-galaxy writes one (">=0.0.1,<0.1.0", or "0.0.1")."""
    for part in (item.strip() for item in spec.split(",")):
        found = re.fullmatch(r"(>=|<=|==|!=|>|<)?\s*(\d+(?:\.\d+)*)", part)
        assert found, f"cannot read the version requirement {part!r}"
        if not COMPARISONS[found.group(1) or "=="](release(version), release(found.group(2))):
            return False
    return True


def collection_requirement() -> tuple[str, str]:
    """Give how sandbox-provisioning's requirements.yml names the collection, and its version requirement."""
    requirements = (EXPORT / "sandbox-provisioning" / "requirements.yml").read_text()
    entry = re.search(
        rf"- name: ({re.escape(COLLECTION)}|{re.escape(REPOSITORY)})\n((?:\s{{4}}\w+: .*\n)+)", requirements
    )
    assert entry, "sandbox-provisioning/requirements.yml does not name the collection"
    fields = dict(re.findall(r"(\w+): \"?([^\"\n]+)\"?", entry.group(2)))
    return entry.group(1), fields["version"]


def test_the_collection_is_pinned_where_it_is_used_at_its_manifest_version() -> None:
    """The manifest's version is inside the range requirements.yml gives, or is the tag it names."""
    source, wanted = collection_requirement()
    version = str(manifest()["ansible-collection-csis-spack"]["version"])
    if source == REPOSITORY:
        assert wanted == version, f"requirements.yml names the tag {wanted}, units.toml {version}"
    else:
        assert satisfies(version, wanted), f"units.toml's {version} is not within {wanted!r}"


@pytest.mark.parametrize(
    ("version", "spec", "inside"),
    [
        ("0.0.1", ">=0.0.1,<0.1.0", True),
        ("0.0.9", ">=0.0.1,<0.1.0", True),
        ("0.1.0", ">=0.0.1,<0.1.0", False),
        ("0.0.0", ">=0.0.1,<0.1.0", False),
        ("0.0.1", "0.0.1", True),
        ("0.0.2", "==0.0.1", False),
    ],
)
def test_a_version_is_inside_a_range_as_galaxy_reads_it(version: str, spec: str, inside: bool) -> None:
    assert satisfies(version, spec) is inside


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


LAUNCH_TAG = re.compile(
    r'^LAUNCH_TAG = \{"Key": "(?P<key>[^"]+)", "Value": "(?P<value>[^"]+)"\}$', re.MULTILINE
)


def reaper_default(name: str) -> str:
    text = (EXPORT / "sandbox-terraform" / "reaper" / "variables.tf").read_text()
    block = re.search(r'variable "' + name + r'" \{(?P<body>.*?)\n\}', text, re.DOTALL)
    assert block, f"reaper/variables.tf has no variable {name}"
    default = re.search(r'default\s*=\s*"(?P<value>[^"]*)"', block["body"])
    assert default, f"{name} has no default"
    return default["value"]


def test_the_launch_tag_cloudflow_adds_is_the_one_the_reaper_requires() -> None:
    # A check between two units, kept here, where both are checked out (spec 003).
    source = (EXPORT / "cloudflow" / "src" / "cloudflow" / "cluster" / "AWSCluster.py").read_text()
    tag = LAUNCH_TAG.search(source)
    assert tag, "cloudflow's AWSCluster.py has no LAUNCH_TAG constant"
    assert (tag["key"], tag["value"]) == (
        reaper_default("launch_tag_key"),
        reaper_default("launch_tag_value"),
    )
