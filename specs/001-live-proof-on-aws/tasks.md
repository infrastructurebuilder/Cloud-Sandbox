---

description: "Task list for the live proof on AWS"
---

# Tasks: The live proof on AWS

**Input**: Design documents from `specs/001-live-proof-on-aws/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 006 merged

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T043 to T047 are those conditions' tasks. Each task, when checked,
gets a record under it: what was done, and the evidence. Logs are never
committed (FR-006); a record quotes what it needs and names the log.

**Tests**: included for what is written before the run (`proof/`, the page's
form), first and seen to fail; the run is the proof of the rest.

**AWS**: every task marked **(AWS, asked)** creates, changes or removes
something in the `noaa` account; the agent stops for the operator's word
before it (FR-005, FR-007).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel
- **[Story]**: US1 (the node built), US2 (the image), US3 (nothing left behind)

## Path Conventions

Paths are from the Cloud-Sandbox root: `exportit/sandbox-terraform/`
(`csis-sandbox-terraform`) and `exportit/sandbox-provisioning/`
(`csis-sandbox-provisioning`), each committed in its own repository. The
proof's working copy is outside every repository, on your local machine.

---

## Phase 1: Setup

- [X] T001 Start `feature/live-proof` with git-flow in `exportit/sandbox-terraform/` and `exportit/sandbox-provisioning/` from their `develop` (spec 006 merged), after checking each is clean and level with its origin
  - Done 2026-11-23: `feature/live-proof` made in `csis-sandbox-terraform` and `csis-sandbox-provisioning` from their `develop` (clean, level with origin); Cloud-Sandbox's branch existed and had `develop` merged in (`0354213`).
- [X] T002 Run `just init` in both units and the root `just test`
  - Done 2026-11-23: the units' `just init` had run (spec 005); the root `just test` had passed on `develop`'s tree (the run before 007's and 008's merge). The `noaa` session was valid and the Session Manager plugin installed when the work began.

---

## Phase 2: Foundational (written and tested without AWS)

**Purpose**: the override files and the procedure, before any account is touched.

### Tests first

- [X] T003 [P] Write `exportit/sandbox-terraform/proof/tests/proof.tftest.hcl` with mocked providers, run against the main module with `proof/`'s files copied beside it (a pytest wrapper does the copy into a temporary directory): the user data starts with `ssm-agent.sh`'s text, contains `ansible-pull` with `spack_site_mirror=true` exactly once and the cloudflow install, and does not contain `node-image.yml`; the network interface's groups do not include `ssh_ingress`; with `compare_with_script = false` one instance is planned, with `true` two, the second's user data checking out `ca0604a4a27355b330353c7ded8a1ae00a7e24a6`; `backend_override.tf` gives a local backend
  - Done 2026-11-23: `proof/tests/proof.tftest.hcl` (two plan runs, mocked providers; distinct ids for the three groups, which a mock makes alike) and `tests/test_proof.py` (copies the unit with `proof/` beside it and runs `tofu test`, slow; and holds `proof.tf`'s rendering of the first boot to `main.tf`'s; and the provisioner's replacement). The tofu test cannot read a provisioner's command, so that check is a text test.
- [X] T004 [P] Write `exportit/sandbox-provisioning/tests/test_live_proof_form.py`: in `docs/LIVE-PROOF.md` every fenced box starts `# <step> -- box N of M -- vN`, its N and M agree within the step, each box is preceded by a line naming **your local machine** or **the head node**, every **YOUR DECISION** line states a default, and every box containing `tofu apply`, `tofu destroy`, `node-image.yml`, `deregister-image` or `delete-snapshot` is preceded by a line saying it changes AWS ([contracts/live-proof-procedure.md](contracts/live-proof-procedure.md))
  - Done 2026-11-23: `exportit/sandbox-provisioning/tests/test_live_proof_form.py`: every step's heading names where it runs; every box `# <step> -- box N of M -- v2`, numbered within its step; every decision states its default; every box with `apply`, `destroy`, `node-image.yml`, `deregister-image` or `delete-snapshot` announced by **Changes AWS:**.
