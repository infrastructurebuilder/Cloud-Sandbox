from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path

import pytest
from support import PROJECT

PLOTTING = PROJECT.parent / "cloudflow-plotting"

pytestmark = pytest.mark.slow

PROBE = """
import os
import cloudflow.plotting.tile
from cloudflow.workflows import tasks
print(tasks.curdir)
print(os.access(os.path.join(tasks.curdir, "fcst_launcher.sh"), os.X_OK))
print(cloudflow.plotting.tile.__file__)
"""


def run(*command: str, cwd: Path, expect: int = 0) -> str:
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    assert done.returncode == expect, done.stdout + done.stderr
    return done.stdout


@pytest.fixture(scope="module")
def wheels(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    out = tmp_path_factory.mktemp("dist")
    run("uv", "build", "--wheel", "--out-dir", str(out), cwd=PROJECT)
    run("uv", "build", "--wheel", "--out-dir", str(out), cwd=PLOTTING)
    (own,) = out.glob("cloudflow-*.whl")
    (plotting,) = out.glob("cloudflow_plotting-*.whl")
    return own, plotting


@pytest.fixture(scope="module")
def installed(wheels: tuple[Path, Path], tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Install both wheels into an empty environment; return its bin directory."""
    venv = tmp_path_factory.mktemp("install") / "venv"
    run("uv", "venv", "--quiet", "--python", "3.12", str(venv), cwd=venv.parent)
    python = venv / "bin" / "python"
    run("uv", "pip", "install", "--quiet", "--python", str(python), *map(str, wheels), cwd=venv.parent)
    return venv / "bin"


def test_the_wheel_carries_what_the_code_looks_up(wheels: tuple[Path, Path]) -> None:
    archive = zipfile.ZipFile(wheels[0])
    members = {info.filename: info for info in archive.infolist()}
    templates = [name for name in members if name.startswith("cloudflow/job/templates/")]
    assert len(templates) == 44
    for launcher in ["fcst_launcher.sh", "experiment_launcher.sh", "scripts/getNomadsProd.sh"]:
        mode = members[f"cloudflow/workflows/{launcher}"].external_attr >> 16
        assert mode & 0o111, f"{launcher} lost its executable bit"


def test_the_two_wheels_share_the_namespace_without_overlap(wheels: tuple[Path, Path]) -> None:
    own, plotting = (set(zipfile.ZipFile(wheel).namelist()) for wheel in wheels)
    code = {name for name in own & plotting if name.startswith("cloudflow/")}
    assert code == set()
    assert "cloudflow/__init__.py" not in own | plotting
    assert not any(name.startswith("cloudflow/plotting/") for name in own)


def test_the_installed_package_finds_its_own_files(installed: Path, tmp_path: Path) -> None:
    lines = run(str(installed / "python"), "-c", PROBE, cwd=tmp_path).splitlines()
    site = str(installed.parent)
    assert lines[-3].startswith(site)
    assert lines[-2] == "True"
    assert lines[-1].startswith(site)


def test_the_installed_command_runs(installed: Path, tmp_path: Path) -> None:
    out = run(str(installed / "cloudflow"), cwd=tmp_path, expect=1)
    assert "cluster_config job_config" in out
