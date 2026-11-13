# Reminders

Things put aside on purpose, to come back to. Each says when it was put
aside and why, and where the details are.

## Open

- **Who owns the Lambda functions** (put aside 2026-11-13). The two
  zombie-node functions stay inside cloudflow's package
  (`src/cloudflow/cluster/`), where they are today, by stage 2's
  decision 5. Whether cloudflow, `sandbox-ops` or someone else should own
  them is not decided. See [MAP.md](MAP.md#cloudflow) and
  [STAGE-2.md](../INPROGRESS/STAGE-2.md#decisions-taken).
- **Whether a site wants JupyterHub** (put aside 2026-11-13).
  `jupyterhub.yml` in `sandbox-provisioning` installs it, and works in
  the container test, but it is not part of `site.yml`; nothing installed
  JupyterHub before stage 7. Decide whether it stays an option, becomes
  part of the standard build, or goes. See
  [MAP.md](MAP.md#sandbox-ops).
- **The live proof on AWS** (put aside 2026-11-13; it will come
  shortly). Every unit is tested locally, and `site.yml`, `users.yml` and
  `jupyterhub.yml` in a container, but nothing has been applied to a
  real AWS account: OpenTofu's `plan` and `apply` of `sandbox-terraform`,
  the head node's first boot pulling `sandbox-provisioning`, the
  compute-node image, and one cloudflow run. Check that the AWS SSO
  session is fresh before starting.
- **Whether to relocate at all** (2026-11-13). The units may never leave
  Cloud-Sandbox. That is decided once the commit tree is in good order;
  until then [MAP.md](MAP.md#the-order-of-the-real-relocations) says how
  it would be done, not that it will be.
