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
- [ ] T016 On the operator's word only: finish both units' branches into their `develop` and push; record their commits; the run uses those tags or commits

**Checkpoint**: everything the run needs is merged and tested; no AWS call yet.

---

## Phase 3: User Story 1 - A head node built by the playbooks on AWS (Priority: P1) 🎯 MVP

**Goal**: a head node in the IOOS VPC, built by spec 006's first boot, applied again and checked by hand.

**Independent Test**: `site.yml`'s recap from the boot, the second apply and check mode.

- [ ] T017 [US1] Box A1: `aws sts get-caller-identity` for the `noaa` account and `session-manager-plugin --version`; if either fails, stop and ask for the session to be refreshed (FR-001, FR-017)
- [ ] T018 [US1] Boxes A2 and A3: the working copy at the unit's merged commit, `proof/` copied in, a new key pair on your local machine; the VPC by its name, its subnets and route tables listed; **YOUR DECISION** the subnet (default: the private one in the module's zone); `proof.tfvars` filled from the example; the VPC's, subnets' and route tables' descriptions saved on your local machine (research R6)
- [ ] T019 [US1] Box A4: `tofu init`, `tofu workspace new live-proof`, `tofu plan -var-file=proof.tfvars`; it must show only additions, `0 to change, 0 to destroy`, every resource with the prefix; otherwise stop (FR-003, FR-008)
- [ ] T020 [US1] **(AWS, asked)** Box A5: `tofu apply`; the node's ID; an SSM session to it opens
- [ ] T021 [US1] Box B1: follow the first boot (`/root/setup.log`, the plays' recap) until it ends, repeatable across sessions (research R8); record how long it took
- [ ] T022 [US1] Box B2: the boot's `site.yml` recap ends `failed=0`; the cloudflow install succeeded; the log says the image waits for stage C (SC-001; spec 006's first real use)
- [ ] T023 [US1] Box B3: the second apply by hand, `spack_site_mirror=true`, its recap kept as `site-second.log`; every task that changed is a finding, a change caused by an upstream release repeated once before it is called one (edge case)
- [ ] T024 [US1] Box B4: check mode, kept as `site-check.log`; every task that would change is a finding
- [ ] T025 [P] [US1] Box B5: Spack's configuration compared with `tests/container/expected-spack-config.json` by `tests/container/compare-spack-config.py`; each difference a finding
- [ ] T026 [P] [US1] Box B6: every module file under the environment's root has the time it had after the boot (`refresh_modules: when_needed`)
- [ ] T027 [US1] Box B7: `jupyterhub.yml` applied; the hub answers on its port, as `tests/jupyterhub-check.yml` checks it (FR-016)

**Checkpoint**: the node is built and its findings recorded.

---

## Phase 4: User Story 2 - An image a compute node can start from (Priority: P2)

- [ ] T028 [US2] **(AWS, asked)** Box C1: `node-image.yml` on the head node, kept as `node-image.log`
- [ ] T029 [US2] Box C2: from your local machine, `aws ec2 describe-images --owners self` for the prefix shows the image `available`, and its snapshot (SC-002)
- [ ] T030 [US2] Box D: with `compare_with_script = false`, skipped; record the last row of the "Not proved" table as deferred by the flag (SC-005)

---

## Phase 5: User Story 3 - Nothing left behind (Priority: P2)

- [ ] T031 [US3] Box E1: `tofu workspace show` prints `live-proof`; otherwise stop
- [ ] T032 [US3] **(AWS, asked)** Box E2: `tofu destroy -var-file=proof.tfvars`; read the list before answering; `Destroy complete!`
- [ ] T033 [US3] **(AWS, asked)** Boxes E3 and E4: the image deregistered and its snapshot deleted, by ID
- [ ] T034 [US3] Box E5: `aws resourcegroupstaggingapi get-resources` for the proof's `Project` tag, and `describe-images`/`describe-snapshots --owners self` for its prefix, all empty (SC-004)
- [ ] T035 [US3] Box E6: the VPC's, subnets' and route tables' descriptions taken again and compared with T018's: equal (SC-004)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T036 In `specs/001-live-proof-on-aws/spec.md`, add an **Outcome** section: the date, the node's type and build time, every finding (T023 to T027), the image, the removal's checks; no address, ID or account identifier (FR-006)
- [ ] T037 In `exportit/MAP.md`, mark each row of the "Not proved" table proved, with the date and what was seen, or not proved, with why (SC-003)
- [ ] T038 [P] In `exportit/sandbox-terraform/init_template.ansible.tpl`'s header, remove "Not run anywhere yet" (spec 006's T014), and link this outcome from spec 006's tasks
- [ ] T039 [P] For each finding that needs fixing, a line in `exportit/REMINDERS.md` naming the unit it concerns, to become a spec of its own (Out of Scope)
- [ ] T040 [P] In `specs/README.md`, set 001's state
- [ ] T041 Commit the units' last changes, if any, on their branches; record the submodules here; run `just constitution-check`
- [ ] T042 Run the root `just test` and `just full-test`
- [ ] T043 Run `/speckit-converge` on `specs/001-live-proof-on-aws/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T044 Walk `specs/001-live-proof-on-aws/quickstart.md`'s "Done when", each line with its evidence from T017 to T035 (done condition 3)
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
