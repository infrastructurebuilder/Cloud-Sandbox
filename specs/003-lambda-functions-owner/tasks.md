---

description: "Task list for the Lambda functions, owned and deployable"
---

# Tasks: The Lambda functions, owned and deployable

**Input**: Design documents from `specs/003-lambda-functions-owner/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0, 2026-11-21): T036 to T040 are those conditions' tasks. Brought up to
date on 2026-11-22, after specs 001, 002 and 004 to 007 were clarified,
planned and tasked: 003 is first in the build order ([../README.md](../README.md)),
and spec 005 waits for its `moved` directive. Each task, when
checked, gets a record under it: what was done, and the evidence (a commit, a
run, a count).

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

- [X] T001 Start `feature/lambda-functions-owner` with git-flow in `exportit/cloudflow/` and in `exportit/sandbox-terraform/`, each from its `develop`, after checking each is clean and level with its origin (Cloud-Sandbox's branch already exists)
  - Done 2026-11-22: `feature/lambda-functions-owner` made in cloudflow and `csis-sandbox-terraform` from their `develop` (`b4476ce`, `b6aa5e7`, both clean and level with origin), in worktrees of their own because the main checkout's units were under the merge script's full test; Cloud-Sandbox's branch existed.
- [ ] T002 Run each unit's `just init` (`exportit/cloudflow/`, `exportit/sandbox-terraform/`) so their tests and OpenTofu are ready, and the root `just test`, to start from passing acceptance tests

---

## Phase 2: Foundational (blocking: the `moved` directive)

**Purpose**: the export tool learns `moved` ([contracts/moved-directive.md](contracts/moved-directive.md)) before any map uses it. Nothing here touches a real unit.

### Tests first (they must fail before T009)

- [X] T003 [P] In `exportit/tools/tests/test_moved.py`, on throw-away repositories built as `tests/test_sync.py` builds them, write the reading tests: `moved <source> <unit> <destination>` is read; each of the contract's five problems is reported (source not taken by the map's own `copy` rule; unknown or own unit; destination the arriving unit copies, or given twice in one unit; source also taken by another unit's `copy` rule; source moved twice)
  - Done 2026-11-22: `exportit/tools/tests/test_moved.py`, a world of an original, three maps and two units (`lib`, from which `pkg/fn.py` moves, and `ops`, where it arrives as `funcs/fn.py`); the reading test, three malformed lines, and one test per problem of the contract.
- [X] T004 [P] In `exportit/tools/tests/test_moved.py`, write the check tests: the leaving unit no longer expects the moved file (`check`, `copy`); the arriving unit accepts it without a `new` line; `check --baselines` and `lineage` of both units are unchanged by the directive
  - Done 2026-11-22: the leaving unit's check without the file; the same maps without the directive (missing, and a stray); the arriving unit accepting it; a moved file absent there; `check --baselines` and `lineage` of both units; the filter directives equal to the copy rules'.
- [X] T005 [P] In `exportit/tools/tests/test_moved.py`, write the sync tests: an upstream change to a moved file lands in the arriving unit on `feature/<branch>` as one commit naming the upstream commits; it does not come back into the leaving unit (no change, and a modify/delete conflict, both kept deleted); only the leaving unit's baseline moves; a patch that does not apply, or an arriving unit with changes or not on `develop`, stops the sync with both units as they were; a conflict on any other file still stops it
  - Done 2026-11-22: a change carried into `ops` on `feature/sync-1` as one commit naming both upstream commits, their author and the range; not back in `lib`; only `lib`'s baseline moved; other changes merged into `lib` as before; no change to the moved file leaves `ops` alone; a patch that does not apply, `ops` with changes, `ops` not on `develop`, and a conflict on another file each stop the sync with both units as they were.
- [X] T006 Run the new tests and see them fail for the right reason (the directive is not read), recording which failed under this task in `specs/003-lambda-functions-owner/tasks.md`
  - Done 2026-11-22, against the unchanged `export.py`: 18 failed for the right reason (`cannot read 'moved pkg/fn.py ops funcs/fn.py'`); 4 passed, which hold without the directive too (the three malformed lines were already refused; the maps without it).

### Implementation

- [X] T007 In `exportit/tools/export.py`, read `moved` into a `Move` (source, arriving unit, destination) on the leaving `Unit`, and document it in the module's docstring beside `local` and `owned`
  - Done 2026-11-22: `Move(unit, source, to, dest, line)`, read by `parse_map` (single files only, three arguments), on `Unit.moves`; the docstring lists `moved` beside `local` and `owned`.
- [X] T008 In `exportit/tools/export.py`, report the contract's five problems in `resolve` (so `check`, `check --baselines`, `lineage` and `sync` all see them), and leave `filter_directives` unchanged, so lineage is computed from the `copy` rules as before
  - Done 2026-11-22: `resolve_moves`, called by `resolve`, reports the five problems; `filter_directives` unchanged, so lineage comes from the copy rules as before (a test holds it).
- [X] T009 In `exportit/tools/export.py`, exclude a moved file from its leaving unit's expected files in `check_unit` and `command_copy`, and accept a moved-in destination in the arriving unit as if declared `new`
  - Done 2026-11-22: `Plan.moved_out`, `Plan.moved_in` and `Plan.kept()`; `check_unit` takes `arrived` (accepted as if declared new, and a problem if absent); `command_check`, `command_check_baselines`, `command_copy` and `command_sync` use `kept()`.
- [X] T010 In `exportit/tools/export.py`'s `command_sync`, before touching either unit, build each moved file's patch (the original's diff of the source between the baseline and the head, path rewritten) and check it with `git apply --check` in the arriving unit, which must be checked out, clean and on `develop`; then merge as today, resolving only modify/delete conflicts on moved files' copied paths by keeping them deleted; then apply the patches on the arriving unit's `feature/<branch>` in one commit naming the upstream commits (subject and author) and the range; move only the leaving unit's baseline; report each carried file and the arriving unit's branch
  - Done 2026-11-22: `moved_changes` (the original's diff of each moved source, path rewritten), `check_arrivals` (checked out, clean, on `develop`, `git apply --check`) before anything changes; `merge_or_undo` keeps a moved file deleted on a modify/delete conflict and still stops on any other; `carry_moved` makes `feature/<branch>` in the arriving unit and one commit naming each file's upstream commits and the range; only the leaving unit's baseline moves; the report names what was carried. All 22 tests of `test_moved.py` pass.
- [ ] T011 Run `just --justfile exportit/tools/Justfile test`: T003 to T005 pass, and the existing tool tests still pass

**Checkpoint**: `moved` works on throw-away repositories; no map uses it yet.

---

## Phase 3: User Story 1 - The functions have an owner and tests (Priority: P1) 🎯 MVP

**Goal**: the functions live in `csis-sandbox-terraform` with tests that prove what they do, without an AWS account, and leave cloudflow.

**Independent Test**: `exportit/sandbox-terraform`'s `just test` runs the handlers' tests, with the AWS calls replaced by `botocore`'s Stubber.

### Tests first (they must fail before T015)

- [X] T012 [P] [US1] In `exportit/sandbox-terraform/tests/test_reaper_functions.py`, with `botocore`'s Stubber and `TABLE_NAME`, `AWS_REGION`, `ORG_MAX_MINUTES` and `REPORT_BUCKET` set for the import, write the four cases of the spec's User Story 1 for the terminating function: a node started more than `ORG_MAX_MINUTES` ago is terminated and its item deleted; one within it is left; one already gone (`InvalidInstanceID.NotFound`) is reported invalid and its item deleted; one refused (for example `UnauthorizedOperation`, an untagged node) is reported and the rest still handled
  - Done 2026-11-22: `exportit/sandbox-terraform/tests/test_reaper_functions.py`, each function imported fresh with its settings and `botocore`'s Stubber on its clients: the four cases, `UnauthorizedOperation` standing for an untagged node. `boto3` joins the unit's dev dependencies.
- [X] T013 [P] [US1] In `exportit/sandbox-terraform/tests/test_reaper_functions.py`, write the identifying function's tests: the overdue nodes found, and the report `monitoring/IOOS_Coastal_Sandbox_Suspect_Report_<YYYY-MM-DD-HH>.html` put in the bucket `REPORT_BUCKET` names, not in `ioos-transfers` when the setting names another (FR-009)
  - Done 2026-11-22: the report put at `monitoring/IOOS_Coastal_Sandbox_Suspect_Report_<YYYY-MM-DD-HH>.html` in the bucket `REPORT_BUCKET` names, for two names; no `"ioos-transfers"` left in the function; `lambda.env` names the setting with a placeholder.
- [X] T014 [US1] Run them in `exportit/sandbox-terraform` (`just test`) and see them fail for the right reason (the functions are not there), recording which failed
  - Done 2026-11-22: 5 failed and 4 errored, all for the right reason (`reaper/functions/` does not exist).

### Implementation

- [X] T015 [US1] Add `exportit/sandbox-terraform/reaper/functions/lambda_identify_zombies.py`, `lambda_terminate_zombies.py` and `lambda.env` with the content cloudflow has for them in `src/cloudflow/cluster/` (byte for byte), and commit that alone in `csis-sandbox-terraform`, its message naming cloudflow's commit they came from
  - Done 2026-11-22: `csis-sandbox-terraform` `5f6be13`, the three files byte for byte (`cmp`) from cloudflow's `b4476ce`, committed alone.
- [X] T016 [US1] In `exportit/sandbox-terraform/reaper/functions/lambda_identify_zombies.py`, read the report's bucket from `REPORT_BUCKET` in place of `bucket_name = "ioos-transfers"` (line 140); in `reaper/functions/lambda.env`, add `export REPORT_BUCKET=` with a placeholder, no real value (FR-009)
  - Done 2026-11-22: `REPORT_BUCKET = os.environ["REPORT_BUCKET"]` and `bucket_name = REPORT_BUCKET`; `lambda.env` gains `export REPORT_BUCKET="<the report bucket>"`.
- [X] T017 [US1] In `exportit/sandbox-terraform`, make T012 and T013 pass, extend `tests/` and the unit's lint and type-check to `reaper/functions/` as its `Justfile` already does for `tests/`, and run `just test`
  - Done 2026-11-22: 9 tests pass (one fix to the test: the stubbed `batch_write_item` answers with `UnprocessedItems`, as DynamoDB does); the unit's `just test`: lint clean, pyright 0 errors, 22 passed. `csis-sandbox-terraform` `b6af91a`. **Deviation:** the functions are not added to the lint and type-check: they keep the original's text but for FR-009, so that a later upstream change still applies to them as a patch (spec 003's sync); reformatting them would make every such patch fail.
- [X] T018 [P] [US1] In `exportit/cloudflow`, delete `src/cloudflow/cluster/lambda_identify_zombies.py`, `lambda_terminate_zombies.py` and `lambda.env`; in `tests/test_modules.py`, remove the two modules from the list of those it cannot import and the `lambda_settings` it unsets (FR-006); record `tests/outward_references.json` again if it named them; run `just test`
  - Done 2026-11-22: cloudflow `88cc9bf`: the three files deleted; `tests/test_modules.py` without the two modules and their settings; `tests/outward_references.json` did not name them; the README says where they went. Cloudflow's `just test`: 147 passed.
- [X] T019 [US1] In `exportit/cloudflow.map`, add the three lines of [contracts/moved-directive.md](contracts/moved-directive.md#cloudflows-lines-this-spec) (`moved cloudflow/cluster/<file> sandbox-terraform reaper/functions/<file>`), leaving its `copy cloudflow/cluster/ src/cloudflow/cluster/` as it is; in `exportit/sandbox-terraform.map`, add `new reaper/`
  - Done 2026-11-22: `exportit/cloudflow.map`, the three `moved` lines under its `copy cloudflow/cluster/` rule, which stays; `exportit/sandbox-terraform.map`, `new reaper/`.
- [X] T020 [US1] In `exportit/tools/rehearse_sync.py`, add the scenario "a change to a moved file": the made-up original changes `cloudflow/cluster/lambda_terminate_zombies.py`; syncing `cloudflow` carries it into a clone of `csis-sandbox-terraform` under `reaper/functions/`, on its sync branch, by one commit, and cloudflow's clone does not get the file back; the rehearsal clones both units for it
  - Done 2026-11-22: `exportit/tools/rehearse_sync.py`, the scenario "a change to a moved file": the made-up original changes `cloudflow/cluster/lambda_terminate_zombies.py`; syncing `cloudflow` must carry it into a clone of `csis-sandbox-terraform` on `feature/sync-r` by one commit naming the upstream commit, without the file coming back into cloudflow or `csis-sandbox-terraform`'s baseline moving.
- [ ] T021 [US1] With the root `Justfile`, run `just export-baselines`, `just export-lineage cloudflow sandbox-terraform` and `just sync-rehearse`: both units' lineage holds, and every scenario, the new one among them, is as promised (SC-003, SC-004)

**Checkpoint**: the functions and their tests are in `csis-sandbox-terraform`, gone from cloudflow, and a later sync carries changes to them to their new home.

---

## Phase 4: User Story 2 - The functions can be deployed by OpenTofu (Priority: P2)

**Goal**: one variable, `enable_reaper`, makes the module create the functions, their schedule, and a role for each allowed exactly what it calls; the terminating role only on tagged nodes.

**Independent Test**: `tofu test` in `exportit/sandbox-terraform/reaper/` with mocked providers, `enable_reaper` false and true; `tofu validate`.

### Tests first (they must fail before T026)

- [X] T022 [P] [US2] In `exportit/cloudflow/tests/test_launch_tag.py`, write a test that a launch request made by `AWSCluster`, with a stand-in EC2 resource, carries `{"Key": "csis:launched-by", "Value": "cloudflow"}` in its instance `TagSpecifications`, beside the cluster description's own tags and `ApprovedSubnet` (FR-008)
  - Done 2026-11-22: `exportit/cloudflow/tests/test_launch_tag.py`: a cluster launched with `boto3`, `AWSHelper` and DynamoDB replaced; the request's instance tags hold `csis:launched-by = cloudflow` after `ApprovedSubnet` and the description's own; the tag is one constant, `LAUNCH_TAG`.
- [X] T023 [P] [US2] In `exportit/sandbox-terraform/reaper/tests/reaper.tftest.hcl`, with `mock_provider "aws"` and `mock_provider "archive"`, write two `run` blocks: `enable_reaper = false` plans no resource; `enable_reaper = true` plans two `aws_lambda_function` on `python3.13` with handler `<file>.lambda_handler`, a schedule rule and its two targets and invoke permissions, and two roles whose policies allow exactly [contracts/reaper-module.md](contracts/reaper-module.md)'s actions, the terminating role's `ec2:TerminateInstances` with `StringEquals ec2:ResourceTag/csis:launched-by = cloudflow` and no other EC2 action, and neither function's environment holding `AWS_REGION` (SC-005)
  - Done 2026-11-22: `exportit/sandbox-terraform/reaper/tests/reaper.tftest.hcl`, mocked `aws` (ARN-shaped defaults, a placeholder account) and `archive`: `off_by_default` plans nothing; `on` plans the two functions, handlers, settings (no `AWS_REGION`), the schedule, two targets and permissions, and the two policies' actions exactly, the terminating one only on the tag; `another_tag_and_bucket` follows the variables.
- [X] T024 [P] [US2] In `exportit/sandbox-terraform/tests/test_reaper_module.py`, write the pytest wrapper that runs `tofu test` in `reaper/` with the unit's pinned OpenTofu and plugin cache, and `tofu validate` there; in `tests/support.py`, add `"reaper"` to `MODULES`, and in `tests/test_module.py` let the pinned-version test read `reaper/versions.tofu`
  - Done 2026-11-22: `exportit/sandbox-terraform/tests/test_reaper_module.py` runs `tofu test` in `reaper/` (`3 passed, 0 failed`); `tests/support.py`'s `MODULES` gains `reaper`, so `validate`, formatting and the pinned-version test cover it.
- [X] T025 [US2] Run T022 in `exportit/cloudflow` and T023 and T024 in `exportit/sandbox-terraform` and see them fail for the right reason, recording which failed
  - Done 2026-11-22: cloudflow's two tests failed for the right reason (no tag; no `LAUNCH_TAG`); the tofu test, run with `reaper/main.tf` and `outputs.tf` moved aside, failed on undeclared resources and variables. The tofu test was written before the module but first run after it; this run, without the module, is the failing one.

### Implementation

- [X] T026 [US2] In `exportit/cloudflow/src/cloudflow/cluster/AWSCluster.py`, add one constant for the launch tag and append it to `self.tags` after `ApprovedSubnet` (line 407); run cloudflow's `just test` and `just full-test`
  - Done 2026-11-22: cloudflow `db9efbf`: `LAUNCH_TAG` and its append after `ApprovedSubnet`; `just test` 149 passed, `just full-test` 6 slow passed.
- [X] T027 [US2] Write `exportit/sandbox-terraform/reaper/versions.tofu` (OpenTofu `1.13.9`; `hashicorp/aws ~> 6.0`; `hashicorp/archive ~> 2.0`) and `reaper/variables.tf` with [contracts/reaper-module.md](contracts/reaper-module.md)'s nine variables and their defaults (`enable_reaper` `false`; `report_bucket` `"ioos-transfers"`; `schedule` `"rate(1 hour)"`; `launch_tag_key` `"csis:launched-by"`; `launch_tag_value` `"cloudflow"`; `region`, `name_prefix`, `table_name`, `lambda_max_minutes` with no default), none holding an account number, a key or a secret
  - Done 2026-11-22: `reaper/versions.tofu` (OpenTofu `1.13.9`, `aws ~> 6.0`, `archive ~> 2.0`) and `reaper/variables.tf` with the nine variables and the contract's defaults; none holds an account number, a key or a secret.
- [X] T028 [US2] Write `exportit/sandbox-terraform/reaper/main.tf` and `reaper/outputs.tf`: every resource counted on `enable_reaper`; two `archive_file` packages from `reaper/functions/`; two functions on `python3.13` with `TABLE_NAME`, `ORG_MAX_MINUTES` and, for the identifying one, `REPORT_BUCKET` (never `AWS_REGION`); the schedule, targets and permissions; two roles and policies as the contract lists; outputs for the functions' and roles' names
  - Done 2026-11-22: `reaper/main.tf` and `outputs.tf`, everything keyed on `local.functions`, empty unless `enable_reaper`; the account read from `aws_caller_identity` only when on (the first test run caught a null ARN when off). `csis-sandbox-terraform` `0811fa4`.
- [X] T029 [US2] In `exportit/sandbox-terraform`, add `reaper/` to `just init` (its `tofu init -backend=false` into the plugin cache) and to `tofu fmt`'s check; run `just test` and `just full-test`: T023 and T024 pass, and every other module still validates
  - Done 2026-11-22: `just init` initialises `reaper/`; `reaper/.build/` ignored; the unit's `just test` 26 passed, `just full-test` 2 slow passed; every module validates.
- [X] T030 [P] [US2] In `exportit/tools/tests/test_umbrella.py`, add a test that cloudflow's launch-tag constant equals `reaper/variables.tf`'s `launch_tag_key` and `launch_tag_value` defaults (a check between units, kept in the workshop)
  - Done 2026-11-22: `exportit/tools/tests/test_umbrella.py`, `test_the_launch_tag_cloudflow_adds_is_the_one_the_reaper_requires`, reading `AWSCluster.py`'s constant and `reaper/variables.tf`'s two defaults.
- [X] T031 [US2] In `exportit/sandbox-terraform/DEPLOYMENT.md`, add how the guard is switched on: apply `reaper/` after the main module, with `enable_reaper = true` and the four required values; what the roles may do; that nodes started before cloudflow added the tag are not stopped and must be stopped by hand (FR-007)
  - Done 2026-11-22: `exportit/sandbox-terraform/DEPLOYMENT.md` section 8: applying `reaper/` after the main module with the four required values, what the roles may do, that nodes started before the tag must be stopped by hand, and removal.

**Checkpoint**: the module plans what the contract says with `enable_reaper` true, nothing with it false; nothing has reached an AWS account.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T032 In `exportit/MAP.md`, say where the functions are now (cloudflow's section and `sandbox-terraform`'s), the `moved` directive under "How a copy is made and checked" and "Syncing from the original", and that `reaper/` uses a newer AWS provider than the main module (research R1)
  - Done 2026-11-22: `exportit/MAP.md`: cloudflow's decisions, defects and expectations say where the functions went; `sandbox-terraform` says they are its `reaper/`, and its newer providers; "How a copy is made and checked" describes `moved`; "Syncing from the original" gains its row and the eighth rehearsal scenario.
- [X] T033 [P] In `exportit/REMINDERS.md`, close the item "Who owns the Lambda functions"
  - Done 2026-11-22: the item "Who owns the Lambda functions" removed from `exportit/REMINDERS.md`'s open list.
- [X] T034 [P] In `specs/README.md`, set 003's state in its row of the build-order table (**merged** after T038, **complete** at T040), and say in its "How a file moves between units" section that the `moved` directive exists ([contracts/moved-directive.md](contracts/moved-directive.md)), which spec 005, next in the order, uses for its 51 files
  - Done 2026-11-22: `specs/README.md`, 003's row **in progress** (implemented, not yet merged; T038 and T040 change it), and its "How a file moves between units" section names the directive and its contract.
- [ ] T035 Commit each unit's work on its `feature/lambda-functions-owner` (cloudflow, `csis-sandbox-terraform`); record both submodules here (`git add exportit/cloudflow exportit/sandbox-terraform`); run `just constitution-check`
- [ ] T036 Run `/speckit-converge` on `specs/003-lambda-functions-owner/` after the last implementation task; record under this task that it appended nothing, or carry out every task it appended before going on (constitution 1.2.0, done condition 2)
- [ ] T037 Walk `specs/003-lambda-functions-owner/quickstart.md` step by step, recording each step's command and result under this task, the root `just test` and `just full-test` among them, all passing (done condition 3)
- [ ] T038 On the operator's word only, in `exportit/cloudflow/`, `exportit/sandbox-terraform/` and the Cloud-Sandbox root: finish each unit's branch into its `develop` and push (cloudflow, `csis-sandbox-terraform`), record their `develop` commits here, then squash `feature/lambda-functions-owner` into Cloud-Sandbox's `develop` from its tree and push, with `just submodules-pushed` first; until then the spec is **in progress**, and once merged, **merged** (done condition 4)
- [ ] T039 Record under this task, in `specs/003-lambda-functions-owner/tasks.md`, that no release applies: the plan names none, and neither unit has a release step yet (its `release` target says so, and `exportit/REMINDERS.md` keeps "Releasing from a unit's own repository" open); unless the operator asks for one, which would then be cut, tagged and taken by `units.toml` (done condition 5)
- [ ] T040 Mark the spec **complete**, with the date, in its Status line in `specs/003-lambda-functions-owner/spec.md` and in its row in `specs/README.md`, only when T001 to T039 are checked, each with its record (done conditions 1 and 6)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none.
- **Foundational (Phase 2)**: after Setup; blocks US1's T019 to T021, which need `moved`.
- **US1 (Phase 3)**: T012 to T018 can start after Setup; T019 to T021 need Phase 2.
- **US2 (Phase 4)**: needs T015 (the functions in `reaper/functions/`, which the module packages); independent of Phase 2.
- **Polish (Phase 5)**: after US1 and US2; T036 (converge) after the last implementation task, then T037, T038 (on the operator's word), T039 and T040 in that order.

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
