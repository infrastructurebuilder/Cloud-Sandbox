# Feature Specification: The Lambda functions, owned and deployable

**Feature Branch**: `feature/lambda-functions-owner` (since 2026-11-20)

**Created**: 2026-11-14, as stage 17; carried into this spec 2026-11-19

**Status**: In progress. Clarified 2026-11-20 (five questions, every open
question settled), planned and broken into 40 tasks the same day; not yet
implemented. Needs nothing first: no
AWS account is needed to write and test it.

**Input**: the stage plan of 2026-11-14 (the reminder "who owns the Lambda
functions", put aside 2026-11-13), carried from the ATTIC on the operator's
instruction of 2026-11-19.

## Why

Two AWS Lambda functions, `lambda_identify_zombies.py` and
`lambda_terminate_zombies.py`, find compute nodes that cloudflow left running
past `ORG_MAX_MINUTES` (from the DynamoDB table cloudflow writes, `TABLE_NAME`,
in `AWS_REGION`) and terminate them, with an HTML report to S3. They are the
sandbox's guard against paying for nodes nobody stops.

- They sit in cloudflow's package (`src/cloudflow/cluster/`), but **cloudflow
  never imports them**: they read their settings from the environment when
  loaded, which is why cloudflow's import test lists them as skipped.
- **Nothing deploys them:** no OpenTofu, no playbook, no packaging. They,
  their schedule and their IAM role are made by hand, like the DynamoDB table.
- cloudflow's `docs/ZOMBIE_JOB_CHECKLIST.md` describes the zombie problem and
  its manual clean-up; `lambda.env` holds the three variables for running
  them locally.

## Clarifications

### Session 2026-11-20

- Q: Which repository should own the two Lambda functions and deploy them? →
  A: `csis-sandbox-terraform` (the stage's default).
- Q: When the functions and `lambda.env` move from cloudflow to
  `csis-sandbox-terraform`, how do both units stay checkable against the
  original? → A: a `moved` directive in the maps, built in `export.py` with
  tests as part of this spec: lineage and syncs keep using each map as the
  unit was made, and a sync carries an upstream change to a moved file into
  its new unit as a patch. (Only `csis-sandbox-terraform` needs the files:
  cloudflow never imports them.)
- Q: Should this spec stop at writing and testing the module, or also apply
  it in an account? → A: write and test only; nothing is created in any
  account. Switching the guard on (`enable_reaper`) is the operator's, later.
- Q: Which compute nodes may the role let the terminating function stop? →
  A: only instances carrying a dedicated tag that cloudflow adds to every
  compute node it launches (for example `csis:launched-by = cloudflow`); the
  sites' `Project` tags are too varied to rely on.
- Q: Where should the identifying function write its report? → A: to the
  bucket named by an environment setting, `REPORT_BUCKET`, which the module
  sets from `report_bucket`, defaulting to today's `ioos-transfers`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The functions have an owner and tests (Priority: P1)

Someone changing the functions finds them in the unit that owns them, with
tests that prove what they do, without an AWS account.

**Why this priority**: they guard the account's bill and have no tests.

**Independent Test**: the handlers' unit tests, with the AWS calls replaced
(`botocore`'s Stubber).

**Acceptance Scenarios**:

1. **Given** a node past its limit, **When** the terminating function runs,
   **Then** it is terminated and reported.
2. **Given** a node within its limit, **When** it runs, **Then** it is left.
3. **Given** a node already gone, **When** it runs, **Then** it is reported as
   invalid.
4. **Given** one failure, **When** it runs, **Then** the failure is reported
   and the rest are still handled, and the report is written.

### User Story 2 - The functions can be deployed by OpenTofu (Priority: P2)

The operator can switch the guard on with one variable, and the module
creates the functions, their schedule and a role allowed exactly what they
need.

**Why this priority**: today they exist only where someone made them by hand.

**Independent Test**: `tofu validate` and `tofu plan` of the module in an
empty workspace, with the guard on and off.

**Acceptance Scenarios**:

1. **Given** `enable_reaper` false, **When** the plan is made, **Then** it
   creates nothing of the functions.
2. **Given** `enable_reaper` true, **When** the plan is made, **Then** it shows
   the two functions, their schedule, and a role and policy for each.

### Edge Cases

- Applying the module starts terminating nodes past their limit: it is the
  operator's to switch on, never a test's.
- A node cloudflow started before FR-008's tag existed carries no tag: the
  role cannot terminate it, and the function reports the failure and goes on
  (User Story 1, scenario 4). Such nodes are stopped by hand, as today.
- The original changes a function after the move: the sync carries the change
  into `csis-sandbox-terraform` as a patch; if the patch does not apply there
  (the unit changed the same lines), the sync stops and leaves both units as
  they were.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The functions MUST be owned by `csis-sandbox-terraform`, as
  infrastructure of the account beside the table they read: their source,
  their tests and their OpenTofu module live there.
- **FR-002**: The two functions and `lambda.env` MUST move from cloudflow to
  `csis-sandbox-terraform` by a new mapping directive, `moved`. Only
  `csis-sandbox-terraform` needs them (cloudflow never imports them), so they
  move rather than going to a common place (constitution 1.1.0, principle I).
- **FR-003**: The module MUST be written and tested only: `tofu validate`,
  and `tofu plan` against a workspace with no resources, with `enable_reaper`
  true and false. Nothing MUST be created in any AWS account by this spec;
  switching the guard on is the operator's, later, in an account they choose.
- **FR-004**: Tests MUST cover the cases of User Story 1, with the AWS calls
  replaced; no test reaches AWS.
- **FR-005**: The module MUST hold the two functions, their packaging, an
  EventBridge schedule, and one role for each function, allowed exactly what
  it calls (research R3): `dynamodb:Scan` and `dynamodb:BatchWriteItem` on
  the table and its logs for both; `s3:PutObject` on the report's bucket for
  the identifying function; `ec2:TerminateInstances` only on instances that
  carry the tag of FR-008 (an `ec2:ResourceTag` condition) for the
  terminating function. Variables `lambda_max_minutes`, `table_name` and
  `report_bucket`; off unless `enable_reaper` is true. (Corrected
  2026-11-20 while planning: the stage named `ec2:DescribeInstances`, which
  neither function calls.)
- **FR-006**: cloudflow's import test MUST lose the two skipped modules once
  they leave its package.
- **FR-007**: `exportit/MAP.md`, the owner's `DEPLOYMENT.md` and
  `exportit/REMINDERS.md` (which loses the item) MUST say where the functions
  are and how they are switched on.
- **FR-008**: cloudflow MUST add one fixed tag to every compute node it
  launches (for example `csis:launched-by = cloudflow`), beside the tags a
  cluster description gives, whatever the site's `Project` value. The tag's
  key and value MUST be one constant, which `csis-sandbox-terraform`'s module
  takes as a variable defaulting to it. This is a change in cloudflow, which
  owns its copied files since 2026-11-19; its tests MUST show the tag on a
  launch request.
- **FR-009**: The identifying function MUST read its report's bucket from
  the environment setting `REPORT_BUCKET` in place of the bucket written into
  its code (`ioos-transfers`, line 140). The module MUST set it from
  `report_bucket`, whose default is `ioos-transfers`, and the role MUST be
  allowed to write report objects there and nowhere else. A test MUST show the
  report written to the bucket the setting names. `lambda.env` gains the
  setting.
- **FR-010**: `exportit/tools/export.py` MUST support `moved`:
  - the lineage check MUST keep filtering each unit with its map as the unit
    was made, so that both units' histories stay valid;
  - a sync MUST carry an upstream change to a moved file into the unit it
    moved to, as a patch on that sync's branch (without the file's upstream
    history), and MUST NOT bring the file back into the unit it left;
  - a moved file that both the old and the new unit's maps claim MUST be a
    problem the check reports;
  - tests MUST prove each of these on throw-away repositories, and the sync
    rehearsal MUST gain a scenario for a change to a moved file.
  The directive is reusable by specs 002, 004 and 005.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The handlers' tests pass, covering every case of User Story 1.
- **SC-002**: `tofu validate` and `tofu plan` succeed with `enable_reaper`
  true and false.
- **SC-003**: The root `just test` and `just full-test` pass, the lineage
  check among them, for both cloudflow and `csis-sandbox-terraform` after the
  move.
- **SC-005**: A plan with `enable_reaper` true shows the role's
  `ec2:TerminateInstances` limited by the tag condition, and no statement
  allowing it on other instances.
- **SC-004**: The sync rehearsal's new scenario, a change to a moved file,
  lands in the unit it moved to and nowhere else.

## Assumptions

- What the functions do does not change, beyond what a test finds broken,
  the report's bucket becoming a setting (FR-009), and the role's limit to
  tagged nodes (FR-005, FR-008).

## Dependencies

None outside this repository and its units. It changes three repositories:
`csis-sandbox-terraform` (the functions, their tests, the module), cloudflow
(the functions leave; the tag is added) and Cloud-Sandbox (the maps,
`export.py`'s `moved`, the records), merged and pushed in that order of units
first.

## Out of Scope

- Changing what the functions do, beyond what a test finds broken and
  FR-008 and FR-009.
- Creating anything in an AWS account (FR-003).

## Carried From

Stage 17, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-17.md`),
as a pointer for a person reading; this spec stands without it.
