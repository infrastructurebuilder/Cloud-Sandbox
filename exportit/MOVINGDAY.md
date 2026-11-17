# Moving day: each unit into a private repository, kept here as a submodule

*Status:* planned 2026-11-17 on `feature/movingday-plan`, at the
operator's request; the first tags corrected by the operator the same
day (0.0.1 for the `model-*` and `sandbox-*` repositories). Nothing is
executed: no repository has been created,
nothing has been pushed, and no directory has been changed. It is
executed on "do moving day", one phase at a time, after each **YOUR
DECISION** below has been asked, one at a time.

## What was asked

The operator, 2026-11-17:

- a new **private** repository on `infrastructurebuilder` for each mapped
  unit under `exportit/`;
- the **mapping files stay in this repository**;
- each new repository becomes a **git submodule at `exportit/<unit>`**, so
  that no path changes;
- a repository for [cloudflow.patches/](cloudflow.patches/) or for
  [tools/](tools/) (as `csis-tools`) only with a reason and the
  operator's approval first.

## The answer in short

- **Fifteen repositories**, one for each `.map` file. They are listed
  under [The units](#the-units).
- **No repository for `cloudflow.patches/` and none for `tools/`.** This
  plan does not propose either, so there is nothing to approve. The
  reasons are under [What stays in this repository](#what-stays-in-this-repository);
  if you want one anyway, say so and it becomes an item.
- **The originals are not touched.** `cloudflow/`, `scripts/`,
  `terraform/`, `models/` and the rest stay where they are, and
  `just export-check` goes on holding every unit to "its source, plus
  the patches". Deleting the originals is stage 22's last step for each
  unit, and is not part of this plan.
- Before any unit moves, **the export tool has to learn about
  submodules**, or the acceptance bar fails for every moved unit.
  That is phase M0.

## What this changes in the standing plan

Existing decisions stand; these are the places where this request
departs from them, each noted so that it is a choice and not an
accident.

| Standing | What moving day does |
| --- | --- |
| "Nothing leaves this repository" ([SPECS/TODO.md](../SPECS/TODO.md), since 2026-11-12) | Replaced: the units' copies leave, into repositories of their own. The originals stay |
| [Stage 19](../SPECS/STAGE-19.md): decide whether to relocate, after stages 12 to 18, the live proof, and the collection's stages | Decided ahead of that, by the operator: relocate all. Stage 15 (the live proof) is waiting for an AWS account, 16 to 18 are not done, and collection stage 5 is waiting for its Galaxy namespace |
| [Stage 22](../SPECS/STAGE-22.md): private or public asked for each unit; the original paths deleted in the same step | Private, all of them. The original paths are **not** deleted, and Cloud-Sandbox holds a submodule where the copy was. Stage 22 is left with only its step 4, the deletion, when the operator wants it |
| [Stage 20](../SPECS/STAGE-20.md): `sandbox-configs` is split by owner before it moves | Decision 4 below: it moves whole unless you say otherwise |
| [Stage 21](../SPECS/STAGE-21.md): the first boot runs the playbooks | Unchanged, and easier afterwards: `sandbox-provisioning` will have a URL to name. A private repository needs a deploy key on the node |
| The parity watch on `main` ([PLAN.md](../PLAN.md)) | Unchanged. A change carried from `main` is committed in the unit's repository, and the submodule here is moved to it |

One thing "private" does not do: Cloud-Sandbox on
`infrastructurebuilder` is a **public** repository, and every file of
every unit, as it is today, is in its history and stays there. The new
repositories keep what is added *after* moving day private; they do not
hide what is already published.

## The units

Order is the order of the work: the smallest first, as a pilot, then
`units.toml`'s relocation order. Because nothing is deleted and no unit
names another by repository yet, the order is for convenience, not
forced.

| # | Unit and path | Repository (default name) | Files | First tag |
| ---: | --- | --- | ---: | --- |
| 1 | [model-common](model-common/) | `model-common` | 11 | 0.0.1 |
| 2 | [cloudflow](cloudflow/) | `cloudflow` | 255 | 1.6.0b0 |
| 3 | [model-adcirc-cora](model-adcirc-cora/) | `model-adcirc-cora` | 63 | 0.0.1 |
| 4 | [model-eccofs](model-eccofs/) | `model-eccofs` | 18 | 0.0.1 |
| 5 | [model-liveocean](model-liveocean/) | `model-liveocean` | 15 | 0.0.1 |
| 6 | [model-necofs](model-necofs/) | `model-necofs` | 22 | 0.0.1 |
| 7 | [model-nosofs](model-nosofs/) | `model-nosofs` | 14 | 0.0.1 |
| 8 | [model-secofs](model-secofs/) | `model-secofs` | 21 | 0.0.1 |
| 9 | [model-ucla-roms](model-ucla-roms/) | `model-ucla-roms` | 9 | 0.0.1 |
| 10 | [model-ufscoastal](model-ufscoastal/) | `model-ufscoastal` | 22 | 0.0.1 |
| 11 | [sandbox-configs](sandbox-configs/) | `sandbox-configs` | 141 | 0.0.1 |
| 12 | [sandbox-provisioning](sandbox-provisioning/) | `sandbox-provisioning` | 101 | 0.0.1 |
| 13 | [sandbox-terraform](sandbox-terraform/) | `sandbox-terraform` | 37 | 0.0.1 |
| 14 | [sandbox-ops](sandbox-ops/) | `sandbox-ops` | 23 | 0.0.1 |
| 15 | [cloud-sandbox](cloud-sandbox/) (the umbrella) | **`cloud-sandbox-umbrella`** | 91 | 0.1.0 |

"Files" is the number tracked in the copy today.

**The first tags were set by the operator on 2026-11-17: 0.0.1 for every
`model-*` and `sandbox-*` repository**, thirteen of them. Until then
[units.toml](cloud-sandbox/units.toml) said 0.1.0 for all thirteen, and
so do the `pyproject.toml` of `sandbox-provisioning`, `sandbox-terraform`
and `sandbox-configs`; M0's item 6 brings them to 0.0.1, so that a tag
names the version its repository declares. `cloudflow` keeps 1.6.0b0,
the version its `pyproject.toml` has carried since stage 2. The umbrella
has no version in `units.toml`, and the instruction does not name it
(`cloud-sandbox` is neither `model-*` nor `sandbox-*`): 0.1.0 is
proposed, and asked with decision 1, where its name is.

**The umbrella cannot be called `cloud-sandbox`.** GitHub's repository
names do not distinguish upper and lower case, and
`infrastructurebuilder/Cloud-Sandbox` is this repository. Its path here
stays `exportit/cloud-sandbox`; only the repository's name differs
(decision 1). No other name is taken: on 2026-11-17 the organisation
held `Cloud-Sandbox` and `ansible-collection-csis-spack`, and nothing
else that these names would collide with.

## What stays in this repository

| What | Why it stays |
| --- | --- |
| The 15 mapping files, `*.map` | Asked. They say which original goes where, and the originals are here |
| [cloudflow.patches/](cloudflow.patches/), the 9 corrections | They are part of the mapping, not of cloudflow. `just export-check` compares each copied file with "its source, plus the patches", so the patches must sit beside the map and the originals. In cloudflow's own repository each patch becomes a commit (step 3 of the method), so nothing of them is missing there. A repository of their own would hold nine files that only this repository reads |
| [tools/](tools/): `export.py`, `configs_schema.py` and their tests | Not one unit uses them: no unit's `Justfile` or test reaches outside its own directory (checked 2026-11-17). `export.py` reads the mapping files and the originals, which stay here. The other tests (`test_umbrella.py`, `test_model_units.py`, `test_configs_schema.py`) hold the units *to each other*, which can only be done where all of them are checked out side by side, and that place is this repository. Its own test already says so: "the export tool itself is how the copies are made; it is not relocated". Stage 20 would move the schema writer into cloudflow; that is its business, not moving day's |
| [MAP.md](MAP.md), [REMINDERS.md](REMINDERS.md), this page, [.gitignore](.gitignore) | The records of this work |
| The originals, `SPECS/`, `PLAN.md`, the root `Justfile` | Not part of any unit's copy |

## Decisions

Asked one at a time at "do moving day", the default first.

1. **YOUR DECISION (the repositories' names):** the unit's own name, and
   `cloud-sandbox-umbrella` for the umbrella (default); or every name
   with a prefix, as `csis-cloudflow`, `csis-model-common`, ...,
   `csis-cloud-sandbox`, which avoids both the clash and such general
   names as `cloudflow` in the organisation; or names you give.
   `units.toml` says a unit's name is its repository's name, so with
   anything but the default it gains a `repository` field (it gains the
   URL either way, in M3).
   Asked with it: **the umbrella's first tag**, 0.1.0 (default), or
   0.0.1 like the thirteen.

2. **YOUR DECISION (history):** each repository starts with the unit's
   history, extracted from this one with `git filter-repo`, as
   [MAP.md](MAP.md#how-a-unit-would-really-be-relocated) describes and
   `just full-test` has rehearsed for every unit since stage 2
   (default); or one first commit holding the unit as it is today, with
   no history.
   With history, the commits of the people who wrote the originals come
   along, under their names, into the private repositories.

3. **YOUR DECISION (branches in the new repositories):** git-flow, as
   here: `main`, `develop`, a feature branch for each phase,
   squash-merged and kept (default: it is your standing rule, and stage
   22's default); or `main` alone.
   The cost of the default with submodules: a squash makes a new commit,
   so when a phase finishes, each unit it touched is finished first, the
   submodule here is moved to the unit's new `develop` commit, and only
   then is Cloud-Sandbox's own branch finished. The procedure is under
   [Working afterwards](#working-afterwards).

4. **YOUR DECISION (`sandbox-configs`):** it moves whole, as one of the
   fifteen (default: it is what was asked); or stage 20's split is done
   first. Moved whole, the split later takes files out of one repository
   and into cloudflow's, and their history does not follow them across.

5. **YOUR DECISION (links that leave a unit):** 27 links in the units'
   own pages lead out of the unit: 25 to [MAP.md](MAP.md), one to
   `SPECS/` and one to a sibling unit. Leave them (default): they still
   resolve wherever the units are checked out under `exportit/`, which
   is where they are worked on; on GitHub, in the unit's own repository,
   they lead nowhere. Or rewrite them as full URLs into Cloud-Sandbox on
   GitHub.

6. **YOUR DECISION (who creates the repositories):** I create each with
   `gh repo create infrastructurebuilder/<name> --private`, asking you
   once before the pilot and once before the other fourteen (default);
   or you create the fifteen empty repositories and I push to them.
   Either way: never a fork, never under `ioos`, and the push goes only
   to a remote whose URL names `infrastructurebuilder`.

Already decided:

- **First tags** (the operator, 2026-11-17): every `model-*` and
  `sandbox-*` repository is first tagged 0.0.1, not the 0.1.0 this plan
  first proposed. The tag is the bare number, as the collection's tags
  are. `cloudflow` is tagged 1.6.0b0 and the umbrella as decision 1
  settles, unless you say otherwise then.

## Phases

Each phase ends with the root `just test` and `just full-test`, a local
commit on its feature branch, and a stop for the operator's word.
Nothing is merged into `develop` or pushed in Cloud-Sandbox without it.

### M0: make this repository ready (nothing leaves yet)

1. **[tools/export.py](tools/export.py) reads a unit's files from the
   unit's own repository** when `exportit/<unit>` is a submodule. Today
   it asks Cloud-Sandbox's git for the files under `exportit/<unit>/`;
   for a submodule git answers with one entry, the submodule itself, and
   the check would report every file the map calls `new` as absent. Both
   forms have to work at once, because the units move one at a time.
   `copy` already writes plain files and needs no change. Tests: a
   throw-away repository with one unit as a directory and one as a
   submodule, checked, with a file added, changed and removed in each.

2. **[cloud-sandbox.map](cloud-sandbox.map) drops `.gitmodules`.** It
   `covers ./`, so the new file at the root would otherwise be "not
   assigned to any unit".

3. **Each unit gets its own `.gitignore`**, declared `new` in its map.
   Today [exportit/.gitignore](.gitignore) and the root's cover them
   all; neither reaches inside a submodule. Each holds what that unit's
   own build makes (`.venv/`, `.ruff_cache/`, `__pycache__/`,
   `.pytest_cache/`, `dist/`, `.collections/`, `.tofu/`, the Terraform
   directories, cloudflow's `docs/sphinx/build/`). The gate that proves
   it complete is in the method: after the unit's full test in its own
   clone, `git status` shows nothing.

4. **The root [Justfile](../Justfile):**
   - `init` first runs `git submodule update --init`;
   - a new target `submodules-check`, part of `test`: every unit's
     directory is there and initialised, so that a fresh clone without
     its submodules fails with one clear line and not with fifteen
     strange ones;
   - a new target `submodules-pushed`, run before Cloud-Sandbox is
     pushed: every commit a submodule is recorded at exists on its
     remote.

5. **One setting in this clone:** `git config push.recurseSubmodules
   check`, so that git itself refuses to push Cloud-Sandbox while a
   recorded submodule commit is unpushed.

6. **The thirteen units' version becomes 0.0.1** (the operator's first
   tag): in [units.toml](cloud-sandbox/units.toml); in the
   `pyproject.toml` and `uv.lock` of `sandbox-provisioning`,
   `sandbox-terraform` and `sandbox-configs`, which
   [tools/tests/test_umbrella.py](tools/tests/test_umbrella.py) holds
   to it; and wherever a test or a page of those units states 0.1.0 as
   the unit's own version. The collection's 0.1.0, named in
   [MAP.md](MAP.md) as history, is not one of these and stays.

M0 changes nothing outside this repository, and `just test` and
`just full-test` pass with all fifteen units still plain directories.

### M1: the pilot, `model-common`

The method below, once, for the smallest unit (11 files). Then a stop:
you look at the repository on GitHub and at the submodule here before
the other fourteen follow.

### M2: the other fourteen

The same method, in the table's order, each unit one commit on the
branch. `cloud-sandbox` goes last, after M3's item 1 has put the other
fourteen URLs into its `units.toml`.

### M3: records

1. [units.toml](cloud-sandbox/units.toml) gains each unit's repository
   (its versions were set in M0);
   its header no longer says "nothing has left Cloud-Sandbox";
   `tests/check_units.py` holds the new field. This is a change inside
   the umbrella unit, made before the umbrella is extracted.
2. [MAP.md](MAP.md): the introduction, the Units table (a new state,
   *relocated: private repository, submodule here*), the method section
   (what was done, and that step 6, the deletion, was not), and the
   order section.
3. [SPECS/TODO.md](../SPECS/TODO.md): the standing decision "nothing
   leaves this repository" replaced; stage 19 marked decided, with what
   was decided; [stage 22](../SPECS/STAGE-22.md) left with its deletion
   step. [REMINDERS.md](REMINDERS.md): "whether to relocate at all"
   closed; new items for the links (decision 5) and for stage 20 if
   `sandbox-configs` moved whole.
4. [PLAN.md](../PLAN.md): this plan's status, and the order of the
   remaining work after it.
5. The units' `release` targets still say "nothing to release from
   exportit/". How a unit is released from its own repository is not
   decided here; a reminder is left.

## The method, for one unit

Boxes 2 and 3 were rehearsed on 2026-11-17, in a scratch directory and
with nothing pushed, for `model-common` (3 commits of history, no
patches) and `cloudflow` (114 commits, 9 patches): both ended with the
`diff` of box 3 printing nothing.

The boxes are what is run, on your local machine, for each unit; at
"do moving day" I run them and read each result before the next, and
stop at every gate. `UNIT` is the directory's name and `REPO` the
repository's (the same, except for the umbrella). Every box sets its
own variables. The working directory for the extractions is beside the
repositories, not in `/tmp`, which the system prunes.

**Before anything, the tree is clean and the copy is what the map says.**

```sh
# moving day, one unit -- box 1 of 7 -- v1
cd /Volumes/MiniSSD/git/Work/Phase3/Cloud-Sandbox
git status --short
just export-check
```

`git status` must print nothing and every unit must say `ok`. If not,
STOP.

**Extract the unit with its history** (decision 2's default). About a
minute: a clone of this repository, then the rewrite.

```sh
# moving day, one unit -- box 2 of 7 -- v1
UNIT=model-common
SANDBOX=/Volumes/MiniSSD/git/Work/Phase3/Cloud-Sandbox
WORK=/Volumes/MiniSSD/git/Work/Phase3/movingday-work
mkdir -p "$WORK"
cd "$SANDBOX" && just export-filter "$UNIT" > "$WORK/$UNIT.paths"
git clone --quiet --no-local "$SANDBOX" "$WORK/$UNIT"
cd "$WORK/$UNIT" && uvx git-filter-repo --quiet --paths-from-file "$WORK/$UNIT.paths"
git -C "$WORK/$UNIT" remote -v
```

`git remote -v` must print **nothing**: the rewrite removes `origin`,
which is the safeguard against pushing rewritten history back. If it
prints a remote, STOP.

**Add what the copy has and the originals do not:** each patch as a
commit of its own, then the files that exist only in the unit, taken
from Cloud-Sandbox's commit, not from the working directory.

```sh
# moving day, one unit -- box 3 of 7 -- v1
UNIT=model-common
SANDBOX=/Volumes/MiniSSD/git/Work/Phase3/Cloud-Sandbox
WORK=/Volumes/MiniSSD/git/Work/Phase3/movingday-work
cd "$WORK/$UNIT"
find "$SANDBOX/exportit/$UNIT.patches" -name '*.patch' 2>/dev/null | sort | while read -r patch; do
  git apply --whitespace=nowarn "$patch" && git add -A
  git commit --quiet -m "Apply $(basename "$patch" .patch), a correction recorded in Cloud-Sandbox"
done
git -C "$SANDBOX" archive "HEAD:exportit/$UNIT" | tar -x -C "$WORK/$UNIT"
git add -A && git commit --quiet -m "Add what exists only in the unit: its build, its tests and its pages"
diff <(git -C "$SANDBOX" ls-tree -r "HEAD:exportit/$UNIT") <(git ls-tree -r HEAD)
```

`diff` must print **nothing**: the new repository's files are then the
copy's, file for file, by content and by mode. Anything printed: STOP.

**The unit passes its own tests, alone.** Minutes for most units; for
`sandbox-provisioning` the container test, and for `cloudflow` its full
suite: time unknown, up to an hour.

```sh
# moving day, one unit -- box 4 of 7 -- v1
UNIT=model-common
WORK=/Volumes/MiniSSD/git/Work/Phase3/movingday-work
cd "$WORK/$UNIT" && just init && just test && just full-test
git -C "$WORK/$UNIT" status --short
```

The tests must pass and `git status` must print nothing: a line there is
something the unit's `.gitignore` misses, or a test that writes into the
tree. Either: STOP, fix it in Cloud-Sandbox (M0's item 3), and begin the
unit again.

**Create the repository and push.** This is the step that leaves this
machine; it is asked first (decision 6).

```sh
# moving day, one unit -- box 5 of 7 -- v1
UNIT=model-common
REPO=model-common
VERSION=0.0.1
WORK=/Volumes/MiniSSD/git/Work/Phase3/movingday-work
GH_PAGER=cat gh repo create "infrastructurebuilder/$REPO" --private --description "Cloud Sandbox unit: $UNIT"
cd "$WORK/$UNIT"
git branch -M main && git branch -f develop main
git tag "$VERSION"
git remote add origin "git@github.com:infrastructurebuilder/$REPO.git"
git push -u origin main develop "$VERSION"
GH_PAGER=cat gh repo view "infrastructurebuilder/$REPO" --json visibility,isFork,defaultBranchRef
```

It must say `PRIVATE`, `"isFork":false`. Only `main`, `develop` and the
one tag are pushed, by name: never `--all`, `--tags` or `--mirror`. The
rewritten clone still holds a rewritten copy of every branch and tag of
Cloud-Sandbox (`feature/stage-2-cloudflow`, `v2.1.0`, and so on), and
those stay behind in the working directory. `-M` and `-f` are there
because one of those copies is itself called `main`, and one `develop`.
With decision 3's other answer there is no `develop`.

**Put the submodule where the copy was.** The copy's tracked files are
removed from Cloud-Sandbox's index; what is left in the directory
(environments, caches) is moved aside, not deleted.

```sh
# moving day, one unit -- box 6 of 7 -- v1
UNIT=model-common
REPO=model-common
SANDBOX=/Volumes/MiniSSD/git/Work/Phase3/Cloud-Sandbox
WORK=/Volumes/MiniSSD/git/Work/Phase3/movingday-work
cd "$SANDBOX"
git rm -r --quiet "exportit/$UNIT"
[ -d "exportit/$UNIT" ] && mv "exportit/$UNIT" "$WORK/$UNIT.leftovers"
git submodule add -b develop "../$REPO.git" "exportit/$UNIT"
diff <(git ls-tree -r "HEAD:exportit/$UNIT") <(git -C "exportit/$UNIT" ls-tree -r HEAD)
```

`diff` must print nothing: what is checked out at `exportit/<unit>` is
what Cloud-Sandbox held there one commit ago. The URL is relative
(`../<repo>.git`), so it follows whatever Cloud-Sandbox's own `origin`
is, over SSH or HTTPS.

**The acceptance bar, then the commit.** The root `just test` takes a
few minutes.

```sh
# moving day, one unit -- box 7 of 7 -- v1
UNIT=model-common
cd /Volumes/MiniSSD/git/Work/Phase3/Cloud-Sandbox
just init && just test
git status --short | grep -v "^D  exportit/$UNIT/"
```

`just test` must pass. The last command leaves out the unit's old files,
which git shows as deleted, and must print two lines and no more:
`.gitmodules` and `exportit/<unit>`. Then the commit, locally, on the
phase's branch. The directories under `movingday-work/` are removed
only at the end of the phase, and only when you say so.

With decision 2's other answer, boxes 2 and 3 become one: an empty
repository, the `git archive` of the unit into it, one commit; the
`diff` gate is the same.

## Working afterwards

- **A change to a unit is a commit in the unit's repository**, made in
  `exportit/<unit>`, on a feature branch there named as the phase's
  branch is here. Cloud-Sandbox's branch then records the new commit
  (`git add exportit/<unit>`).
- **A change carried from an original** (the parity watch, or a new
  patch) is made as before: the original or the patch changes here,
  `just export <unit>` writes the copy, and `just export-check` holds
  it. The difference is that the written copy is then committed in the
  unit's repository.
- **Finishing a phase**, with git-flow in the units: finish each touched
  unit (squash, keep); move its submodule here to the unit's `develop`;
  `just test` and `just full-test` at the root; commit; finish
  Cloud-Sandbox's branch.
- **Pushing**, on the operator's word only, as now: the units first,
  then Cloud-Sandbox. `just submodules-pushed` and git's own check both
  refuse the wrong order.
- **A fresh clone** of Cloud-Sandbox needs
  `git clone --recurse-submodules`, or `just init` afterwards, and access
  to the fifteen private repositories. Without that access the units'
  directories are empty and the root `just test` fails at
  `submodules-check`. A linked worktree needs its own
  `git submodule update --init`.

## Out of scope

- Deleting any original path (stage 22's remaining step).
- Splitting `sandbox-configs` (stage 20), unless decision 4 says so, and
  the first-boot change (stage 21).
- Any use of the new repositories by one another: no unit installs
  another from its repository yet, and `sandbox-provisioning` goes on
  installing the collection from its public repository at a tag.
- Releases, continuous integration, and access settings in the new
  repositories. The organisation is on GitHub's free plan; as far as I
  know, branch protection is not available there for private
  repositories.
- Anything toward `ioos`: no push, no pull request, no remote, no fork.
- The collection `ansible-collection-csis-spack`: it has its own
  repository and its own workspace.

## Acceptance

- Fifteen private repositories on `infrastructurebuilder`, none a fork,
  each holding exactly what `exportit/<unit>` held, shown by the `diff`
  gates, and each passing its own `just test` and `just full-test`
  alone.
- In Cloud-Sandbox: fifteen submodules at the same paths; the fifteen
  mapping files, `cloudflow.patches/` and `tools/` where they were; the
  originals untouched.
- The root `just test` and `just full-test` pass, the fifteen extraction
  proofs among them.
- Nothing pushed to Cloud-Sandbox's `origin` and nothing merged into
  `develop` except on the operator's word; nothing anywhere toward
  `ioos`.
