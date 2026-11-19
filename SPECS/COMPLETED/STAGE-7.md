# Stage 7: operator utilities as an independent unit

*Status:* executed and merged into `develop` 2026-11-12. The decisions are
under [Decisions taken](#decisions-taken); the result under
[Outcome](#outcome).

## Why

[scripts/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts) holds more than provisioning. Once the setup
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
  spack-stack equivalents, and [misc/spack/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/misc/spack).
- **Data scrubbing:** `scrub_nosofs.sh`, `scrub_liveocean.sh`.
- **Instance helpers:** `change-instance-type.sh`, `disableHT.sh`,
  `mountEFS.sh`, `update_efs_driver.sh`, `newamised.sh`, `getaws.sh`.
- **Reporting:** `weekly_summary.nu`, which reads the DynamoDB table
  of C8.
- **JupyterHub:** two install scripts, five files under
  `scripts/system/`, and [jupyterhub/README.md\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/jupyterhub/README.md).
- **Slurm leftovers:** unit files and notes under `scripts/system/`,
  `scripts/archived/` and [misc/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/misc).
- **Other stacks:** the UFS, spack-stack and `ncdis` entry scripts.
- **Notes and one-offs** in [misc/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/misc).

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
5. The ops section of [MAP.md](../../exportit/MAP.md).

## Decisions taken

1. **Users and JupyterHub:** Ansible roles in `sandbox-provisioning`,
   `sandbox_users` and `jupyterhub`, each with its own playbook.
2. **Dead files:** *(changed by the operator on 2026-11-13: the attic
   does not travel with the code; it stays with the original
   repository, as `attic/` of the umbrella `cloud-sandbox`; see
   [MAP.md](../../exportit/MAP.md#the-attic-stays-with-the-original-repository).)*
   copied into `attic/` of the export, under their
   status and original path.
3. **Conda for JupyterHub** (surfaced by the container test, where the
   script's Miniconda 23.1 had not solved the conda-forge install after
   25 minutes): Miniforge, conda-forge only.

## Out of scope

Rewriting any tool. The other stacks stay scripts.

## Acceptance

`just test` passes at the root and in the export; with stage 3's
mapping, the copy check covers every tracked file under `scripts/`,
`misc/` and `jupyterhub/`.

## Sizing and branch

About 100 files read and sorted. Branch `feature/stage-7-ops`.

## Outcome

- Item 1: all 108 files read and marked with evidence: 21 in use, 28
  superseded, 59 dead (the reading was delegated to a subagent and
  spot-checked). The catalogue in
  [exportit/sandbox-ops/CATALOGUE.tsv](../../exportit/sandbox-ops/CATALOGUE.tsv)
  keeps it for the 92 files copied there.
- Item 2: `users.yml` with role `sandbox_users`, and `jupyterhub.yml`
  with role `jupyterhub`, in
  [sandbox-provisioning](../../exportit/sandbox-provisioning/README.md):
  16 files moved there (the originals into `legacy/`, two as role
  files). Traceability and parity tests cover them; the container test
  applies both twice and removes its test user.
- Items 3 and 4: [exportit/sandbox-ops/](../../exportit/sandbox-ops/README.md),
  92 files byte-identical: 16 tools in `bin/` and `keys/`, 26
  superseded and 50 dead in `attic/`. Tests: the catalogue matches the
  files; 50 scripts parse except one recorded; 559 shellcheck findings
  recorded.
- Item 5: [MAP.md](../../exportit/MAP.md#sandbox-ops).
- Root `just full-test` passed: the container applies all of `site.yml`'s
  testable roles, `users.yml` and `jupyterhub.yml` twice with nothing
  changed the second time, the hub answers, the test user is removed;
  every unit's extraction gives its files.
- Found: nothing installed JupyterHub before (both scripts were broken);
  `scrub_liveocean.sh` does not parse; `add-ufs-setup.sh` calls a
  function that no longer exists; personal data in a few files.

---

\* A link marked with an asterisk opens the file or directory as it was at
commit [`ca0604a`](https://github.com/infrastructurebuilder/Cloud-Sandbox/commit/ca0604a4a27355b330353c7ded8a1ae00a7e24a6)
of this repository: the original project, from which every unit was made,
and every unit's baseline. These files are no longer on `develop`, because
[stage 22](STAGE-22.md) deleted the originals on 2026-11-19 once
each unit owned its copies.
