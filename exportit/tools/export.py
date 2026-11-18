"""Copy units of this repository into ``exportit/`` and check the copies.

A unit is described by ``exportit/<unit>.map``. Each line of that file is one
directive::

    covers <path>             every tracked file under <path> must belong to a unit
                              ("covers ./": every tracked file of the repository)
    copy   <source> <dest>    copy <source> to <dest> inside the unit
    drop   <source>           the file is deliberately not carried over
    new    <path>             a file that exists only in the unit
    local  <source>           a file of this repository's own work, never of the
                              original: dropped here, and a problem if a given
                              original (``--source``) ever has it

A path that ends in ``/`` stands for everything beneath it; as a destination,
``./`` is the root of the unit. When several
``copy`` or ``drop`` directives match a file, the longest source wins, and that
is also how a file is shared out between two units.

Corrections to copied files are kept as patches in ``exportit/<unit>.patches/``
and are applied, in name order, after the copy. The check therefore compares
each file in the unit with "its source, plus the patches", so a copy can never
differ from its origin in a way that is not written down.

A unit's directory is either part of this repository or a repository of its
own, kept here as a git submodule at the same path (``exportit/MOVINGDAY.md``).
The mapping file, the patches and the checks are the same for both; only where
the list of the unit's files is asked differs.

The originals are read from this repository, unless ``--source`` names a git
checkout of the original repository to read them from instead (stage 23): the
mapping files and the patches are always this repository's. ``--at REV`` reads
them as they were at a commit of that repository, or of this one.

Commands::

    export.py copy [UNIT ...]     write or refresh the copies
    export.py check [UNIT ...]    verify units (all when none is named); exit 1 if anything is wrong
    export.py check --baselines   verify every unit against its own baseline (units.toml)
    export.py filter UNIT         print directives for ``git filter-repo``
    export.py prove UNIT          run the extraction on a throw-away clone
    export.py sync UNIT --source PATH --branch NAME
                                  carry the original's commits since the unit's
                                  baseline into the unit's repository, on a branch
"""

from __future__ import annotations

import argparse
import contextlib
import filecmp
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path

EXPORT_DIR = "exportit"
COMMENT = "#"
SUBMODULE_MODE = "160000"
"""How git's index marks an entry that is another repository's commit."""


class MapError(Exception):
    """A mapping file is wrong, or the units disagree with each other."""


@dataclass(frozen=True)
class Rule:
    """One ``copy`` or ``drop`` directive."""

    unit: str
    source: str
    dest: str | None
    line: int
    local: bool = False
    """A ``local`` directive: this repository's own file, never the original's."""

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
class Source:
    """Where the originals are read from."""

    repo: Path
    """The git repository they come from: this one, or a given checkout of the original."""
    tree: Path
    """Where their files are on disk."""
    files: list[str]
    """Their paths, as tracked."""
    external: bool
    """True when they are not this repository's working tree: a given original, or a commit."""


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
            # "covers ./" is the whole repository (outside exportit/).
            unit.covers.append("" if args[0] == "./" else args[0])
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
        elif verb == "local" and len(args) == 1:
            unit.rules.append(Rule(unit.name, args[0], None, number, local=True))
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


def git_output(repo: Path, *args: str) -> str:
    """Run git in ``repo`` and return what it prints."""
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


@contextlib.contextmanager
def open_source(root: Path, given: Path | None = None, rev: str | None = None) -> Generator[Source]:
    """Give the originals: this repository's, a given checkout's, or either at a commit."""
    if given is None and rev is None:
        yield Source(root, root, tracked_sources(root), external=False)
        return
    repo = (given or root).resolve()
    if not (repo / ".git").exists():
        raise MapError(f"{repo} is not a git checkout")
    if rev is None:
        if git_output(repo, "status", "--porcelain", "--untracked-files=no").strip():
            raise MapError(f"{repo} has changes; give a clean checkout of the original")
        yield Source(repo, repo, tracked_sources(repo), external=True)
        return
    try:
        git_output(repo, "cat-file", "-e", f"{rev}^{{commit}}")
    except subprocess.CalledProcessError as error:
        raise MapError(f"{repo} has no commit {rev}") from error
    prefix = EXPORT_DIR + "/"
    listing = git_output(repo, "ls-tree", "-r", "-z", "--format=%(objecttype) %(path)", rev)
    files = [
        entry.split(" ", 1)[1]
        for entry in listing.split("\0")
        if entry.startswith("blob ") and not entry.split(" ", 1)[1].startswith(prefix)
    ]
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch)
        archive = subprocess.run(["git", "-C", str(repo), "archive", rev], check=True, capture_output=True)
        subprocess.run(["tar", "-x", "-C", str(tree)], input=archive.stdout, check=True)
        yield Source(repo, tree, files, external=True)


