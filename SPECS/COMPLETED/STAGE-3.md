# Stage 3: head-node provisioning as Ansible playbooks

*Status:* executed on `feature/stage-3-ansible` and merged into `develop`
2026-11-12.
The decisions are under [Decisions taken](#decisions-taken); the
result is under [Outcome](#outcome).

## Why

[scripts/setup-instance.sh](../../scripts/setup-instance.sh) builds the
whole software stack in one pass of shell functions. It cannot be run
twice, cannot be run in part without editing a copy of it (nine
sibling scripts are such copies), does not stop when a step fails, and
is fetched by cloning the monorepo (C5, C10, F6 to F10 in
[ANALYSIS.md](../ANALYSIS.md)). The operator asked for a way to do the
same work as Ansible playbooks that are applied.

## What exists

The table "setup-instance.sh, step by step" in
[ANALYSIS.md](../ANALYSIS.md#setup-instancesh-step-by-step) lists the
13 functions and the image step, where each one's result lands (root
volume, EFS or a home directory) and whether it survives a second run.
The versions are in
[environment-vars.sh](../../scripts/environment-vars.sh); the files that
get installed are under [scripts/system/](../../scripts/system/). The
steps that come before it (EFS client, mount, `/save`, the clone) are
in [terraform/init_template.tpl](../../terraform/init_template.tpl).

## The proposal

**One role per function, one playbook, applied by the node to
itself.**

- `exportit/sandbox-provisioning/` holds `site.yml`,
  `node-image.yml`, `roles/`, `group_vars/all.yml`, two inventories,
  `requirements.yml` and a `Justfile`.
- `group_vars/all.yml` is `environment-vars.sh` as data: every version
  and every site name (mirror bucket, project tag, prompt) becomes a
  variable, with today's values as defaults.
- Each function becomes a role, applied in the script's order:
  `sandbox_paths`, `user_shell`, `base_system`, `prefect_server`,
  `mpi_ssh`, `efa_driver`, `fsx_lustre_client`, `python_user_env`,
  `spack`, `intel_oneapi`, `spack_environment` (the two
  Spack-environment functions together) and `hpc_tuning`. The files in
  `scripts/system/` that a function installs become that role's
  `files/` or `templates/`.
- Every role carries a tag. The sibling scripts stop being copies:
  `update-efa.sh` becomes `--tags efa_driver`, `setup-python-deps.sh`
  becomes `--tags python_user_env`, and so on.
- Shell that cannot be repeated is replaced by modules that can:
  `user` and `group` for the Prefect account, `file` for the
  directories, a drop-in under `/etc/ssh/ssh_config.d/` for the host
  rules, `creates:` guards and `spack` queries around the Spack
  commands.
- The play becomes root once instead of calling `sudo` per command
  (the script notes that each `sudo` costs 25 seconds under
  cloud-init), turns SELinux enforcement off at the start and back on
  in an `always` section, and stops at the first failed task.
- Image creation is its own playbook, `node-image.yml`, so that
  re-applying the stack does not register a new image each time.

**How it is applied.** The first-boot template shrinks to: install
the EFS client, mount, install `ansible-core`, then
`ansible-pull -U <provisioning repository> -C <version> site.yml`
with the values Terraform already passes (`ami_name`, project tag,
region). `ansible-pull` clones the playbooks and runs them against the
local machine, which is what the clone-and-run lines do today, without
the monorepo. The same `site.yml` also runs from an operator's machine
against a running head node, through a second inventory that finds
the node by its project tag; that is the route for later changes.

## Items

1. The skeleton, `group_vars/all.yml` and the two inventories.

   **YOUR DECISION (how it is applied):** `ansible-pull` at first
   boot, with push from an operator's machine for later changes
   (default); push only; or baking images ahead of time with Packer.
2. The twelve roles, in the order above, each translated from its
   function.

   **YOUR DECISION (fidelity):** same packages, versions and order as
   the script, changing only what is needed for a second run to be
   safe, and writing down every place where the script's behaviour
   was an accident (default); or also correct the defects F6 to F10
   now.

   **YOUR DECISION (kernel updates):** keep today's behaviour, where
   `dnf update` may install a new kernel and the EFA driver is then
   built without a reboot (default), or reboot and resume when the
   kernel changed.

   **YOUR DECISION (user Python packages):** keep installing the same
   pip list for the login user (default), or install the cloudflow
   project from [stage 2](STAGE-2.md) and let it bring its own
   dependencies.
3. `node-image.yml`.

   **YOUR DECISION (image creation):** run the existing
   [create_image.py](../../scripts/create_image.py) from a task, passing
   the region it currently ignores (default), or rewrite it with the
   `amazon.aws` modules.
4. The `Justfile`: `test` runs `ansible-playbook --syntax-check`,
   `ansible-lint` and a check that every variable in
   `environment-vars.sh` has a counterpart in `group_vars/all.yml`.

   **YOUR DECISION (proof):** no AWS run in this stage; `full-test`
   applies the roles that need no kernel, EFS or AWS to a RHEL-10
   compatible container and the stage writes the live proof as a
   procedure for the operator to run when they choose (default); or
   one live run on a real instance as part of the stage, which costs
   several hours of an EC2 instance.
5. The provisioning section of [MAP.md](../../exportit/MAP.md): function
   to role, variable to variable, file to file, and the new first-boot
   template.

## Decisions taken

Asked one at a time on 2026-11-12, before execution.

1. **How it is applied:** `ansible-pull` at first boot; the same
   playbook pushed from an operator's machine for later changes.
2. **Fidelity:** faithful. Same packages, versions and order; only
   what a safe second run needs is changed; every accident of the
   script is kept and written down.
3. **Kernel updates:** today's behaviour. No reboot; the play says so
   when the running kernel is not the newest installed.
4. **User Python packages:** the same pip list as the script.
5. **Image creation:** rewritten with the `amazon.aws` modules. This
   is the one place where the mechanism is new and not a translation.
6. **Proof:** static checks in `just test`; a container apply, twice,
   in `just full-test`; a written procedure for the live run, which
   the operator runs when they choose.

Asked when it surfaced, during execution:

7. **The Prefect server:** the script's install no longer gives a
   working server (FastAPI too new). Pin `fastapi<0.155` by default;
   the one deliberate departure from the script.

## Out of scope

- The other stacks (`ufs-setup-instance.sh`, spack-stack, `ncdis`).
  They are mapped, and three of them already call functions that do
  not exist.
- JupyterHub and user management ([stage 7](STAGE-7.md)).
- Changing [terraform/init_template.tpl](../../terraform/init_template.tpl)
  itself. The new template is written into the export;
  [stage 4](STAGE-4.md) owns the Terraform side.

## Acceptance

- `just test` passes at the root and in the export.
- Every function that `setup-instance.sh` calls has a role, and every
  task that replaces a shell line names the line it replaces.
- The map's provisioning section is complete.

## Outcome

- [exportit/sandbox-provisioning/](../../exportit/sandbox-provisioning/):
  `site.yml` with twelve roles, `node-image.yml`, two inventories, the
  first-boot script, 9 source files carried under `legacy/` and as
  role files, and [docs/LIVE-PROOF.md](../../exportit/sandbox-provisioning/docs/LIVE-PROOF.md).
- `just test` and `just full-test` pass at the repository root
  (full-test 19 minutes on 2026-11-12).
- 310 tests compare the playbooks with the scripts: every task names
  its lines or says why it is new; every acting line of the scripts is
  replaced or listed in `not_carried.yml` (ten entries); every value,
  package list and copied text equals what the script computes.
- The container test applied eight roles with `ansible-pull` to
  AlmaLinux 10: first run 49 changes, second run 0, result checked.
  `intel_oneapi` turned out to work in a container and was added; the
  plan had expected seven.
- Not proved: `efa_driver`, `fsx_lustre_client`, `spack_environment`,
  `hpc_tuning`, `node-image.yml`, the first-boot script, and anything
  on RHEL or AWS. The live-proof page is written, not run.
- Extraction rehearsal: the same 9 files with 15 commits of history.
- Found: the script's Prefect server does not start today (corrected,
  decision 7); Spack v1.2.0 ships its own `spack-public` mirror, which
  makes the script's second `mirror add` a no-op; the two
  `compiler find` steps undo each other on a repeated run; the module
  search path line never arrives on AlmaLinux 10. Details in
  [MAP.md](../../exportit/MAP.md#found-while-testing).

## Sizing and branch

12 roles, 98 named tasks and blocks, 14 in `node-image.yml`. Branch
`feature/stage-3-ansible`, cut from `feature/stage-2-cloudflow`;
commits local.
