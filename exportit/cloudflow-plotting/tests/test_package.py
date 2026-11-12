from __future__ import annotations

import importlib
from pathlib import Path

import pytest

import cloudflow.plotting

PACKAGE = Path(next(iter(cloudflow.plotting.__path__)))

MODULES = ["plot_fvcom", "plot_roms", "shared", "tile"]

# Python files that cannot be imported as modules, and why.
SCRIPTS = {
    "hlfs": "an exported notebook: it runs main('hlfs.config') when it is imported",
}


def python_files() -> list[Path]:
    return sorted(PACKAGE.glob("*.py"))


def test_every_python_file_is_accounted_for() -> None:
    assert {path.stem for path in python_files()} == set(MODULES) | set(SCRIPTS)


@pytest.mark.parametrize("path", python_files(), ids=lambda path: path.name)
def test_file_compiles(path: Path) -> None:
    compile(path.read_text(), str(path), "exec")


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name: str) -> None:
    importlib.import_module(f"cloudflow.plotting.{name}")


def test_cloudflow_is_a_namespace() -> None:
    import cloudflow  # noqa: PLC0415

    assert cloudflow.__file__ is None
    assert not (PACKAGE.parent / "__init__.py").exists()
