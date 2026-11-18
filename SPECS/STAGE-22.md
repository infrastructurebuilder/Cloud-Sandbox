# Stage 22: the real relocations

*Status:* **half done by moving day, 2026-11-17;** the rest, the deletion
of the original paths, **planned 2026-11-18** on `feature/deletion-plan`
at the operator's request, and not executed. It is executed on "do 22",
after each **YOUR DECISION** under [The decisions](#the-decisions) has
been asked, one at a time; with decision 1's default, each step after
that on its own `do 22.<n>`. Nothing is ever pushed to `ioos`.

Moving day carried out steps 1 to 3 of the plan of 2026-11-14 for every
unit (kept below, under [As planned on 2026-11-14](#as-planned-on-2026-11-14)):
each unit is a private repository on `infrastructurebuilder`, with its
history and its first tag, kept here as a submodule at its old path under
`exportit/` ([MOVINGDAY.md](../exportit/MOVINGDAY.md)). The deletion
waited for [stage 23](STAGE-23.md), which since 2026-11-18 lets a later
original reach the units without the originals here.

## Why

Cloud-Sandbox still carries all 802 files of the original, at
`ca0604a`, beside the fifteen units made from them. Every unit's repository
is now the place its files live; the originals here only duplicate what
the units hold, and keep this repository looking like the project it was
split from. The operator asked for them to go.

## What the deletion breaks, and what replaces it

Found by reading what in this repository reads an original path
(2026-11-18):

| Reads the originals here | Replaced by |
| --- | --- |
| `just export-check`, in `just test`: every copied file against the original in the working tree | `just export-baselines`, already in `just full-test`: every unit against its baseline, read from this repository's history, which keeps `ca0604a` after the deletion. It moves into `just test`, and `export-check` is kept for a given clone (`source=`) only |
| `just export-prove <unit>`, in `just full-test`: the extraction from this repository's HEAD | a **lineage check**: the original at the unit's baseline (this repository's history, or a given clone), filtered with the unit's directives, gives a commit that is in the unit's own history. That is what a sync depends on, and stays true when the unit changes its own files |
| [tools/configs_schema.py](../exportit/tools/configs_schema.py), which writes `sandbox-configs`' schema from `cloudflow/job/` and `cloudflow/cluster/` | the same code, read from the unit: `exportit/cloudflow/src/cloudflow/job/` and `.../cluster/` |
| [tools/tests/test_model_units.py](../exportit/tools/tests/test_model_units.py), which reads the launchers in `cloudflow/workflows/` against the install contract | the launchers in `exportit/cloudflow/src/cloudflow/workflows/` |
| The parity watch's step 2 ([PLAN.md](../PLAN.md)): `git merge origin/main` here. After the deletion, a merge of `main` would bring back every original `main` changes, and conflict on the rest | the sync alone: `just export-sync <unit> <clone of main> sync-<n>`, one unit at a time, as stage 23 built it. `main` is never merged into `develop` again |
| The shared constitution's principle S3: "a copied file is changed in Cloud-Sandbox" | amended by decision 5 |

Nothing in the units reads an original path in Cloud-Sandbox: each
unit's tests run in its own repository, as moving day proved. The 27
links from units' pages to MAP.md stay valid, because MAP.md stays.

What does not break, and why:

- **The units' histories.** Deleting files here makes new commits here;
  the units' repositories already hold their history.
- **A sync.** It reads a given clone of the original, never these files.
- **`main`.** It is the copy of the original that the parity watch reads,
  and is not touched: the deletion happens on `develop` only. Anyone who
  wants the original as it was reads `main`, or `ca0604a`.

## The steps

In MAP.md's order. Each step deletes its unit's original paths on a
branch, `feature/delete-<unit>`, together with whatever the table above
says must change at that step, and passes the root `just test` and
`just full-test` before it is merged.

| Step | Unit | Original paths deleted | Also at this step |
| ---: | --- | --- | --- |
| 0 | (none) | none | The replacements first: `export-baselines` into `just test`; the lineage check in place of `export-prove`; the parity watch rewritten. Nothing is deleted, so the old checks and the new ones both pass |
| 1 | `cloudflow` | `cloudflow/`, `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, the Miniforge guide; and `docs/`, whose sources cloudflow copied and whose built HTML its map drops (decision 3) | `configs_schema.py` and `test_model_units.py` read the unit |
| 2 | `model-common` | `models/modulefiles/`, `models/utils/`, `models/TODO`, the two notes | |
| 3 | the eight `model-<name>` | the rest of `models/`, `patches/` | |
| 4 | `sandbox-configs` | `job.configs/`, `cluster.configs/` | |
| 5 | `sandbox-provisioning` | its scripts under `scripts/` and `scripts/system/`, `jupyterhub/` | |
| 6 | `sandbox-terraform` | `terraform/` | |
| 7 | `sandbox-ops` | the rest of `scripts/` and `misc/` | |
| 8 | `cloud-sandbox`, the umbrella | `README.md`, `DEPLOYMENT.md`, the template, `TODO`, `images/`, `.github/`, and the originals of the attic | A new root `README.md` saying what Cloud-Sandbox now is (decision 4); principle S3 amended (decision 5) |

Kept at every step (decision 2): the root `.gitignore`, whose patterns
(`*.pem`, `*.key`, `*.tfstate`, `**/*nda*` and the rest) keep secrets out
of this repository too, and `LICENSE`.

Stage 20 (splitting `sandbox-configs`) and stage 21 (the first boot
running the playbooks) no longer come first: they change files in the
units' repositories, not the originals, and can be done before or after.

## The decisions

1. **YOUR DECISION (pace):** one step at a time, each on its own
   `do 22.<n>`, merged before the next begins (default: the stage's
   standing form, and each step is a deletion you can look at); or all
   nine steps on one branch, one commit each, merged together.

2. **YOUR DECISION (what stays):** the root `.gitignore` and `LICENSE`
   (default: the ignore patterns guard this repository, and the licence
   is the project's); or nothing of the original, each replaced by a file
   of this repository's own.

3. **YOUR DECISION (the files no unit took):** the maps drop
   `cloudflow/README.md`, the built HTML under `docs/` and the older copy
   of the documentation's sources in `docs/save/` on purpose, each with
   its reason. Deleted with their unit's step (default: history
   keeps them, and `main` has them); or kept here.

4. **YOUR DECISION (what Cloud-Sandbox is afterwards):** the workshop:
   the maps, the patches, the tools, the fifteen submodules, `SPECS/`,
   `PLAN.md` and the root `Justfile`, which is where syncs and
   cross-unit work happen, with a root `README.md` saying so (default);
   or archived on GitHub once the deletion is done, with syncs and
   cross-unit work moving to the umbrella's repository, which is a
   larger change and a stage of its own.

5. **YOUR DECISION (copied files after the deletion):** a unit may change
   its own copied files directly, in its own repository, once its
   originals are deleted here (default: that is what relocating it
   means). Its patches are already commits in its history; later
   changes from the original arrive by sync and are merged with the
   unit's own, and a conflict stops the sync for you to settle. The
   shared constitution's S3 becomes "a change from the original arrives
   by sync", at shared version 2.0.0 (a principle redefined), written
   out to the units of each step as it is taken. `export-baselines`
   then stops checking those units' copies, and the lineage check alone
   holds them to the original. Or: a copied file is still changed only
   by a patch in Cloud-Sandbox, applied to the unit by hand, and S3
   stays.

## Out of scope

- Changing `main`, or anything on `ioos`.
- Deleting any history: the originals stay in this repository's history
  and in `main`.
- Stages 20 and 21, and the live proof.

## Acceptance

- After step 8, `develop` holds no file of the original except those
  decision 2 keeps; `git ls-files` outside `exportit/` lists only this
  repository's own files.
- The root `just test` and `just full-test` pass after every step, with
  `export-baselines` and the lineage check in place of `export-check`
  and `export-prove`.
- `just sync-rehearse` still passes after step 8: a later original can
  reach every unit.
- `main` is unchanged.

---

## As planned on 2026-11-14

Planned on `feature/remaining-plans`; stage 19 decided to relocate on
2026-11-17. Steps 1 to 3 of "each step" were then carried out for every
unit on moving day, in another order than the one below, because nothing
was deleted; its two decisions were asked there (names `csis-<unit>`
except `cloudflow`, private for all; git-flow in each).

| Step | Unit | Needs first |
| ---: | --- | --- |
| 1 | `cloudflow` | nothing |
| 2 | `model-common` | nothing |
| 3 | the eight `model-<name>` units | step 2 (ADCIRC only) |
| 4 | `sandbox-configs` (split by stage 20) | step 1 |
| 5 | `sandbox-provisioning` | the collection (already in its own repository) |
| 6 | `sandbox-terraform`, with stage 21's change filled in | step 5 |
| 7 | `sandbox-ops` | step 5 |
| 8 | `cloud-sandbox`, the umbrella | every step before it |

Each step:

1. `just export-filter <unit>` on a fresh clone of Cloud-Sandbox, as the
   rehearsal does, giving the unit's files at their paths in the unit
   with their history.
2. The unit's own `just test` and `just full-test` in the extracted
   repository, where the copy's tests and the unit's are now the same.
3. A new repository on `infrastructurebuilder`, created by the operator
   or with the operator's approval, private or public as decided; the
   extracted history pushed to it; a first tag, the version in
   `units.toml`.
4. In Cloud-Sandbox, on a branch: the unit's original paths deleted;
   anything that referred to them (MAP.md lists each) pointed at the new
   repository; `units.toml` given the repository's URL. Merged only when
   the step is accepted. **This is what is left, planned above.**
