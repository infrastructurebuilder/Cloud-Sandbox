# sandbox-terraform

Terraform that creates a Cloud Sandbox in an AWS account: a network (or
the use of an existing one), an EFS volume, an IAM role, a placement
group, and the head node. On its first boot the head node mounts the
EFS volume and installs the software stack. [DEPLOYMENT.md](DEPLOYMENT.md)
walks through a deployment.

```sh
tofu init -backend-config=config.s3.tfbackend
tofu workspace new my_workspace
tofu plan -var-file=mysettings.tfvars -out=my.plan
tofu apply my.plan
```

`remote-state/` is a second, separate module that creates the S3 bucket
the main module keeps its state in. It is applied once, first.

## This is a copy

This directory is a copy of `terraform/` from the Cloud-Sandbox
repository, made there. Every file from that directory is here,
byte-identical. [../MAP.md](../MAP.md) lists them, says which are
examples and which are history, and describes how this project would
be moved to a repository of its own. Do not edit the copied files here:
change the original and run `just export sandbox-terraform` at the
repository root.

What is new: this README, `LICENSE`, `Justfile`, `tests/`, the Python
files that run the tests,
[init_template.ansible.tpl](init_template.ansible.tpl), and
[DEPLOYMENT.md](DEPLOYMENT.md), the walk-through for deploying a sandbox
(with its screenshot in `docs/images/`, a copy of the original's). Also new: `tools/install-tofu.sh`, and a `versions.tofu`
in each module that requires OpenTofu 1.13.9. OpenTofu reads
`required_version` only from `.tofu` files, so the constraint is there
rather than in `main.tf`, which stays the same as the original.

## Two first-boot scripts

| File | What the head node does with it |
| --- | --- |
| `init_template.tpl` | Mounts EFS, clones Cloud-Sandbox, runs `scripts/setup-instance.sh`. This is what `main.tf` uses |
| `init_template.ansible.tpl` | Mounts EFS, then applies the Ansible playbooks of `sandbox-provisioning` with `ansible-pull`, and makes the node image. Not used by `main.tf` yet |

Switching `main.tf` to the second needs two more values, which the
tests prove are the only ones missing:

```hcl
variable "provisioning_repo" {
  description = "Git URL of the sandbox-provisioning playbooks"
  type        = string
}

variable "provisioning_version" {
  description = "Branch, tag or commit of the playbooks to apply"
  type        = string
}
```

and, in the head node's `user_data`, `"init_template.ansible.tpl"` in
place of `"init_template.tpl"` with
`provisioning_repo = var.provisioning_repo` and
`provisioning_version = var.provisioning_version` added to the map.
Neither change is made here; the copy stays the same as the original.

## What the files are

| Files | What they are |
| --- | --- |
| `main.tf`, `variables.tf`, `outputs.tf`, `security.tf` | The module |
| `init_template.tpl`, `init_template_rhel8.tpl` | First-boot scripts for RHEL 10 (used) and RHEL 8 (kept) |
| `remote-state/` | The module for the state bucket |
| `mysettings.tfvars`, `config.s3.tfbackend`, `remote-state/s3.defaults.tfvars` | Examples of settings. `mysettings.tfvars` holds placeholders; the backend file names one site's bucket |
| `ec2.policy`, `policy`, `s3.policy`, `generated.policy.template.sh` | IAM policies, kept for reference. The module itself attaches AWS managed policies and one inline S3 policy |
| `scp.terraform.output.sh`, `login` | Helpers: copy the deployment notes to the head node; print and run the login command |
| `pipeline/` | A sketch of an EC2 Image Builder pipeline. It does not validate |
| `modules/orig.main.tf`, `save/main.tf.saved` | Older copies of `main.tf`. The first does not validate |
| `quickstart.notes`, `TODO.txt` | Notes |

## What the other units take from it

Terraform writes `deployment_info.txt` with the values that a cluster
description for cloudflow needs: `key_name`, `sg_ids` (three security
groups), `subnet_id` and `placement_group`. The fifth, `image_id`, is
made later, on the head node, by `sandbox-provisioning`'s
`node-image.yml`. [../MAP.md](../MAP.md) has the table.

## Working on it

You need `just`, `uv`, `curl`, `unzip` and `shellcheck`. `just init`
fetches OpenTofu 1.13.9 into `.tofu/` (checking it against the release's
checksums) and every target uses that copy, so whatever `tofu` or
`terraform` is on your PATH does not matter. No AWS account or
credentials are needed: nothing here plans or applies.

```sh
just init        # OpenTofu into .tofu/, test environment, both modules initialised without a backend
just test        # both modules validate; formatting and templates as recorded
just full-test   # also: the two fragments still fail to validate
```

The copies keep the originals' formatting: `tofu fmt -check`
would rewrite nine of them, and the tests hold that list fixed.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
