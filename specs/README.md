# Specs

The work in Cloud-Sandbox that spans units is planned here, with Spec Kit,
one directory per spec: `spec.md` (what and why), and, once it is taken up,
`plan.md` (how) and `tasks.md` (the steps). The rules every spec is held to
are in the [constitution](../.specify/memory/constitution.md). Work inside a
single unit is planned in that unit's own `specs/`.

Specs 001 to 006 were carried on 2026-11-19 from the stage plans that were
open then (stages 15, 16, 17, 18, 20 and 21), each a Draft whose open
questions were its `[NEEDS CLARIFICATION]` markers. All of them were answered
with `/speckit-clarify`, spec 003's on 2026-11-20 and the rest on 2026-11-21;
each spec's Clarifications section records the answers. Spec 007 was written
on 2026-11-21, from one of those answers. Every spec was then planned
(`plan.md` and its design documents) and tasked (`tasks.md`), on its own
branch, by 2026-11-22. The stage plans themselves, and the finished ones,
are in the [ATTIC](../ATTIC/), as history.

## In the order they are to be built

A spec's state is **in progress** until the six conditions of done in the
constitution (Development Workflow) all hold; **merged** once its branch is
merged but not all six hold yet; **complete**, with the date, when they do.
Every spec below is planned and tasked and none is started, so every one is
**in progress**.

| # | Spec | What | Needs first | Branch | Tasks | AWS |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | [003](003-lambda-functions-owner/spec.md) | The Lambda functions: an owner, tests, an OpenTofu module, and the `moved` directive. **Complete**, 2026-11-22 | nothing | `feature/lambda-functions-owner` | 40 | none: nothing applied |
| 2 | [006](006-first-boot-runs-playbooks/spec.md) | The first boot runs the playbooks: four required values, the playbooks and cloudflow cloned from their own public repositories. **Complete**, 2026-11-22 | nothing | `feature/first-boot-runs-playbooks` | 28 | none: proved by a mocked plan |
| 3 | [005](005-configs-split-by-owner/spec.md) | `csis-sandbox-configs` split: the 23 unreadable repaired or retired, then 51 examples and the schema to cloudflow. **Complete**, 2026-11-23 | 003 (`moved`) | `feature/configs-split-by-owner` | 44 | none |
| 4 | [001](001-live-proof-on-aws/spec.md) | **The live proof on AWS**: a head node built by 006's first boot, an image, and nothing left behind. **Complete**, 2026-11-24 (run 2026-11-23; [outcome](001-live-proof-on-aws/spec.md#outcome)) | 006 (its first boot) | `feature/live-proof` | 47 | **yes**: a head node in `noaa`, us-east-2, for an afternoon; all of it removed |
| 5 | [002](002-rhel10-build-cache/spec.md) | A build cache for RHEL 10 in a bucket of its own, pushed by a playbook. **Complete**, 2026-11-25 ([outcome](002-rhel10-build-cache/spec.md#outcome)): the bucket made and kept, 24 packages pushed with a new key, and the defaults install from it since `csis-sandbox-provisioning` 0.0.4 | 001 (`proof/`, the procedure) | `feature/rhel10-build-cache` | 44 | **yes**: a bucket that stays, and a head node |
| 6 | [004](004-spack-stack-ufs-coastal/spec.md) | spack-stack for UFS Coastal, in place of the broken `add-ufs-setup.sh` | 001 (`proof/`); 002 (the catalogue's `superseded_by` rule) | `feature/spack-stack-ufs-coastal` | 40 | **yes**: a head node of its own |
| 7 | [007](007-private-playbooks-access/spec.md) | The first boot reads a private playbooks' repository, with a deploy key or a fine-grained token | 006 | `feature/private-playbooks-access` | 30 | only for its last proof, when someone wants a private repository |
| 8 | [008](008-site-configs-at-first-boot/spec.md) | The first boot puts the site's private descriptions (`csis-sandbox-configs`) on the head node, with spec 007's credential | 006, 007 | `feature/site-configs-at-first-boot` | 47 | for its proof, a head node |
| 9 | [009](009-collection-from-mirrors/spec.md) | The playbooks take the collection's 0.0.3 and its `from_mirrors` again, in place of spec 002's `command` workaround | 002 (merged first) | `feature/collection-from-mirrors` | (not yet tasked) | for its proof, a head node |

**Why this order:**

1. **003 first**: it needs nothing, and 005 needs its `moved` directive.
2. **006 next**: it is small, needs nothing, and 001's head node boots with
   it, which is also its first real use.
3. **005 before 001**: both can go after their dependency; 005 touches no
   account and is the smaller, so it does not wait on an AWS session.
4. **001**: the first AWS work, once 006 is merged; its `proof/` files and
   procedure are what 002 and 004 build their head nodes with.
5. **002, then 004**: each builds a head node as 001 does; 004 also uses the
   catalogue rule 002 adds to `csis-sandbox-ops`. If spec 002's cache is in
   place by 004, the sandbox's own build on 004's node is shorter.
6. **007 last**: nothing needs it while the playbooks' repository is public;
   its code can be built any time after 006, its AWS proof when a private
   repository is wanted.

Specs 001, 002 and 004 each run a head node of 32 processors (about $1.36
an hour for a `c6i.8xlarge`), every AWS step on the operator's word, and
remove what they made at their end (002's bucket stays). On 001's run the
first boot took 34 minutes; the node's hours were mostly spent waiting for
answers and fixes.

## How a file moves between units

Specs 002, 004 and 005 each found that the files they would move belong to
one unit only. 002 and 004 leave theirs in `csis-sandbox-ops`, marked as
replaced; 005 moves cloudflow's examples with the `moved` mapping directive
that spec 003 built ([its contract](003-lambda-functions-owner/contracts/moved-directive.md)),
which keeps both units' lineage and carries a later sync's changes to a
moved file where it went.

Before any of those moves, each spec asks whether both units need the file
(constitution 1.1.0, principle I): a file more than one unit needs lives in
one place, a common unit such as `csis-model-common`, or a single source in
this repository written into each unit and checked, as the units' shared
constitution, `CLAUDE.md` and `LICENSE` are. Only a file that belongs to one
unit moves.

## Standing beside them

- **The parity watch on `main`** (the constitution's principle II): when
  `origin/main` has moved past the units' baselines (`ca0604a`), the sync is
  planned as a spec here and carried with `just export-sync`. On 2026-11-19
  it had not moved.
- **The collection** `infrastructurebuilder.csis_spack` plans its own work
  in its own repository; the sandbox installs it from Ansible Galaxy.

## Done before Spec Kit

Stages 1 to 13, 19, 22 and 23 (2026-11-12 to 2026-11-19): the analysis, the
copies of every unit, their translation and tests, moving day (each unit a
private repository and a submodule here), syncing from the original, and the
deletion of the originals. Stage 14 (clearing old model output on a timer)
was set aside on 2026-11-15. Their plans and outcomes are in
`ATTIC/SPECS/`, and their record, unit by unit, is
[exportit/MAP.md](../exportit/MAP.md).
