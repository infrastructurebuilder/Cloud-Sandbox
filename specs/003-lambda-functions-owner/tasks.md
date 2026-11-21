---

description: "Task list for the Lambda functions, owned and deployable"
---

# Tasks: The Lambda functions, owned and deployable

**Input**: Design documents from `specs/003-lambda-functions-owner/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: included, written first and seen to fail before the code they test;
the constitution asks for them (principle IV), and FR-004, FR-008, FR-009 and
FR-010 name them.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files or repositories, no dependency on an unfinished task)
- **[Story]**: the user story the task belongs to (US1, US2)

## Path Conventions

Paths are from the Cloud-Sandbox root. A unit's files are under its submodule:
`exportit/cloudflow/` (cloudflow) and `exportit/sandbox-terraform/`
(`csis-sandbox-terraform`); a change there is committed in that unit's own
repository.

---

## Phase 1: Setup

- [ ] T001 Start `feature/lambda-functions-owner` with git-flow in `exportit/cloudflow/` and in `exportit/sandbox-terraform/`, each from its `develop`, after checking each is clean and level with its origin (Cloud-Sandbox's branch already exists)
- [ ] T002 Run each unit's `just init` (`exportit/cloudflow/`, `exportit/sandbox-terraform/`) so their tests and OpenTofu are ready, and the root `just test`, to start from passing acceptance tests

---

## Phase 2: Foundational (blocking: the `moved` directive)

**Purpose**: the export tool learns `moved` ([contracts/moved-directive.md](contracts/moved-directive.md)) before any map uses it. Nothing here touches a real unit.

### Tests first (they must fail before T009)

- [ ] T003 [P] In `exportit/tools/tests/test_moved.py`, on throw-away repositories built as `tests/test_sync.py` builds them, write the reading tests: `moved <source> <unit> <destination>` is read; each of the contract's five problems is reported (source not taken by the map's own `copy` rule; unknown or own unit; destination the arriving unit copies, or given twice in one unit; source also taken by another unit's `copy` rule; source moved twice)
- [ ] T004 [P] In `exportit/tools/tests/test_moved.py`, write the check tests: the leaving unit no longer expects the moved file (`check`, `copy`); the arriving unit accepts it without a `new` line; `check --baselines` and `lineage` of both units are unchanged by the directive
- [ ] T005 [P] In `exportit/tools/tests/test_moved.py`, write the sync tests: an upstream change to a moved file lands in the arriving unit on `feature/<branch>` as one commit naming the upstream commits; it does not come back into the leaving unit (no change, and a modify/delete conflict, both kept deleted); only the leaving unit's baseline moves; a patch that does not apply, or an arriving unit with changes or not on `develop`, stops the sync with both units as they were; a conflict on any other file still stops it
- [ ] T006 Run the new tests and see them fail for the right reason (the directive is not read), recording which failed under this task in `specs/003-lambda-functions-owner/tasks.md`

### Implementation

- [ ] T007 In `exportit/tools/export.py`, read `moved` into a `Move` (source, arriving unit, destination) on the leaving `Unit`, and document it in the module's docstring beside `local` and `owned`
- [ ] T008 In `exportit/tools/export.py`, report the contract's five problems in `resolve` (so `check`, `check --baselines`, `lineage` and `sync` all see them), and leave `filter_directives` unchanged, so lineage is computed from the `copy` rules as before
- [ ] T009 In `exportit/tools/export.py`, exclude a moved file from its leaving unit's expected files in `check_unit` and `command_copy`, and accept a moved-in destination in the arriving unit as if declared `new`
- [ ] T010 In `exportit/tools/export.py`'s `command_sync`, before touching either unit, build each moved file's patch (the original's diff of the source between the baseline and the head, path rewritten) and check it with `git apply --check` in the arriving unit, which must be checked out, clean and on `develop`; then merge as today, resolving only modify/delete conflicts on moved files' copied paths by keeping them deleted; then apply the patches on the arriving unit's `feature/<branch>` in one commit naming the upstream commits (subject and author) and the range; move only the leaving unit's baseline; report each carried file and the arriving unit's branch
- [ ] T011 Run `just --justfile exportit/tools/Justfile test`: T003 to T005 pass, and the existing tool tests still pass

**Checkpoint**: `moved` works on throw-away repositories; no map uses it yet.

---

## Phase 3: User Story 1 - The functions have an owner and tests (Priority: P1) 🎯 MVP

**Goal**: the functions live in `csis-sandbox-terraform` with tests that prove what they do, without an AWS account, and leave cloudflow.

**Independent Test**: `exportit/sandbox-terraform`'s `just test` runs the handlers' tests, with the AWS calls replaced by `botocore`'s Stubber.

### Tests first (they must fail before T015)

- [ ] T012 [P] [US1] In `exportit/sandbox-terraform/tests/test_reaper_functions.py`, with `botocore`'s Stubber and `TABLE_NAME`, `AWS_REGION`, `ORG_MAX_MINUTES` and `REPORT_BUCKET` set for the import, write the four cases of the spec's User Story 1 for the terminating function: a node started more than `ORG_MAX_MINUTES` ago is terminated and its item deleted; one within it is left; one already gone (`InvalidInstanceID.NotFound`) is reported invalid and its item deleted; one refused (for example `UnauthorizedOperation`, an untagged node) is reported and the rest still handled
- [ ] T013 [P] [US1] In `exportit/sandbox-terraform/tests/test_reaper_functions.py`, write the identifying function's tests: the overdue nodes found, and the report `monitoring/IOOS_Coastal_Sandbox_Suspect_Report_<YYYY-MM-DD-HH>.html` put in the bucket `REPORT_BUCKET` names, not in `ioos-transfers` when the setting names another (FR-009)
- [ ] T014 [US1] Run them in `exportit/sandbox-terraform` (`just test`) and see them fail for the right reason (the functions are not there), recording which failed

### Implementation

- [ ] T015 [US1] Add `exportit/sandbox-terraform/reaper/functions/lambda_identify_zombies.py`, `lambda_terminate_zombies.py` and `lambda.env` with the content cloudflow has for them in `src/cloudflow/cluster/` (byte for byte), and commit that alone in `csis-sandbox-terraform`, its message naming cloudflow's commit they came from
- [ ] T016 [US1] In `exportit/sandbox-terraform/reaper/functions/lambda_identify_zombies.py`, read the report's bucket from `REPORT_BUCKET` in place of `bucket_name = "ioos-transfers"` (line 140); in `reaper/functions/lambda.env`, add `export REPORT_BUCKET=` with a placeholder, no real value (FR-009)
- [ ] T017 [US1] In `exportit/sandbox-terraform`, make T012 and T013 pass, extend `tests/` and the unit's lint and type-check to `reaper/functions/` as its `Justfile` already does for `tests/`, and run `just test`
- [ ] T018 [P] [US1] In `exportit/cloudflow`, delete `src/cloudflow/cluster/lambda_identify_zombies.py`, `lambda_terminate_zombies.py` and `lambda.env`; in `tests/test_modules.py`, remove the two modules from the list of those it cannot import and the `lambda_settings` it unsets (FR-006); record `tests/outward_references.json` again if it named them; run `just test`
- [ ] T019 [US1] In `exportit/cloudflow.map`, add the three lines of [contracts/moved-directive.md](contracts/moved-directive.md#cloudflows-lines-this-spec) (`moved cloudflow/cluster/<file> sandbox-terraform reaper/functions/<file>`), leaving its `copy cloudflow/cluster/ src/cloudflow/cluster/` as it is; in `exportit/sandbox-terraform.map`, add `new reaper/`
- [ ] T020 [US1] In `exportit/tools/rehearse_sync.py`, add the scenario "a change to a moved file": the made-up original changes `cloudflow/cluster/lambda_terminate_zombies.py`; syncing `cloudflow` carries it into a clone of `csis-sandbox-terraform` under `reaper/functions/`, on its sync branch, by one commit, and cloudflow's clone does not get the file back; the rehearsal clones both units for it
- [ ] T021 [US1] With the root `Justfile`, run `just export-baselines`, `just export-lineage cloudflow sandbox-terraform` and `just sync-rehearse`: both units' lineage holds, and every scenario, the new one among them, is as promised (SC-003, SC-004)

**Checkpoint**: the functions and their tests are in `csis-sandbox-terraform`, gone from cloudflow, and a later sync carries changes to them to their new home.

---

## Phase 4: User Story 2 - The functions can be deployed by OpenTofu (Priority: P2)

**Goal**: one variable, `enable_reaper`, makes the module create the functions, their schedule, and a role for each allowed exactly what it calls; the terminating role only on tagged nodes.

**Independent Test**: `tofu test` in `exportit/sandbox-terraform/reaper/` with mocked providers, `enable_reaper` false and true; `tofu validate`.

### Tests first (they must fail before T026)

- [ ] T022 [P] [US2] In `exportit/cloudflow/tests/test_launch_tag.py`, write a test that a launch request made by `AWSCluster`, with a stand-in EC2 resource, carries `{"Key": "csis:launched-by", "Value": "cloudflow"}` in its instance `TagSpecifications`, beside the cluster description's own tags and `ApprovedSubnet` (FR-008)
- [ ] T023 [P] [US2] In `exportit/sandbox-terraform/reaper/tests/reaper.tftest.hcl`, with `mock_provider "aws"` and `mock_provider "archive"`, write two `run` blocks: `enable_reaper = false` plans no resource; `enable_reaper = true` plans two `aws_lambda_function` on `python3.13` with handler `<file>.lambda_handler`, a schedule rule and its two targets and invoke permissions, and two roles whose policies allow exactly [contracts/reaper-module.md](contracts/reaper-module.md)'s actions, the terminating role's `ec2:TerminateInstances` with `StringEquals ec2:ResourceTag/csis:launched-by = cloudflow` and no other EC2 action, and neither function's environment holding `AWS_REGION` (SC-005)
- [ ] T024 [P] [US2] In `exportit/sandbox-terraform/tests/test_reaper_module.py`, write the pytest wrapper that runs `tofu test` in `reaper/` with the unit's pinned OpenTofu and plugin cache, and `tofu validate` there; in `tests/support.py`, add `"reaper"` to `MODULES`, and in `tests/test_module.py` let the pinned-version test read `reaper/versions.tofu`
- [ ] T025 [US2] Run T022 in `exportit/cloudflow` and T023 and T024 in `exportit/sandbox-terraform` and see them fail for the right reason, recording which failed

### Implementation

- [ ] T026 [US2] In `exportit/cloudflow/src/cloudflow/cluster/AWSCluster.py`, add one constant for the launch tag and append it to `self.tags` after `ApprovedSubnet` (line 407); run cloudflow's `just test` and `just full-test`
- [ ] T027 [US2] Write `exportit/sandbox-terraform/reaper/versions.tofu` (OpenTofu `1.13.9`; `hashicorp/aws ~> 6.0`; `hashicorp/archive ~> 2.0`) and `reaper/variables.tf` with [contracts/reaper-module.md](contracts/reaper-module.md)'s nine variables and their defaults (`enable_reaper` `false`; `report_bucket` `"ioos-transfers"`; `schedule` `"rate(1 hour)"`; `launch_tag_key` `"csis:launched-by"`; `launch_tag_value` `"cloudflow"`; `region`, `name_prefix`, `table_name`, `lambda_max_minutes` with no default), none holding an account number, a key or a secret
- [ ] T028 [US2] Write `exportit/sandbox-terraform/reaper/main.tf` and `reaper/outputs.tf`: every resource counted on `enable_reaper`; two `archive_file` packages from `reaper/functions/`; two functions on `python3.13` with `TABLE_NAME`, `ORG_MAX_MINUTES` and, for the identifying one, `REPORT_BUCKET` (never `AWS_REGION`); the schedule, targets and permissions; two roles and policies as the contract lists; outputs for the functions' and roles' names
- [ ] T029 [US2] In `exportit/sandbox-terraform`, add `reaper/` to `just init` (its `tofu init -backend=false` into the plugin cache) and to `tofu fmt`'s check; run `just test` and `just full-test`: T023 and T024 pass, and every other module still validates
- [ ] T030 [P] [US2] In `exportit/tools/tests/test_umbrella.py`, add a test that cloudflow's launch-tag constant equals `reaper/variables.tf`'s `launch_tag_key` and `launch_tag_value` defaults (a check between units, kept in the workshop)
- [ ] T031 [US2] In `exportit/sandbox-terraform/DEPLOYMENT.md`, add how the guard is switched on: apply `reaper/` after the main module, with `enable_reaper = true` and the four required values; what the roles may do; that nodes started before cloudflow added the tag are not stopped and must be stopped by hand (FR-007)

**Checkpoint**: the module plans what the contract says with `enable_reaper` true, nothing with it false; nothing has reached an AWS account.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T032 In `exportit/MAP.md`, say where the functions are now (cloudflow's section and `sandbox-terraform`'s), the `moved` directive under "How a copy is made and checked" and "Syncing from the original", and that `reaper/` uses a newer AWS provider than the main module (research R1)
- [ ] T033 [P] In `exportit/REMINDERS.md`, close the item "Who owns the Lambda functions"
- [ ] T034 [P] In `specs/README.md`, mark 003 done; in specs 002, 004 and 005, note under their move question that the `moved` directive now exists ([contracts/moved-directive.md](contracts/moved-directive.md)), without answering their questions
- [ ] T035 Commit each unit's work on its `feature/lambda-functions-owner` (cloudflow, `csis-sandbox-terraform`); record both submodules here (`git add exportit/cloudflow exportit/sandbox-terraform`); run `just constitution-check`
- [ ] T036 Run the root `just test` and `just full-test` (quickstart.md, steps 1 to 4); then mark this spec's Status done in `specs/003-lambda-functions-owner/spec.md` and tick this file
- [ ] T037 On the operator's word only, in `exportit/cloudflow/`, `exportit/sandbox-terraform/` and the Cloud-Sandbox root: finish each unit's branch into its `develop` and push (cloudflow, `csis-sandbox-terraform`), record their `develop` commits here, then squash `feature/lambda-functions-owner` into Cloud-Sandbox's `develop` from its tree and push, with `just submodules-pushed` first

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none.
- **Foundational (Phase 2)**: after Setup; blocks US1's T019 to T021, which need `moved`.
- **US1 (Phase 3)**: T012 to T018 can start after Setup; T019 to T021 need Phase 2.
- **US2 (Phase 4)**: needs T015 (the functions in `reaper/functions/`, which the module packages); independent of Phase 2.
- **Polish (Phase 5)**: after US1 and US2.

### User Story Dependencies

- **US1 (P1)**: the MVP; needs `moved` for its map lines.
- **US2 (P2)**: needs US1's T015 only.

### Within Each Story

- Tests are written and seen to fail before the code they test.
- In each unit, its own `just test` passes before the root's is run.

### Parallel Opportunities

- T003, T004 and T005 (one new file, written as separate sets of tests).
- T012 and T013 alongside T018 (different repositories).
- T022, T023 and T024 (three files in two repositories); T030 with T031.
- Phase 2 (Cloud-Sandbox) alongside T012 to T018 (the units).

---

## Parallel Example: User Story 2

```text
Task: "T022 [US2] the launch-tag test in exportit/cloudflow/tests/test_launch_tag.py"
Task: "T023 [US2] the mocked-provider tftest in exportit/sandbox-terraform/reaper/tests/reaper.tftest.hcl"
Task: "T024 [US2] the pytest wrapper in exportit/sandbox-terraform/tests/test_reaper_module.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1, then Phase 2 (`moved`), then Phase 3.
2. Stop and validate: the functions and their tests in `csis-sandbox-terraform`, gone from cloudflow, lineage and the rehearsal passing.

### Incremental Delivery

1. US1: the functions owned and tested.
2. US2: the module, the tag, the roles; deployable, not deployed.
3. Polish: the records; then the operator's word for the merges.

---

## Notes

- Nothing in any task creates, changes or removes anything in an AWS account.
- Each unit's change is committed in its own repository; Cloud-Sandbox records the units' commits after them, and is pushed after them.
- Nothing in `ATTIC/` is read for any task.
