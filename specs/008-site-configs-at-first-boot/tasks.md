---

description: "Task list for putting the site's descriptions on the head node at first boot"
---

# Tasks: The first boot puts the site's descriptions on the head node

**Input**: Design documents from `specs/008-site-configs-at-first-boot/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); **spec 007 built and merged** (its secret steps and its golden file, `tests/golden/first-boot.none.sh`)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T042 to T047 are those conditions' tasks. Each task, when checked,
gets a record under it: what was done, and the evidence.

**Tests**: included, written first and seen to fail before the code they test
(principle IV; FR-007 names them).

**AWS**: tasks marked **(AWS, asked)** wait for the operator's word. The
deploy key is the operator's to make; no task makes it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: US1 (the descriptions on a new head node), US2 (the guides say where)

## Path Conventions

From the Cloud-Sandbox root: `exportit/sandbox-terraform/`
(`csis-sandbox-terraform`), `exportit/sandbox-configs/`
(`csis-sandbox-configs`), `exportit/sandbox-provisioning/`, and the units of
research R5, each committed in its own repository.

---

## Phase 1: Setup

- [ ] T001 Check that spec 007 is merged in `exportit/sandbox-terraform/` (its `provisioning_access`, `aws_iam_role_policy.provisioning_secret` and `tests/golden/first-boot.none.sh` on `develop`); start `feature/site-configs-at-first-boot` with git-flow there and in `exportit/sandbox-configs/`, each clean and level with its origin
- [ ] T002 Run `just init` in both units and the root `just test`

---

## Phase 2: Foundational (pin spec 007's boot before anything changes)

- [ ] T003 In `exportit/sandbox-terraform/tests/test_template.py`, add a test that the template rendered with the configs settings unset (and `provisioning_access = "none"`) still equals `tests/golden/first-boot.none.sh` (SC-002); run `just test`: it passes now, and must keep passing

**Checkpoint**: an unset deployment's boot is pinned.

---

## Phase 3: User Story 1 - A new head node has the site's descriptions (Priority: P1) 🎯 MVP

**Goal**: three optional settings; when set, the first boot clones the site's descriptions with the deploy key, removes the key, and links them in two places.

**Independent Test**: the rendered user data and the plans, without AWS; then a head node's first boot.

### Tests first

- [ ] T004 [P] [US1] Write `exportit/sandbox-terraform/tests/configs.tftest.hcl` with mocked `aws`, `random` and `local`, as [contracts/configs-at-first-boot.md](contracts/configs-at-first-boot.md)'s table: unset, `length(aws_iam_role_policy.configs_secret) == 0`; set (an SSH URL, a tag, an ARN), one policy whose only action is `secretsmanager:GetSecretValue` and only resource that ARN; `configs_repo` without `configs_version` fails on `var.configs_version`; without `configs_secret_arn` fails on `var.configs_secret_arn`; an HTTPS `configs_repo` fails on `var.configs_repo`; with spec 007's `provisioning_access = "deploy_key"` and its ARN set as well, exactly two secret policies, each allowing `secretsmanager:GetSecretValue` on its own ARN only, and no wider grant (FR-005; the analysis of 2026-11-28); a pytest wrapper in `tests/test_plan.py` expecting the runs to pass
- [ ] T005 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, add: rendered with the three set, the text has, in this order, cloudflow's clone, `set +x`, a `mktemp -d` under `/run` handed to `$RUNUSER` (0700), `get-secret-value --secret-id <arn>` written to a file there (0600), GitHub's host keys for `github.com` and `[ssh.github.com]:443`, `StrictHostKeyChecking=yes`, the clone as `$RUNUSER` at the tag into `/save/$RUNUSER/sandbox-configs`, the directory removed, `set -x`, the four links (`/save/$RUNUSER/cloudflow/src/job.configs`, `…/cluster.configs`, `/save/$RUNUSER/Cloud-Sandbox/job.configs`, `…/cluster.configs`), the two lines added to cloudflow's `.git/info/exclude`, then the playbooks' fetch; a `trap` removing the directory; no `accept-new`; "Fetching the site's descriptions FAILED" followed by `exit 1`; the ARN present and no key material; and the kept-volume case of the spec's Edge Cases: the clone skipped when `/save/$RUNUSER/sandbox-configs` is a clone of `configs_repo` at `configs_version` (the links still made), and a line naming the path and what was found, then `exit 1`, when it is anything else
- [ ] T006 [P] [US1] Write `exportit/sandbox-terraform/tests/test_links.py`: in a temporary directory, the node's tree of research R2 (`save/u/cloudflow/src/cloudflow`, the `Cloud-Sandbox/cloudflow` link, `save/u/sandbox-configs/{job,cluster}.configs/<file>`), made by the same `ln -s` lines the rendered template holds (read from the rendering, with `$RUNUSER` and `/save` mapped into the directory); a program started in the `Cloud-Sandbox/cloudflow` link opens `../job.configs/<file>` and `../cluster.configs/<file>` and reads them, and `Cloud-Sandbox/job.configs/<file>` reads too
- [ ] T007 [US1] Run `just test` and see T004 to T006 fail for the right reason (the variables, the policy and the block are missing), recording which failed

### Implementation

- [ ] T008 [US1] In `exportit/sandbox-terraform/variables.tf`, add, as [data-model.md](data-model.md) says: `configs_repo` (string, `null`; "when set: SSH form, `git@github.com:<owner>/<repo>.git` or `ssh://git@ssh.github.com:443/<owner>/<repo>.git`"), `configs_version` (string, `null`; "required when `configs_repo` is set: a tag"), `configs_secret_arn` (string, `null`; "required when `configs_repo` is set: `arn:aws:secretsmanager:…`"), each validation's message naming the variable (research R1)
- [ ] T009 [US1] In `exportit/sandbox-terraform/main.tf`, pass the three to the template, and add `aws_iam_role_policy.configs_secret` with `count = var.configs_repo == null ? 0 : 1`, allowing only `secretsmanager:GetSecretValue` on `var.configs_secret_arn`, beside spec 007's `provisioning_secret` (research R6)
- [ ] T010 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, after cloudflow's clone and spec 006's link, a `%{ if configs_repo != null ~}` block as research R3 and R4 say: the AWS CLI installed unless `aws --version` answers (shared with spec 007's condition), `set +x`, the directory under `/run` for `$RUNUSER`, its `trap`, the secret read to a file, the known-hosts file, the clone as `$RUNUSER` with `GIT_SSH_COMMAND` and the tag, the failure line and `exit 1`, the directory removed, `set -x`, the four links, the two `exclude` lines; before the clone, the kept-volume check of the spec's Edge Cases (an existing clone at the tag kept, anything else stopping the boot with a line naming the path); and the template's header names the three new values
- [ ] T011 [US1] Run the unit's `just test` and `just full-test`: T003 to T006 pass
- [ ] T012 [P] [US1] In `exportit/sandbox-terraform/DEPLOYMENT.md`, beside spec 007's section on the playbooks' credential: the three settings; how to make the deploy key (`ssh-keygen -t ed25519`), add its public half to `csis-sandbox-configs` as a read-only deploy key, put its private half in a new Secrets Manager secret with the sandbox's prefix under the account's default key, name its ARN, and replace it; that without it the site's descriptions are not on the node (FR-008)
- [ ] T013 [P] [US1] In `exportit/sandbox-terraform/README.md`'s first-boot section, the clone of the site's descriptions, its key, and the two places of the links (FR-008)
- [ ] T014 [P] [US1] In `exportit/sandbox-terraform/proof/proof.tfvars.example`, the three settings, commented out, saying what they need
- [ ] T015 [US1] Commit `csis-sandbox-terraform`'s work on its branch; record it here; run the root `just test` and `just full-test`
- [ ] T016 [US1] On the operator's word only: finish `csis-sandbox-terraform`'s branch into its `develop` and push; record its commit (the AWS steps use it)
- [ ] T017 [US1] On the operator's word only: tag `csis-sandbox-configs`' `develop` as `0.0.2` and push (research R7); record the commit
- [ ] T018 [US1] The operator makes the deploy key on the local machine and adds its public half to `csis-sandbox-configs` as read-only (GitHub's settings); record that it was done and its fingerprint, never the key
- [ ] T019 [US1] **(AWS, asked)** The secret: its private half put in a new Secrets Manager secret by the operator, or by the agent from the file on the operator's word (`--secret-string file://…`, never on a command line); record its name, not its ARN in a repository
- [ ] T020 [US1] **(AWS, asked)** A head node, as spec 001's tasks T017 to T022 (its stages A and B), with `configs_repo`, `configs_version` (`0.0.2`) and `configs_secret_arn` in `proof.tfvars`. A first boot that fails at `base_system`'s package update with a downloaded RPM missing from dnf's cache is the account's patch scan (spec 004's T017; `csis-sandbox-provisioning`'s spec 001), not this spec's: the node is replaced as LIVE-PROOF.md's box B2 says, and the failure recorded
- [ ] T021 [US1] On the node: the boot's recap `failed=0`; `/save/$RUNUSER/sandbox-configs` at `0.0.2`; from `/save/$RUNUSER/Cloud-Sandbox/cloudflow`, `ls ../job.configs/` and a Python `open('../cluster.configs/<a site file>')` reach the site's files; `Cloud-Sandbox/job.configs/<file>` too; cloudflow's `git status` clean (SC-001, SC-004)
- [ ] T022 [US1] A search of the node for the key's text (`grep -rF` of a line of the private key, given by the operator as a file and never shown, over `/`, `/run`, the cloud-init logs and the EFS volume): nothing found (SC-003)
- [ ] T023 [US1] **(AWS, asked)** The node removed as spec 001's tasks T031 to T035 (stage E); the secret and the deploy key kept unless the operator says otherwise

**Checkpoint**: a new head node has the site's descriptions where the guides look.

---

## Phase 4: User Story 2 - The run guides say where the descriptions are (Priority: P2)

**Goal**: every guide that names the old relative paths carries the note of FR-006, each in its own unit, the commands left as they are.

**Independent Test**: a search of the units for `../job.configs/` and `../cluster.configs/` finds only guides that carry the note (SC-004).

- [ ] T024 [P] [US2] In `csis-cloud-sandbox` (`exportit/cloud-sandbox/`), `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`: the note (research R5), committed on a branch of that unit
- [ ] T025 [P] [US2] In `cloudflow` (`exportit/cloudflow/`), `docs/CLOUDFLOW_MODEL_EXECUTION_INSTRUCTIONS.md` and `docs/CLOUDFLOW_PYTHON_MODEL_EXECUTION_INSTRUCTIONS.md`: the note, committed on a branch of that unit
- [ ] T026 [P] [US2] In `csis-model-liveocean` (`exportit/model-liveocean/`), `LIVEOCEAN-MODEL.md` and `README`: the note, committed on a branch of that unit
- [ ] T027 [P] [US2] In `csis-model-nosofs` (`exportit/model-nosofs/`), `NOSOFS-MODELS.md`: the note, committed on a branch of that unit
- [ ] T028 [P] [US2] In `csis-model-secofs` (`exportit/model-secofs/`), `README.md`: the note, committed on a branch of that unit
- [ ] T029 [P] [US2] In `csis-model-ucla-roms` (`exportit/model-ucla-roms/`), `README`: the note, committed on a branch of that unit
- [ ] T030 [P] [US2] In `csis-model-ufscoastal` (`exportit/model-ufscoastal/`), `README`: the note, committed on a branch of that unit
- [ ] T031 [P] [US2] In `csis-sandbox-configs` (`exportit/sandbox-configs/`), `README.md`: the note, and that the repository is private and head nodes read it with the deploy key (FR-008), on its branch
- [ ] T032 [US2] Search every unit again for `../job.configs/` and `../cluster.configs/` in Markdown and `README*` files: each file found carries the note; any new one found is given it, recorded (SC-004); run each changed unit's `just test`

The note, in each: on a head node, these paths reach the site's descriptions
in `/save/$RUNUSER/sandbox-configs` through links the first boot makes, and
only when the deployment set `configs_repo` and its deploy key
(`csis-sandbox-terraform`'s `DEPLOYMENT.md`).

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T033 [P] In `exportit/sandbox-provisioning/DEPLOYMENT.md`, "What happens at first boot": the clone of the site's descriptions, its key, and that without it they are not on the node (FR-008), committed in `csis-sandbox-provisioning` on a branch
- [ ] T034 [P] In `exportit/MAP.md`'s `sandbox-terraform` first-boot section: the settings, the key, the clone and the two places of the links (FR-008)
- [ ] T035 [P] In `specs/README.md`, set 008's state
- [ ] T036 Search the places FR-008 lists for `configs_secret_arn` and "deploy key": each one says the key is needed, and how it is made and kept (SC-005)
- [ ] T037 Commit the units' last changes on their branches; record the submodules here; run `just constitution-check`
- [ ] T038 Run the root `just test`
- [ ] T039 Run the root `just full-test`
- [ ] T040 In `specs/008-site-configs-at-first-boot/spec.md`, an **Outcome** section: the date, the clone and the links seen on the node, the key search's result, the guides changed; no identifiers
- [ ] T041 Re-read [quickstart.md](quickstart.md) against what was run; correct it if a step differed
- [ ] T042 Run `/speckit-converge` on `specs/008-site-configs-at-first-boot/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T043 Walk `specs/008-site-configs-at-first-boot/quickstart.md`, each step with its evidence from the tasks above (done condition 3)
- [ ] T044 On the operator's word only: finish every unit's branch (`csis-sandbox-terraform` if not done at T016, `csis-sandbox-configs`, `csis-sandbox-provisioning`, and the units of T024 to T030) into its `develop` and push, record their commits, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T045 Record the release: `csis-sandbox-configs` `0.0.2` (T017), cut on the operator's word; no other release applies unless the operator asks (done condition 5)
- [ ] T046 Record that the secret and the deploy key are kept, with what they are for, in the outcome and in `exportit/REMINDERS.md` if anything about them is left to do
- [ ] T047 Mark the spec **complete**, with the date, only when T001 to T046 are checked (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup**: needs spec 007 merged in `csis-sandbox-terraform`.
- **Foundational (T003)**: before any template change.
- **US1**: after Phase 2; T004 to T006 before T008; T008 to T010 in order; T016 before any AWS task; T017 to T019 before T020; T020 to T023 in order.
- **US2**: independent of US1's code and of AWS; can run alongside it; T032 after T024 to T031.
- **Polish**: after US1 and US2; T033 to T036 before T037; then T037 to T047 in order.

### Parallel Opportunities

- T004, T005 and T006; T012, T013 and T014; T024 to T031 (eight units); T033, T034 and T035.

---

## Implementation Strategy

1. Pin spec 007's boot (Phase 2), then the settings, the policy, the block and their tests (US1): the MVP, provable without AWS.
2. The notes in the guides (US2), alongside.
3. The tag, the key, the secret and one head node, each on the operator's word.

---

## Notes

- The deploy key's private half is never in a repository, a variable, a command line or a log; the operator makes it.
- Nothing in `ATTIC/` is read for any task.
