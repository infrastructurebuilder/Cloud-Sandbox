# Reminders

Things put aside on purpose, to come back to. Each says when it was put
aside and why, and where the details are.

## Open

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
- **Remove the link at `/save/$RUNUSER/Cloud-Sandbox/cloudflow`**
  (2026-11-22, spec 006). The first boot links the old checkout's path to
  cloudflow's new place, because about twenty of `csis-sandbox-configs`'
  job descriptions (`CONFIGTMPL`) and some of cloudflow's scripts and
  examples (`run_liveocean.sh`, `liveocean_fallback.sh`, `examples/cron/`)
  name it; [spec 006's research R3](../specs/006-first-boot-runs-playbooks/research.md)
  lists them. Once they name the new place, each in its own unit, the
  template's link goes.
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
