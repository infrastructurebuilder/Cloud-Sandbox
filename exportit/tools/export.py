"""Copy units of this repository into ``exportit/`` and check the copies.

A unit is described by ``exportit/<unit>.map``. Each line of that file is one
directive::

    covers <path>             every tracked file under <path> must belong to a unit
    copy   <source> <dest>    copy <source> to <dest> inside the unit
    drop   <source>           the file is deliberately not carried over
    new    <path>             a file that exists only in the unit

A path that ends in ``/`` stands for everything beneath it; as a destination,
``./`` is the root of the unit. When several
``copy`` or ``drop`` directives match a file, the longest source wins, and that
is also how a file is shared out between two units.

Corrections to copied files are kept as patches in ``exportit/<unit>.patches/``
and are applied, in name order, after the copy. The check therefore compares
each file in the unit with "its source, plus the patches", so a copy can never
differ from its origin in a way that is not written down.

Commands::

    export.py copy [UNIT ...]   write or refresh the copies
    export.py check             verify every unit; exit 1 if anything is wrong
    export.py filter UNIT       print directives for ``git filter-repo``
    export.py prove UNIT        run the extraction on a throw-away clone
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

EXPORT_DIR = "exportit"
COMMENT = "#"


class MapError(Exception):
    """A mapping file is wrong, or the units disagree with each other."""


@dataclass(frozen=True)
class Rule:
    """One ``copy`` or ``drop`` directive."""

    unit: str
    source: str
    dest: str | None
    line: int

    def matches(self, path: str) -> bool:
        """Say whether this rule applies to the tracked file ``path``."""
        if self.source.endswith("/"):
            return path.startswith(self.source)
        return path == self.source

    def destination(self, path: str) -> str | None:
        """Give the place of ``path`` inside the unit, or None when dropped."""
        if self.dest is None:
            return None
        if self.source.endswith("/"):
            return self.dest + path[len(self.source) :]
        return self.dest


@dataclass
class Unit:
    """Everything one mapping file says."""

    name: str
    covers: list[str] = field(default_factory=list[str])
    rules: list[Rule] = field(default_factory=list[Rule])
    new: list[str] = field(default_factory=list[str])


@dataclass
class Plan:
    """The mapping files resolved against the tracked files."""

    files: dict[str, dict[str, str]]
    """unit name -> destination inside the unit -> source path in the repository"""
    dropped: dict[str, list[str]]
    """unit name -> source paths the unit drops"""
    problems: list[str]


def list_files(root: Path, *args: str) -> list[str]:
    """Run ``git ls-files`` in ``root`` with ``args`` and return the paths."""
    done = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [item for item in done.stdout.split("\0") if item]


def parse_map(path: Path) -> Unit:
    """Read one mapping file."""
    unit = Unit(name=path.stem)
    for number, raw in enumerate(path.read_text().splitlines(), start=1):
        words = raw.split(COMMENT, 1)[0].split()
        if not words:
            continue
        verb, args = words[0], words[1:]
        where = f"{path.name}:{number}"
        if verb == "covers" and len(args) == 1:
            unit.covers.append(args[0])
        elif verb == "copy" and len(args) == 2:  # noqa: PLR2004
            source, dest = args
            if source.endswith("/") != dest.endswith("/"):
                raise MapError(f"{where}: a directory must be copied to a directory")
            if dest == "./":
                dest = ""
            unit.rules.append(Rule(unit.name, source, dest, number))
        elif verb == "drop" and len(args) == 1:
            unit.rules.append(Rule(unit.name, args[0], None, number))
        elif verb == "new" and len(args) == 1:
            unit.new.append(args[0])
        else:
            raise MapError(f"{where}: cannot read '{raw.strip()}'")
    return unit


def load_units(root: Path) -> dict[str, Unit]:
    """Read every mapping file under ``exportit/``."""
    maps = sorted((root / EXPORT_DIR).glob("*.map"))
    return {path.stem: parse_map(path) for path in maps}


def tracked_sources(root: Path) -> list[str]:
    """List the tracked files that are candidates for export."""
    prefix = EXPORT_DIR + "/"
    return [path for path in list_files(root) if not path.startswith(prefix)]


def resolve(units: dict[str, Unit], tracked: list[str]) -> Plan:
    """Decide, for every tracked file, which unit takes it and where it goes."""
    plan = Plan(
        files={name: {} for name in units},
        dropped={name: [] for name in units},
        problems=[],
    )
    rules = [rule for unit in units.values() for rule in unit.rules]
    covers = [root for unit in units.values() for root in unit.covers]
    used: set[Rule] = set()
    for path in tracked:
        matching = [rule for rule in rules if rule.matches(path)]
        if not matching:
            if any(path == root or path.startswith(root) for root in covers):
                plan.problems.append(f"not assigned to any unit: {path}")
            continue
        longest = max(len(rule.source) for rule in matching)
        best = [rule for rule in matching if len(rule.source) == longest]
        if len(best) > 1:
            owners = ", ".join(f"{rule.unit}.map:{rule.line}" for rule in best)
            plan.problems.append(f"claimed more than once ({owners}): {path}")
            continue
        rule = best[0]
        used.add(rule)
        dest = rule.destination(path)
        if dest is None:
            plan.dropped[rule.unit].append(path)
        elif dest in plan.files[rule.unit]:
            other = plan.files[rule.unit][dest]
            plan.problems.append(f"{rule.unit}: {path} and {other} both go to {dest}")
        else:
            plan.files[rule.unit][dest] = path
    plan.problems.extend(
        f"{rule.unit}.map:{rule.line}: matches no tracked file: {rule.source}"
        for rule in rules
        if rule not in used
    )
    return plan


def is_executable(path: Path) -> bool:
    """Say whether the owner may execute ``path``."""
    return bool(path.stat().st_mode & stat.S_IXUSR)


def copy_file(source: Path, dest: Path) -> None:
    """Copy contents and the executable bit, creating directories as needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    dest.chmod(0o755 if is_executable(source) else 0o644)


