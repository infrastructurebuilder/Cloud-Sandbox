# Stage 7: operator utilities as an independent unit

*Status:* planned 2026-11-12. Waits for validation and "do 7".
After [stage 3](STAGE-3.md), which decides what provisioning takes.

## Why

[scripts/](../scripts/) holds more than provisioning. Once the setup
path has gone to Ansible, what is left is a set of unrelated operator
tools, some current and some dead. They need sorting before they can
be moved, and some of them are better as an Ansible role than as a
script.

## What exists

The part of the 93 files under `scripts/` that
[stage 3](STAGE-3.md) does not take, in these groups:

- **Users:** `add-users.py`, `add_group.sh`, `remove-user.sh`,
  `test_user.sh`, the sample user list and three `sudoers` files.
- **Spack mirror upkeep:** `spack-mirror-create.sh`,
  `spack-update-mirror.sh`, `spack-pubkey.sh`, `scp-secret.sh`, the
  spack-stack equivalents, and [misc/spack/](../misc/spack/).
- **Data scrubbing:** `scrub_nosofs.sh`, `scrub_liveocean.sh`.
- **Instance helpers:** `change-instance-type.sh`, `disableHT.sh`,
  `mountEFS.sh`, `update_efs_driver.sh`, `newamised.sh`, `getaws.sh`.
- **Reporting:** `weekly_summary.nu`, which reads the DynamoDB table
  of C8.
- **JupyterHub:** two install scripts, five files under
  `scripts/system/`, and [jupyterhub/README.md](../jupyterhub/README.md).
- **Slurm leftovers:** unit files and notes under `scripts/system/`,
  `scripts/archived/` and [misc/](../misc/).
- **Other stacks:** the UFS, spack-stack and `ncdis` entry scripts.
- **Notes and one-offs** in [misc/](../misc/).

## Items

1. Read every file and mark it: in use, superseded, or dead, with the
   evidence (who calls it, what it refers to that no longer exists).
2. **YOUR DECISION (users and JupyterHub):** make them Ansible roles
   in `sandbox-provisioning` (default), or keep them as scripts in
   this unit.
3. **YOUR DECISION (dead files):** copy them into an `attic/`
   directory of the export so the map accounts for every file
   (default), or list them in the map as "not relocated".
4. Copy the rest to `exportit/sandbox-ops/` through a mapping file,
   with `README.md`, `LICENSE` and a `Justfile` (`test` =
   `shellcheck` and `bash -n`, under the same rule as
   [stage 5](STAGE-5.md)).
5. The ops section of [MAP.md](../exportit/MAP.md).

## Out of scope

Rewriting any tool. The other stacks stay scripts.

## Acceptance

`just test` passes at the root and in the export; with stage 3's
mapping, the copy check covers every tracked file under `scripts/`,
`misc/` and `jupyterhub/`.

## Sizing and branch

About 100 files read and sorted. Branch `feature/stage-7-ops`.
