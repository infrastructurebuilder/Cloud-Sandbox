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
- **Whether a site wants JupyterHub** (put aside 2026-11-13; planned as
  [stage 13](../INPROGRESS/STAGE-13.md)).
  `jupyterhub.yml` in `sandbox-provisioning` installs it, and works in
  the container test, but it is not part of `site.yml`; nothing installed
  JupyterHub before stage 7. Decide whether it stays an option, becomes
  part of the standard build, or goes. See
  [MAP.md](MAP.md#sandbox-ops).
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
- **Leftover Spack settings in the login user's scope on head nodes built
  before stage 11** (put aside 2026-11-14; planned as
  [stage 12](../INPROGRESS/STAGE-12.md)). The script's two
  `spack config add` lines have no `--scope`, so on a head node built by
  the script, or by the playbooks before stage 11, the install-tree
  padding (73) and the Tcl modules setting are in the login user's
  `~/.spack/config.yaml` and `~/.spack/modules.yaml`. Stage 11 writes them
  to the site scope instead and leaves the old copies alone: they have
  the same values, and the user scope wins over the site scope, so they
  do no harm until someone changes the site's values, when the login user
  alone would keep the old ones. To fix: a step of state `absent` in the
  user scope for those two paths (`spack_config` does this), run once on
  each existing head node, or added to the `spack` role's list for a
  while. Decide which, and whether any other user has the same in their
  own `~/.spack`. See [MAP.md](MAP.md#spack-set-up-through-the-collection-stage-11) and
  [STAGE-11.md](../INPROGRESS/STAGE-11.md).