def patches_of(root: Path, unit: str) -> list[Path]:
    """List a unit's patch files in the order they are applied."""
    return sorted((root / EXPORT_DIR / f"{unit}.patches").glob("*.patch"))


def build_expected(root: Path, unit: str, files: dict[str, str], out: Path, *, patched: bool) -> None:
    """Write into ``out`` what the unit's copied files should be."""
    for dest, source in files.items():
        copy_file(root / source, out / dest)
    if not patched:
        return
    for patch in patches_of(root, unit):
        done = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", str(patch)],
            cwd=out,
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode != 0:
            raise MapError(f"{unit}: {patch.name} does not apply: {done.stderr.strip()}")


def same_file(expected: Path, actual: Path) -> str | None:
    """Compare two files; return what differs, or None when they agree."""
    if not actual.is_file():
        return "missing"
    if not filecmp.cmp(expected, actual, shallow=False):
        return "content differs"
    if is_executable(expected) != is_executable(actual):
        return "executable bit differs"
    return None


def is_declared_new(path: str, declared: list[str]) -> bool:
    """Say whether a ``new`` directive accounts for ``path``."""
    return any(path == item or (item.endswith("/") and path.startswith(item)) for item in declared)


def check_unit(root: Path, unit: Unit, files: dict[str, str]) -> list[str]:
    """Compare one unit's directory with what its mapping file promises."""
    problems: list[str] = []
    unit_dir = root / EXPORT_DIR / unit.name
    prefix = f"{EXPORT_DIR}/{unit.name}/"
    with tempfile.TemporaryDirectory() as scratch:
        expected_dir = Path(scratch)
        build_expected(root, unit.name, files, expected_dir, patched=True)
        for dest in sorted(files):
            verdict = same_file(expected_dir / dest, unit_dir / dest)
            if verdict:
                problems.append(f"{unit.name}: {dest}: {verdict} (source {files[dest]})")
    present = list_files(root, "--cached", "--others", "--exclude-standard", "--", prefix)
    here = {path[len(prefix) :] for path in present if (root / path).is_file()}
    extra = sorted(path for path in here if path not in files and not is_declared_new(path, unit.new))
    problems.extend(f"{unit.name}: {path}: neither copied nor declared new" for path in extra)
    for item in unit.new:
        if not any(path == item or path.startswith(item) for path in here):
            problems.append(f"{unit.name}: declared new but absent: {item}")
    hidden = sorted(dest for dest in files if dest not in here and (unit_dir / dest).is_file())
    problems.extend(
        f"{unit.name}: {dest}: ignored by .gitignore; add it with 'git add -f'" for dest in hidden
    )
    return problems


