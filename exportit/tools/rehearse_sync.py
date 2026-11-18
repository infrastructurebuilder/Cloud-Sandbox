"""Rehearse a sync from a changed original into the real units' histories (stage 23).

``just sync-rehearse`` runs this. Every repository it touches is a throw-away
one in a temporary directory: the "changed original" is a clone of this
repository at the units' baseline with one made-up upstream commit, and each
unit is a clone of its checked-out repository under ``exportit/``. Nothing is
pushed, and nothing here or in the units' repositories changes.

Each scenario makes one kind of change to the original, syncs one unit, and
holds the outcome to what ``export.py sync`` promises: the commit carried with
its author, or the change reported and the unit left as it was.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import export

ROOT = export.repository_root()
EXPORT = ROOT / export.EXPORT_DIR
WHO = ["-c", "user.name=Rehearsal Upstream", "-c", "user.email=upstream@example.invalid"]


def git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` as the made-up upstream author."""
    done = subprocess.run(["git", "-C", str(repo), *WHO, *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


@dataclass
class Scenario:
    """One kind of upstream change, the unit it is synced into, and what must happen."""

    title: str
    unit: str
    change: Callable[[Path], None]
    carried: bool
    says: str


def edit(path: str, how: Callable[[str], str]) -> Callable[[Path], None]:
    """Give a change that rewrites one original file."""

    def change(original: Path) -> None:
        target = original / path
        target.write_text(how(target.read_text()))
        git(original, "add", path)

    return change


def add(path: str, text: str) -> Callable[[Path], None]:
    """Give a change that adds a file to the original."""

    def change(original: Path) -> None:
        (original / path).parent.mkdir(parents=True, exist_ok=True)
        (original / path).write_text(text)
        git(original, "add", path)

    return change


def remove(path: str) -> Callable[[Path], None]:
    """Give a change that deletes a file from the original."""

    def change(original: Path) -> None:
        git(original, "rm", "--quiet", path)

    return change


AWS = "cloudflow/cluster/AWSCluster.py"
IMPORT = "from botocore.exceptions import ClientError\n"

SCENARIOS = [
    Scenario(
        "a change to a copied file",
        "model-common",
        edit("models/compilation.notes", lambda text: text + "\nA note added upstream.\n"),
        carried=True,
        says="carried 1 commits",
    ),
    Scenario(
        "a new file inside a copied directory",
        "cloudflow",
        add("cloudflow/workflows/added_upstream.py", '"""Added upstream."""\n'),
        carried=True,
        says="carried 1 commits",
    ),
    Scenario(
        "a new file outside every map",
        "model-common",
        add("added-upstream/thing.txt", "where does this go?\n"),
        carried=False,
        says="not assigned to any unit: added-upstream/thing.txt",
    ),
    Scenario(
        "a deleted file that a map names",
        "model-common",
        remove("scripts/upgrade-mpi.sh"),
        carried=False,
        says="matches no tracked file: scripts/upgrade-mpi.sh",
    ),
    Scenario(
        "a change to a patched file that the patch survives",
        "cloudflow",
        edit(AWS, lambda text: text + "# A line added upstream, far from the patch.\n"),
        carried=True,
        says="carried 1 commits",
    ),
    Scenario(
        "a change to a patched file that the patch does not survive",
        "cloudflow",
        edit(
            AWS,
            lambda text: text.replace(IMPORT, "from botocore.exceptions import ClientError  # upstream\n"),
        ),
        carried=False,
        says="conflict with the unit's own commits in src/cloudflow/cluster/AWSCluster.py",
    ),
    Scenario(
        "a change to the script sandbox-provisioning translates",
        "sandbox-provisioning",
        edit("scripts/setup-instance.sh", lambda text: text + "# A line added upstream.\n"),
        carried=True,
        says="its own files translate these originals",
    ),
]


def build(work: Path, scenario: Scenario, baseline: str) -> tuple[Path, Path, Path]:
    """Make the changed original, a sandbox holding the maps, and a clone of the unit."""
    original = work / "original"
    subprocess.run(
        ["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(original)], check=True
    )
    git(original, "switch", "--quiet", "--create", "upstream", baseline)
    git(original, "remote", "remove", "origin")
    scenario.change(original)
    git(original, "commit", "--quiet", "-m", f"Upstream: {scenario.title}")

    sandbox = work / "sandbox"
    (sandbox / export.EXPORT_DIR / export.UMBRELLA).mkdir(parents=True)
    for item in EXPORT.iterdir():
        if item.suffix == ".map":
            shutil.copy2(item, sandbox / export.EXPORT_DIR / item.name)
        elif item.name.endswith(".patches"):
            shutil.copytree(item, sandbox / export.EXPORT_DIR / item.name)
    shutil.copy2(export.manifest_path(ROOT), export.manifest_path(sandbox))

    unit = sandbox / export.EXPORT_DIR / scenario.unit
    subprocess.run(
        ["git", "clone", "--quiet", "--no-local", str(EXPORT / scenario.unit), str(unit)], check=True
    )
    git(unit, "remote", "remove", "origin")
    git(unit, "switch", "--quiet", "develop")
    return original, sandbox, unit


def rehearse(scenario: Scenario, baseline: str) -> list[str]:
    """Run one scenario; give what did not happen as promised."""
    with tempfile.TemporaryDirectory() as scratch:
        original, sandbox, unit = build(Path(scratch), scenario, baseline)
        before = git(unit, "rev-parse", "HEAD")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = export.main(
                [
                    "--root",
                    str(sandbox),
                    "--source",
                    str(original),
                    "sync",
                    scenario.unit,
                    "--branch",
                    "sync-r",
                ]
            )
        said = out.getvalue() + err.getvalue()
        wrong: list[str] = []
        if code != (0 if scenario.carried else 1):
            wrong.append(f"exit {code}")
        if scenario.says not in said:
            wrong.append(f"did not say {scenario.says!r}")
        if scenario.carried:
            authors = git(unit, "log", "--no-merges", "--format=%an", "develop..HEAD").splitlines()
            if authors != ["Rehearsal Upstream"]:
                wrong.append(f"carried commits by {authors}, not the one upstream commit")
            if git(unit, "status", "--porcelain"):
                wrong.append("left changes in the unit")
            moved = export.baselines(sandbox)[scenario.unit]
            if moved != git(original, "rev-parse", "HEAD"):
                wrong.append("did not move the baseline to the original's HEAD")
        else:
            if git(unit, "rev-parse", "HEAD") != before or git(unit, "branch", "--show-current") != "develop":
                wrong.append("changed the unit although it refused")
            if export.baselines(sandbox)[scenario.unit] != baseline:
                wrong.append("moved the baseline although it refused")
        if wrong:
            wrong.append(f"output: {said.strip()}")
        return wrong


def main() -> int:
    """Run every scenario; exit 1 if any did not happen as promised."""
    baselines = export.baselines(ROOT)
    failed = 0
    for scenario in SCENARIOS:
        wrong = rehearse(scenario, baselines[scenario.unit])
        verdict = "as promised" if not wrong else "NOT as promised"
        print(
            f"{scenario.title} ({scenario.unit}): {'carried' if scenario.carried else 'refused'}, {verdict}"
        )
        for line in wrong:
            print(f"  PROBLEM {line}", file=sys.stderr)
        failed += bool(wrong)
    print(f"sync rehearsal: {len(SCENARIOS) - failed} of {len(SCENARIOS)} scenarios as promised")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