def resolve(units: dict[str, Unit], tracked: list[str], *, external: bool = False) -> Plan:
    """Decide, for every tracked file, which unit takes it and where it goes.

    With ``external``, the files are an original's, and ``local`` directives
    stand for files it must not have: they match nothing, and are never unused.
    """
    plan = Plan(
        files={name: {} for name in units},
        dropped={name: [] for name in units},
        problems=[],
    )
    every = [rule for unit in units.values() for rule in unit.rules]
    rules = [rule for rule in every if not (external and rule.local)]
    if external:
        for rule in every:
            if rule.local:
                plan.problems.extend(
                    f"{rule.unit}.map:{rule.line}: the original has {path}, which this repository "
                    "keeps as its own (a local directive)"
                    for path in tracked
                    if rule.matches(path)
                )
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


def build_expected(  # noqa: PLR0913 -- the originals' tree is the sixth, and keyword-only
    root: Path, unit: str, files: dict[str, str], out: Path, *, patched: bool, tree: Path | None = None
) -> None:
    """Write into ``out`` what the unit's copied files should be, from the originals in ``tree``."""
    for dest, source in files.items():
        copy_file((tree or root) / source, out / dest)
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


def is_submodule(root: Path, name: str) -> bool:
    """Say whether this repository records ``exportit/<name>`` as a submodule."""
    done = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "--", f"{EXPORT_DIR}/{name}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return done.stdout.startswith(SUBMODULE_MODE + " ")


def unit_files(root: Path, name: str) -> set[str] | None:
    """List the files a unit holds, tracked or not yet, by their path inside it.

    A unit is either a directory of this repository or a repository of its
    own, kept here as a submodule. This repository's git knows a submodule as
    one entry and nothing of what is in it, so a submodule is asked itself.
    None means the submodule is recorded here and not checked out.
    """
    unit_dir = root / EXPORT_DIR / name
    if (unit_dir / ".git").exists():
        present = list_files(unit_dir, "--cached", "--others", "--exclude-standard")
        return {path for path in present if (unit_dir / path).is_file()}
    if is_submodule(root, name):
        return None
    prefix = f"{EXPORT_DIR}/{name}/"
    present = list_files(root, "--cached", "--others", "--exclude-standard", "--", prefix)
    return {path[len(prefix) :] for path in present if (root / path).is_file()}


def check_unit(root: Path, unit: Unit, files: dict[str, str], tree: Path | None = None) -> list[str]:
    """Compare one unit's directory with what its mapping file promises."""
    problems: list[str] = []
    unit_dir = root / EXPORT_DIR / unit.name
    here = unit_files(root, unit.name)
    if here is None:
        return [f"{unit.name}: a submodule that is not checked out; run 'git submodule update --init'"]
    with tempfile.TemporaryDirectory() as scratch:
        expected_dir = Path(scratch)
        build_expected(root, unit.name, files, expected_dir, patched=True, tree=tree)
        for dest in sorted(files):
            verdict = same_file(expected_dir / dest, unit_dir / dest)
            if verdict:
                problems.append(f"{unit.name}: {dest}: {verdict} (source {files[dest]})")
    extra = sorted(path for path in here if path not in files and not is_declared_new(path, unit.new))
    problems.extend(f"{unit.name}: {path}: neither copied nor declared new" for path in extra)
    for item in unit.new:
        if not any(path == item or path.startswith(item) for path in here):
            problems.append(f"{unit.name}: declared new but absent: {item}")
    hidden = sorted(dest for dest in files if dest not in here and (unit_dir / dest).is_file())
    problems.extend(
        f"{unit.name}: {dest}: ignored by .gitignore; add it with 'git add -f', in the unit's own "
        f"repository when the unit is a submodule"
        for dest in hidden
    )
    return problems


def load_plan(root: Path, source: Source | None = None) -> tuple[dict[str, Unit], Plan]:
    """Read the mapping files and resolve them against the originals, failing on any conflict."""
    units = load_units(root)
    if not units:
        raise MapError(f"no mapping files in {EXPORT_DIR}/")
    if source is None:
        plan = resolve(units, tracked_sources(root))
    else:
        plan = resolve(units, source.files, external=source.external)
    if plan.problems:
        raise MapError("\n".join(plan.problems))
    return units, plan


