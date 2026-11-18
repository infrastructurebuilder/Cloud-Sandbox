# Stage 23: syncing from the original after its paths are deleted

*Status:* planned 2026-11-18 on `feature/upstream-sync-plan`, at the
operator's request, and **executed the same day on "do 23"**, on
`feature/stage-23-upstream-sync` here and `feature/baselines` in the
umbrella's repository, and merged into both `develop`s and pushed the
same day, after the root `just full-test` passed. The decisions are under
[Decisions taken](#decisions-taken), the result under
[Outcome](#outcome). It comes
before [stage 22](STAGE-22.md)'s deletion of the original paths: once
they are gone, this is the only way changes made to the original
repository can reach the units.

## Why

The operator asked (2026-11-18): if the originals are deleted from
Cloud-Sandbox, and a changed version of the original repository is
given, do the mapping files still say enough to carry its changes into
the fifteen unit repositories?

They say almost enough. Every `copy` line names the unit and the place a
file goes; the umbrella's map `covers ./`, so a new upstream file that no
map claims is reported, not lost; a map line that matches nothing any
more is reported; a patch that no longer applies is reported. And the
history can be carried, not only the contents: re-extracting
`model-common` and `cloudflow` from Cloud-Sandbox on 2026-11-18 gave
the same commit IDs their repositories already hold, so filtering a
newer clone of the original with the same directives gives the shared
history unchanged and the new upstream commits on top of it.

Two things are missing, and one has never been tried:

1. **[export.py](../exportit/tools/export.py) reads the originals from
   the repository it lives in.** After the deletion that repository has
   none. It needs to read them from another checkout, the changed
   original, while the maps and patches stay here.
2. **Nothing records which upstream commit each unit was made from.**
   [PLAN.md](../PLAN.md)'s parity watch keeps one baseline for the
   repository (`ca0604a`). Without a baseline for each unit, "what has
   changed for this unit since" cannot be worked out, and after a first
   sync the units will no longer share one.
3. **A sync has never been run.** The extraction has been rehearsed for
   every unit since stage 2; carrying new upstream commits into a unit's
   existing repository, and merging them over the unit's own commits,
   has not.

## What exists

- The originals in Cloud-Sandbox are exactly `ca0604a`'s: on 2026-11-18,
  `git diff ca0604a develop` outside `exportit/`, `SPECS/`, `PLAN.md`,
  the `Justfile` and `.gitmodules` showed nothing. `origin/main` had not
  moved past it. So every unit's copied files are `ca0604a`'s, plus the
  unit's patches.
- `origin` (`infrastructurebuilder/Cloud-Sandbox`) is a copy of the
  original project, with the same history. A newer clone of the original
  shares every commit up to `ca0604a`.
- Each unit's repository holds the filtered history, then one commit per
  patch (cloudflow's nine), then one commit adding what exists only in
  the unit, then the unit's own work (Spec Kit, since 2026-11-18).
- The parity watch's procedure (PLAN.md) plans each upstream change as a
  `SYNC-<n>` stage; it has never had anything to carry.

## Items

1. **The export tool reads the originals from a checkout of its own.**
   `export.py` gains `--source <path>`: a git checkout of the original
   repository, clean, whose tracked files are the originals. `check`,
   `copy`, `filter` and `prove` read the files and their list from it;
   the maps, the patches and the units are still read here. Without
   `--source` it behaves as today. The root `Justfile` passes it through
   (`just export-check source=<path>` and the others). Tests: the tool's
   existing tests run both ways, and a throw-away "original" beside a
   throw-away Cloud-Sandbox with no originals of its own.

2. **Each unit's baseline in [units.toml](../exportit/cloud-sandbox/units.toml).**
   A field `baseline`: the commit of the original repository the unit's
   copied files are (with its patches). `ca0604a` for all fifteen today,
   which the tests prove: a check that every unit's copied files equal
   its baseline's files plus its patches, read from that commit with
   `--source`. A sync moves a unit's baseline forward, in the same
   change.

3. **`export.py sync UNIT --source <path>`**, which carries a unit from
   its baseline to the source's HEAD, on a branch of the unit's
   repository, and reports what it could not carry:
   - with history (decision 2's default): the source is cloned and
     filtered with the unit's directives, as for the extraction; the
     commits after the baseline's rewritten commit are fetched into the
     unit's repository and merged onto a feature branch there; the
     patches are applied again where they no longer are;
   - what it reports and does not decide: an upstream file that no map
     claims, a map line that matches nothing, a patch that does not
     apply, a merge conflict with the unit's own commits, and, for
     `sandbox-provisioning`, a changed original whose roles the parity
     tests no longer hold to it.

   Nothing is pushed: a sync ends with a branch in each touched unit and
   one here (baselines, any map or patch change), for the operator to
   look at.

4. **A rehearsal, kept as a target** (`just sync-rehearse`): a
   throw-away "changed original" is made from Cloud-Sandbox at `ca0604a`
   with one commit of each kind of change:
   - a change to a copied file (for `model-common`);
   - a new file inside a copied directory (for `cloudflow`, which takes
     `cloudflow/` whole);
   - a new file outside every map;
   - a deleted file that a map names;
   - a change to a file cloudflow patches, one that the patch survives
     and one that it does not;
   - a change to `scripts/setup-instance.sh` (for
     `sandbox-provisioning`).

   It then syncs throw-away clones of the unit repositories, never the
   real ones, and checks each outcome against what item 3 promises: the
   carried commits with their authors and dates, the reports for what
   was not carried. It goes in `just full-test`.

5. **The parity watch** in PLAN.md is rewritten around the sync: "look"
   compares each unit's baseline with the given original, and "carry"
   is `export.py sync`, one unit at a time, one branch per unit there and
   one stage branch here.

6. **Records:** MAP.md gains "Syncing from the original" (what the maps
   decide, what they leave to the operator); [stage 22](STAGE-22.md)
   says that its deletion waits for this stage;
   [REMINDERS.md](../exportit/REMINDERS.md) says so as well.

## Decisions

1. **YOUR DECISION (where the changed original comes from):** a local
   git clone that you give me, by its path, each time (default: this
   repository gains no remote and no path of its own toward the
   original, and certainly none toward `ioos`); or a fixed place beside
   this repository (`../Cloud-Sandbox-upstream`) that you keep up to
   date yourself, named in the `Justfile`.

2. **YOUR DECISION (how changes are carried):** with their history, the
   upstream commits merged into each unit's repository under their
   authors (default: the units keep the history they were made with);
   or by contents only, `just export <unit>` writing the new copies and
   one commit in each unit saying which upstream commit they are.

3. **YOUR DECISION (when a sync touches several units):** one branch per
   unit, named after the sync (`feature/sync-<n>`), and one stage here,
   `SPECS/SYNC-<n>.md`, as the parity watch already says (default); or
   each unit synced and finished on its own, with no stage here.

## Decisions taken

Asked on 2026-11-18, one at a time; every answer was the default:

1. The changed original is a local clone the operator gives, by its
   path, each time.
2. Changes are carried with their history.
3. A sync that touches several units: one `feature/sync-<n>` branch in
   each, and one `SPECS/SYNC-<n>.md` stage here.

## Outcome

- **`export.py`** reads the originals from `--source <clone>` and
  `--at <commit>` for every command (`prove` takes no `--at`: it reads
  a whole history); `check` takes units; `check --baselines` checks each
  unit at its own baseline; `sync <unit> --source <clone> --branch <name>`
  carries the original's commits. A new directive, `local`, marks
  `SPECS/`, `PLAN.md`, the `Justfile` and `.gitmodules` as this
  repository's own in [cloud-sandbox.map](../exportit/cloud-sandbox.map).
- **The sync refuses**, leaving the unit as it was, when: the maps do not
  resolve against the original; the original does not descend from the
  baseline; the filtered original brings a different number of new
  commits than touch the unit's paths since the baseline (the histories
  are not shared); the merge conflicts; the unit has changes. It reports,
  after carrying, the originals that changed, and for
  `sandbox-provisioning` that its translation must be checked.
- **Baselines** are in the umbrella's
  [units.toml](../exportit/cloud-sandbox/units.toml), `ca0604a` for every
  unit and for the umbrella; its check requires a full commit for every
  copied unit and none for an external one. `just export-baselines`
  passes: every unit is `ca0604a`'s files plus its patches.
- **Tests:** 14 in `tools/tests/test_sync.py`, on small repositories made
  as moving day made the real ones (81 in the tool in all).
- **The rehearsal**, [rehearse_sync.py](../exportit/tools/rehearse_sync.py),
  `just sync-rehearse`, in `just full-test`: seven scenarios against
  throw-away clones of the real `model-common`, `cloudflow` and
  `sandbox-provisioning`, from a made-up original built on `ca0604a`'s
  history alone (none of Cloud-Sandbox's own commits). All seven did as
  promised; the carried commits kept their upstream author. That is the
  proof that a clone of the original, not of Cloud-Sandbox, gives the
  units' commit IDs.
- **Root `Justfile`:** `export-check source=`, `export-baselines`,
  `export-sync`, `sync-rehearse`.
- **Records:** MAP.md's new section "Syncing from the original", the
  parity watch in PLAN.md, REMINDERS.md, and stage 22, whose deletion
  waited for this.

## Out of scope

- Deleting the originals (stage 22).
- Running a sync against a real changed original: none exists yet. The
  first real one is a `SYNC-<n>` stage of its own.
- Carrying changes the other way, from a unit back to the original.
- Anything toward `ioos`: no remote, no push, no pull request. A clone of
  the original that you give me is read, never pushed from or to.

## Acceptance

- `export.py --source` works for every command, and every unit's copied
  files equal its baseline's plus its patches, read from the baseline
  commit.
- `just sync-rehearse` passes: each kind of change in item 4 is carried
  or reported as promised, into throw-away clones only.
- The root `just test` and `just full-test` pass, the rehearsal among
  them.
