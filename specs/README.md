# Specs

The work in Cloud-Sandbox that spans units is planned here, with Spec Kit,
one directory per spec: `spec.md` (what and why), and, once it is taken up,
`plan.md` (how) and `tasks.md` (the steps). The rules every spec is held to
are in the [constitution](../.specify/memory/constitution.md). Work inside a
single unit is planned in that unit's own `specs/`.

Specs 001 to 006 were carried on 2026-11-19 from the stage plans that were
open then (stages 15, 16, 17, 18, 20 and 21). Each is a Draft: the stage's
open questions are its `[NEEDS CLARIFICATION]` markers, each with the
stage's default, to be asked with `/speckit-clarify` when the spec is taken
up. The stage plans themselves, and the finished ones, are in the
[ATTIC](../ATTIC/), as history.

## In the order they are to be taken up

| # | Spec | What | Needs first | Size |
| ---: | --- | --- | --- | --- |
| 1 | [001](001-live-proof-on-aws/spec.md) | **The live proof on AWS**: a head node built by the playbooks, an image, and nothing left behind | **an AWS account that can create a network** (the `noaa` profile cannot) | large: hours of a head node |
| 2 | [002](002-rhel10-build-cache/spec.md) | A build cache for RHEL 10, pushed by the collection, not by scripts | 001: a real build to push | medium |
| 3 | [003](003-lambda-functions-owner/spec.md) | The Lambda functions: an owner, tests, an OpenTofu module (a decision, then its work) | nothing | medium to large |
| 4 | [004](004-spack-stack-ufs-coastal/spec.md) | spack-stack for UFS Coastal, in place of the broken `add-ufs-setup.sh` | 001: a head node to build on | large |
| 5 | [005](005-configs-split-by-owner/spec.md) | `csis-sandbox-configs` split: examples and schema to cloudflow, the site's files kept | nothing | medium |
| 6 | [006](006-first-boot-runs-playbooks/spec.md) | The first boot runs the playbooks: `main.tf`'s two values, and how the node reaches a private repository | nothing | small |

The order is by what each needs first; where two need nothing of each
other, the smaller comes first. While 001 waits for an account, 003, 005
and 006 can be taken up.

## A question four of them share

Specs 002, 003, 004 and 005 each move files from one unit to another (push
scripts out of `csis-sandbox-ops`, the Lambda functions out of cloudflow,
the examples out of `csis-sandbox-configs`). Every unit is held to the
original by its lineage: the original at its baseline, filtered with its
mapping file, must be a commit of the unit's history, which is what a sync
from a later original depends on. Moving a file changes two mapping files,
and with them both units' filtered histories. How a file moves without
breaking either unit's lineage, or a later sync, is not settled; each of
those specs carries it as a `[NEEDS CLARIFICATION]`. It may want a spec of
its own, taken up before the first of them.

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