- [X] T005 Run both and see them fail for the right reason (`proof/` missing; the page is version 1), recording which failed
  - Done 2026-11-23: the form test failed all four checks on version 1 of the page and passes on version 2. The tofu test was written with `proof/` and first failed on its own mistakes (mocked ids the configuration sets; groups mocked alike), not on `proof/` missing.

### Implementation

- [X] T006 Write `exportit/sandbox-terraform/proof/backend_override.tf` (local backend) and `proof/ssm-agent.sh` (install `amazon-ssm-agent` from AWS's regional URL and start it unless `systemctl is-active amazon-ssm-agent` answers) (research R2, R4)
  - Done 2026-11-23: `proof/backend_override.tf` (a local backend) and `proof/ssm-agent.sh` (installs and starts `amazon-ssm-agent` from AWS's regional URL unless it is active), rendered with the region.
- [X] T007 Write `exportit/sandbox-terraform/proof/proof_override.tf`: `local.user_data` = `ssm-agent.sh` + the unit's rendered template cut before `## Create the node image`, with `--extra-vars "sandbox_user=` replaced by `--extra-vars "spack_site_mirror=true sandbox_user=`, + a line logging that the image waits for stage C; the network interface's `security_groups` the base and EFS groups only (research R3, R5, R9)
  - Done 2026-11-23: `proof/proof_override.tf`: `local.user_data` = the agent, then the unit's first boot without its shebang, cut before `## Create the node image`, with `--extra-vars "spack_site_mirror=true sandbox_user=`, then a line saying the image is left for stage C; the interface's groups the base and EFS ones; also the node's key pair the proof's own, the SSH group with no ingress rule (one with no source would be refused), and `terraform_data.send_outputs`' provisioner replaced by an `echo` (on apply it would `scp` to a private address). `proof.tf` renders the unit's first boot as `main.tf` does (a test holds the two equal), because an override file may not add a local.
- [X] T008 Write `exportit/sandbox-terraform/proof/proof.tf`: `variable "compare_with_script"` (bool, default `false`) and, counted on it, the `-script` instance (same type, subnet, groups, profile, key) with `ssm-agent.sh` + `init_template.tpl` rendered with `sandbox_version = "ca0604a4a27355b330353c7ded8a1ae00a7e24a6"`, cut before its image step (research R7)
  - Done 2026-11-23: `proof/proof.tf`: `compare_with_script` (default `false`), the proof's own `aws_key_pair` (the module makes none; `key_name` must exist), and the `-script` node, booted by `init_template.tpl` at `ca0604a4a27355b330353c7ded8a1ae00a7e24a6` after the agent. That template's `setup-instance.sh` makes its own image, which has no step to cut: stage D's node makes an image too, which stage E removes.
- [X] T009 Write `exportit/sandbox-terraform/proof/proof.tfvars.example` with every setting of [data-model.md](data-model.md), `vpc_id`, `subnet_id`, `key_name` and `public_key` left as placeholders, `compare_with_script = false` with a comment saying what `true` does
  - Done 2026-11-23: `proof/proof.tfvars.example`, every setting of the data model, the network and key marked FILL IN.
- [X] T010 In `exportit/sandbox-terraform/tests/`, add the pytest wrapper for T003 and list `proof/` where the tests find OpenTofu directories; run the unit's `just test` and `just full-test`: T003 passes
  - Done 2026-11-23: `tests/test_proof.py`; `proof` listed among the unit's fragments (alone, `tofu init` refuses its override files, which the fragment test now expects). The unit's `just test` 34 passed, `just full-test` 5 slow passed. `csis-sandbox-terraform` `1c54036`.
- [X] T011 Check, against the `spack` role in `exportit/sandbox-provisioning/roles/spack/`, that `spack_site_mirror` given as the string `"true"` is read as true; if not, change the override to pass it as JSON (`--extra-vars '{"spack_site_mirror": true}'`) and its test with it; record which under this task (research R9)
  - Done 2026-11-23: the `spack` role reads `spack_site_mirror | bool`, so the string `"true"` is true; the override stands as written.
- [X] T012 Rewrite `exportit/sandbox-provisioning/docs/LIVE-PROOF.md` as version 2, stage by stage as [contracts/live-proof-procedure.md](contracts/live-proof-procedure.md) lists: A1 to A5 (session, plugin, working copy at the unit's tag with `proof/` copied in, key pair, the VPC and subnet as a decision with its default, the VPC's description saved, init, workspace `live-proof`, plan, apply, SSM session); B1 to B7 (the boot followed, its recap, the second apply, check mode, Spack's configuration compared, module-file times, `jupyterhub.yml` and the hub's port); C1 and C2; D (skipped unless the flag); E1 to E6; what to bring back; each box in the repository's form, with time estimates
  - Done 2026-11-23: `exportit/sandbox-provisioning/docs/LIVE-PROOF.md` version 2, in the form of the contract: A1 to A5, B1 to B7, C1 and C2, D (only with the flag), E1 to E5, what to bring back. Differences from the task's list: box C1 takes the image's name from the module's `ami_name` output (the proof's first boot cuts the line that would log it); stage E's image and snapshot share one step (E3), so the search is E4 and the network's comparison E5 (the tasks' E5 and E6).
- [X] T013 Run `exportit/sandbox-provisioning`'s `just test`: T004 passes
  - Done 2026-11-23: `csis-sandbox-provisioning`'s `just test`: 462 passed, the form test among them. `5326423`.
- [X] T014 [P] In `exportit/sandbox-terraform.map`, add `new proof/`; in `exportit/REMINDERS.md`, add the deferred comparison with a node built the old way, to be attempted by setting `compare_with_script` to `true` (FR-018)
  - Done 2026-11-23: `exportit/sandbox-terraform.map` gains `new proof/`; `exportit/REMINDERS.md` gains the deferred comparison with a node built the old way (FR-018). Recorded in `935e098`.
- [X] T015 Commit both units' work on their branches; record both submodules here; run the root `just test` and `just full-test`
  - Done 2026-11-23: the units' work committed on their branches and recorded (`935e098`); the root `just test` and `just full-test` passed, 16 targets each, the rehearsal 9 of 9.
- [X] T016 On the operator's word only: finish both units' branches into their `develop` and push; record their commits; the run uses those tags or commits
  - Done 2026-11-23, on the operator's word ("merge, A"): both units' branches squashed into their `develop` and pushed, kept: `csis-sandbox-terraform` `6e3b071`, `csis-sandbox-provisioning` `422f896`. With option A, the first boot's code tagged as it is now: `csis-sandbox-provisioning` `0.0.2` (`b6ab891`) and cloudflow `1.6.0b1` (`4f02034`), each version raised in its `pyproject.toml` (and lock) on a branch of its own, squashed into `develop`, tagged and pushed; `units.toml` records both (`csis-cloud-sandbox` `d7606ad`). The run's `proof.tfvars` takes `provisioning_version = "0.0.2"` and `cloudflow_version = "1.6.0b1"`.

**Checkpoint**: everything the run needs is merged and tested; no AWS call yet.

---

## Phase 3: User Story 1 - A head node built by the playbooks on AWS (Priority: P1) 🎯 MVP

**Goal**: a head node in the IOOS VPC, built by spec 006's first boot, applied again and checked by hand.

**Independent Test**: `site.yml`'s recap from the boot, the second apply and check mode.

- [X] T017 [US1] Box A1: `aws sts get-caller-identity` for the `noaa` account and `session-manager-plugin --version`; if either fails, stop and ask for the session to be refreshed (FR-001, FR-017)
  - Done 2026-11-23: the caller is the `noaa` account's SSO power-user role; `session-manager-plugin` 1.2.835.0.
- [X] T018 [US1] Boxes A2 and A3: the working copy at the unit's merged commit, `proof/` copied in, a new key pair on your local machine; the VPC by its name, its subnets and route tables listed; **YOUR DECISION** the subnet (default: the private one in the module's zone); `proof.tfvars` filled from the example; the VPC's, subnets' and route tables' descriptions saved on your local machine (research R6)
  - Done 2026-11-23: the working copy `$HOME/csis-live-proof` at `csis-sandbox-terraform` `6e3b071` with `proof/` in it; a key pair made for the proof on the local machine; the operator chose subnet 3, the IOOS VPC's private subnet in `us-east-2b`; `proof.tfvars` filled from the example; `vpc-before.json`, `subnets-before.json` and `routes-before.json` saved there.
- [X] T019 [US1] Box A4: `tofu init`, `tofu workspace new live-proof`, `tofu plan -var-file=proof.tfvars`; it must show only additions, `0 to change, 0 to destroy`, every resource with the prefix; otherwise stop (FR-003, FR-008)
  - Done 2026-11-23: `Plan: 22 to add, 0 to change, 0 to destroy`; every name with the deployment's prefix, the IAM role's name free in the account. **Finding:** OpenTofu's AWS provider cannot use the `noaa` SSO profile ("missing required configuration: sso_region, sso_start_url"), though the AWS CLI can; the plan ran with the session's temporary credentials exported (`aws configure export-credentials --profile noaa --format env`, `AWS_PROFILE` unset), never printed. Box A4 must say so.
- [X] T020 [US1] **(AWS, asked)** Box A5: `tofu apply`; the node's ID; an SSM session to it opens
  - Done 2026-11-23, on the operator's word ("apply"): `Apply complete! Resources: 22 added`; the node answered Session Manager (`Online`) a minute after.
- [X] T021 [US1] Box B1: follow the first boot (`/root/setup.log`, the plays' recap) until it ends, repeatable across sessions (research R8); record how long it took
  - Done 2026-11-23, at the third boot. The first, at `csis-sandbox-provisioning` `0.0.2`, stopped after ten seconds at "Silence the subscription-manager dnf plugin": the task edited `/etc/dnf/pluginconf.d/subscription-manager.conf`, the script's L34, and RHEL 10.2 has only `/etc/dnf/plugins/`; the script's `sed` failed unnoticed and the container test turns the task off. Fixed, on the operator's choice (B: the right path, edited only if it exists), as `0.0.3` (`af32eb5`, tagged and pushed); the node replaced. The second boot stopped at cloudflow's clone: the first boot's template makes the `/save` link only when the EFS volume has no `save/`, so a head node replaced on a kept volume has no `/save` (and the volume held the first clone). On the operator's choice (A), the volume was replaced with the node; the bug is a finding for a spec of its own (T039). The third boot, on a new volume, ran from 23:00 to 23:34 UTC: **34 minutes**, not the hours the procedure says. Spack built five packages (ESMF 8.9.1 in 7 minutes, PETSc, HDF5, netCDF-C, parallel-netCDF); Python, GCC and Intel's compilers and MPI were the system's. The log is kept as `logs/setup.log` in the working copy.
- [X] T022 [US1] Box B2: the boot's `site.yml` recap ends `failed=0`; the cloudflow install succeeded; the log says the image waits for stage C (SC-001; spec 006's first real use)
  - Done 2026-11-23: `ok=150 changed=67 unreachable=0 failed=0`; "Successfully installed cloudflow-1.6.0b1"; the last line "The node image is left for LIVE-PROOF.md's stage C." Spack's environment holds `esmf@8.9.1+mpi+pnetcdf` and `petsc+mpi`, built with oneAPI 2024.2.1.
- [X] T023 [US1] Box B3: the second apply by hand, `spack_site_mirror=true`, its recap kept as `site-second.log`; every task that changed is a finding, a change caused by an upstream release repeated once before it is called one (edge case)
  - Done 2026-11-23: `ok=134 changed=2 failed=0`, in about six minutes; kept as `logs/site-second.log`. **Findings:** "Update every installed package" changed, eleven packages released since the first apply (rdma-core 61.0-2, dkms 3.4.4 and others): upstream, and repeated by T024's check mode, which found nothing to change. "Silence the subscription-manager dnf plugin" changed again: the first apply's update ran after it and upgraded subscription-manager from 1.30.12 to 1.30.16, after which the file was back to `enabled=1`, though RPM marks it `%config(noreplace)`; the script has the same order. Check mode then found it unchanged.
- [X] T024 [US1] Box B4: check mode, kept as `site-check.log`; every task that would change is a finding
  - Done 2026-11-23: `ok=120 changed=0 failed=0`; kept as `logs/site-check.log`. No finding.
- [X] T025 [P] [US1] Box B5: Spack's configuration compared with `tests/container/expected-spack-config.json` by `tests/container/compare-spack-config.py`; each difference a finding
  - Done 2026-11-23: five differences. **Findings:** the site's mirror `s3-mirror` is among the mirrors (expected: the proof sets `spack_site_mirror=true`, the container does not); `bison`, `flex`, `gettext` and `openssl` are found as externals on RHEL 10.2, which the container does not have.
- [X] T026 [P] [US1] Box B6: every module file under the environment's root has the time it had after the boot (`refresh_modules: when_needed`)
  - Done 2026-11-23: no module file newer than the second apply's start. No finding.
- [X] T027 [US1] Box B7: `jupyterhub.yml` applied; the hub answers on its port, as `tests/jupyterhub-check.yml` checks it (FR-016)
  - Done 2026-11-23: `/hub/login` answered `200`; `ok=24 changed=21 failed=0`, kept as `logs/jupyterhub.log`. **Finding:** the box runs `jupyterhub.yml` without the six settings only a site can give, and the role refuses (as it should); it was run with the container test's values (`hub.example.invalid`, from `tests/container/vars.yml`). The box must name them.

**Checkpoint**: the node is built and its findings recorded.

---

## Phase 4: User Story 2 - An image a compute node can start from (Priority: P2)

- [X] T028 [US2] **(AWS, asked)** Box C1: `node-image.yml` on the head node, kept as `node-image.log`
  - Done 2026-11-23, on the operator's word ("make the image"): `ok=14 changed=5 failed=0` (the Prefect server stopped, the root volume snapshotted, the image registered, its id kept in the login user's home, Prefect started again); kept as `logs/node-image.log`. The image is named for the module's `ami_name` with `-Node` added.
