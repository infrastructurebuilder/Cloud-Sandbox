# Feature Specification: sandbox-configs split by owner

**Feature Branch**: none yet; `feature/configs-split-by-owner` when it is
taken up

**Created**: 2026-11-14, as stage 20; carried into this spec 2026-11-19

**Status**: Draft. Clarified 2026-11-21; ready for `/speckit-plan`. **Needs
spec 003 first,** for its `moved` directive. `csis-sandbox-configs` moved
whole on moving day (2026-11-17, its decision 4), so this split is now a move
between two repositories.

**Input**: the stage plan of 2026-11-14, carried from the ATTIC on the
operator's instruction of 2026-11-19.

## Why

`csis-sandbox-configs` is two kinds of file with two owners: 3 templates and 48
examples that show how cloudflow is used, and 71 descriptions of one site's
deployments, which are that site's. And 23 of the 122 cannot be read by
today's cloudflow, the template a new site copies among them (it has no
`table_name`). `exportit/MAP.md`'s sandbox-configs section has the details.

## Clarifications

### Session 2026-11-21

- Q: Where should the IOOS deployment's 71 site descriptions live? → A: kept
  as the unit `csis-sandbox-configs`, with its catalogue and a schema check
  against cloudflow's published schema.
- Q: What should happen to the 23 descriptions cloudflow cannot read? → A:
  before the move, in `csis-sandbox-configs`, repair what can be repaired,
  the template's `table_name` first; retire the rest to its attic with the
  reason.
- Q: What should replace `current.system` and `current.image_id`? → A: an
  output of `csis-sandbox-terraform` carrying a complete cluster-description
  fragment, `table_name` included, checked against cloudflow's schema; the
  two files retire to the attic, naming it.
- Q: How should the 51 templates and examples move to cloudflow without
  breaking lineage? → A: with spec 003's `moved` directive, one line per file
  in `sandbox-configs.map`; this spec waits for spec 003's implementation.

### Session 2026-11-23

- Q: What happens to `cloud_sandbox_experiment.template`, whose `MODEL` and
  `JOBTYPE` are placeholders for a model cloudflow has no class for yet?
  (asked while implementing) → A: it stays a template for a new model, as
  `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md` uses it, and moves as it is;
  the schema check reads it as a "new-model template": `MODEL` is
  `MODEL_CLASS`, `JOBTYPE` ends in `_EXPERIMENT`, and its other keys are
  those an existing experiment type requires. It is the one exception to
  "readable by the schema".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A new site starts from cloudflow's examples (Priority: P1)

Someone setting up a new sandbox finds templates and examples beside the code
that reads them, in cloudflow, and every one of them is readable by that
cloudflow.

**Why this priority**: today the template a new site copies cannot be read.

**Independent Test**: cloudflow's tests check every example it carries
against its schema.

**Acceptance Scenarios**:

1. **Given** cloudflow's examples, **When** its tests run, **Then** every
   example is read by its schema.
2. **Given** the template, **When** a site copies it, **Then** it has a
   `table_name`.

### User Story 2 - The site's own files stay the site's (Priority: P2)

The descriptions of the IOOS deployment stay in their own place, checked
against the schema cloudflow publishes.

**Why this priority**: they are one site's, not cloudflow's.

**Independent Test**: `csis-sandbox-configs`' catalogue and schema check.

**Acceptance Scenarios**:

1. **Given** the site's files, **When** the schema check runs, **Then** each
   is read by cloudflow's published schema, or is in the attic with its
   reason.

### Edge Cases

- A description that can be repaired and one that cannot: the first is
  repaired, the second retired with its reason, both before the move
  (FR-003).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The templates and examples MUST move to cloudflow, under its
  `examples/configs/`, and the schema writer
  (`exportit/tools/configs_schema.py`) into cloudflow, so that the schema is
  published with the code that reads it. `csis-sandbox-configs` keeps the
  site's files and the schema check, against cloudflow's published schema.
