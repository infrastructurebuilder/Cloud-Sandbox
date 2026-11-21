# Data model: The first boot reads a private playbooks' repository

## Module variables (added to spec 006's)

| Variable | Type | Default | Validation |
| --- | --- | --- | --- |
| `provisioning_access` | string | `"none"` | one of `none`, `deploy_key`, `token`; otherwise the plan fails listing the three (FR-001) |
| `provisioning_secret_arn` | string | `null` | required, and of the form `arn:aws:secretsmanager:<region>:<account>:secret:<name>`, when `provisioning_access` is not `none` (FR-002); unused with `none` |
| `provisioning_repo` (spec 006's) | string | none | with `deploy_key`: SSH form, `git@github.com:…` or `ssh://git@ssh.github.com:443/…` (research R5); with `none` or `token`: HTTPS |

## The secret (the operator's, outside Terraform)

| Mode | `SecretString` holds | Made by |
| --- | --- | --- |
| `deploy_key` | the private half of a key pair (OpenSSH format) whose public half is a read-only deploy key on the repository | `ssh-keygen -t ed25519`, then GitHub's repository settings |
| `token` | a fine-grained personal access token: only the repository, `Contents: Read-only`, nothing else | GitHub's developer settings, with an expiry date |

One secret per head-node deployment or shared between them, as the operator
chooses; the module only reads the ARN it is given.

## Resources the module adds

| Resource | When | Allows |
| --- | --- | --- |
| `aws_iam_role_policy.provisioning_secret` | `provisioning_access != "none"` | `secretsmanager:GetSecretValue` on `provisioning_secret_arn`, nothing else, for the head node's role |

## On the node, during the first boot

```text
none:       clone (anonymous HTTPS) ─▶ ansible-pull ─▶ … (spec 006, unchanged)
deploy_key: AWS CLI ─▶ set +x ─▶ secret → /run/<tmp>/key (0600) + pinned known_hosts
            ─▶ clone over SSH ─▶ ansible-pull ─▶ /run/<tmp> removed ─▶ set -x ─▶ …
token:      AWS CLI ─▶ set +x ─▶ secret → /run/<tmp>/token (0600)
            ─▶ clone over HTTPS with the helper ─▶ ansible-pull ─▶ /run/<tmp> removed ─▶ set -x ─▶ …
any failure ─▶ /run/<tmp> removed (trap) ─▶ "… FAILED" naming the secret or the clone ─▶ exit 1
```