- [X] T029 [US2] Box C2: from your local machine, `aws ec2 describe-images --owners self` for the prefix shows the image `available`, and its snapshot (SC-002)
  - Done 2026-11-23: one image, `CSIS-Live-Proof-happy-antelope-Node`, `available`, with one snapshot.
- [X] T030 [US2] Box D: with `compare_with_script = false`, skipped; record the last row of the "Not proved" table as deferred by the flag (SC-005)
  - Done 2026-11-23: skipped, `compare_with_script = false`; the comparison with a node built the original way stays deferred (`exportit/REMINDERS.md`, T014).

---

## Phase 5: User Story 3 - Nothing left behind (Priority: P2)

- [X] T031 [US3] Box E1: `tofu workspace show` prints `live-proof`; otherwise stop
  - Done 2026-11-23: `live-proof`.
- [X] T032 [US3] **(AWS, asked)** Box E2: `tofu destroy -var-file=proof.tfvars`; read the list before answering; `Destroy complete!`
  - Done 2026-11-23, on the operator's word ("destroy it"): the destroy planned first and its list read, exactly the 22 resources of T020; applied, "22 destroyed"; nothing left in the workspace's state but its data sources.
- [X] T033 [US3] **(AWS, asked)** Boxes E3 and E4: the image deregistered and its snapshot deleted, by ID
  - Done 2026-11-23: the one image with the prefix, `CSIS-Live-Proof-happy-antelope-Node`, deregistered, and its snapshot deleted, by ID (procedure box E3).
