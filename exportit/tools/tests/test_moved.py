"""A file moved from one unit to another, keeping both units' lineage (spec 003).

The directive, written in the map of the unit a file leaves::

    moved <source> <unit> <destination>

Each test builds an "original", a Cloud-Sandbox-like root with three maps and
units.toml, and two units' repositories made from the original as moving day
made the real ones: ``lib`` (``pkg/`` under ``src/pkg/``), from which
``pkg/fn.py`` moves, and ``ops`` (``other/``), which it moves to, as
``funcs/fn.py``. See specs/003-lambda-functions-owner/contracts/moved-directive.md.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import export

AUTHOR = ["-c", "user.name=Upstream Author", "-c", "user.email=upstream@example.invalid"]
US = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]

LIB_MAP = """\
copy pkg/ src/pkg/
moved pkg/fn.py ops funcs/fn.py
new README.md
"""

OPS_MAP = """\
copy other/ other/
new README.md
"""

UMBRELLA_MAP = """\
covers ./
copy top.txt top.txt
new units.toml
"""

FN = "def fn():\n    return 1\n"


def git(repo: Path, *args: str, who: list[str] = US) -> str:
    done = subprocess.run(["git", "-C", str(repo), *who, *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def commit(repo: Path, message: str, files: dict[str, str | None], who: list[str] = AUTHOR) -> str:
    for name, text in files.items():
        if text is None:
            git(repo, "rm", "--quiet", name)
            continue
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        git(repo, "add", name)
    git(repo, "commit", "--quiet", "-m", message, who=who)
    return git(repo, "rev-parse", "HEAD")


def run(root: Path, *args: str) -> int:
    return export.main(["--root", str(root), *args])


def extract(original: Path, unit: Path, directives: str, scratch: Path) -> None:
    """Make a unit's repository from the original, as moving day did."""
    paths = scratch / f"{unit.name}.paths"
    paths.write_text(directives)
    subprocess.run(["git", "clone", "--quiet", "--no-local", str(original), str(unit)], check=True)
    subprocess.run(
        ["uvx", "--quiet", "git-filter-repo", "--quiet", "--paths-from-file", str(paths)],
        cwd=unit,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def world(tmp_path: Path) -> dict[str, Path | str]:
    original = tmp_path / "original"
    original.mkdir()
    git(original, "init", "--quiet", "--initial-branch", "main")
    commit(
        original,
        "Start",
        {
            "pkg/a.py": "a = 1\n",
            "pkg/fn.py": FN,
            "other/x.txt": "x\n",
            "top.txt": "top\n",
        },
    )
    baseline = commit(original, "Change a upstream", {"pkg/a.py": "a = 2\n"})

    root = tmp_path / "sandbox"
    export_dir = root / "exportit"
    export_dir.mkdir(parents=True)
    (export_dir / "lib.map").write_text(LIB_MAP)
    (export_dir / "ops.map").write_text(OPS_MAP)
    (export_dir / "cloud-sandbox.map").write_text(UMBRELLA_MAP)
    umbrella = export_dir / "cloud-sandbox"
    umbrella.mkdir()
    (umbrella / "top.txt").write_text("top\n")
    (umbrella / "units.toml").write_text(
        f'[[unit]]\nname = "lib"\nrepository = "x"\nversion = "0.0.1"\nbaseline = "{baseline}"\n\n'
        f'[[unit]]\nname = "ops"\nrepository = "y"\nversion = "0.0.1"\nbaseline = "{baseline}"\n\n'
        f'[umbrella]\nbaseline = "{baseline}"\n'
    )
    git(root, "init", "--quiet")
    git(root, "add", "-A")
    git(root, "commit", "--quiet", "-m", "the maps")

    lib, ops = export_dir / "lib", export_dir / "ops"
    extract(original, lib, "pkg/\npkg/==>src/pkg/\n", tmp_path)
    commit(lib, "Add what exists only in the unit", {"README.md": "lib\n"}, who=US)
    commit(lib, "The function leaves for ops", {"src/pkg/fn.py": None}, who=US)
    git(lib, "branch", "-M", "develop")
    extract(original, ops, "other/\n", tmp_path)
    commit(ops, "Add what exists only in the unit", {"README.md": "ops\n"}, who=US)
    commit(ops, "The function arrives from lib", {"funcs/fn.py": FN}, who=US)
    git(ops, "branch", "-M", "develop")
    return {"original": original, "root": root, "lib": lib, "ops": ops, "baseline": baseline}


def parts(world: dict[str, Path | str]) -> tuple[Path, Path, Path, Path]:
    return Path(world["original"]), Path(world["root"]), Path(world["lib"]), Path(world["ops"])


def with_lib_map(root: Path, text: str) -> None:
    (root / "exportit/lib.map").write_text(text)


def problems(root: Path, original: Path, capsys: pytest.CaptureFixture[str]) -> str:
    assert run(root, "--source", str(original), "check") == 1
    return capsys.readouterr().err


# Reading the directive, and its five problems (T003)


def test_moved_is_read_into_the_leaving_unit(world: dict[str, Path | str]) -> None:
    _, root, _, _ = parts(world)
    unit = export.parse_map(root / "exportit/lib.map")
    assert unit.moves == [export.Move("lib", "pkg/fn.py", "ops", "funcs/fn.py", 2)]


@pytest.mark.parametrize(
    "line",
    ["moved pkg/fn.py ops", "moved pkg/ ops funcs/", "moved pkg/fn.py ops funcs/ extra"],
)
def test_a_moved_line_of_the_wrong_form_is_refused(world: dict[str, Path | str], line: str) -> None:
    _, root, _, _ = parts(world)
    with_lib_map(root, f"copy pkg/ src/pkg/\n{line}\n")
    with pytest.raises(export.MapError, match=r"lib\.map:2"):
        export.parse_map(root / "exportit/lib.map")


def test_a_source_the_maps_own_copy_rules_do_not_take_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    with_lib_map(root, LIB_MAP + "moved other/x.txt ops funcs/x.txt\n")
    assert "not taken by a copy rule of lib.map: other/x.txt" in problems(root, original, capsys)


def test_moving_to_an_unknown_unit_or_to_its_own_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    with_lib_map(root, "copy pkg/ src/pkg/\nmoved pkg/fn.py nowhere funcs/fn.py\nnew README.md\n")
    assert "moves pkg/fn.py to nowhere, which is not a unit" in problems(root, original, capsys)
    with_lib_map(root, "copy pkg/ src/pkg/\nmoved pkg/fn.py lib funcs/fn.py\nnew README.md\n")
    assert "moves pkg/fn.py to its own unit" in problems(root, original, capsys)


def test_a_destination_the_arriving_unit_copies_or_given_twice_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    with_lib_map(root, "copy pkg/ src/pkg/\nmoved pkg/fn.py ops other/x.txt\nnew README.md\n")
    assert "other/x.txt is a file ops.map copies" in problems(root, original, capsys)
    with_lib_map(root, LIB_MAP + "moved pkg/a.py ops funcs/fn.py\n")
    assert "ops: funcs/fn.py is the destination of two moved lines" in problems(root, original, capsys)


def test_a_source_another_units_copy_rule_also_takes_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    (root / "exportit/ops.map").write_text(OPS_MAP + "copy pkg/ vendored/\n")
    assert "pkg/fn.py is also taken by ops.map:3" in problems(root, original, capsys)


def test_a_source_moved_twice_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    with_lib_map(root, LIB_MAP + "moved pkg/fn.py ops funcs/again.py\n")
    assert "pkg/fn.py is moved more than once" in problems(root, original, capsys)


# What the check sees (T004)


def test_the_leaving_unit_no_longer_expects_the_file(world: dict[str, Path | str]) -> None:
    original, root, _, _ = parts(world)
    assert run(root, "--source", str(original), "check", "lib") == 0


def test_without_the_directive_the_leaving_unit_misses_it_and_the_arriving_unit_has_a_stray(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, _ = parts(world)
    with_lib_map(root, "copy pkg/ src/pkg/\nnew README.md\n")
    assert run(root, "--source", str(original), "check") == 1
    err = capsys.readouterr().err
    assert "lib: src/pkg/fn.py: missing" in err
    assert "ops: funcs/fn.py: neither copied nor declared new" in err


def test_the_arriving_unit_accepts_the_file_without_a_new_line(world: dict[str, Path | str]) -> None:
    original, root, _, _ = parts(world)
    assert run(root, "--source", str(original), "check", "ops") == 0


def test_a_moved_file_absent_from_the_arriving_unit_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, ops = parts(world)
    commit(ops, "Lose it", {"funcs/fn.py": None}, who=US)
    assert run(root, "--source", str(original), "check", "ops") == 1
    assert "ops: funcs/fn.py: moved here from lib but absent" in capsys.readouterr().err


def test_baselines_and_lineage_of_both_units_are_unchanged(world: dict[str, Path | str]) -> None:
    original, root, _, _ = parts(world)
    assert run(root, "--source", str(original), "check", "--baselines") == 0
    assert run(root, "--source", str(original), "lineage", "lib", "ops") == 0


def test_the_filter_directives_are_those_of_the_copy_rules(world: dict[str, Path | str]) -> None:
    original, root, _, _ = parts(world)
    with export.open_source(root, original) as source:
        units, plan = export.load_plan(root, source)
        assert export.filter_directives(units, plan, "lib", source.files) == ["pkg/", "pkg/==>src/pkg/"]


# Syncing the leaving unit (T005)


def sync(root: Path, original: Path) -> int:
    return run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1")


def test_a_change_to_a_moved_file_lands_in_the_arriving_unit(world: dict[str, Path | str]) -> None:
    original, root, lib, ops = parts(world)
    first = commit(original, "Fix fn", {"pkg/fn.py": "def fn():\n    return 2\n"})
    head = commit(original, "Fix fn again", {"pkg/fn.py": "def fn():\n    return 3\n"})
    assert sync(root, original) == 0
    assert git(ops, "branch", "--show-current") == "feature/sync-1"
    assert (ops / "funcs/fn.py").read_text() == "def fn():\n    return 3\n"
    carried = git(ops, "log", "--format=%B", "develop..HEAD")
    assert git(ops, "rev-list", "--count", "develop..HEAD") == "1"
    for needed in ("Fix fn", "Fix fn again", "Upstream Author", first[:12], head[:12], "funcs/fn.py"):
        assert needed in carried
    assert not (lib / "src/pkg/fn.py").exists()
    assert git(lib, "status", "--porcelain") == ""
    units = (root / "exportit/cloud-sandbox/units.toml").read_text()
    assert units.count(f'baseline = "{head}"') == 1
    assert export.baselines(root)["lib"] == head
    assert export.baselines(root)["ops"] == world["baseline"]


def test_other_changes_are_merged_into_the_leaving_unit_as_before(world: dict[str, Path | str]) -> None:
    original, root, lib, ops = parts(world)
    commit(original, "Change a and fn", {"pkg/a.py": "a = 3\n", "pkg/fn.py": "def fn():\n    return 2\n"})
    assert sync(root, original) == 0
    assert git(lib, "branch", "--show-current") == "feature/sync-1"
    assert (lib / "src/pkg/a.py").read_text() == "a = 3\n"
    assert not (lib / "src/pkg/fn.py").exists()
    assert (ops / "funcs/fn.py").read_text() == "def fn():\n    return 2\n"


def test_no_change_to_a_moved_file_leaves_the_arriving_unit_alone(world: dict[str, Path | str]) -> None:
    original, root, _, ops = parts(world)
    commit(original, "Change a", {"pkg/a.py": "a = 3\n"})
    assert sync(root, original) == 0
    assert git(ops, "branch", "--show-current") == "develop"
    assert "feature/sync-1" not in git(ops, "branch", "--list")


def assert_untouched(world: dict[str, Path | str], before: dict[str, str]) -> None:
    _, root, lib, ops = parts(world)
    for unit in (lib, ops):
        assert git(unit, "branch", "--show-current") == "develop"
        assert git(unit, "rev-parse", "HEAD") == before[unit.name]
        assert "feature/sync-1" not in git(unit, "branch", "--list")
    assert export.baselines(root)["lib"] == world["baseline"]


def heads(world: dict[str, Path | str]) -> dict[str, str]:
    _, _, lib, ops = parts(world)
    return {"lib": git(lib, "rev-parse", "HEAD"), "ops": git(ops, "rev-parse", "HEAD")}


def test_a_patch_that_does_not_apply_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, ops = parts(world)
    commit(ops, "ops changes the function its own way", {"funcs/fn.py": "def fn():\n    return 9\n"}, who=US)
    before = heads(world)
    commit(original, "Fix fn", {"pkg/fn.py": "def fn():\n    return 2\n"})
    assert sync(root, original) == 1
    assert "funcs/fn.py: the original's change does not apply in ops" in capsys.readouterr().err
    assert_untouched(world, before)


def test_an_arriving_unit_with_changes_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, ops = parts(world)
    before = heads(world)
    (ops / "README.md").write_text("edited\n")
    commit(original, "Fix fn", {"pkg/fn.py": "def fn():\n    return 2\n"})
    assert sync(root, original) == 1
    assert "ops: the arriving unit's repository has changes" in capsys.readouterr().err
    (ops / "README.md").write_text("ops\n")
    assert_untouched(world, before)


def test_an_arriving_unit_not_on_develop_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _, ops = parts(world)
    before = heads(world)
    git(ops, "switch", "--quiet", "-c", "elsewhere")
    commit(original, "Fix fn", {"pkg/fn.py": "def fn():\n    return 2\n"})
    assert sync(root, original) == 1
    assert "ops: the arriving unit is on elsewhere, not develop" in capsys.readouterr().err
    git(ops, "switch", "--quiet", "develop")
    assert_untouched(world, before)


def test_a_conflict_on_any_other_file_still_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, lib, _ = parts(world)
    commit(lib, "lib changes a", {"src/pkg/a.py": "a = 'ours'\n"}, who=US)
    before = heads(world)
    commit(original, "Change a and fn", {"pkg/a.py": "a = 3\n", "pkg/fn.py": "def fn():\n    return 2\n"})
    assert sync(root, original) == 1
    assert "conflict with the unit's own commits in src/pkg/a.py" in capsys.readouterr().err
    assert_untouched(world, before)
