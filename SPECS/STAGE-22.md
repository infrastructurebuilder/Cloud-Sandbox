# Stage 22: the real relocations

*Status:* **half done by moving day, 2026-11-17.** Steps 1 to 3 of
"each step" were carried out for every unit, in another order than the
one below, because nothing was deleted: each unit is a private
repository on `infrastructurebuilder` (`csis-<unit>`, `cloudflow` under
its own name), pushed with its history and first tag, and kept in
Cloud-Sandbox as a submodule at its old path under `exportit/`
([MOVINGDAY.md](../exportit/MOVINGDAY.md)). Its two decisions were asked
there: names as above, private for all; git-flow in each. **What is left
is item 4 of each step: deleting the unit's original paths**, in the
order of the table, with what that breaks. Planned 2026-11-14 on
`feature/remaining-plans`; stage 19 decided to relocate on 2026-11-17. Last in the order of the remaining
work ([PLAN.md](../PLAN.md)). It is executed one step at a time, each on
"do 22.<n>", after that step's **YOUR DECISION**s, and nothing is ever
pushed to `ioos`.

## Why

Everything before this proves the units in place. This moves them: each
unit gets a repository of its own, with its history, and Cloud-Sandbox
becomes the umbrella that names them and their versions. The method is
in [MAP.md](../exportit/MAP.md#how-a-unit-would-really-be-relocated);
every unit's extraction has been rehearsed by `just full-test` on
throw-away clones since stage 2.

## The steps, in MAP.md's order

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
   the step is accepted.

**YOUR DECISION (for every step, asked at its "do"):** the repository's
name (default: the unit's name), and whether it is private or public
(default: as Cloud-Sandbox's fork is).

**YOUR DECISION (once, at step 1):** whether the relocated repositories
keep git-flow (`main`, `develop`, feature branches, squash merges, kept
branches) as this repository does (default), or start with `main` alone.

## What this stage does not do

Push anything to `ioos/Cloud-Sandbox`, open a pull request there, or add
a remote toward it. If IOOS is to receive any of this, that is the
operator's to arrange, outside this work.

## Acceptance

Each relocated unit passes its own `just full-test` in its own
repository, with its history; Cloud-Sandbox's root `just test` passes
after each step; after step 8, Cloud-Sandbox holds the umbrella and
nothing else, and `units.toml` names every repository at a tag.