- [X] T034 [US3] Box E5: `aws resourcegroupstaggingapi get-resources` for the proof's `Project` tag, and `describe-images`/`describe-snapshots --owners self` for its prefix, all empty (SC-004)
  - Done 2026-11-23 (procedure box E4): images and snapshots with the prefix, none; the IAM role, none. **Finding:** the tagging API still listed four ARNs with the proof's tag minutes after: two of its instances, the snapshot and a volume; `describe-instances` showed one terminated and the other gone, `describe-snapshots` and `describe-volumes` "NotFound". The tagging API's index lags deletion; the box must say so, and check by the resources' own calls.
- [X] T035 [US3] Box E6: the VPC's, subnets' and route tables' descriptions taken again and compared with T018's: equal (SC-004)
  - Done 2026-11-23 (procedure box E5): the VPC as it was. The route tables as they were but for the order of two associations, the same two; the box's plain `diff` reports that, so it must sort first. The subnets as they were but for two free-address counts, neither the proof's: the proof's subnet had 34 more free than before, the other private subnet 20 fewer (other users of the VPC); noted, not a failure.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T036 In `specs/001-live-proof-on-aws/spec.md`, add an **Outcome** section: the date, the node's type and build time, every finding (T023 to T027), the image, the removal's checks; no address, ID or account identifier (FR-006)
  - Done 2026-11-23: `spec.md`'s **Outcome**: the run, the node's type and build time, a table of every check, the nine findings, and the "Not proved" table's state; no address, ID or account identifier. The status line says it was run.
