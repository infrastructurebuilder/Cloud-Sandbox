# Data model: The live proof on AWS

## The proof's settings (`proof.tfvars`, in the working copy only)

| Setting | Value | From |
| --- | --- | --- |
| `preferred_region` | `us-east-2` | FR-008 |
| `vpc_id`, `subnet_id` | the IOOS Cloud Sandbox VPC and one private subnet, by ID | box A3 (research R6); never committed |
| `availability_zone` | the subnet's zone | box A3 |
| `instance_type` | `c6i.8xlarge` (or another compute-optimized type with ≥32 processors) | FR-009 |
| `nameprefix`, `name_tag`, `project_tag` | `csis_live_proof`, `CSIS-Live-Proof`, `CSIS-Live-Proof` | the proof's prefix (FR-008) |
| `key_name`, `public_key` | a key pair made for the proof (`ssh-rsa`, as the module requires) | box A2 |
| `allowed_ssh_cidr_list` | `[]` | research R5 |
| `managed_policies` | the module's list plus `AmazonSSMManagedInstanceCore` | research R4 |
| `provisioning_repo`, `provisioning_version` | `https://github.com/infrastructurebuilder/csis-sandbox-provisioning.git`, its newest tag | spec 006 |
| `cloudflow_repo`, `cloudflow_version` | `https://github.com/infrastructurebuilder/cloudflow.git`, its newest tag | spec 006 |
| `compare_with_script` | `false` | FR-013 |

## What the proof creates (all new, all with the prefix)

| Resource | Made by | Removed by |
| --- | --- | --- |
| IAM role, its policy, instance profile | `tofu apply` | `tofu destroy` |
| key pair | `tofu apply` | `tofu destroy` |
| security groups (base, EFS, and the unattached SSH one) | `tofu apply` | `tofu destroy` |
| EFS volume and mount target | `tofu apply` | `tofu destroy` |
| network interface, head node (and the `-script` node if the flag is `true`) | `tofu apply` | `tofu destroy` |
| placement group | `tofu apply` | `tofu destroy` |
| machine image and its snapshot | `node-image.yml`, box C1 | boxes E3–E4, by ID |

## The findings (kept in the spec's outcome; logs are not committed)

| Finding | Where it comes from |
| --- | --- |
| a task that changed on the second apply | the recap and `changed:` lines of `site-second.log` |
| a task that would change in check mode | `site-check.log` |
| a difference in Spack's configuration | `compare-spack-config.py` against `expected-spack-config.json` |
| a module file whose time moved | the times before and after the second apply |
| a row of the "Not proved" table | proved, with the date and what was seen, or not, with why (SC-003) |
| a difference between the two nodes | stage D, only with the flag `true` |

## The proof's states

```text
session checked ─▶ A: working copy, workspace, settings, plan (only additions) ─▶ apply (operator's word)
  ─▶ first boot builds the node (hours) ─▶ B: second apply, check mode, comparisons, JupyterHub
  ─▶ C: node-image.yml (operator's word) ─▶ image available
  ─▶ D: (only if compare_with_script) the second node compared
  ─▶ E: destroy, image and snapshot removed (each asked) ─▶ nothing with the prefix; VPC as it was
any gate failing ─▶ stop and ask
```
