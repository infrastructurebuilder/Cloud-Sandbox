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
on 2026-11-21, from one of those answers. The stage plans themselves, and the finished ones, are in the
[ATTIC](../ATTIC/), as history.

## In the order they are to be taken up

A spec's state is **in progress** until the six conditions of done in the
constitution (Development Workflow) all hold; **merged** once its branch is
merged but not all six hold yet; **complete**, with the date, when they do.

| # | Spec | What | Needs first | Size |
| ---: | --- | --- | --- | --- |
| 1 | [001](001-live-proof-on-aws/spec.md) | **The live proof on AWS**: a head node built by the playbooks, an image, and nothing left behind | nothing: it runs in the `noaa` account, in the existing IOOS VPC, creating only new resources (2026-11-21) | large: hours of a head node |
| 2 | [002](002-rhel10-build-cache/spec.md) | A build cache for RHEL 10, pushed by the collection, not by scripts | 001: a real build to push | medium |
| 3 | [003](003-lambda-functions-owner/spec.md) | The Lambda functions: an owner, tests, an OpenTofu module (a decision, then its work) | nothing | medium to large |
| 4 | [004](004-spack-stack-ufs-coastal/spec.md) | spack-stack for UFS Coastal, in place of the broken `add-ufs-setup.sh` | 001: a head node to build on | large |
| 5 | [005](005-configs-split-by-owner/spec.md) | `csis-sandbox-configs` split: examples and schema to cloudflow, the site's files kept | nothing | medium |
| 6 | [006](006-first-boot-runs-playbooks/spec.md) | The first boot runs the playbooks: `main.tf`'s values, the playbooks and cloudflow cloned from their own public repositories | cloudflow's repository made public | small |
| 7 | [007](007-private-playbooks-access/spec.md) | The first boot reads a private playbooks' repository, with a deploy key or a fine-grained token, if someone wants one | 006 | small |

The order is by what each needs first; where two need nothing of each
other, the smaller comes first. Spec 005 now needs spec 003 first, for its
`moved` directive.

## How a file moves between units

Specs 002, 004 and 005 each found that the files they would move belong to
one unit only. 002 and 004 leave theirs in `csis-sandbox-ops`, marked as
replaced; 005 moves cloudflow's examples with the `moved` mapping directive
that spec 003 designs, which keeps both units' lineage and a later sync.

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
