# Stage 4: Terraform as an independent unit

*Status:* planned 2026-11-12. Waits for validation and "do 4".
Depends on [stage 3](STAGE-3.md) for the first-boot template.

## Why

[terraform/](../terraform/) creates the network, the EFS volume, the
IAM role and the head node. It is tied to the rest of the repository
by one thing: the head node's first boot clones the monorepo from
`ioos/Cloud-Sandbox` and runs a script inside it (C5 in
[ANALYSIS.md](ANALYSIS.md)). It also writes the identifiers that
cluster descriptions need (C7) into a text file that a person copies
by hand.

## What exists

22 tracked files: the root module (`main.tf`, `security.tf`,
`variables.tf`, `outputs.tf`), two first-boot templates (RHEL 10 and
RHEL 8), a remote-state module, a pipeline sketch, IAM policy files,
one site's settings in
[mysettings.tfvars](../terraform/mysettings.tfvars) and
[config.s3.tfbackend](../terraform/config.s3.tfbackend), saved older
copies, and notes.

## Items

1. Copy `terraform/` to `exportit/sandbox-terraform/` through a
   mapping file, as [stage 2](STAGE-2.md) does for cloudflow.
2. Add what makes it stand alone: `README.md`, `LICENSE`, a
   `Justfile` (`test` = `fmt -check` and `validate`, with no AWS
   call).
3. Describe, in the map, the first-boot template that would replace
   [init_template.tpl](../terraform/init_template.tpl): the
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

## Out of scope

Running `plan` or `apply`. Changing any resource.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under `terraform/`; the map's Terraform
section is complete.

## Sizing and branch

22 files copied, about 5 written. Branch `feature/stage-4-terraform`.
