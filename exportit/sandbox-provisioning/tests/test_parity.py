"""The values the playbooks use are the values the scripts compute."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml
from support import ENVIRONMENT, FUNCS, UNIT, VARIABLES, functions, lines_of, rendered, script_values

DEFAULT_NPROC = 8


@pytest.fixture(scope="module")
def values(tmp_path_factory: pytest.TempPathFactory) -> dict:
    return rendered(tmp_path_factory.mktemp("render") / "values.json", nproc=DEFAULT_NPROC)


@pytest.fixture(scope="module")
def script() -> dict[str, str]:
    return script_values(DEFAULT_NPROC)


def body(function: str) -> list[str]:
    """Give the lines of one function, without blank lines and comments."""
    lines = lines_of(FUNCS)
    stripped = [lines[number].strip() for number in functions()[function]]
    return [line for line in stripped if line and not line.startswith("#")]


def substitute(text: str, known: dict[str, str]) -> str:
    """Put the script's values in place of $NAME and ${NAME}."""
    return re.sub(r"\$\{?(\w+)\}?", lambda match: known.get(match.group(1), match.group(0)), text)


def test_every_exported_variable_is_mapped() -> None:
    exported = set(re.findall(r"^\s*export (\w+)=", ENVIRONMENT.read_text(), re.MULTILINE))
    assert exported == set(VARIABLES)


def test_every_mapped_variable_exists() -> None:
    defined = yaml.safe_load((UNIT / "group_vars" / "all.yml").read_text())
    assert set(VARIABLES.values()) <= set(defined)


@pytest.mark.parametrize("name", sorted(set(VARIABLES) - {"ami_name"}))
def test_a_variable_has_the_value_the_script_gives_it(
    name: str, values: dict, script: dict[str, str]
) -> None:
    assert str(values[name]) == script[name]


def test_the_fallback_image_name_has_the_scripts_form(values: dict, script: dict[str, str]) -> None:
    form = re.compile(r"IOOS-Cloud-Sandbox-\d{8}_\d\d-\d\d")
    assert form.fullmatch(script["ami_name"])
    assert form.fullmatch(values["ami_name"])


@pytest.mark.parametrize("nproc", [1, 2, 3, 96])
def test_build_jobs_follow_the_processor_count(nproc: int, tmp_path: Path) -> None:
    ours, theirs = rendered(tmp_path / "v.json", nproc=nproc), script_values(nproc)
    assert ours["JOBS"] == theirs["JOBS"]
    assert ours["SPACKOPTS"] == theirs["SPACKOPTS"]


@pytest.mark.parametrize("cache_only", [1, 0, -1])
def test_the_cache_flag_follows_the_setting(cache_only: int, tmp_path: Path) -> None:
    ours = rendered(tmp_path / "v.json", cache_only=cache_only)
    assert ours["SPACKOPTS"] == script_values(DEFAULT_NPROC, cache_only)["SPACKOPTS"]


def test_the_pip_list_is_the_scripts(values: dict, script: dict[str, str]) -> None:
    theirs = []
    for line in body("install_python_modules_user"):
        match = re.match(r"python3 -m pip install (--upgrade )?(\S+)", line)
        if match:
            spec = substitute(match.group(2).strip('"'), script)
            theirs.append({"spec": spec, "upgrade": bool(match.group(1))})
    assert values["pip"] == theirs
    assert len(theirs) == 14


def dnf_installs(function: str, known: dict[str, str]) -> list[str]:
    found: list[str] = []
    for line in body(function):
        match = re.match(r"sudo dnf -y install (.+)", line)
        if match:
            found.extend(substitute(match.group(1), known).split())
    return found


def test_the_base_packages_are_the_scripts(values: dict, script: dict[str, str]) -> None:
    defaults = yaml.safe_load((UNIT / "roles/base_system/defaults/main.yml").read_text())
    ours = [
        defaults["base_system_epel_release_url"],
        "rh-amazon-rhui-client",
        *values["dnf_base"],
        defaults["base_system_ssm_agent_url"],
        "environment-modules",
    ]
    assert ours == dnf_installs("setup_environment", script)


