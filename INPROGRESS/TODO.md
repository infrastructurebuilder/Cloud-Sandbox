# TODO

Staged work for taking Cloud-Sandbox apart into independent units.
Start with [ANALYSIS.md](ANALYSIS.md).

A stage is a plan first. Its file is written, the operator validates
it, and it is executed only on an explicit "do N". At "do N" every
**YOUR DECISION** in the file is asked, one question at a time, before
any work starts.

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
  [stage 2](STAGE-2.md).
- **Copies are byte-identical to their originals.** A correction is a
  patch beside the unit's mapping file, never an edit to the copy.

## Open

| Stage | Unit | State |
| ---: | --- | --- |
| [1](STAGE-1.md) | Analysis and plan | Merged into `develop` 2026-11-12 |
| [2](STAGE-2.md) | `cloudflow` and `cloudflow-plotting` (plotting folded back into cloudflow 2026-11-13) | Merged into `develop` 2026-11-12 |
| [3](STAGE-3.md) | `sandbox-provisioning` (Ansible) | Merged into `develop` 2026-11-12; live proof not run |
| [4](STAGE-4.md) | `sandbox-terraform` | Merged into `develop` 2026-11-12 |
| [5](STAGE-5.md) | `model-*` (eight models) and `model-common` | Merged into `develop` 2026-11-12 |
| [6](STAGE-6.md) | `sandbox-configs` | Merged into `develop` 2026-11-12 |
| [7](STAGE-7.md) | `sandbox-ops`, and two roles in `sandbox-provisioning` | Merged into `develop` 2026-11-12 |
| [8](STAGE-8.md) | Documentation and the umbrella | Merged into `develop` 2026-11-12 |
| [9](STAGE-9.md) | `spack.yaml` from a template; the `csis_spack` collection begun | Merged into `develop` 2026-11-13 |
| [10](STAGE-10.md) | `spack_environment` through the `csis_spack` collection | Merged into `develop` 2026-11-14 |
| [11](STAGE-11.md) | Spack set up through the `csis_spack` collection at 0.3.0 (the collection's stage 3) | Merged into `develop` 2026-11-14 |
| [12](STAGE-12.md) | The live proof on AWS | Planned 2026-11-14 |

## Landed

All eight stages, squash-merged into `develop` on 2026-11-12, one commit
each; their feature branches are kept. Nothing has been relocated: see
[exportit/MAP.md](../exportit/MAP.md#the-order-of-the-real-relocations).
