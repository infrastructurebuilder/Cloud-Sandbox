# Quickstart: checking the access modes

## 1. Without AWS (your local machine)

```sh
cd exportit/sandbox-terraform
just test
just full-test
```

Expected, from `tests/access.tftest.hcl` (mocked providers) and
`test_template.py`:

- `none`: the rendered user data equals `tests/golden/first-boot.none.sh`;
  no `aws_iam_role_policy.provisioning_secret` is planned.
- `deploy_key` and `token`: one policy, its only resource the given ARN; the
  user data names the ARN, turns tracing off before reading it, and removes
  the temporary directory after `ansible-pull`.
- An unknown mode, a missing ARN, and `deploy_key` with an HTTPS URL each fail
  the plan with their message.

## 2. On AWS, when someone wants a private repository (not part of `just`)

Needs a private copy of the playbooks' repository, made on the operator's
word and removed after, and a head node built as spec 001 builds one.

1. Make the credential (the deploy key or the token,
   [data-model.md](data-model.md)) and put it in a new secret with the
   sandbox's prefix.
2. Plan and apply with `provisioning_access` and `provisioning_secret_arn`
   set, and `provisioning_repo` naming the private copy.
3. On the node, after the first boot: `~/setup.log` shows the playbooks
   applied; searching the node for the credential's value finds nothing:

   ```sh
   sudo grep -rIl --exclude-dir={proc,sys} -F -f /dev/stdin / <<< "<first 12 characters of it>"
   ```

4. `tofu show -json` and the state file: the same search finds nothing.
5. Remove everything, each step asked first, as spec 001's FR-015.
