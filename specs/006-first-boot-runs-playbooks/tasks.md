---

description: "Task list for the first boot that runs the playbooks"
---

# Tasks: The first boot runs the playbooks

**Input**: Design documents from `specs/006-first-boot-runs-playbooks/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T024 to T028 are those conditions' tasks. Each task, when checked,
gets a record under it: what was done, and the evidence (a commit, a run, a
count).

**Tests**: included, written first and seen to fail before the code they test
(principle IV; FR-004 names them).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: the user story the task belongs to (US1)

## Path Conventions

Paths are from the Cloud-Sandbox root. `csis-sandbox-terraform` is the
submodule `exportit/sandbox-terraform/`; a change there is committed in that
unit's own repository.

---

## Phase 1: Setup

- [X] T001 Start `feature/first-boot-runs-playbooks` with git-flow in `exportit/sandbox-terraform/` from its `develop`, after checking it is clean and level with its origin (Cloud-Sandbox's branch already exists)
  - Done 2026-11-22: `feature/first-boot-runs-playbooks` made in `csis-sandbox-terraform` from its `develop` (`7cf68b2`, clean and level with origin); Cloud-Sandbox's branch existed and had `develop` merged in (`34f08b9`).
- [X] T002 Run `just init` in `exportit/sandbox-terraform/` and the root `just test`, to start from passing acceptance tests
  - Done 2026-11-22: the unit's `just init` passed; the root `just test` had passed on the same tree as `develop` just before (spec 003's final run, `74ea9be`).

---

## Phase 2: Foundational

**Purpose**: `main.tf` renders its user data through a `local`, which every later test reads (research R4).

- [X] T003 In `exportit/sandbox-terraform/main.tf`, move the `templatefile(...)` call out of `aws_instance.head_node` into `locals { user_data = ... }` and set `user_data = local.user_data`, still rendering `init_template.tpl` with today's values; in `tests/support.py`, make `template_variables()` read the call from `local.user_data`; run `just test` (nothing else changes)
  - Done 2026-11-22: `csis-sandbox-terraform` `e1b3700`: `locals { user_data = templatefile(...) }`, the instance takes `local.user_data`; `template_variables()` checks the instance takes it; `just test` 26 passed, nothing changed.

**Checkpoint**: the user data is one named value; behaviour unchanged.

---

## Phase 3: User Story 1 - A new head node builds itself from the playbooks (Priority: P1) 🎯 MVP

**Goal**: `main.tf` renders `init_template.ansible.tpl` with the four values; the first boot clones the playbooks and cloudflow from their public repositories, applies the plays, installs cloudflow, and makes the image.

**Independent Test**: the rendered user data, held to the template, and a mocked plan, without AWS ([quickstart.md](quickstart.md)).

### Tests first (they must fail before T010)

- [X] T004 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, rewrite `test_main_tf_renders_the_template_that_is_here`: `main.tf` renders `init_template.ansible.tpl`, and the names it passes are exactly `efs_name`, `ami_name`, `aws_region`, `project`, `provisioning_repo`, `provisioning_version`, `cloudflow_repo`, `cloudflow_version` ([contracts/first-boot.md](contracts/first-boot.md)); and a test that the template's own placeholders are that same set
  - Done 2026-11-22: `tests/test_template.py` rewritten: `main.tf` renders `init_template.ansible.tpl` with the eight names in order; the template's placeholders are those names but `aws_region`, which is passed and unused, as it was before; each of the four new values is needed.
- [X] T005 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, write the order test: in the rendered text the cloudflow clone (`git clone --quiet --branch "<cloudflow_version>" "<cloudflow_repo>" /save/$RUNUSER/cloudflow`) and the link come before the playbooks' clone, `ansible-pull` before `pip install --user --no-deps --editable`, and that before `node-image.yml`; no line names `ioos/Cloud-Sandbox`; each clone and the install is followed by its `FAILED` line and `exit 1` (research R6)
  - Done 2026-11-22: the order test (cloudflow's clone, the link, the playbooks' clone, `ansible-pull`, the install, `node-image.yml`); no `ioos/Cloud-Sandbox`; each clone and the install followed by its `FAILED` line and `exit 1`.
- [X] T006 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, keep a test that `init_template.tpl` still renders with the five values it names, `sandbox_version` among them (research R5)
  - Done 2026-11-22: the old template still renders with the values it names (three of the five it was given).
- [X] T007 [P] [US1] Write `exportit/sandbox-terraform/tests/firstboot.tftest.hcl`: `mock_provider` for `aws` (with `mock_data "aws_ami"` giving an ID), `random` and `local`; one `run` with `command = plan` and sample values for the four variables and the module's required ones, asserting `local.user_data` contains both repositories and versions and `ansible-pull`, and does not contain `ioos/Cloud-Sandbox`
  - Done 2026-11-22: `tests/firstboot.tftest.hcl`: mocked `aws` (an AMI ID), `random` and `local`; one plan run asserting `local.user_data` names both repositories and tags and `ansible-pull`, not `ioos/Cloud-Sandbox`, and that the instance is given it.
- [X] T008 [P] [US1] Write `exportit/sandbox-terraform/tests/test_plan.py` (marked `slow`): copy the module to a temporary directory with a `backend_override.tf` giving a `local` backend, `tofu init` from the plugin cache, `tofu plan -input=false` with every required value but `provisioning_repo`; assert a non-zero exit and a message naming `provisioning_repo` (SC-001); and a pytest wrapper that runs `tofu test` (T007) in the unit
  - Done 2026-11-22: `tests/test_plan.py`: the `tofu test` wrapper; and, `slow`, a copy of the module with a local backend, `tofu init`, `tofu plan` without `provisioning_repo`: non-zero, `No value for required variable` naming it, before any provider call.
- [X] T009 [US1] Run `just test` and `just full-test` in `exportit/sandbox-terraform/` and see T004, T005, T007 and T008 fail for the right reason (the old template rendered, the variables missing), recording which failed under this task
  - Done 2026-11-22: 8 of the 9 new tests failed for the right reason (the old template rendered; the variables undeclared). The ninth, the old template's, failed on my own assertion (its placeholders equal to the five values; it uses three) and was corrected to a subset.

### Implementation

- [X] T010 [US1] In `exportit/sandbox-terraform/variables.tf`, add `provisioning_repo`, `provisioning_version`, `cloudflow_repo` and `cloudflow_version`, each `type = string`, `nullable = false`, no default, with a description naming what it is ([data-model.md](data-model.md)); remove `sandbox_version` (research R1)
  - Done 2026-11-22: the four variables, `type = string`, `nullable = false`, no default, each described; `sandbox_version` removed, and with it its output (now `provisioning_version` and `cloudflow_version`) and its line in `mysettings.tfvars` (now today's four values).
- [X] T011 [US1] In `exportit/sandbox-terraform/main.tf`, make `local.user_data` render `init_template.ansible.tpl` with `efs_name`, `ami_name`, `aws_region`, `project` and the four new variables
  - Done 2026-11-22: `local.user_data` renders `init_template.ansible.tpl` with the eight values.
- [X] T012 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, replace the clone of `ioos/Cloud-Sandbox` (and `BRANCH=${sandbox_version}`) with the cloudflow clone at `${cloudflow_version}` into `/save/$RUNUSER/cloudflow` as `$RUNUSER`, its `FAILED` line and `exit 1`, and the link `/save/$RUNUSER/Cloud-Sandbox/cloudflow` → `/save/$RUNUSER/cloudflow/src/cloudflow` (research R2, R3)
  - Done 2026-11-22: the clone of `ioos/Cloud-Sandbox` and `BRANCH=` replaced by cloudflow's clone at its tag into `/save/$RUNUSER/cloudflow` as `$RUNUSER`, with `Fetching cloudflow FAILED` and `exit 1`, and the link `/save/$RUNUSER/Cloud-Sandbox/cloudflow` → `…/cloudflow/src/cloudflow`.
- [X] T013 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, after `ansible-pull` succeeds and before the node image, install cloudflow as `$RUNUSER` with `python3 -m pip install --user --no-deps --editable /save/$RUNUSER/cloudflow`, with its `FAILED` line and `exit 1` (research R2)
  - Done 2026-11-22: after `ansible-pull`, before the image, `sudo -u $RUNUSER python3 -m pip install --user --no-deps --editable /save/$RUNUSER/cloudflow`, with `Installing cloudflow FAILED` and `exit 1`.
- [X] T014 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`'s header, replace "Terraform has to pass two values more than it does today" with the eight values `main.tf` passes, say that `main.tf` renders this template and `init_template.tpl` is kept for comparison and sync, and remove "Not run anywhere yet" only once spec 001 has run it
  - Done 2026-11-22: the header names the eight values, says `main.tf` renders this template and `init_template.tpl` is kept for comparison and sync; "Not run anywhere yet" stays until spec 001 runs it.