def pick(units: dict[str, Unit], names: list[str]) -> list[str]:
    """Check unit names given on the command line."""
    unknown = [name for name in names if name not in units]
    if unknown:
        raise MapError(f"no such unit: {', '.join(unknown)} (have: {', '.join(units)})")
    return names or list(units)


def command_copy(root: Path, names: list[str], source: Source) -> int:
    """Write or refresh the copies of the named units."""
    units, plan = load_plan(root, source)
    for name in pick(units, names):
        files = plan.files[name]
        unit_dir = root / EXPORT_DIR / name
        written = 0
        with tempfile.TemporaryDirectory() as scratch:
            expected_dir = Path(scratch)
            build_expected(root, name, files, expected_dir, patched=True, tree=source.tree)
            for dest in sorted(files):
                if same_file(expected_dir / dest, unit_dir / dest):
                    copy_file(expected_dir / dest, unit_dir / dest)
                    written += 1
        dropped = len(plan.dropped[name])
        print(f"{name}: {len(files)} files mapped, {written} written, {dropped} dropped")
    return 0


def command_check(root: Path, source: Source, names: list[str] | None = None) -> int:
    """Verify the named units (all when none is named) against their mapping files."""
    units, plan = load_plan(root, source)
    problems: list[str] = []
    for name in pick(units, names or []):
        unit = units[name]
        found = check_unit(root, unit, plan.files[name], source.tree)
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


def command_filter(root: Path, name: str, source: Source) -> int:
    """Print the ``git filter-repo`` directives for one unit."""
    units, plan = load_plan(root, source)
    pick(units, [name])
    print("\n".join(filter_directives(units, plan, name, source.files)))
    return 0


def tree_of(root: Path) -> set[str]:
    """List the files under ``root``, ignoring git's own directory."""
    found: set[str] = set()
    for folder, subdirs, names in os.walk(root):
        if ".git" in subdirs:
            subdirs.remove(".git")
        found.update(str((Path(folder) / item).relative_to(root)) for item in names)
    return found


