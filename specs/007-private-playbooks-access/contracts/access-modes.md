# Contract: the access modes of the first boot

**Where**: `csis-sandbox-terraform`'s `variables.tf`, `main.tf` and
`init_template.ansible.tpl`.

## Inputs

| `provisioning_access` | `provisioning_secret_arn` | `provisioning_repo` | Plan |
| --- | --- | --- | --- |
| `none` (default) | ignored | HTTPS | succeeds; no secret permission |
| `deploy_key` | a Secrets Manager ARN | SSH form | succeeds; one policy, that ARN |
| `token` | a Secrets Manager ARN | HTTPS | succeeds; one policy, that ARN |
| `deploy_key` or `token` | missing | any | **fails**, naming `provisioning_secret_arn` |
| `deploy_key` | an ARN | HTTPS | **fails**, saying the deploy key needs the SSH form |
| anything else | any | any | **fails**, listing the three modes |

## What the rendered user data holds

- With `none`: exactly spec 006's user data (byte for byte, research R7).
- With either other mode: the secret's ARN, the commands that read it, and
  GitHub's public host keys; **never** the credential itself.

## What the first boot guarantees

1. The credential is read only after the AWS CLI is present, into a file
   under `/run` readable by root alone, with tracing off.
2. It is used for the playbooks' clone and `ansible-pull`, and for nothing
   else (cloudflow's clone stays anonymous, spec 007 FR-008).
3. It is removed when `ansible-pull` returns, whether it passed or failed, and
   on any earlier exit; the node image is made after.
4. A secret that cannot be read stops the boot before any clone, naming the
   secret; there is no fallback to an anonymous clone.
5. A refused clone stops the boot; with `token`, the log line says the token
   may have expired.
