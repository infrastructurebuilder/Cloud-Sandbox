# Reminders

Things put aside on purpose, to come back to. Each says when it was put
aside and why, and where the details are.

## Open

- **Who owns the Lambda functions** (put aside 2026-11-13; planned as
  [spec 003](../specs/003-lambda-functions-owner/spec.md)). The two
  zombie-node functions stay inside cloudflow's package
  (`src/cloudflow/cluster/`), where they are today, by stage 2's
  decision 5. Whether cloudflow, `sandbox-ops` or someone else should own
  them is not decided. See [MAP.md](MAP.md#cloudflow) and
  [STAGE-2.md](../ATTIC/SPECS/COMPLETED/STAGE-2.md#decisions-taken).
- **The live proof on AWS** (planned as
  [spec 001](../specs/001-live-proof-on-aws/spec.md); put aside 2026-11-13; it will come
  shortly). Every unit is tested locally, and `site.yml`, `users.yml` and
  `jupyterhub.yml` in a container, but nothing has been applied to a
  real AWS account: OpenTofu's `plan` and `apply` of `sandbox-terraform`,
  the head node's first boot pulling `sandbox-provisioning`, the
  compute-node image, and one cloudflow run. Check that the AWS SSO
  session is fresh before starting.
- **Links that leave a unit** (2026-11-17, moving day's decision 5).
  27 links in the units' own pages lead out of the unit, 25 of them to
  [MAP.md](MAP.md). They resolve where the units are checked out under
  `exportit/`; in a unit's own repository on GitHub they lead nowhere.
  Left on purpose; rewrite them when a unit is first used apart from
  Cloud-Sandbox.
- **`sandbox-configs` moved whole** (2026-11-17, moving day's decision
  4). [Spec 005](../specs/005-configs-split-by-owner/spec.md)'s split, templates and examples to
  cloudflow, is still possible; the files that move will not bring their
  history from `csis-sandbox-configs` into `cloudflow`.
- **Releasing from a unit's own repository** (2026-11-17). Each unit's
  `release` target still says "nothing to release from exportit/". How a
  unit is released, now that it has a repository and a first tag, is not
  decided.
- **The stage 12 tasks of the `spack` role can go** (2026-11-14). Since
  [stage 12](../ATTIC/SPECS/COMPLETED/STAGE-12.md) the role removes the script's two
  settings (the install-tree padding and the Tcl modules) from the login
  user's `~/.spack` on head nodes built before stage 11, where they hold
  what the site scope holds. Once no such head node is left, its three
  stage 12 tasks and `tasks/user_scope.yml` can be deleted, with their
  tests (`tests/test_user_scope.py`, the step's parity test, and the
  container test's seeding in `converge.sh` and check in `verify.yml`).
