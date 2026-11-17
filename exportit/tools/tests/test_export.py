from __future__ import annotations

import stat
import subprocess
from pathlib import Path

import pytest

import export

SOURCES = {
    "pkg/a.py": "print('a')\n",
    "pkg/run.sh": "#!/bin/sh\necho run\n",
    "pkg/plot/p.py": "print('p')\n",
    "pkg/empty.txt": "",
    "top.txt": "top\n",
    "other/left.txt": "not part of any unit\n",
}

LIB_MAP = """\
covers pkg/
covers top.txt
copy pkg/a.py     src/pkg/a.py
copy pkg/run.sh   src/pkg/run.sh
drop pkg/empty.txt        # replaced by a new file
copy top.txt      docs/top.txt
new  README.md
"""

PLOT_MAP = """\
copy pkg/plot/    src/pkg/plot/
"""


def run_git(repo: Path, *args: str) -> None:
    identity = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]
    subprocess.run(["git", "-C", str(repo), *identity, *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for name, text in SOURCES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (root / "pkg/run.sh").chmod(0o755)
    (root / "exportit").mkdir()
    (root / "exportit/lib.map").write_text(LIB_MAP)
    (root / "exportit/plot.map").write_text(PLOT_MAP)
    (root / "exportit/lib").mkdir()
    (root / "exportit/lib/README.md").write_text("new\n")
    run_git(root, "init", "--quiet")
    run_git(root, "add", "-A")
    run_git(root, "commit", "--quiet", "-m", "start")
    return root


def run(repo: Path, *args: str) -> int:
    return export.main(["--root", str(repo), *args])


def test_copy_then_check_passes(repo: Path) -> None:
    assert run(repo, "copy") == 0
    assert run(repo, "check") == 0
    assert (repo / "exportit/lib/src/pkg/a.py").read_text() == SOURCES["pkg/a.py"]
    assert (repo / "exportit/plot/src/pkg/plot/p.py").read_text() == SOURCES["pkg/plot/p.py"]
    assert not (repo / "exportit/lib/src/pkg/empty.txt").exists()


def test_the_executable_bit_is_copied_and_checked(repo: Path) -> None:
    run(repo, "copy")
    copied = repo / "exportit/lib/src/pkg/run.sh"
    assert copied.stat().st_mode & stat.S_IXUSR
    copied.chmod(0o644)
    assert run(repo, "check") == 1


def test_a_changed_source_fails_until_copied_again(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(repo, "copy")
    (repo / "pkg/a.py").write_text("print('changed')\n")
    assert run(repo, "check") == 1
    assert "src/pkg/a.py: content differs" in capsys.readouterr().err
    assert run(repo, "copy") == 0
    assert run(repo, "check") == 0


def test_an_edited_copy_fails(repo: Path) -> None:
    run(repo, "copy")
    (repo / "exportit/lib/docs/top.txt").write_text("edited in the copy\n")
    assert run(repo, "check") == 1


def test_a_tracked_file_under_a_covered_path_must_be_assigned(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "pkg/forgotten.py").write_text("x = 1\n")
    run_git(repo, "add", "pkg/forgotten.py")
    assert run(repo, "check") == 1
    assert "not assigned to any unit: pkg/forgotten.py" in capsys.readouterr().err


def test_a_file_outside_covered_paths_is_ignored(repo: Path) -> None:
    run(repo, "copy")
    assert run(repo, "check") == 0
    assert not (repo / "exportit/lib/other").exists()


def test_a_file_in_the_unit_must_be_copied_or_declared_new(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(repo, "copy")
    (repo / "exportit/lib/stray.txt").write_text("who put this here\n")
    assert run(repo, "check") == 1
    assert "stray.txt: neither copied nor declared new" in capsys.readouterr().err


def test_a_declared_new_file_must_exist(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(repo, "copy")
    (repo / "exportit/lib/README.md").unlink()
    assert run(repo, "check") == 1
    assert "declared new but absent: README.md" in capsys.readouterr().err


def test_a_patch_is_part_of_what_is_expected(repo: Path) -> None:
    patches = repo / "exportit/lib.patches"
    patches.mkdir()
    (patches / "01-fix.patch").write_text(
        "--- a/src/pkg/a.py\n+++ b/src/pkg/a.py\n@@ -1 +1 @@\n-print('a')\n+print('fixed')\n"
    )
    assert run(repo, "copy") == 0
    assert (repo / "exportit/lib/src/pkg/a.py").read_text() == "print('fixed')\n"
    assert run(repo, "check") == 0
    (repo / "exportit/lib/src/pkg/a.py").write_text(SOURCES["pkg/a.py"])
    assert run(repo, "check") == 1


def test_a_patch_that_does_not_apply_is_a_problem(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    patches = repo / "exportit/lib.patches"
    patches.mkdir()
    (patches / "01-stale.patch").write_text(
        "--- a/src/pkg/a.py\n+++ b/src/pkg/a.py\n@@ -1 +1 @@\n-print('gone')\n+print('fixed')\n"
    )
    assert run(repo, "copy") == 1
    assert "01-stale.patch does not apply" in capsys.readouterr().err


def test_an_ignored_copy_is_reported(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / ".gitignore").write_text("top.txt\n")
    run(repo, "copy")
    assert run(repo, "check") == 1
    assert "docs/top.txt: ignored by .gitignore" in capsys.readouterr().err


def test_two_units_cannot_claim_one_file_equally(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "exportit/plot.map").write_text(PLOT_MAP + "copy top.txt top.txt\n")
    assert run(repo, "check") == 1
    assert "claimed more than once" in capsys.readouterr().err


def test_a_rule_that_matches_nothing_is_a_problem(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "exportit/plot.map").write_text(PLOT_MAP + "copy gone/ src/gone/\n")
    assert run(repo, "check") == 1
    assert "matches no tracked file: gone/" in capsys.readouterr().err


def test_an_unreadable_directive_is_a_problem(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "exportit/plot.map").write_text("move pkg/plot/ somewhere/\n")
    assert run(repo, "check") == 1
    assert "plot.map:1: cannot read" in capsys.readouterr().err


def test_filter_directives_keep_and_rename(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(repo, "filter", "lib") == 0
    lines = capsys.readouterr().out.split()
    assert lines == [
        "pkg/run.sh",
        "pkg/a.py",
        "top.txt",
        "pkg/run.sh==>src/pkg/run.sh",
        "pkg/a.py==>src/pkg/a.py",
        "top.txt==>docs/top.txt",
    ]


def test_filter_refuses_a_directory_shared_with_another_unit(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "exportit/lib.map").write_text("copy pkg/ src/pkg/\ncopy top.txt docs/top.txt\nnew README.md\n")
    assert run(repo, "filter", "lib") == 1
    assert "also holds files of another unit" in capsys.readouterr().err


def test_renames_follow_filter_repo_rules() -> None:
    renames = [("pkg/plot/", "src/pkg/plot/"), ("pkg/a.py", "lib/a.py"), ("src/", "moved/")]
    assert export.renamed_by_filter_repo("pkg/plot/p.py", renames) == "moved/pkg/plot/p.py"
    assert export.renamed_by_filter_repo("pkg/a.py", renames) == "lib/a.py"
    assert export.renamed_by_filter_repo("pkg/a.pyc", renames) == "pkg/a.pyc"


def test_filter_refuses_renames_that_chain(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    chained = ["copy pkg/a.py top.txt/a.py", "copy pkg/run.sh src/run.sh", "copy top.txt docs/top.txt"]
    (repo / "exportit/lib.map").write_text("\n".join([*chained, "new README.md", ""]))
    assert run(repo, "filter", "lib") == 1
    assert "filter-repo would move pkg/a.py to docs/top.txt/a.py" in capsys.readouterr().err


def test_a_directory_can_be_copied_to_the_root_of_a_unit(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "exportit/plot.map").write_text("copy pkg/plot/ ./\n")
    assert run(repo, "copy") == 0
    assert (repo / "exportit/plot/p.py").read_text() == SOURCES["pkg/plot/p.py"]
    assert run(repo, "check") == 0
    capsys.readouterr()
    assert run(repo, "filter", "plot") == 0
    assert capsys.readouterr().out.split() == ["pkg/plot/", "pkg/plot/==>"]


def test_a_file_cannot_be_copied_to_the_root_itself(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "exportit/plot.map").write_text(PLOT_MAP + "copy top.txt ./\n")
    assert run(repo, "check") == 1
    assert "a directory must be copied to a directory" in capsys.readouterr().err


def test_covering_the_root_makes_every_file_count(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(repo, "copy")
    assert run(repo, "check") == 0
    (repo / "exportit/plot.map").write_text(PLOT_MAP + "covers ./\n")
    assert run(repo, "check") == 1
    assert "not assigned to any unit: other/left.txt" in capsys.readouterr().err
    (repo / "exportit/plot.map").write_text(PLOT_MAP + "covers ./\ndrop other/left.txt\n")
    assert run(repo, "check") == 0


# A unit kept as a submodule (exportit/MOVINGDAY.md): its files are in a
# repository of its own, checked out where the copy was.


@pytest.fixture
def moved(repo: Path, tmp_path: Path) -> Path:
    """The repository of ``repo``, with the unit ``lib`` moved out and kept as a submodule."""
    run(repo, "copy")
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "--quiet", "-m", "the copies")
    unit = repo / "exportit/lib"
    home = tmp_path / "lib-home"
    unit.rename(home)
    run_git(home, "init", "--quiet")
    run_git(home, "add", "-A")
    run_git(home, "commit", "--quiet", "-m", "the unit, in a repository of its own")
    run_git(repo, "rm", "-r", "--quiet", "--cached", "exportit/lib")
    # git refuses a submodule from a local path unless told that this one is meant.
    local = ["-c", "protocol.file.allow=always"]
    run_git(repo, *local, "submodule", "add", "--quiet", str(home), "exportit/lib")
    run_git(repo, "commit", "--quiet", "-m", "lib is a submodule")
    return repo


def test_a_unit_kept_as_a_submodule_is_checked_like_a_directory(moved: Path) -> None:
    assert export.is_submodule(moved, "lib")
    assert not export.is_submodule(moved, "plot")
    assert run(moved, "check") == 0


def test_the_submodule_does_not_have_to_be_dropped_by_a_map(moved: Path) -> None:
    # Everything under exportit/ is left out of what the maps must cover.
    (moved / "exportit/plot.map").write_text(PLOT_MAP + "covers pkg/\n")
    assert run(moved, "check") == 0


def test_gitmodules_is_a_tracked_file_that_covering_the_root_must_assign(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (moved / "exportit/plot.map").write_text(PLOT_MAP + "covers ./\ndrop other/left.txt\n")
    assert run(moved, "check") == 1
    assert "not assigned to any unit: .gitmodules" in capsys.readouterr().err
    (moved / "exportit/plot.map").write_text(PLOT_MAP + "covers ./\ndrop other/left.txt\ndrop .gitmodules\n")
    assert run(moved, "check") == 0


def test_an_edited_copy_in_a_submodule_fails(moved: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (moved / "exportit/lib/docs/top.txt").write_text("edited in the unit's repository\n")
    assert run(moved, "check") == 1
    assert "docs/top.txt: content differs" in capsys.readouterr().err


def test_a_file_added_in_a_submodule_must_be_declared_new(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (moved / "exportit/lib/stray.txt").write_text("who put this here\n")
    assert run(moved, "check") == 1
    assert "stray.txt: neither copied nor declared new" in capsys.readouterr().err
    (moved / "exportit/lib.map").write_text(LIB_MAP + "new stray.txt\n")
    assert run(moved, "check") == 0


def test_a_declared_new_file_must_exist_in_a_submodule(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (moved / "exportit/lib/README.md").unlink()
    assert run(moved, "check") == 1
    assert "declared new but absent: README.md" in capsys.readouterr().err


def test_a_changed_source_is_copied_into_the_submodule(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (moved / "pkg/a.py").write_text("print('changed')\n")
    assert run(moved, "check") == 1
    assert "src/pkg/a.py: content differs" in capsys.readouterr().err
    assert run(moved, "copy", "lib") == 0
    assert (moved / "exportit/lib/src/pkg/a.py").read_text() == "print('changed')\n"
    assert run(moved, "check") == 0


def test_a_file_ignored_inside_a_submodule_is_reported(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run_git(moved / "exportit/lib", "rm", "--quiet", "--cached", "docs/top.txt")
    (moved / "exportit/lib/.gitignore").write_text("top.txt\n")
    (moved / "exportit/lib.map").write_text(LIB_MAP + "new .gitignore\n")
    assert run(moved, "check") == 1
    assert "docs/top.txt: ignored by .gitignore" in capsys.readouterr().err


def test_a_submodule_that_is_not_checked_out_is_one_clear_problem(
    moved: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run_git(moved, "submodule", "deinit", "--quiet", "--force", "exportit/lib")
    assert run(moved, "check") == 1
    problems = [line for line in capsys.readouterr().err.splitlines() if line.startswith("PROBLEM")]
    assert problems == ["PROBLEM lib: a submodule that is not checked out; run 'git submodule update --init'"]