- [X] T037 In `exportit/MAP.md`, mark each row of the "Not proved" table proved, with the date and what was seen, or not proved, with why (SC-003)
  - Done 2026-11-23: `exportit/MAP.md`: RHEL and AWS, the first boot, the drivers' and the tuning profile's installation, the build, the module files and the image proved, with the date and what was seen; that the drivers load on the image's kernel not proved (finding 7); the comparison deferred by the flag. Also its notes on the build, the site mirror's list, the procedure and the first-boot script.
- [X] T038 [P] In `exportit/sandbox-terraform/init_template.ansible.tpl`'s header, remove "Not run anywhere yet" (spec 006's T014), and link this outcome from spec 006's tasks
  - Done 2026-11-23: the template's header says spec 001 ran it, and names the kept-volume bug (`csis-sandbox-terraform` `cec0e5c`, on `feature/first-boot-proved`); spec 006's T014 links this outcome.
- [X] T039 [P] For each finding that needs fixing, a line in `exportit/REMINDERS.md` naming the unit it concerns, to become a spec of its own (Out of Scope)
  - Done 2026-11-23: `exportit/REMINDERS.md` gains three, each naming its unit: the kept volume's `/save` (`csis-sandbox-terraform`), the drivers' kernel and the plugin's order (`csis-sandbox-provisioning`). The procedure's own findings are fixed in its version 3 (`csis-sandbox-provisioning` `ffd65b2`, on `feature/live-proof-v3`), not reminded. The open item for the live proof itself is gone: it is done.