def test_the_intel_packages_are_the_scripts(values: dict, script: dict[str, str]) -> None:
    assert values["dnf_intel"] == dnf_installs("install_intel_oneapi_dnf", script)


def test_the_intel_modules_are_the_ones_the_script_loads(values: dict) -> None:
    theirs = [line.split()[2] for line in body("install_intel_oneapi_dnf") if line.startswith("module load ")]
    assert values["intel_modules"] == theirs


def test_spack_is_told_about_the_same_externals_and_providers(values: dict, script: dict[str, str]) -> None:
    text = "\n".join(body("install_intel_oneapi_dnf")).replace("\\\n", " ")
    externals = re.findall(r"add_spack_site_external\s+(\S+)\s+(\S+)\s+(\S+)", text)
    ours = [(item["package"], item["spec"], item["prefix"]) for item in values["spack_externals"]]
    assert ours == externals
    providers = re.findall(r"spack config --scope site add '([^']+)'", text)
    assert values["spack_providers"] == providers


def test_the_spack_environment_gets_the_same_settings_and_specs(values: dict, script: dict[str, str]) -> None:
    settings = re.findall(r"spack config add '([^']+)'", "\n".join(body("create_spack-environment")))
    assert values["spack_settings"] == settings
    known = {**script, "COMPILER": f"intel-oneapi-compilers@{script['ONEAPI_VER']}"}
    specs = re.findall(r'^spack add "([^"]+)"', "\n".join(body("build_spack-environment")), re.MULTILINE)
    assert values["spack_specs"] == [substitute(spec, known) for spec in specs]


def test_the_spack_role_runs_the_scripts_commands_in_order() -> None:
    theirs = [line for line in body("install_spack") if line.startswith("spack ")]
    role = (UNIT / "roles/spack/tasks/main.yml").read_text()
    ours = [
        line.strip().replace("$spack ", "spack ", 1)
        for line in role.splitlines()
        if line.strip().startswith("$spack ")
    ]
    assert ours == theirs


@pytest.mark.parametrize(
    ("role_file", "first", "last"),
    [
        ("roles/mpi_ssh/files/sandbox-local-net.conf", 1355, 1437),
        ("roles/intel_oneapi/files/oneAPI.repo", 892, 898),
        ("roles/hpc_tuning/files/tuned.conf", 196, 208),
    ],
)
def test_a_file_written_out_of_the_script_has_the_scripts_text(role_file: str, first: int, last: int) -> None:
    theirs = "\n".join(lines_of(FUNCS)[first : last + 1]) + "\n"
    assert (UNIT / role_file).read_text() == theirs


@pytest.mark.parametrize(
    ("kernel", "edits"),
    [
        ("6.12.0-211.5.1.el10_2.x86_64", ["s#gpgcheck=1#gpgcheck=0#"]),
        ("6.12.0-124.8.1.el10_1.x86_64", ["s#gpgcheck=1#gpgcheck=0#", "s#10#10.1#"]),
        ("6.12.0-55.9.1.el10_0.x86_64", ["s#gpgcheck=1#gpgcheck=0#"]),
    ],
)
def test_the_lustre_repository_gets_the_edits_sed_would_make(
    kernel: str, edits: list[str], tmp_path: Path
) -> None:
    ours = rendered(tmp_path / "v.json", kernel=kernel)["fsx_repo_text"]
    theirs = (UNIT / "tests" / "fsx-lustre-client.repo.sample").read_text()
    for edit in edits:
        theirs = subprocess.run(
            ["sed", edit], input=theirs, capture_output=True, text=True, check=True
        ).stdout
    assert ours == theirs
    assert "gpgcheck=1" not in ours
    assert ("/el/10.1/" in ours) == (len(edits) == 2)
