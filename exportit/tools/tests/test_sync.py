"""Reading the originals from another checkout, and carrying its new commits into a unit (stage 23).

Each test builds three small repositories: an "original", a Cloud-Sandbox-like
root holding the mapping files, a patch and units.toml, and the unit's own
repository, made from the original as moving day made the real ones: filtered
with the unit's directives, then the patch and the unit's own files as commits.
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
new README.md
"""

UMBRELLA_MAP = """\
covers ./
copy top.txt top.txt
drop other/
local PLAN.md
new units.toml
"""

PATCH = """\
--- a/src/pkg/b.py
+++ b/src/pkg/b.py
@@ -1,3 +1,3 @@
 one = 1
-two = 2
+two = 2  # corrected
 three = 3
"""


def git(repo: Path, *args: str, who: list[str] = US) -> str:
    done = subprocess.run(["git", "-C", str(repo), *who, *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


def commit(repo: Path, message: str, files: dict[str, str | None], who: list[str] = AUTHOR) -> str:
    for name, text in files.items():
        path = repo / name
        if text is None:
            git(repo, "rm", "--quiet", name)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        git(repo, "add", name)
    git(repo, "commit", "--quiet", "-m", message, who=who)
    return git(repo, "rev-parse", "HEAD")


def run(root: Path, *args: str) -> int:
    return export.main(["--root", str(root), *args])


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
            "pkg/b.py": "one = 1\ntwo = 2\nthree = 3\n",
            "top.txt": "top\n",
            "other/x.txt": "not carried\n",
        },
    )
    baseline = commit(original, "Change a upstream", {"pkg/a.py": "a = 2\n"})

    root = tmp_path / "sandbox"
    export_dir = root / "exportit"
    (export_dir / "lib.patches").mkdir(parents=True)
    (export_dir / "lib.map").write_text(LIB_MAP)
    (export_dir / "cloud-sandbox.map").write_text(UMBRELLA_MAP)
    (export_dir / "lib.patches" / "01-two.patch").write_text(PATCH)
    umbrella = export_dir / "cloud-sandbox"
    umbrella.mkdir()
    (umbrella / "top.txt").write_text("top\n")
    (umbrella / "units.toml").write_text(
        f'[[unit]]\nname = "lib"\nrepository = "x"\nversion = "0.0.1"\nbaseline = "{baseline}"\n\n'
        f'[umbrella]\nbaseline = "{baseline}"\n'
    )
    (root / "PLAN.md").write_text("ours\n")
    git(root, "init", "--quiet")
    git(root, "add", "-A")
    git(root, "commit", "--quiet", "-m", "the maps")

    # The unit's repository, made as moving day made them.
    paths = tmp_path / "lib.paths"
    paths.write_text("pkg/\npkg/==>src/pkg/\n")
    unit = export_dir / "lib"
    subprocess.run(["git", "clone", "--quiet", "--no-local", str(original), str(unit)], check=True)
    subprocess.run(
        ["uvx", "--quiet", "git-filter-repo", "--quiet", "--paths-from-file", str(paths)],
        cwd=unit,
        check=True,
        capture_output=True,
    )
    git(unit, "apply", str(export_dir / "lib.patches" / "01-two.patch"))
    git(unit, "commit", "--quiet", "-am", "Apply 01-two")
    commit(unit, "Add what exists only in the unit", {"README.md": "lib\n"}, who=US)
    git(unit, "branch", "-M", "develop")
    return {"original": original, "root": root, "unit": unit, "baseline": baseline}


def paths_of(world: dict[str, Path | str]) -> tuple[Path, Path, Path]:
    return Path(world["original"]), Path(world["root"]), Path(world["unit"])


def test_the_unit_is_its_baseline_read_from_the_original(world: dict[str, Path | str]) -> None:
    original, root, _ = paths_of(world)
    assert run(root, "--source", str(original), "check", "lib") == 0
    assert run(root, "--source", str(original), "--at", str(world["baseline"]), "check", "lib") == 0
    assert run(root, "--source", str(original), "check", "--baselines") == 0


