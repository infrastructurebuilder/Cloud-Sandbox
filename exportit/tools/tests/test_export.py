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