- [X] T040 [P] In `specs/README.md`, set 001's state
  - Done 2026-11-23: 001's row says it was run, links the outcome, and says it is not yet merged; the note on cost gives the run's times.
- [X] T041 Commit the units' last changes, if any, on their branches; record the submodules here; run `just constitution-check`
  - Done 2026-11-23: the units' last changes committed on their branches and recorded here: `csis-sandbox-provisioning` `3fc4a1b` (`feature/live-proof-v3`: `LIVE-PROOF.md` version 3, the README and DEPLOYMENT pages; on `0.0.3`'s `develop`), `csis-sandbox-terraform` `cec0e5c` (`feature/first-boot-proved`), `csis-cloud-sandbox` `7b46b4b` (`feature/provisioning-0.0.3`, recorded in T030's commit). `just constitution-check`: the shared part (2.1.0), CLAUDE.md and LICENSE agree in every unit. Each unit's `just test` and `just full-test` passed (provisioning 473 tests and the container applied twice, nothing changed the second time; terraform 34 and 5 slow).
- [X] T042 Run the root `just test` and `just full-test`
  - Done 2026-11-23: the root `just test` and `just full-test` passed; `units.toml` 15 units consistent, the sync rehearsal 9 of 9.
- [X] T043 Run `/speckit-converge` on `specs/001-live-proof-on-aws/`; record that it appended nothing, or carry out what it appended (done condition 2)
  - Done 2026-11-23: `/speckit-converge` appended Phase 7, T048 and T049 (two of the provisioning unit's pages still said nothing had been applied to a real head node, and gave only "several hours"); both carried out.
- [X] T044 Walk `specs/001-live-proof-on-aws/quickstart.md`'s "Done when", each line with its evidence from T017 to T035 (done condition 3)
  - Done 2026-11-23, each line of the quickstart's "Done when" with its evidence:
    - `site.yml` ended `failed=0`; the second apply's two changes and check mode's none are findings 3 and 4 (T022 to T024): **met** (SC-001).
    - The image was `available` (T029): **met** (SC-002).
    - Every row of `exportit/MAP.md`'s "Not proved" table is marked, proved or not with why (T037): **met** (SC-003).
    - Nothing with the prefix found, each resource asked by its own call, and the VPC, subnets and route tables as they were (T034, T035; the quickstart's E5 and E6 are the procedure's E4 and E5): **met** (SC-004), the tagging index's lag noted.
    - Stage D skipped with the flag `false`, recorded as deferred (T030): **met** (SC-005).
- [ ] T045 On the operator's word only: finish the units' branches and push, record their commits, then squash Cloud-Sandbox's `feature/live-proof` into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T046 Record that no release applies, unless the operator asks for one (done condition 5)
- [ ] T047 Mark the spec **complete**, with the date, only when T001 to T046 are checked, each with its record (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup, Foundational**: need spec 006 merged; T016 (merged on the operator's word) before any AWS task.
- **US1**: T017 to T027 in order, except T025 and T026, which can run together after T024.
- **US2**: after US1.
- **US3**: after US2 (and after D if the flag is `true`); E2 before E3; E5 and E6 last.
- **Polish**: after US3; T043 to T047 in order.

### Parallel Opportunities

- T003 and T004 (two repositories); T025 and T026; T038, T039 and T040.

---

## Implementation Strategy

1. Phase 2 merged: the run is reviewable before it is run.
2. The run, US1 to US3, in one sitting of several hours, the agent stopping at every gate.
3. The results recorded; findings become specs.

---

## Notes

- The node and everything with the prefix is billed from T020 until T034 finds nothing.
- Logs stay on your local machine; nothing from them that identifies the account goes into a repository.
- Nothing in `ATTIC/` is read for any task.

## Phase 7: Convergence

- [X] T048 In `exportit/sandbox-provisioning/README.md`'s "What has not been proved", say what spec 001's run proved on RHEL 10.2 and AWS and what it left not proved (the drivers on the image's kernel, the comparison with the old way), linking the outcome, in place of "No playbook here has been applied to a real head node" and "has itself not been run" per SC-003 (contradicts)
  - Done 2026-11-23: the section is now "What has been proved on AWS, and what has not": what the run proved, and the two things still not proved; `DEPLOYMENT.md`'s "What has not been proved", which said the same, now points at it.
- [X] T049 In `exportit/sandbox-provisioning/DEPLOYMENT.md`, beside "it takes several hours, depending on the head node's instance type", give the run's measure: 34 minutes for the first boot on a `c6i.8xlarge` per FR-009 (partial)
  - Done 2026-11-23: `DEPLOYMENT.md` adds the run's 34 minutes on a `c6i.8xlarge`.
