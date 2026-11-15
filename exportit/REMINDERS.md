# Reminders

Things put aside on purpose, to come back to. Each says when it was put
aside and why, and where the details are.

## Open

- **Who owns the Lambda functions** (put aside 2026-11-13; planned as
  [stage 17](../INPROGRESS/STAGE-17.md)). The two
  zombie-node functions stay inside cloudflow's package
  (`src/cloudflow/cluster/`), where they are today, by stage 2's
  decision 5. Whether cloudflow, `sandbox-ops` or someone else should own
  them is not decided. See [MAP.md](MAP.md#cloudflow) and
  [STAGE-2.md](../INPROGRESS/STAGE-2.md#decisions-taken).
- **The live proof on AWS** (planned as
  [stage 15](../INPROGRESS/STAGE-15.md); put aside 2026-11-13; it will come
  shortly). Every unit is tested locally, and `site.yml`, `users.yml` and
  `jupyterhub.yml` in a container, but nothing has been applied to a
  real AWS account: OpenTofu's `plan` and `apply` of `sandbox-terraform`,
  the head node's first boot pulling `sandbox-provisioning`, the
  compute-node image, and one cloudflow run. Check that the AWS SSO
  session is fresh before starting.
- **Whether to relocate at all** (2026-11-13; planned as
  [stage 19](../INPROGRESS/STAGE-19.md)). The units may never leave
  Cloud-Sandbox. That is decided once the commit tree is in good order;
  until then [MAP.md](MAP.md#the-order-of-the-real-relocations) says how
  it would be done, not that it will be.
- **The stage 12 tasks of the `spack` role can go** (2026-11-14). Since
  [stage 12](../INPROGRESS/STAGE-12.md) the role removes the script's two
  settings (the install-tree padding and the Tcl modules) from the login
  user's `~/.spack` on head nodes built before stage 11, where they hold
  what the site scope holds. Once no such head node is left, its three
  stage 12 tasks and `tasks/user_scope.yml` can be deleted, with their
  tests (`tests/test_user_scope.py`, the step's parity test, and the
  container test's seeding in `converge.sh` and check in `verify.yml`).