def test_a_later_original_is_not_the_unit_until_synced(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _ = paths_of(world)
    commit(original, "Change a again", {"pkg/a.py": "a = 3\n"})
    assert run(root, "--source", str(original), "check", "lib") == 1
    assert "src/pkg/a.py: content differs" in capsys.readouterr().err
    assert run(root, "--source", str(original), "check", "--baselines") == 0


def test_a_local_file_in_the_original_is_a_problem(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _ = paths_of(world)
    commit(original, "Upstream adds a plan", {"PLAN.md": "theirs\n"})
    assert run(root, "--source", str(original), "check", "lib") == 1
    assert "the original has PLAN.md, which this repository keeps as its own" in capsys.readouterr().err


def test_a_dirty_original_is_refused(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _ = paths_of(world)
    (original / "pkg/a.py").write_text("edited, not committed\n")
    assert run(root, "--source", str(original), "check") == 1
    assert "has changes; give a clean checkout" in capsys.readouterr().err


def test_sync_carries_the_new_commits_with_their_history(world: dict[str, Path | str]) -> None:
    original, root, unit = paths_of(world)
    shared = git(unit, "rev-list", "--count", "develop")
    head = commit(original, "Change a again", {"pkg/a.py": "a = 3\n"})
    commit(original, "Touch something the unit does not take", {"other/x.txt": "still not carried\n"})
    head = git(original, "rev-parse", "HEAD")
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 0
    assert git(unit, "branch", "--show-current") == "feature/sync-1"
    carried = git(unit, "log", "--format=%an|%s", "develop..HEAD", "--no-merges")
    assert carried == "Upstream Author|Change a again"
    assert (unit / "src/pkg/a.py").read_text() == "a = 3\n"
    assert (unit / "src/pkg/b.py").read_text().endswith("# corrected\nthree = 3\n")
    assert git(unit, "rev-list", "--count", "develop") == shared
    assert f'baseline = "{head}"' in (root / "exportit/cloud-sandbox/units.toml").read_text()
    assert run(root, "--source", str(original), "check", "lib") == 0


def test_a_change_that_the_patch_survives_is_carried(world: dict[str, Path | str]) -> None:
    original, root, unit = paths_of(world)
    commit(original, "Add a line to b", {"pkg/b.py": "one = 1\ntwo = 2\nthree = 3\nfour = 4\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 0
    assert (unit / "src/pkg/b.py").read_text() == "one = 1\ntwo = 2  # corrected\nthree = 3\nfour = 4\n"


def test_a_change_the_patch_does_not_survive_leaves_the_unit_as_it_was(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, unit = paths_of(world)
    before = git(unit, "rev-parse", "HEAD")
    commit(original, "Change the patched line", {"pkg/b.py": "one = 1\ntwo = 22\nthree = 3\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 1
    assert "conflict with the unit's own commits in src/pkg/b.py" in capsys.readouterr().err
    assert git(unit, "branch", "--show-current") == "develop"
    assert git(unit, "rev-parse", "HEAD") == before
    assert git(unit, "status", "--porcelain") == ""
    assert "feature/sync-1" not in git(unit, "branch", "--list")
    assert f'baseline = "{world["baseline"]}"' in (root / "exportit/cloud-sandbox/units.toml").read_text()


def test_a_file_no_map_claims_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, unit = paths_of(world)
    commit(original, "A new top-level file", {"new-dir/thing.txt": "where does this go?\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 1
    err = capsys.readouterr().err
    assert "the maps do not resolve against the original" in err
    assert "not assigned to any unit: new-dir/thing.txt" in err
    assert git(unit, "branch", "--show-current") == "develop"


def test_a_deleted_file_a_map_names_stops_the_sync(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, _ = paths_of(world)
    commit(original, "Remove top", {"top.txt": None})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 1
    assert "cloud-sandbox.map:2: matches no tracked file: top.txt" in capsys.readouterr().err


def test_a_new_file_in_a_copied_directory_is_carried(world: dict[str, Path | str]) -> None:
    original, root, unit = paths_of(world)
    commit(original, "A new module", {"pkg/c.py": "c = 1\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 0
    assert (unit / "src/pkg/c.py").read_text() == "c = 1\n"


def test_nothing_to_carry_moves_only_the_baseline(world: dict[str, Path | str]) -> None:
    original, root, unit = paths_of(world)
    head = commit(original, "Only outside the unit", {"other/x.txt": "changed\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 0
    assert git(unit, "branch", "--show-current") == "develop"
    assert f'baseline = "{head}"' in (root / "exportit/cloud-sandbox/units.toml").read_text()


def test_an_unrelated_history_is_refused(
    world: dict[str, Path | str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, root, unit = paths_of(world)
    stranger = tmp_path / "stranger"
    stranger.mkdir()
    git(stranger, "init", "--quiet")
    commit(stranger, "Another project", {"pkg/a.py": "a = 1\n", "top.txt": "top\n"})
    assert run(root, "--source", str(stranger), "sync", "lib", "--branch", "sync-1") == 1
    assert "does not descend from the baseline" in capsys.readouterr().err
    assert git(unit, "branch", "--show-current") == "develop"


def test_a_unit_with_changes_is_refused(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, unit = paths_of(world)
    (unit / "README.md").write_text("edited\n")
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 1
    assert "the unit's repository has changes" in capsys.readouterr().err


def test_set_baseline_changes_one_unit_only(world: dict[str, Path | str]) -> None:
    _, root, _ = paths_of(world)
    text = (root / "exportit/cloud-sandbox/units.toml").read_text()
    export.set_baseline(root, "lib", "f" * 40)
    after = (root / "exportit/cloud-sandbox/units.toml").read_text()
    assert after.count("f" * 40) == 1
    assert after.replace("f" * 40, str(world["baseline"]), 1) == text
    export.set_baseline(root, "cloud-sandbox", "e" * 40)
    assert export.baselines(root) == {"lib": "f" * 40, "cloud-sandbox": "e" * 40}


def test_the_units_history_holds_the_original_at_its_baseline(world: dict[str, Path | str]) -> None:
    original, root, _ = paths_of(world)
    assert run(root, "--source", str(original), "lineage", "lib") == 0


def test_a_unit_whose_history_is_not_the_originals_fails_the_lineage(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, unit = paths_of(world)
    subprocess.run(["rm", "-rf", str(unit)], check=True)
    unit.mkdir()
    git(unit, "init", "--quiet")
    commit(unit, "The same files, written afresh", {"src/pkg/a.py": "a = 2\n", "README.md": "lib\n"}, who=US)
    assert run(root, "--source", str(original), "lineage", "lib") == 1
    assert "which its history does not hold" in capsys.readouterr().err


def test_an_owned_unit_may_change_its_copies(
    world: dict[str, Path | str], capsys: pytest.CaptureFixture[str]
) -> None:
    original, root, unit = paths_of(world)
    commit(unit, "The unit changes a copied file", {"src/pkg/a.py": "a = 'ours'\n"}, who=US)
    assert run(root, "--source", str(original), "check", "--baselines") == 1
    capsys.readouterr()
    (root / "exportit/lib.map").write_text(LIB_MAP + "owned\n")
    assert run(root, "--source", str(original), "check", "--baselines") == 0
    assert "owned, not checked: lib" in capsys.readouterr().out
    assert run(root, "--source", str(original), "lineage", "lib") == 0


def test_an_owned_unit_still_takes_a_sync_merged_with_its_own_changes(world: dict[str, Path | str]) -> None:
    original, root, unit = paths_of(world)
    (root / "exportit/lib.map").write_text(LIB_MAP + "owned\n")
    commit(unit, "The unit adds a line of its own", {"src/pkg/a.py": "a = 2\n# ours\n"}, who=US)
    commit(original, "Upstream adds a module", {"pkg/c.py": "c = 1\n"})
    assert run(root, "--source", str(original), "sync", "lib", "--branch", "sync-1") == 0
    assert (unit / "src/pkg/a.py").read_text() == "a = 2\n# ours\n"
    assert (unit / "src/pkg/c.py").read_text() == "c = 1\n"
