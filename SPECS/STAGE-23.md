# Stage 23: syncing from the original after its paths are deleted

*Status:* planned 2026-11-18 on `feature/upstream-sync-plan`, at the
operator's request; nothing executed. It is executed on "do 23", after
each **YOUR DECISION** below has been asked, one at a time. It comes
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
