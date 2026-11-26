# Reminders

Things put aside on purpose, to come back to. Each says when it was put
aside and why, and where the details are.

## Open

- **A head node replaced on a kept EFS volume gets no `/save`**
  (2026-11-23, a finding of [spec 001](../specs/001-live-proof-on-aws/spec.md#outcome);
  `csis-sandbox-terraform`). The first boot makes the `/save` link only
  inside `if [ ! -d save ]`, that is, only on a new volume; a node booted
  on a volume an earlier node used has no link, and cloudflow's clone into
  `/save/$RUNUSER/cloudflow` fails. The volume also holds the earlier
  clone. The original had the same `if`, but cloned into its working
  directory and ran the old checkout unnoticed. To become a spec: make the
  link always, and decide what a second boot does with an existing clone.
- **The drivers are built for a kernel the image does not boot**
  (2026-11-23, a finding of spec 001; `csis-sandbox-provisioning`). The
  first boot's "Update every installed package" installed a newer kernel
  (RHEL 10.3's) without rebooting, then `efa_driver` and
  `fsx_lustre_client` were installed for the running one (RHEL 10.2's);
  `efa_driver` says so in a warning. The image boots the newer kernel by
  default, so whether the EFA and Lustre modules load on a compute node
  is not proved. The script does the same (it does not reboot). To become a spec:
  reboot, or build for the newest installed kernel, before the drivers, and
  prove it on a compute node.
- **The subscription-manager plugin is silenced before the update that
  upgrades it** (2026-11-23, a finding of spec 001;
  `csis-sandbox-provisioning`). On the first boot the update upgraded
  subscription-manager (1.30.12 to 1.30.16) after "Silence the
  subscription-manager dnf plugin" ran, and by the second apply the file
  said `enabled=1` again, so that apply changed it. Small, and in the
  script's order; to become a spec if a second apply must change nothing.
- **Narrow the head node's managed policies** (2026-11-24, spec 002's
  research R2; `csis-sandbox-terraform`). The main module's default
  `managed_policies` attach `AmazonEC2FullAccess`, `AmazonS3FullAccess`,
  `AmazonFSxFullAccess`, `AmazonDynamoDBFullAccess_v2` and others to the head
  node's role (its `variables.tf` says `TODO: limit this`), so a node may write
  to any bucket, `ioos-cloud-sandbox` included. Spec 002's scoped policy on the
  build cache (`build_cache_bucket`) is written for when that list is narrowed;
  narrowing it, to what cloudflow and the playbooks use, is a spec of its own.
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
- **Compare a node built by the playbooks with one built the old way**
  (2026-11-23, spec 001, FR-018). The live proof's stage D builds a second
  head node by the original's first boot at the units' baseline and compares
  the two; it is off by default (`compare_with_script = false` in
  `csis-sandbox-terraform`'s `proof/proof.tfvars.example`), so the last row of
  the "Not proved" table stays deferred. To attempt it, set the flag to `true`
  for a run of `csis-sandbox-provisioning`'s `docs/LIVE-PROOF.md`.
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