def load_plan(root: Path) -> tuple[dict[str, Unit], Plan]:
    """Read the mapping files and resolve them, failing on any conflict."""
    units = load_units(root)
    if not units:
        raise MapError(f"no mapping files in {EXPORT_DIR}/")
    plan = resolve(units, tracked_sources(root))
    if plan.problems:
        raise MapError("\n".join(plan.problems))
    return units, plan


def pick(units: dict[str, Unit], names: list[str]) -> list[str]:
    """Check unit names given on the command line."""
    unknown = [name for name in names if name not in units]
    if unknown:
        raise MapError(f"no such unit: {', '.join(unknown)} (have: {', '.join(units)})")
    return names or list(units)


def command_copy(root: Path, names: list[str]) -> int:
    """Write or refresh the copies of the named units."""
    units, plan = load_plan(root)
    for name in pick(units, names):
        files = plan.files[name]
        unit_dir = root / EXPORT_DIR / name
        written = 0
        with tempfile.TemporaryDirectory() as scratch:
            expected_dir = Path(scratch)
            build_expected(root, name, files, expected_dir, patched=True)
            for dest in sorted(files):
                if same_file(expected_dir / dest, unit_dir / dest):
                    copy_file(expected_dir / dest, unit_dir / dest)
                    written += 1
        dropped = len(plan.dropped[name])
        print(f"{name}: {len(files)} files mapped, {written} written, {dropped} dropped")
    return 0


def command_check(root: Path) -> int:
    """Verify every unit against its mapping file."""
    units, plan = load_plan(root)
    problems: list[str] = []
    for name, unit in units.items():
        found = check_unit(root, unit, plan.files[name])
        problems.extend(found)
        patches = len(patches_of(root, name))
        state = "ok" if not found else f"{len(found)} problems"
        print(f"{name}: {len(plan.files[name])} files, {patches} patches: {state}")
    for problem in problems:
        print(f"PROBLEM {problem}", file=sys.stderr)
    return 1 if problems else 0


def renamed_by_filter_repo(path: str, renames: list[tuple[str, str]]) -> str:
    """Apply renames the way ``git filter-repo`` does.

    It takes them in the order given, each acting on the result of the one
    before. A rename matches a path that equals its source or lies beneath it.
    """
    for source, dest in renames:
        stem = source.rstrip("/")
        if path == stem or path.startswith(stem + "/"):
            path = path.replace(source, dest, 1)
    return path


def filter_directives(units: dict[str, Unit], plan: Plan, name: str, tracked: list[str]) -> list[str]:
    """Turn a unit's ``copy`` rules into ``git filter-repo`` path directives.

    A directory rule is only usable when everything under it goes to this unit,
    because ``filter-repo`` keeps the whole directory. The renames are also run
    here on every file of the unit, to be sure that their combined effect is
    the destination the mapping file asks for.
    """
    copies = [rule for rule in units[name].rules if rule.dest is not None]
    copies.sort(key=lambda rule: (-len(rule.source), rule.source))
    theirs = set(plan.files[name].values())
    for rule in copies:
        strays = [path for path in tracked if rule.matches(path) and path not in theirs]
        if strays:
            raise MapError(
                f"{name}.map:{rule.line}: {rule.source} also holds files of another unit "
                f"or dropped files (for example {strays[0]}); list its files one by one"
            )
    renames = [
        (rule.source, rule.dest) for rule in copies if rule.dest is not None and rule.source != rule.dest
    ]
    for dest, source in plan.files[name].items():
        result = renamed_by_filter_repo(source, renames)
        if result != dest:
            raise MapError(f"{name}: filter-repo would move {source} to {result}, not to {dest}")
    keep = [rule.source for rule in copies]
    return keep + [f"{source}==>{dest}" for source, dest in renames]