- [X] T015 [US1] Run `just test` and `just full-test` in `exportit/sandbox-terraform/`: T004 to T008 pass, every module still validates, formatting as recorded
  - Done 2026-11-22: `csis-sandbox-terraform` `4c29342`; `just test` 30 passed, `just full-test` 3 slow passed; every module validates; formatting as recorded. Two assertions of mine corrected on the way: the first `ln -s` in the template is its older `/save` link (the test now names the cloudflow link), and `aws_region` is passed and unused.
- [X] T016 [P] [US1] In `exportit/sandbox-terraform/Justfile`, add `render-first-boot`: render `local.user_data`'s template with sample values through `tofu console` and print it (the plan's quickstart, step 2)
  - Done 2026-11-22: `just render-first-boot`, rendering in an empty directory (the module's own wants its S3 backend) with today's repositories and tags.
- [X] T017 [P] [US1] In `exportit/sandbox-terraform/DEPLOYMENT.md`, add the four values: what each is, that `provisioning_repo` is `csis-sandbox-provisioning`'s URL and `provisioning_version` one of its tags, `cloudflow_repo` and `cloudflow_version` likewise, today's tags (`0.0.1`, `1.6.0b0`), that all four are required, and that `sandbox_version` is gone (FR-005)
  - Done 2026-11-22: `DEPLOYMENT.md` step 4: the four values, today's tags, all required, tags not branches, both repositories public; how the first boot differs from the original's. `csis-sandbox-terraform` `e9093e8`.

**Checkpoint**: a plan without AWS shows the new first boot; a plan without `provisioning_repo` fails naming it.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T018 [P] In `exportit/REMINDERS.md`, add "Remove the link at `/save/$RUNUSER/Cloud-Sandbox/cloudflow`": the job descriptions and cloudflow scripts that name the old path (research R3's table), to change in their own units, after which the template's link goes
  - Done 2026-11-22: `exportit/REMINDERS.md`: "Remove the link at `/save/$RUNUSER/Cloud-Sandbox/cloudflow`", pointing at research R3's table.
- [X] T019 [P] In `exportit/MAP.md`'s `sandbox-terraform` section, say that `main.tf` renders `init_template.ansible.tpl` with four required values, and that the first boot no longer clones the original
  - Done 2026-11-22: `exportit/MAP.md`'s first-boot section describes the switch, the four values, the first boot's steps and its tests.
- [X] T020 [P] In `specs/README.md`, set 006's state (**in progress** until T026)
  - Done 2026-11-22: `specs/README.md`, 006 **in progress** (implemented, not yet merged).
- [X] T021 Commit `csis-sandbox-terraform`'s work on its `feature/first-boot-runs-playbooks`; record the submodule here (`git add exportit/sandbox-terraform`); run `just constitution-check`
  - Done 2026-11-22: the unit's branch recorded here (`da23987`); `just constitution-check`: every unit agrees.
- [X] T022 Run the root `just test`
  - Done 2026-11-22: the root `just test` passed, 16 targets.
- [X] T023 Run the root `just full-test`
  - Done 2026-11-22: the root `just full-test` passed, 16 targets: lineage of every unit, the sync rehearsal 8 of 8; `csis-sandbox-terraform` 30 and 3 slow passed.
- [X] T024 Run `/speckit-converge` on `specs/006-first-boot-runs-playbooks/` after the last implementation task; record under this task that it appended nothing, or carry out every task it appended before going on (done condition 2)
  - Done 2026-11-22: `/speckit-converge` appended nothing: converged. Two LOW findings, neither actionable: `outputs.tf` and `mysettings.tfvars` changed though the plan's list does not name them (they named `sandbox_version`, which FR-001 removes); `aws_region` is passed and no placeholder uses it (as before this spec; the test says so).
- [X] T025 Walk `specs/006-first-boot-runs-playbooks/quickstart.md` step by step, recording each step's command and result under this task, all passing (done condition 3)
  - Done 2026-11-22, each step's command and result: 1. `just test` and `just full-test` in `exportit/sandbox-terraform`: 30 and 3 passed (the template's names and order, the mocked plan, the plan without `provisioning_repo` failing on it); 2. `just render-first-boot`: cloudflow cloned at `1.6.0b0`, the link, the playbooks cloned at `0.0.1`, `ansible-pull`, the install, in that order; no line names a credential or `ioos/Cloud-Sandbox`; 3. the root `just test` and `just full-test`: passed (T022, T023).
- [ ] T026 On the operator's word only: finish `csis-sandbox-terraform`'s branch into its `develop` and push, record its `develop` commit here, then squash Cloud-Sandbox's `feature/first-boot-runs-playbooks` into `develop` from its tree and push, with `just submodules-pushed` first; until then **in progress**, then **merged** (done condition 4)
- [ ] T027 Record under this task that no release applies (the plan names none; the unit's `release` target says nothing is released from it; `exportit/REMINDERS.md` keeps "Releasing from a unit's own repository" open), unless the operator asks for one (done condition 5)
- [ ] T028 Mark the spec **complete**, with the date, in its Status line and its row in `specs/README.md`, only when T001 to T027 are checked, each with its record; the first real boot is spec 001's, whose outcome is linked here when it runs (done conditions 1 and 6)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none.
- **Foundational (Phase 2)**: after Setup; T003 blocks every test that reads `local.user_data`.
- **US1 (Phase 3)**: after T003; tests T004 to T008, then T009, then T010 to T014 in order (one template), T015, then T016 and T017.
- **Polish (Phase 4)**: after US1; T024, T025, T026 (operator's word), T027, T028 in that order.

### User Story Dependencies

- **US1 (P1)**: the only story; spec 007 and spec 001 build on it.

### Parallel Opportunities

- T004 to T008 (different files or independent tests in one file).
- T016 and T017; T018, T019 and T020.

---

## Parallel Example: User Story 1

```text
Task: "T007 [US1] the mocked plan in exportit/sandbox-terraform/tests/firstboot.tftest.hcl"
Task: "T008 [US1] the plan without provisioning_repo in exportit/sandbox-terraform/tests/test_plan.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1 and T003.
2. The tests, failing; then the variables, `main.tf`, the template.
3. Stop and validate: `just test` and `just full-test` in the unit, then the root's.

### Incremental Delivery

One story: deployable, not deployed. Its first real boot is spec 001's.

---

## Notes

- Nothing in any task creates, changes or removes anything in an AWS account.
- `init_template.tpl` is not edited (research R5).
- Nothing in `ATTIC/` is read for any task.

---

## Phase 5: Convergence

- [X] T029 Rewrite `exportit/sandbox-terraform/README.md`'s "Two first-boot scripts" section and the lines that say `main.tf` "stays the same as the original" and that `init_template.tpl` is the one "used": `main.tf` renders `init_template.ansible.tpl` into `local.user_data` with the eight values; `init_template.tpl` is kept, unused, for comparison and sync; remove the "Switching `main.tf` to the second needs two more values" instructions, which describe a change now made, per FR-001 (contradicts)
  - Done 2026-11-22: `csis-sandbox-terraform` `b8de3b1`: the README's "Two first-boot scripts" says `main.tf` renders `init_template.ansible.tpl`, what it does, its eight values; `init_template.tpl` kept unused; the switch-over instructions removed; the file table lists the Ansible template and `reaper/`. The unit's `just test`: 30 passed.
- [X] T030 Update `exportit/MAP.md`'s `sandbox-provisioning` section, "The first-boot script", which says Terraform "would have to pass two more values" and that the first boot "still clones Cloud-Sandbox, because cloudflow runs from that checkout": both are no longer true; say what the first boot does now and point to the `sandbox-terraform` section, per FR-001 and FR-002 (contradicts)
  - Done 2026-11-22: `exportit/MAP.md`'s `sandbox-provisioning` "The first-boot script" says what the first boot does since spec 006, that nothing of the original is cloned, and links the `sandbox-terraform` section.
- [X] T031 In `exportit/sandbox-provisioning/DEPLOYMENT.md`'s "What happens at first boot", add the steps the first boot now has around the playbooks (cloudflow cloned from its own repository before them, installed after them), committed in `csis-sandbox-provisioning` on a `feature/first-boot-runs-playbooks` branch and recorded here, per FR-002 (partial)
  - Done 2026-11-22: `csis-sandbox-provisioning` `c476cdb`, on `feature/first-boot-runs-playbooks` from its `develop` (`e8c4b41`, clean and level with origin): `DEPLOYMENT.md`'s five first-boot steps, cloudflow's clone and install among them. The unit's `just test`: 458 passed. Recorded here with T029's commit.
