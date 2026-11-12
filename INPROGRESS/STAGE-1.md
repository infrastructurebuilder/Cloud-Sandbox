# Stage 1: analysis and reconstruction plan

*Status:* executed 2026-11-12 on `feature/stage-1-analysis`; committed
locally, not pushed, not merged. Waits for the operator's validation.

## Why

Cloud-Sandbox is to be taken apart into units that can each live in
their own repository. Before anything moves, there has to be a record
of what is in the repository, what ties the parts together, and an
agreed order of work.

## What this stage produces

- [ANALYSIS.md](ANALYSIS.md): the inventory, the couplings, the
  step-by-step reading of `setup-instance.sh`, and the defects
  noticed on the way.
- One plan per unit: [stage 2](STAGE-2.md) to [stage 8](STAGE-8.md).
- [TODO.md](TODO.md): the open list and the standing decisions.
- A section in [PLAN.md](../PLAN.md) that points here.
- A first [exportit/MAP.md](../exportit/MAP.md): every tracked path
  assigned to a unit, and the relocation method. Each later stage
  fills in its own section when it copies its unit.

## Decisions taken

Asked on 2026-11-12, before any file was written.

- **How far to go now:** write the plans, then execute
  [stage 2](STAGE-2.md) (cloudflow). Every other stage waits for an
  explicit "do N".
- **Where plans live:** this folder. `TODO.md` moved here; one
  `STAGE-<n>.md` per stage; `PLAN.md` keeps a pointer.
- **Commits:** local commits on the stage's feature branch. No push,
  and no merge into `develop`, until the operator says so.

Standing instructions given with the request: the feature branch is
never removed, and nothing is ever pushed to `ioos/Cloud-Sandbox`.

## Out of scope

No file outside `INPROGRESS/`, `PLAN.md` and `exportit/MAP.md` is
created or changed. Nothing is copied and no playbook is written.

## Acceptance

- Every tracked top-level path appears in the inventory of
  [ANALYSIS.md](ANALYSIS.md) and in the unit table of
  [exportit/MAP.md](../exportit/MAP.md).
- `git status` shows changes only under `INPROGRESS/`, `exportit/`
  and `PLAN.md`.
- There is no `Justfile` yet, so there is no `just test` to run for
  this stage. It changes documents only. [Stage 2](STAGE-2.md) adds
  the `Justfile`.

## Records

Branch `feature/stage-1-analysis`, cut from `develop` at `ca0604a`.