def command_filter(root: Path, name: str) -> int:
    """Print the ``git filter-repo`` directives for one unit."""
    units, plan = load_plan(root)
    pick(units, [name])
    print("\n".join(filter_directives(units, plan, name, tracked_sources(root))))
    return 0


def tree_of(root: Path) -> set[str]:
    """List the files under ``root``, ignoring git's own directory."""
    found: set[str] = set()
    for folder, subdirs, names in os.walk(root):
        if ".git" in subdirs:
            subdirs.remove(".git")
        found.update(str((Path(folder) / item).relative_to(root)) for item in names)
    return found


def command_prove(root: Path, name: str) -> int:
    """Extract one unit from a throw-away clone and compare it with the copy.

    The clone is rewritten by ``git filter-repo``; this repository is only
    read. Patches are left out, because the extraction carries history and a
    patch would be a commit made after it.
    """
    units, plan = load_plan(root)
    pick(units, [name])
    directives = filter_directives(units, plan, name, tracked_sources(root))
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        clone, expected = work / "clone", work / "expected"
        (work / "paths.txt").write_text("\n".join(directives) + "\n")
        build_expected(root, name, plan.files[name], expected, patched=False)
        steps = [
            ["git", "clone", "--quiet", "--no-local", str(root), str(clone)],
            ["uvx", "--quiet", "git-filter-repo", "--quiet", "--paths-from-file", str(work / "paths.txt")],
        ]
        for step in steps:
            cwd = clone if step[0] == "uvx" else work
            done = subprocess.run(step, cwd=cwd, capture_output=True, text=True, check=False)
            if done.returncode != 0:
                print(done.stdout + done.stderr, file=sys.stderr)
                return 1
        remotes = subprocess.run(
            ["git", "remote"], cwd=clone, capture_output=True, text=True, check=True
        ).stdout.split()
        commits = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"], cwd=clone, capture_output=True, text=True, check=True
        ).stdout.strip()
        want, got = tree_of(expected), tree_of(clone)
        problems = [f"missing after extraction: {path}" for path in sorted(want - got)]
        problems += [f"unexpected after extraction: {path}" for path in sorted(got - want)]
        for path in sorted(want & got):
            verdict = same_file(expected / path, clone / path)
            if verdict:
                problems.append(f"{path}: {verdict}")
        if remotes:
            problems.append(f"the rewritten clone still has remotes: {' '.join(remotes)}")
    for problem in problems:
        print(f"PROBLEM {name}: {problem}", file=sys.stderr)
    if not problems:
        print(f"{name}: extraction gives the same {len(want)} files, with {commits} commits of history")
    return 1 if problems else 0


def repository_root() -> Path:
    """Find the top of the repository this tool lives in."""
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    """Run one command; see the module docstring."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: this one)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("copy").add_argument("units", nargs="*")
    commands.add_parser("check")
    commands.add_parser("filter").add_argument("unit")
    commands.add_parser("prove").add_argument("unit")
    args = parser.parse_args(argv)
    root: Path = (args.root or repository_root()).resolve()
    command: str = args.command
    try:
        if command == "copy":
            return command_copy(root, list(args.units))
        if command == "check":
            return command_check(root)
        if command == "filter":
            return command_filter(root, str(args.unit))
        return command_prove(root, str(args.unit))
    except MapError as error:
        print(f"PROBLEM {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
