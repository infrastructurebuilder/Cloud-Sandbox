from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.slow


def run(*command: str, cwd: Path) -> str:
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout


@pytest.fixture(scope="module")
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("dist")
    run("uv", "build", "--wheel", "--out-dir", str(out), cwd=PROJECT)
    (built,) = out.glob("cloudflow_plotting-*.whl")
    return built


def test_the_wheel_holds_the_package_and_no_namespace_init(wheel: Path) -> None:
    names = set(zipfile.ZipFile(wheel).namelist())
    for module in ["plot_fvcom", "plot_roms", "shared", "tile", "hlfs"]:
        assert f"cloudflow/plotting/{module}.py" in names
    assert "cloudflow/__init__.py" not in names
    assert "cloudflow/plotting/__init__.py" not in names


def test_the_wheel_works_away_from_the_source_tree(wheel: Path, tmp_path: Path) -> None:
    venv = tmp_path / "venv"
    python = venv / "bin" / "python"
    run("uv", "venv", "--quiet", "--python", "3.12", str(venv), cwd=tmp_path)
    run("uv", "pip", "install", "--quiet", "--python", str(python), str(wheel), cwd=tmp_path)
    where = run(
        str(python),
        "-c",
        "import cloudflow.plotting.tile as t; print(t.__file__); print(t.Tile4326().tile(-76.0, 38.0, 5))",
        cwd=tmp_path,
    ).splitlines()
    assert str(venv) in where[0]
    assert where[1] == "(9, 12, 5)"