def command_prove(root: Path, name: str, source: Source) -> int:
    """Extract one unit from a throw-away clone and compare it with the copy.

    The clone is rewritten by ``git filter-repo``; this repository is only
    read. Patches are left out, because the extraction carries history and a
    patch would be a commit made after it.
    """
    units, plan = load_plan(root, source)
    pick(units, [name])
    directives = filter_directives(units, plan, name, source.files)
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        clone, expected = work / "clone", work / "expected"
        (work / "paths.txt").write_text("\n".join(directives) + "\n")
        build_expected(root, name, plan.files[name], expected, patched=False, tree=source.tree)
        steps = [
            ["git", "clone", "--quiet", "--no-local", str(source.repo), str(clone)],
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


UMBRELLA = "cloud-sandbox"
TRANSLATED = {"sandbox-provisioning"}
"""Units whose own files translate their originals: a changed original is work, not only a copy."""


def manifest_path(root: Path) -> Path:
    """Give the umbrella's units.toml, which holds every unit's baseline."""
    return root / EXPORT_DIR / UMBRELLA / "units.toml"


def baselines(root: Path) -> dict[str, str]:
    """Map every unit to its baseline: the commit of the original its copies are."""
    data = tomllib.loads(manifest_path(root).read_text())
    found = {unit["name"]: unit["baseline"] for unit in data["unit"] if not unit.get("external")}
    found[UMBRELLA] = data["umbrella"]["baseline"]
    return found


def set_baseline(root: Path, name: str, commit: str) -> None:
    """Write a unit's new baseline into units.toml, leaving the rest of the file as it is."""
    path = manifest_path(root)
    text = path.read_text()
    if name == UMBRELLA:
        pattern = re.compile(r'(\[umbrella\][^\[]*?\nbaseline = ")[0-9a-f]+(")', re.DOTALL)
    else:
        pattern = re.compile(r'(name = "' + re.escape(name) + r'"\n(?:[^\[]*?\n)?baseline = ")[0-9a-f]+(")')
    new, count = pattern.subn(lambda match: match.group(1) + commit + match.group(2), text)
    if count != 1:
        raise MapError(f"{path}: cannot find the baseline of {name}")
    path.write_text(new)


def concerns(problem: str, names: set[str], units: dict[str, Unit]) -> bool:
    """Say whether a problem of the whole plan is about one of the named units."""
    if problem.startswith("not assigned to any unit: "):
        return any(units[name].covers for name in names)
    return any(f"{name}.map:" in problem or problem.startswith(f"{name}: ") for name in names)


def command_check_baselines(root: Path, given: Path | None) -> int:
    """Verify every unit against the original as it was at the unit's own baseline."""
    units = load_units(root)
    groups: dict[str, list[str]] = {}
    for name, commit in baselines(root).items():
        groups.setdefault(commit, []).append(name)
    if set(units) - {name for names in groups.values() for name in names}:
        raise MapError(f"units with no baseline in {manifest_path(root)}")
    problems: list[str] = []
    for commit, names in sorted(groups.items()):
        with open_source(root, given, commit) as source:
            plan = resolve(units, source.files, external=True)
            found = [problem for problem in plan.problems if concerns(problem, set(names), units)]
            for name in sorted(names):
                found += check_unit(root, units[name], plan.files[name], source.tree)
        problems += found
        state = "ok" if not found else f"{len(found)} problems"
        print(f"baseline {commit[:12]}: {len(names)} units ({', '.join(sorted(names))}): {state}")
    for problem in problems:
        print(f"PROBLEM {problem}", file=sys.stderr)
    return 1 if problems else 0


def keep_paths(units: dict[str, Unit], name: str) -> list[str]:
    """List the original paths a unit takes, as git pathspecs."""
    return [rule.source for rule in units[name].rules if rule.dest is not None]


def fetch_filtered(original: Path, directives: list[str], unit_dir: Path, name: str) -> str:
    """Filter a clone of the original with a unit's directives, fetch it into the unit, and give its HEAD."""
    with tempfile.TemporaryDirectory() as scratch:
        clone = Path(scratch) / "clone"
        (Path(scratch) / "paths.txt").write_text("\n".join(directives) + "\n")
        subprocess.run(["git", "clone", "--quiet", "--no-local", str(original), str(clone)], check=True)
        subprocess.run(
            [
                "uvx",
                "--quiet",
                "git-filter-repo",
                "--quiet",
                "--paths-from-file",
                str(Path(scratch) / "paths.txt"),
            ],
            cwd=clone,
            check=True,
            capture_output=True,
        )
        if git_output(clone, "remote").strip():
            raise MapError(f"{name}: the filtered clone still has a remote; nothing was carried")
        subprocess.run(["git", "-C", str(unit_dir), "fetch", "--quiet", str(clone), "HEAD"], check=True)
    return git_output(unit_dir, "rev-parse", "FETCH_HEAD").strip()


def merge_or_undo(unit_dir: Path, start: str, target: str, upstream: str, message: str) -> None:
    """Merge the original's commits onto the new branch; on a conflict, leave the unit as it was."""
    name = unit_dir.name
    merged = subprocess.run(
        ["git", "-C", str(unit_dir), "merge", "--no-ff", "--quiet", "-m", message, upstream],
        capture_output=True,
        text=True,
        check=False,
    )
    if merged.returncode == 0:
        return
    conflicts = git_output(unit_dir, "diff", "--name-only", "--diff-filter=U").split()
    subprocess.run(["git", "-C", str(unit_dir), "merge", "--abort"], check=False)
    subprocess.run(["git", "-C", str(unit_dir), "switch", "--quiet", start], check=True)
    subprocess.run(["git", "-C", str(unit_dir), "branch", "--quiet", "-D", target], check=True)
    raise MapError(
        f"{name}: the original's changes conflict with the unit's own commits in "
        f"{', '.join(conflicts) or 'the merge'}; nothing was carried. A patch there may need "
        "writing again, in this repository"
    )


def command_sync(root: Path, name: str, given: Path, branch: str) -> int:
    """Carry the original's commits since a unit's baseline into the unit's repository.

    The original (a clean checkout of it, ``given``) is cloned and filtered with
    the unit's directives, as for the unit's first extraction, which gives the
    unit's existing history the same commit IDs. The commits after it are merged
    onto ``feature/<branch>`` in the unit's repository, from ``develop``. What
    cannot be decided here is reported and stops the sync: files the maps do not
    resolve, a merge that conflicts, a copy that is then not its original plus
    its patches. Nothing is pushed, and this repository's own files are only
    touched in the umbrella's units.toml, whose baseline for the unit moves.
    """
    unit_dir = root / EXPORT_DIR / name
    if not (unit_dir / ".git").exists():
        raise MapError(f"{name}: exportit/{name} is not a repository of its own (a checked-out submodule)")
    if git_output(unit_dir, "status", "--porcelain").strip():
        raise MapError(f"{name}: the unit's repository has changes")
    baseline = baselines(root)[name]
    with open_source(root, given) as source:
        head = git_output(source.repo, "rev-parse", "HEAD").strip()
        try:
            git_output(source.repo, "merge-base", "--is-ancestor", baseline, head)
        except subprocess.CalledProcessError as error:
            raise MapError(
                f"{name}: the original's HEAD does not descend from the baseline {baseline}"
            ) from error
        try:
            units, plan = load_plan(root, source)
        except MapError as error:
            raise MapError(
                f"the maps do not resolve against the original; decide these first:\n{error}"
            ) from error
        directives = filter_directives(units, plan, name, source.files)
        paths = keep_paths(units, name)
        expected = int(
            git_output(source.repo, "rev-list", "--count", "--no-merges", f"{baseline}..{head}", "--", *paths)
        )
        changed = sorted(
            line
            for line in git_output(
                source.repo, "diff", "--name-only", baseline, head, "--", *paths
            ).splitlines()
            if line
        )
        upstream = fetch_filtered(source.repo, directives, unit_dir, name)
        new = git_output(unit_dir, "rev-list", "--no-merges", upstream, "^develop").split()
        if len(new) != expected:
            raise MapError(
                f"{name}: the filtered original brings {len(new)} commits the unit does not have, where "
                f"{expected} touch its paths since the baseline: the histories are not shared, so "
                "nothing was carried"
            )
        if not new:
            set_baseline(root, name, head)
            print(f"{name}: nothing to carry since {baseline[:12]}; the baseline is now {head[:12]}")
            return 0
        start = git_output(unit_dir, "rev-parse", "--abbrev-ref", "HEAD").strip()
        target = f"feature/{branch}"
        subprocess.run(["git", "-C", str(unit_dir), "switch", "--quiet", "-c", target, "develop"], check=True)
        message = (
            f"Carry {len(new)} commits of the original since {baseline[:12]}, to {head[:12]}\n\n"
            f"Synced by Cloud-Sandbox's export.py sync {name}, from {given}."
        )
        merge_or_undo(unit_dir, start, target, upstream, message)
        problems = check_unit(root, units[name], plan.files[name], source.tree)
    if problems:
        for problem in problems:
            print(f"PROBLEM {problem}", file=sys.stderr)
        print(
            f"{name}: carried onto {target}, but the unit is not its original plus its patches",
            file=sys.stderr,
        )
        return 1
    set_baseline(root, name, head)
    print(f"{name}: carried {len(new)} commits onto {target}; the baseline is now {head[:12]}")
    print(f"{name}: originals changed: {', '.join(changed)}")
    if name in TRANSLATED:
        print(
            f"{name}: its own files translate these originals; run its just test, whose parity tests "
            "say where the translation no longer holds"
        )
    return 0


def repository_root() -> Path:
    """Find the top of the repository this tool lives in."""
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    """Run one command; see the module docstring."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", maxsplit=1)[0])
    parser.add_argument("--root", type=Path, default=None, help="repository root (default: this one)")
    parser.add_argument("--source", type=Path, default=None, help="a git checkout of the original to read")
    parser.add_argument("--at", default=None, help="read the originals as they were at this commit")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("copy").add_argument("units", nargs="*")
    check = commands.add_parser("check")
    check.add_argument("units", nargs="*")
    check.add_argument("--baselines", action="store_true", help="each unit at its own baseline")
    commands.add_parser("filter").add_argument("unit")
    commands.add_parser("prove").add_argument("unit")
    sync = commands.add_parser("sync")
    sync.add_argument("unit")
    sync.add_argument("--branch", required=True, help="the branch to make in the unit, as sync-1")
    args = parser.parse_args(argv)
    root: Path = (args.root or repository_root()).resolve()
    command: str = args.command
    given: Path | None = args.source
    try:
        if command == "sync":
            if given is None or args.at is not None:
                raise MapError("sync needs --source, the original's checkout, and takes no --at")
            return command_sync(root, str(args.unit), given.resolve(), str(args.branch))
        if command == "check" and args.baselines:
            if args.at is not None or args.units:
                raise MapError("check --baselines takes no --at and no units: each unit has its own")
            return command_check_baselines(root, given)
        if command == "prove" and args.at is not None:
            raise MapError("prove reads a whole history, not one commit: give no --at")
        with open_source(root, given, args.at) as source:
            run = {
                "copy": lambda: command_copy(root, list(args.units), source),
                "check": lambda: command_check(root, source, list(args.units)),
                "filter": lambda: command_filter(root, str(args.unit), source),
                "prove": lambda: command_prove(root, str(args.unit), source),
            }
            return run[command]()
    except MapError as error:
        print(f"PROBLEM {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
