# Stage 4: Terraform as an independent unit

*Status:* executed on `feature/stage-4-terraform` and merged into `develop`
2026-11-12.
The decisions are under [Decisions taken](#decisions-taken); the
result is under [Outcome](#outcome).

## Why

[terraform/](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform) creates the network, the EFS volume, the
IAM role and the head node. It is tied to the rest of the repository
by one thing: the head node's first boot clones the monorepo from
`ioos/Cloud-Sandbox` and runs a script inside it (C5 in
[ANALYSIS.md](../ANALYSIS.md)). It also writes the identifiers that
cluster descriptions need (C7) into a text file that a person copies
by hand.

## What exists

22 tracked files: the root module (`main.tf`, `security.tf`,
`variables.tf`, `outputs.tf`), two first-boot templates (RHEL 10 and
RHEL 8), a remote-state module, a pipeline sketch, IAM policy files,
one site's settings in
[mysettings.tfvars](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform/mysettings.tfvars) and
[config.s3.tfbackend](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform/config.s3.tfbackend), saved older
copies, and notes.

## Items

1. Copy `terraform/` to `exportit/sandbox-terraform/` through a
   mapping file, as [stage 2](STAGE-2.md) does for cloudflow.
2. Add what makes it stand alone: `README.md`, `LICENSE`, a
   `Justfile` (`test` = `fmt -check` and `validate`, with no AWS
   call).
3. Describe, in the map, the first-boot template that would replace
   [init_template.tpl](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform/init_template.tpl): the
   `ansible-pull` form from [stage 3](STAGE-3.md), with the
   provisioning repository and version as Terraform variables instead
   of a literal URL.

   **YOUR DECISION (template):** write the new template into the
   export beside the copied one (default), or only describe it.
4. Separate what is one site's data from the module: the settings
   file, the backend file and the saved copies.

   **YOUR DECISION (site data):** keep them in the export as examples
   with the identifiers left as they are (default), or assign them to
   `sandbox-configs` ([stage 6](STAGE-6.md)).
5. State the outputs as an interface: which values cluster
   descriptions take from Terraform.

   **YOUR DECISION (tool):** validate with `terraform`, as the
   repository's documents say (default), or with `tofu`.

## Decisions taken

Asked one at a time on 2026-11-12, after a survey (both `terraform`
and `tofu` validate the root module and `remote-state/`; `pipeline/`
and `modules/` do not validate; `fmt -check` flags several files).

1. **Template:** the new first-boot template beside the copied one;
   `main.tf` not changed; the switch described.
2. **Site data:** kept in the Terraform copy as examples, old copies
   included.
3. **Tool:** `terraform`, pinned to 1.9.8 through tfenv.
4. **The bar for copied Terraform** (surfaced in the survey): validate
   what can be validated; the unformatted files and the two fragments
   are named lists that fail when they change.

## Out of scope

Running `plan` or `apply`. Changing any resource.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under `terraform/`; the map's Terraform
section is complete.

## Outcome

- [exportit/sandbox-terraform/](../../exportit/sandbox-terraform/): all
  22 files of `terraform/`, unchanged, at the unit's root, with a
  README, `Justfile` and tests.
- The first-boot template written in stage 3 moved here from
  `sandbox-provisioning/first-boot/` as `init_template.ansible.tpl`,
  since Terraform renders it. One copy, no drift.
- The copy tool can now place a directory at a unit's root (`./`),
  with two new tests; extraction renames `terraform/` to the root.
- Tests: Terraform 1.9.8 runs; both modules validate; the nine
  unformatted files are as recorded (Terraform flags `variables.tf`
  too, OpenTofu does not); both templates render, the new one needing
  exactly `provisioning_repo` and `provisioning_version`; the two
  fragments still fail. Extraction: 22 files, 44 commits.
- Found: nothing creates the DynamoDB table cloudflow needs or deploys
  the Lambda functions; the interface table is in
  [MAP.md](../../exportit/MAP.md#what-it-provides-the-interface).
  Afterwards the operator decided the table stays made by hand and is
  supplied as configuration; MAP.md records it.
- Netrc workaround removed from the provisioning `Justfile` first, at
  the operator's request (separate commit on stage 3's branch).

## Sizing and branch

22 files copied, 9 written, 1 moved. Branch `feature/stage-4-terraform`,
cut from `feature/stage-3-ansible`; commits local.
