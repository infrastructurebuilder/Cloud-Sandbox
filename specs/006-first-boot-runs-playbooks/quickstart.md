# Quickstart: checking the first boot runs the playbooks

Everything here runs on your local machine, in Cloud-Sandbox's checkout, with
no AWS credentials. The real first boot is spec 001's.

## 1. The unit's tests

```sh
cd exportit/sandbox-terraform
just test        # lint, types, validate, the template tests, tofu test (mocked)
just full-test   # and the plan without provisioning_repo (downloads nothing new)
```

Expected:

- `test_template.py`: the module renders `init_template.ansible.tpl` with the
  four values; the template's placeholders equal what `main.tf` passes; the
  clone of cloudflow comes before the plays and its install after them.
- `tofu test` (`tests/firstboot.tftest.hcl`): pass; the planned user data
  names both repositories and versions and not `ioos/Cloud-Sandbox`.
- The slow test: `tofu plan` without `provisioning_repo` exits non-zero with a
  message naming `provisioning_repo`.

## 2. Look at what a node would be given

```sh
cd exportit/sandbox-terraform
just render-first-boot   # prints the rendered user data for sample values
```

Read it for the order of [contracts/first-boot.md](contracts/first-boot.md),
and that no line names a credential.

## 3. The workshop's acceptance tests

```sh
cd ../..
just test
just full-test
```

Both pass (SC-003).
