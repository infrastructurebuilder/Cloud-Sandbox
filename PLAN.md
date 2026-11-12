# Plans

## Reconstruction into independent units (2026-11-12)

*Status:* stages 1 (analysis and plan), 2 (cloudflow), 3
(provisioning as Ansible), 4 (Terraform) and 5 (model recipes)
executed, waiting for validation. Stages 6 to 8 planned.

Cloud-Sandbox is being taken apart into units that could each live in
their own repository: the cloudflow workflow engine, head-node
provisioning (as Ansible playbooks), Terraform, the model recipes, the
job and cluster descriptions, operator utilities, and documentation.
Nothing is moved out of this repository. Each unit is copied into
[exportit/](exportit/), and [exportit/MAP.md](exportit/MAP.md) says
how the real relocation would be done.

The plan is kept as one file per stage, because each is reviewed and
executed on its own:

- [INPROGRESS/ANALYSIS.md](INPROGRESS/ANALYSIS.md): what is in the
  repository and what ties its parts together.
- [INPROGRESS/TODO.md](INPROGRESS/TODO.md): the open stages and the
  standing decisions.
- [INPROGRESS/STAGE-1.md](INPROGRESS/STAGE-1.md) to
  [INPROGRESS/STAGE-8.md](INPROGRESS/STAGE-8.md): the stage plans.
