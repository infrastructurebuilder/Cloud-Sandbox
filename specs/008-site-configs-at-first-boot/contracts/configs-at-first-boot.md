# Contract: the site's descriptions at first boot

**Where**: `csis-sandbox-terraform`'s `variables.tf`, `main.tf` and
`init_template.ansible.tpl`.

## Inputs, and the plan

| `configs_repo` | `configs_version` | `configs_secret_arn` | Plan |
| --- | --- | --- | --- |
| unset (default) | ignored | ignored | succeeds; user data spec 007's, byte for byte; no `configs_secret` policy |
| SSH form | a tag | a Secrets Manager ARN | succeeds; one `configs_secret` policy, on that ARN |
| SSH form | missing | any | **fails**, naming `configs_version` |
| SSH form | a tag | missing | **fails**, naming `configs_secret_arn` |
| HTTPS | any | any | **fails**, saying a deploy key needs the SSH form |

## What the rendered user data holds

- Unset: nothing of this spec.
- Set: the repository, the tag, the secret's ARN, the commands that read it,
  and GitHub's public host keys; **never** the key itself.

## What the first boot guarantees

1. The key is read with tracing off into a file (0600) in a directory under
   `/run` (0700) owned by `$RUNUSER`, after the AWS CLI is present.
2. It is used for one clone, as `$RUNUSER`, over SSH with GitHub's pinned host
   keys and `StrictHostKeyChecking=yes`, and for nothing else.
3. It is removed when the clone returns, passing or failing, and on any
   earlier exit; tracing is turned back on after.
4. A secret that cannot be read, or a refused clone, stops the boot before the
   playbooks, naming what failed; nothing falls back.
5. On success, `job.configs` and `cluster.configs` are links to the clone's
   directories in `/save/$RUNUSER/cloudflow/src/` and in
   `/save/$RUNUSER/Cloud-Sandbox/`, and cloudflow's `git status` does not show
   them.
