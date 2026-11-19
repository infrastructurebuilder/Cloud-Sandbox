# Feature Specification: The Lambda functions, owned and deployable

**Feature Branch**: none yet; `feature/lambda-functions-owner` when it is
taken up

**Created**: 2026-11-14, as stage 17; carried into this spec 2026-11-19

**Status**: Draft. Needs nothing first: no AWS account is needed to write and
test it.

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

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

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
   the two functions, their schedule, their role and its policy.

### Edge Cases

- Applying the module starts terminating nodes past their limit: it is the
  operator's to switch on, never a test's.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Who owns them: [NEEDS CLARIFICATION: `csis-sandbox-terraform`,
  as infrastructure of the account beside the table they read (default); a
  unit of their own, `csis-sandbox-reaper`, with its own tests and OpenTofu
  module, applied after `csis-sandbox-terraform` (one more repository, which
  is the operator's to create); or they stay in cloudflow, outside the
  package, deployed by hand, and documented as such.]
- **FR-002**: Moving them out of cloudflow moves files between units:
  [NEEDS CLARIFICATION: how their mapping lines move (cloudflow's map drops
  the two files and `lambda.env`, the new owner's map takes them) and both
  units' lineage is kept (constitution, principle I).]
- **FR-003**: Deploying now: [NEEDS CLARIFICATION: with either of the first
  two owners, write the module and test it with `tofu validate` and `tofu plan`
  against a workspace with no resources (default); or also apply it in the
  account.]
- **FR-004**: Tests MUST cover the cases of User Story 1, with the AWS calls
  replaced; no test reaches AWS.
- **FR-005**: The module (with the default owner) MUST hold the two functions,
  their packaging, an EventBridge schedule, a role allowed exactly the table,
  `ec2:DescribeInstances` and `ec2:TerminateInstances` on instances the
  sandbox tagged, and the report's bucket; variables `lambda_max_minutes`,
  `table_name` and `report_bucket`; off unless `enable_reaper` is true.
- **FR-006**: cloudflow's import test MUST lose the two skipped modules once
  they leave its package.
- **FR-007**: `exportit/MAP.md`, the owner's `DEPLOYMENT.md` and
  `exportit/REMINDERS.md` (which loses the item) MUST say where the functions
  are and how they are switched on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The handlers' tests pass, covering every case of User Story 1.
- **SC-002**: `tofu validate` and `tofu plan` succeed with `enable_reaper`
  true and false.
- **SC-003**: The root `just test` and `just full-test` pass, the lineage
  check among them.

## Assumptions

- What the functions do does not change, beyond what a test finds broken.

## Dependencies

None.

## Out of Scope

Changing what the functions do, beyond what a test finds broken.

## Carried From

Stage 17, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-17.md`),
as a pointer for a person reading; this spec stands without it.
