---

description: "Task list for reading a private playbooks' repository at first boot"
---

# Tasks: The first boot reads a private playbooks' repository

**Input**: Design documents from `specs/007-private-playbooks-access/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 006 merged

**Done**: (T031 to T034 added 2026-11-23, on the operator's word: the credential noted in every place a deployer reads) By the six conditions of the constitution's Development Workflow
(1.2.0): T026 to T030 are those conditions' tasks. Each task, when checked,
gets a record under it: what was done, and the evidence.

**Tests**: included, written first and seen to fail before the code they test
(principle IV; FR-009 names them).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: US1 (`none` unchanged), US2 (deploy key), US3 (token)

## Path Conventions

Paths are from the Cloud-Sandbox root; `csis-sandbox-terraform` is
`exportit/sandbox-terraform/`, committed in its own repository.

---

## Phase 1: Setup

- [ ] T001 Start `feature/private-playbooks-access` with git-flow in `exportit/sandbox-terraform/` from its `develop` (with spec 006 merged there), after checking it is clean and level with its origin
- [ ] T002 Run `just init` in `exportit/sandbox-terraform/` and the root `just test`

---

## Phase 2: Foundational (pin `none` before anything changes)

- [ ] T003 Write `exportit/sandbox-terraform/tests/golden/first-boot.none.sh`: the user data spec 006's template renders for fixed sample values (`just render-first-boot`'s values), byte for byte, before any template change (research R7)
- [ ] T004 In `exportit/sandbox-terraform/tests/test_template.py`, add the golden test: the template rendered with those values and `provisioning_access = "none"` equals the golden file; run `just test` (it passes now, and must keep passing)

**Checkpoint**: today's boot is pinned.

---

## Phase 3: User Story 1 - Nothing changes for a public repository (Priority: P1) 🎯 MVP

**Goal**: two new variables with `none` as the default, and no permission for `none`.

**Independent Test**: T004's golden comparison, and no policy planned for `none`.

### Tests first

- [ ] T005 [P] [US1] Write `exportit/sandbox-terraform/tests/access.tftest.hcl` with mocked `aws`, `random` and `local`: a `run` with no access variables asserts `length(aws_iam_role_policy.provisioning_secret) == 0` and `local.user_data` unchanged from the `none` rendering; a `run` with `provisioning_access = "other"` and `expect_failures = [var.provisioning_access]`
- [ ] T006 [US1] Run `just test` in the unit and see T005 fail for the right reason (the variable and resource are missing), recording which failed

### Implementation

- [ ] T007 [US1] In `exportit/sandbox-terraform/variables.tf`, add `provisioning_access` (string, default `"none"`, validation: one of `none`, `deploy_key`, `token`, its message listing the three) and `provisioning_secret_arn` (string, default `null`, validation: an `arn:aws:secretsmanager:` ARN when `provisioning_access` is not `none`) ([contracts/access-modes.md](contracts/access-modes.md))
- [ ] T008 [US1] In `exportit/sandbox-terraform/main.tf`, pass `provisioning_access` and `provisioning_secret_arn` to the template, and add `aws_iam_role_policy.provisioning_secret` with `count = var.provisioning_access == "none" ? 0 : 1`, allowing only `secretsmanager:GetSecretValue` on `var.provisioning_secret_arn` (research R2)
- [ ] T009 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, add the `%{ if provisioning_access != "none" ~}` … `%{ endif ~}` frame where the credential steps will go, empty, and run `just test`: T004 and T005 pass

**Checkpoint**: the choice exists; `none` is byte for byte spec 006's.

---

## Phase 4: User Story 2 - A private repository read with a deploy key (Priority: P2)

**Goal**: with `deploy_key`, the boot reads the key into `/run`, clones over SSH with pinned host keys, and removes it.

**Independent Test**: the rendered user data for `deploy_key`, without AWS; then quickstart step 2.

### Tests first

- [ ] T010 [P] [US2] In `exportit/sandbox-terraform/tests/access.tftest.hcl`, add: `deploy_key` with an SSH URL and an ARN plans one policy whose only resource is that ARN and only action `secretsmanager:GetSecretValue`; `deploy_key` without an ARN fails on `var.provisioning_secret_arn`; `deploy_key` with an HTTPS URL fails on `var.provisioning_repo`
- [ ] T011 [P] [US2] In `exportit/sandbox-terraform/tests/test_template.py`, add: rendered with `deploy_key`, the text has, in this order, `set +x`, the AWS CLI check, `get-secret-value --secret-id <arn>` written to a file under a `mktemp -d` in `/run`, the known-hosts file with GitHub's keys for `github.com` and `[ssh.github.com]:443`, `GIT_SSH_COMMAND` with `StrictHostKeyChecking=yes`, the clone, `ansible-pull`, the directory's removal, `set -x`; a `trap` removing the directory; no `accept-new`
- [ ] T012 [US2] Run them and see them fail for the right reason, recording which failed

### Implementation

- [ ] T013 [US2] Check whether the RHEL 10 image `data.aws_ami.rhel_10` selects carries the AWS CLI and git 2.31 or later (its package list, or AWS's and Red Hat's documentation), and whether Ansible's `git` module, as the boot installs it, passes `GIT_SSH_COMMAND` through when no key file is given; record both answers in `specs/007-private-playbooks-access/research.md` under R3 and R5
- [ ] T014 [US2] In `exportit/sandbox-terraform/variables.tf`, add to `provisioning_repo` the validation that `deploy_key` needs the SSH form (research R5)
- [ ] T015 [US2] In `exportit/sandbox-terraform/init_template.ansible.tpl`, inside the frame: the AWS CLI installed with AWS's installer unless `aws --version` answers; `set +x`; the temporary directory under `/run` (0700) and its `trap`; the secret read to a file (0600), failing with a line naming the secret and `exit 1` (no fallback); for `deploy_key`, GitHub's published host keys written to a known-hosts file there and `GIT_SSH_COMMAND` exported for the clone and `ansible-pull` (or `--private-key` if T013 found the environment is not passed); after `ansible-pull`, the directory removed and `set -x`
- [ ] T016 [US2] Run `just test` and `just full-test` in the unit: T010 and T011 pass; T004 still passes

**Checkpoint**: the deploy-key path is rendered and planned as the contract says.

---

## Phase 5: User Story 3 - A private repository read with a fine-grained token (Priority: P2)

**Goal**: with `token`, the boot reads the token into `/run`, clones over HTTPS with a credential helper, and removes it.

### Tests first

- [ ] T017 [P] [US3] In `exportit/sandbox-terraform/tests/access.tftest.hcl`, add: `token` with an HTTPS URL and an ARN plans the one policy; `token` without an ARN fails
- [ ] T018 [P] [US3] In `exportit/sandbox-terraform/tests/test_template.py`, add: rendered with `token`, the text sets `GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=credential.helper` and a `GIT_CONFIG_VALUE_0` helper that reads the token file, for the clone and `ansible-pull` only; no `x-access-token:` in a URL; no `extraHeader`; the refused-clone line says the token may have expired
- [ ] T019 [US3] Run them and see them fail for the right reason, recording which failed

### Implementation

- [ ] T020 [US3] In `exportit/sandbox-terraform/init_template.ansible.tpl`, inside the frame, the `token` branch: the helper given through the environment for the clone and `ansible-pull`, reading the token file; the clone's failure line naming a possible expiry (research R6)
- [ ] T021 [US3] Run `just test` and `just full-test` in the unit: T017 and T018 pass; T004 still passes

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T022 [P] In `exportit/sandbox-terraform/DEPLOYMENT.md`, for each mode: making the credential (a read-only deploy key; a fine-grained token, the repository only, `Contents: Read-only`, an expiry), keeping it in a new Secrets Manager secret with the sandbox's prefix under the account's default key, naming its ARN, renewing a token (FR-010)
- [ ] T031 [P] In `exportit/sandbox-terraform/README.md`'s "Two first-boot scripts", say that a private playbooks' repository needs `provisioning_access` and its credential (a read-only deploy key or a fine-grained token, in its own secret), that a public one needs none, and point at `DEPLOYMENT.md` (FR-011)
- [ ] T032 [P] In `exportit/sandbox-provisioning/DEPLOYMENT.md`'s "What happens at first boot" and `README.md`'s "How it is applied", say that the playbooks' clone needs that credential when their repository is private, and that without it the first boot stops before applying anything (FR-011), committed in `csis-sandbox-provisioning` on this spec's branch and recorded here
- [ ] T033 [P] In `exportit/MAP.md`'s `sandbox-terraform` first-boot section, the access modes and their credential; in `specs/README.md`, 007's row says a private playbooks' repository needs one (FR-011)
- [ ] T034 Search the places FR-010 and FR-011 list for "deploy key" and "token": each one says the credential is needed and points at how it is made (SC-006)
- [ ] T023 [P] In `specs/README.md`, set 007's state
- [ ] T024 Commit `csis-sandbox-terraform`'s work on its branch; record the submodule here; run `just constitution-check`
- [ ] T025 Run the root `just test` and `just full-test`
- [ ] T026 Run `/speckit-converge` on `specs/007-private-playbooks-access/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T027 Walk `specs/007-private-playbooks-access/quickstart.md`'s step 1, recording each command and result; record that step 2, on AWS, waits for someone who needs a private repository and the operator's word to make one (done condition 3, as far as it reaches without AWS)
- [ ] T028 On the operator's word only: finish `csis-sandbox-terraform`'s branch into its `develop` and push, record its commit, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T029 Record that no release applies, unless the operator asks for one (done condition 5)
- [ ] T030 Mark the spec **complete**, with the date, only when T001 to T029 are checked and quickstart step 2 has been run; until then it stays **merged** (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup**: needs spec 006 merged in the unit.
- **Foundational (T003, T004)**: before any template change.
- **US1**: after Phase 2; blocks US2 and US3 (the variables, the frame).
- **US2 and US3**: after US1; T013 before T015; US3 after US2's T015 (the shared steps).
- **Polish**: after US3; T031 to T034 with T022 and T023, before T024; then T026 to T030 in order.

### Parallel Opportunities

- T005; T010 and T011; T017 and T018; T022 and T023.

---

## Implementation Strategy

1. Pin `none` (Phase 2), then the variables (US1): the MVP is that nothing changes.
2. The deploy key (US2), then the token (US3).
3. The AWS proof when it is wanted.

---

## Notes

- No credential is ever created by a task; making one is the operator's.
- Nothing in `ATTIC/` is read for any task.
