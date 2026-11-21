# Data model: The first boot runs the playbooks

The "data" of this spec is the module's input and what the first boot makes
on the node from it.

## Module variables (`csis-sandbox-terraform`'s `variables.tf`)

| Variable | Type | Default | Rule | Used for |
| --- | --- | --- | --- | --- |
| `provisioning_repo` | string, `nullable = false` | none | a plan without it fails, naming it (FR-001, SC-001) | the playbooks' clone and `ansible-pull --url` |
| `provisioning_version` | string, `nullable = false` | none | a tag of that repository (`DEPLOYMENT.md`) | `git clone --branch` and `ansible-pull --checkout` |
| `cloudflow_repo` | string, `nullable = false` | none | cloudflow's repository URL, HTTPS (FR-002) | the cloudflow clone |
| `cloudflow_version` | string, `nullable = false` | none | a tag of that repository | `git clone --branch` |
| `sandbox_version` | removed | | | it named the original's branch, no longer cloned |

The values `main.tf` passes to the template, in `local.user_data`:
`efs_name`, `ami_name`, `aws_region`, `project` (as today), and the four
above. The template names exactly these (a test holds the two lists equal).

## What the first boot makes on the node

| Path | What | Made when |
| --- | --- | --- |
| `/save/$RUNUSER/cloudflow` | cloudflow's checkout at `cloudflow_version` | before the plays, where the old clone was |
| `/save/$RUNUSER/Cloud-Sandbox/cloudflow` | a link to `/save/$RUNUSER/cloudflow/src/cloudflow` (research R3) | with the clone |
| `/opt/sandbox-provisioning` | the playbooks' checkout at `provisioning_version` | as today |
| `$RUNUSER`'s user site | cloudflow, editable, no dependencies (research R2) | after `site.yml` succeeds, before `node-image.yml` |
| `~/setup.log` | the log, with a line naming what failed, if anything did | throughout |

## States of a first boot

```text
start ─▶ EFS mounted ─▶ cloudflow cloned ─▶ playbooks cloned, collections installed
      ─▶ site.yml applied ─▶ cloudflow installed ─▶ node image made ─▶ done
any step failing ─▶ "… FAILED" in ~/setup.log, exit 1, no image
```
