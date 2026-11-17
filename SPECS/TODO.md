# TODO

Staged work for taking Cloud-Sandbox apart into independent units.
Start with [ANALYSIS.md](ANALYSIS.md).

A stage is a plan first. Its file is written, the operator validates
it, and it is executed only on an explicit "do N". At "do N" every
**YOUR DECISION** in the file is asked, one question at a time, before
any work starts.

The plans of the stages still to do are in this directory. A stage
merged into `develop` moves to [COMPLETED/](COMPLETED/); a plan the
operator sets aside moves to [ATTIC/](ATTIC/). (Until 2026-11-15 this
directory was `INPROGRESS/`.)

## Standing decisions

- **Nothing leaves this repository.** A unit is relocated by copying
  it into [exportit/](../exportit/) and describing the real relocation
  in [exportit/MAP.md](../exportit/MAP.md). The original paths stay
  untouched.
- **Never push to `ioos/Cloud-Sandbox`**, and never open a pull
  request against it.
- **One feature branch per stage**, squash-merged into `develop`. The
  feature branch is kept, never deleted.
- **Commits are local.** Nothing is pushed, and nothing is merged into
  `develop`, until the operator says so.
- **`just test` is the acceptance bar**, and `just full-test` before
  a stage is called done. The repository's `Justfile` arrived with
  [stage 2](COMPLETED/STAGE-2.md).
- **Copies are byte-identical to their originals.** A correction is a
  patch beside the unit's mapping file, never an edit to the copy.

## Open

| Stage | Unit | State |
| ---: | --- | --- |
| [1](COMPLETED/STAGE-1.md) | Analysis and plan | Merged into `develop` 2026-11-12 |
| [2](COMPLETED/STAGE-2.md) | `cloudflow` and `cloudflow-plotting` (plotting folded back into cloudflow 2026-11-13) | Merged into `develop` 2026-11-12 |
| [3](COMPLETED/STAGE-3.md) | `sandbox-provisioning` (Ansible) | Merged into `develop` 2026-11-12; live proof not run |
| [4](COMPLETED/STAGE-4.md) | `sandbox-terraform` | Merged into `develop` 2026-11-12 |
| [5](COMPLETED/STAGE-5.md) | `model-*` (eight models) and `model-common` | Merged into `develop` 2026-11-12 |
| [6](COMPLETED/STAGE-6.md) | `sandbox-configs` | Merged into `develop` 2026-11-12 |
| [7](COMPLETED/STAGE-7.md) | `sandbox-ops`, and two roles in `sandbox-provisioning` | Merged into `develop` 2026-11-12 |
| [8](COMPLETED/STAGE-8.md) | Documentation and the umbrella | Merged into `develop` 2026-11-12 |
| [9](COMPLETED/STAGE-9.md) | `spack.yaml` from a template; the `csis_spack` collection begun | Merged into `develop` 2026-11-13 |
| [10](COMPLETED/STAGE-10.md) | `spack_environment` through the `csis_spack` collection | Merged into `develop` 2026-11-14 |
| [11](COMPLETED/STAGE-11.md) | Spack set up through the `csis_spack` collection at 0.3.0 (the collection's stage 3) | Merged into `develop` 2026-11-14 |
| [12](COMPLETED/STAGE-12.md) | The old Spack settings in the login user's scope | Merged into `develop` 2026-11-14 |
| [13](COMPLETED/STAGE-13.md) | JupyterHub, decided | Merged into `develop` 2026-11-15 |
| [14](ATTIC/STAGE-14.md) | Clearing old model output on a timer | Set aside 2026-11-15 by the operator; the plan is in `ATTIC/` |
| [15](STAGE-15.md) | The live proof on AWS | Planned 2026-11-14 |
| [16](STAGE-16.md) | A build cache for RHEL 10, pushed by the collection | Planned 2026-11-14 |
| [17](STAGE-17.md) | The Lambda functions, owned | Planned 2026-11-14 |
| [18](STAGE-18.md) | spack-stack for UFS Coastal | Planned 2026-11-14 |
| [19](STAGE-19.md) | Relocate, or not | Planned 2026-11-14 |
| [20](STAGE-20.md) | `sandbox-configs` split by owner | Planned 2026-11-14; only if 19 relocates it |
| [21](STAGE-21.md) | The first boot runs the playbooks | Planned 2026-11-14; only if 19 relocates |
| [22](STAGE-22.md) | The real relocations | Planned 2026-11-14; only if 19 relocates |

The order of the work is in [PLAN.md](../PLAN.md), with the collection's
stages 4 and 5 among these.

Beside the stages: [moving day](../exportit/MOVINGDAY.md), planned
2026-11-17 at the operator's request. It gives each unit a private
repository and keeps it here as a submodule, which decides stage 19
ahead of its turn and leaves stage 22 only the deletion of the original
paths. Until it is executed, the standing decision "nothing leaves this
repository" above still describes what is true.

## Landed

All eight stages, squash-merged into `develop` on 2026-11-12, one commit
each; their feature branches are kept. Nothing has been relocated: see
[exportit/MAP.md](../exportit/MAP.md#the-order-of-the-real-relocations).
