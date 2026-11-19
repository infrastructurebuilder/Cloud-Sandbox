# Feature Specification: sandbox-configs split by owner

**Feature Branch**: none yet; `feature/configs-split-by-owner` when it is
taken up

**Created**: 2026-11-14, as stage 20; carried into this spec 2026-11-19

**Status**: Draft. Needs nothing first. `csis-sandbox-configs` moved whole on
moving day (2026-11-17, its decision 4), so this split is now a move between
two repositories.

**Input**: the stage plan of 2026-11-14, carried from the ATTIC on the
operator's instruction of 2026-11-19.

## Why

`csis-sandbox-configs` is two kinds of file with two owners: 3 templates and 48
examples that show how cloudflow is used, and 71 descriptions of one site's
deployments, which are that site's. And 23 of the 122 cannot be read by
today's cloudflow, the template a new site copies among them (it has no
`table_name`). `exportit/MAP.md`'s sandbox-configs section has the details.

## Clarifications

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

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
  repaired, the second retired with its reason (FR-003).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The templates and examples MUST move to cloudflow, under its
  `examples/configs/`, and the schema writer
  (`exportit/tools/configs_schema.py`) into cloudflow, so that the schema is
  published with the code that reads it. `csis-sandbox-configs` keeps the
  site's files and the schema check, against cloudflow's published schema.
- **FR-002**: The site's files: [NEEDS CLARIFICATION: kept as one unit,
  `csis-sandbox-configs`, for the IOOS deployment (default); or not kept as a
  unit at all, returned to the site.]
- **FR-003**: The 23 that cannot be read: [NEEDS CLARIFICATION: repair what
  can be repaired (the trailing commas, the missing `table_name` in the
  template, the missing keys) in the unit, which owns its files since
  2026-11-19, and retire the rest to its attic with the reason (default); or
  leave them, recorded, for the site.]
- **FR-004**: `current.system` and `current.image_id`, read by nothing and
  kept by hand: [NEEDS CLARIFICATION: replaced by what `csis-sandbox-terraform`
  writes, an output carrying a complete cluster-description fragment,
  `table_name` included, which this spec adds (default); or left.]
- **FR-005**: The move is between two units: [NEEDS CLARIFICATION: first,
  whether both units need them, in which case they go to a common unit or a
  single source instead (constitution 1.1.0, principle I); if only one does,
  how the moved files' mapping lines move from `sandbox-configs.map` to
  `cloudflow.map`, and both units' lineage is kept, given that their history
  will not follow them across (constitution, principle I).]
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

None.

## Out of Scope

Changing what cloudflow reads.

## Carried From

Stage 20, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-20.md`),
as a pointer for a person reading; this spec stands without it.
