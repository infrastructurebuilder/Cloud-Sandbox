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

- [ ] T001 Start `feature/first-boot-runs-playbooks` with git-flow in `exportit/sandbox-terraform/` from its `develop`, after checking it is clean and level with its origin (Cloud-Sandbox's branch already exists)
- [ ] T002 Run `just init` in `exportit/sandbox-terraform/` and the root `just test`, to start from passing acceptance tests

---

## Phase 2: Foundational

**Purpose**: `main.tf` renders its user data through a `local`, which every later test reads (research R4).

- [ ] T003 In `exportit/sandbox-terraform/main.tf`, move the `templatefile(...)` call out of `aws_instance.head_node` into `locals { user_data = ... }` and set `user_data = local.user_data`, still rendering `init_template.tpl` with today's values; in `tests/support.py`, make `template_variables()` read the call from `local.user_data`; run `just test` (nothing else changes)

**Checkpoint**: the user data is one named value; behaviour unchanged.

---

## Phase 3: User Story 1 - A new head node builds itself from the playbooks (Priority: P1) 🎯 MVP

**Goal**: `main.tf` renders `init_template.ansible.tpl` with the four values; the first boot clones the playbooks and cloudflow from their public repositories, applies the plays, installs cloudflow, and makes the image.

**Independent Test**: the rendered user data, held to the template, and a mocked plan, without AWS ([quickstart.md](quickstart.md)).

### Tests first (they must fail before T010)

- [ ] T004 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, rewrite `test_main_tf_renders_the_template_that_is_here`: `main.tf` renders `init_template.ansible.tpl`, and the names it passes are exactly `efs_name`, `ami_name`, `aws_region`, `project`, `provisioning_repo`, `provisioning_version`, `cloudflow_repo`, `cloudflow_version` ([contracts/first-boot.md](contracts/first-boot.md)); and a test that the template's own placeholders are that same set
- [ ] T005 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, write the order test: in the rendered text the cloudflow clone (`git clone --quiet --branch "<cloudflow_version>" "<cloudflow_repo>" /save/$RUNUSER/cloudflow`) and the link come before the playbooks' clone, `ansible-pull` before `pip install --user --no-deps --editable`, and that before `node-image.yml`; no line names `ioos/Cloud-Sandbox`; each clone and the install is followed by its `FAILED` line and `exit 1` (research R6)
- [ ] T006 [P] [US1] In `exportit/sandbox-terraform/tests/test_template.py`, keep a test that `init_template.tpl` still renders with the five values it names, `sandbox_version` among them (research R5)
- [ ] T007 [P] [US1] Write `exportit/sandbox-terraform/tests/firstboot.tftest.hcl`: `mock_provider` for `aws` (with `mock_data "aws_ami"` giving an ID), `random` and `local`; one `run` with `command = plan` and sample values for the four variables and the module's required ones, asserting `local.user_data` contains both repositories and versions and `ansible-pull`, and does not contain `ioos/Cloud-Sandbox`
- [ ] T008 [P] [US1] Write `exportit/sandbox-terraform/tests/test_plan.py` (marked `slow`): copy the module to a temporary directory with a `backend_override.tf` giving a `local` backend, `tofu init` from the plugin cache, `tofu plan -input=false` with every required value but `provisioning_repo`; assert a non-zero exit and a message naming `provisioning_repo` (SC-001); and a pytest wrapper that runs `tofu test` (T007) in the unit
- [ ] T009 [US1] Run `just test` and `just full-test` in `exportit/sandbox-terraform/` and see T004, T005, T007 and T008 fail for the right reason (the old template rendered, the variables missing), recording which failed under this task

### Implementation

- [ ] T010 [US1] In `exportit/sandbox-terraform/variables.tf`, add `provisioning_repo`, `provisioning_version`, `cloudflow_repo` and `cloudflow_version`, each `type = string`, `nullable = false`, no default, with a description naming what it is ([data-model.md](data-model.md)); remove `sandbox_version` (research R1)
- [ ] T011 [US1] In `exportit/sandbox-terraform/main.tf`, make `local.user_data` render `init_template.ansible.tpl` with `efs_name`, `ami_name`, `aws_region`, `project` and the four new variables
- [ ] T012 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, replace the clone of `ioos/Cloud-Sandbox` (and `BRANCH=${sandbox_version}`) with the cloudflow clone at `${cloudflow_version}` into `/save/$RUNUSER/cloudflow` as `$RUNUSER`, its `FAILED` line and `exit 1`, and the link `/save/$RUNUSER/Cloud-Sandbox/cloudflow` → `/save/$RUNUSER/cloudflow/src/cloudflow` (research R2, R3)
- [ ] T013 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`, after `ansible-pull` succeeds and before the node image, install cloudflow as `$RUNUSER` with `python3 -m pip install --user --no-deps --editable /save/$RUNUSER/cloudflow`, with its `FAILED` line and `exit 1` (research R2)
- [ ] T014 [US1] In `exportit/sandbox-terraform/init_template.ansible.tpl`'s header, replace "Terraform has to pass two values more than it does today" with the eight values `main.tf` passes, say that `main.tf` renders this template and `init_template.tpl` is kept for comparison and sync, and remove "Not run anywhere yet" only once spec 001 has run it
- [ ] T015 [US1] Run `just test` and `just full-test` in `exportit/sandbox-terraform/`: T004 to T008 pass, every module still validates, formatting as recorded
- [ ] T016 [P] [US1] In `exportit/sandbox-terraform/Justfile`, add `render-first-boot`: render `local.user_data`'s template with sample values through `tofu console` and print it (the plan's quickstart, step 2)
- [ ] T017 [P] [US1] In `exportit/sandbox-terraform/DEPLOYMENT.md`, add the four values: what each is, that `provisioning_repo` is `csis-sandbox-provisioning`'s URL and `provisioning_version` one of its tags, `cloudflow_repo` and `cloudflow_version` likewise, today's tags (`0.0.1`, `1.6.0b0`), that all four are required, and that `sandbox_version` is gone (FR-005)

**Checkpoint**: a plan without AWS shows the new first boot; a plan without `provisioning_repo` fails naming it.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T018 [P] In `exportit/REMINDERS.md`, add "Remove the link at `/save/$RUNUSER/Cloud-Sandbox/cloudflow`": the job descriptions and cloudflow scripts that name the old path (research R3's table), to change in their own units, after which the template's link goes
- [ ] T019 [P] In `exportit/MAP.md`'s `sandbox-terraform` section, say that `main.tf` renders `init_template.ansible.tpl` with four required values, and that the first boot no longer clones the original
- [ ] T020 [P] In `specs/README.md`, set 006's state (**in progress** until T026)
- [ ] T021 Commit `csis-sandbox-terraform`'s work on its `feature/first-boot-runs-playbooks`; record the submodule here (`git add exportit/sandbox-terraform`); run `just constitution-check`
- [ ] T022 Run the root `just test`
- [ ] T023 Run the root `just full-test`
- [ ] T024 Run `/speckit-converge` on `specs/006-first-boot-runs-playbooks/` after the last implementation task; record under this task that it appended nothing, or carry out every task it appended before going on (done condition 2)
- [ ] T025 Walk `specs/006-first-boot-runs-playbooks/quickstart.md` step by step, recording each step's command and result under this task, all passing (done condition 3)
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
