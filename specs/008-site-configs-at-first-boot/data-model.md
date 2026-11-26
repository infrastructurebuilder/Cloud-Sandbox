# Data model: The first boot puts the site's descriptions on the head node

## The settings (`csis-sandbox-terraform`'s main module)

| Variable | Type | Default | Rule |
| --- | --- | --- | --- |
| `configs_repo` | string | `null` | when set: SSH form, `git@github.com:<owner>/<repo>.git` or `ssh://git@ssh.github.com:443/<owner>/<repo>.git` |
| `configs_version` | string | `null` | required when `configs_repo` is set: a tag |
| `configs_secret_arn` | string | `null` | required when `configs_repo` is set: `arn:aws:secretsmanager:…` |

## The permission

| Resource | Count | Allows |
| --- | --- | --- |
| `aws_iam_role_policy.configs_secret` | 1 when `configs_repo` is set, else 0 | `secretsmanager:GetSecretValue` on `configs_secret_arn`, nothing else |
| `aws_iam_role_policy.provisioning_secret` (spec 007) | unchanged | unchanged |

## The secret (the operator's, outside OpenTofu)

| Field | Value |
| --- | --- |
| Name | with the sandbox's prefix, for example `csis-sandbox-configs-deploy-key` |
| Value | the deploy key's private half, OpenSSH format, as the secret string |
| Key | the account's default for Secrets Manager (no `kms:Decrypt` grant needed) |

## On the head node

| Path | What | Owner |
| --- | --- | --- |
| `/run/tmp.*` (during the clone only) | the key (0600) and the known-hosts file, in a 0700 directory | `$RUNUSER` |
| `/save/$RUNUSER/sandbox-configs` | the clone, at `configs_version` | `$RUNUSER` |
| `/save/$RUNUSER/cloudflow/src/job.configs`, `…/cluster.configs` | links to the clone's two directories (the guides' relative paths) | `$RUNUSER` |
| `/save/$RUNUSER/Cloud-Sandbox/job.configs`, `…/cluster.configs` | the same links (the old absolute paths) | `$RUNUSER` |
| `/save/$RUNUSER/cloudflow/.git/info/exclude` | gains the two names | `$RUNUSER` |

## States of a first boot

```text
configs_repo unset ─▶ spec 007's boot, unchanged
configs_repo set ─▶ secret read ─▶ clone ─▶ key removed ─▶ links ─▶ the plays …
                  ╰▶ secret unreadable or clone refused ─▶ key removed (trap) ─▶ "FAILED", exit 1, no image
```