- **FR-002**: The site's 71 descriptions MUST stay in `csis-sandbox-configs`,
  which remains a unit for the IOOS deployment: its mapping file, its
  catalogue, and a schema check against the schema cloudflow publishes.
- **FR-003**: Before anything moves, the 23 descriptions today's cloudflow
  cannot read MUST be dealt with in `csis-sandbox-configs`, which owns them
  since 2026-11-19: each repairable one repaired (trailing commas, missing
  keys, and first the template's missing `table_name`), each other retired to
  the unit's attic with its reason in the catalogue. Cloudflow then receives
  only files its schema reads, with one exception: the template for a new
  model, `cloud_sandbox_experiment.template`, whose `MODEL` and `JOBTYPE` are
  placeholders by design, is checked as a new-model template (its other keys
  those an existing experiment type requires; clarified 2026-11-23).
- **FR-004**: `csis-sandbox-terraform` MUST gain an output carrying a
  complete cluster-description fragment (the image ID, region, subnet,
  security groups and `table_name`), and a test MUST check that fragment
  against cloudflow's published schema. `cluster.configs/IOOS/current.system`
  and `current.image_id`, read by nothing and kept by hand, MUST then retire
  to `csis-sandbox-configs`' attic, their catalogue reason naming the output.
- **FR-005**: Each of the 51 templates and examples has one owner after the
  split, cloudflow, so it MUST move with spec 003's `moved` directive: one
  line per file in `sandbox-configs.map`,
  `moved <source> cloudflow examples/configs/<name>`. `just export-lineage`
  MUST stay green for both units, and `just export-sync` MUST carry an
  upstream change to a moved file into cloudflow (constitution, principle I).
- **FR-006**: The catalogue and the schema check MUST follow the files;
  cloudflow's tests MUST check the examples it carries against its schema.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every description, in either place, is read by cloudflow, or is
  in an attic with its reason.
- **SC-002**: The root `just test` and `just full-test` pass, the lineage check
  among them.

## Assumptions

- cloudflow is the right owner of its own examples and schema.

## Dependencies

- Spec 003: its `moved` directive, implemented and merged first (FR-005).
- `csis-sandbox-terraform` gains the output of FR-004, changed and pushed in
  its own repository first.

## Out of Scope

Changing what cloudflow reads.

## Outcome

Implemented 2026-11-23, nothing on AWS.

- **The 23 unreadable**, dealt with in `csis-sandbox-configs` before anything
  moved: 17 repaired (2 trailing commas; 6 missing `table_name`; 9 keys a
  sibling of the same model gave: `GRID` for three CORA reanalyses, `SAVEDIR`
  for five ROMS forecasts, and three for `local.plots`); 4 retired to `attic/`
  with their reasons (no sibling gave what they lacked); the new-model template
  read as one (clarified 2026-11-23); `current.system` retired with
  `current.image_id` (FR-004).
- **Moved**: 51 templates and examples (3 and 48) to cloudflow's
  `examples/configs/`, by 51 `moved` lines; searched first (no secret, account
  number or real email; two personal paths already public in the original).
- **Kept**: 66 site descriptions, every one read by cloudflow; 7 helpers,
  notes and pointers; 6 retired, with their reasons.
- **The schema** lives in cloudflow (`schema/`, `tools/configs_schema.py`,
  `tools/schema_check.py`); `csis-sandbox-configs` holds checked copies of the
  schema and the rules (`just configs-schema-check`).
- **FR-004**: `csis-sandbox-terraform`'s output `cluster_description`, its
  keys held to cloudflow's cluster schema; it carries the head node's three
  security groups (as `current.system` did) and `key_name`, beyond the plan's
  list. Its finding of the image once `node-image.yml` has made it is proved
  only by a real deployment (spec 001).
- **SC-001**: every description, in either place, is read by cloudflow or is
  in an attic with its reason. **SC-002**: see tasks T034 and T035.

## Carried From

Stage 20, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-20.md`),
as a pointer for a person reading; this spec stands without it.
