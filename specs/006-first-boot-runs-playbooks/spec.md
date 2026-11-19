# Feature Specification: The first boot runs the playbooks

**Feature Branch**: none yet; `feature/first-boot-runs-playbooks` when it is
taken up

**Created**: 2026-11-14, as stage 21; carried into this spec 2026-11-19

**Status**: Draft. Needs nothing first: it is written and tested without AWS,
and put into use by the first head node built after it (spec 001 can be that
node).

**Input**: the stage plan of 2026-11-14 ("the two-variable change"), carried
from the ATTIC on the operator's instruction of 2026-11-19.

## Why

`csis-sandbox-terraform`'s `main.tf` still renders `init_template.tpl`, which
clones `ioos/Cloud-Sandbox` (read only) and runs the old `setup-instance.sh`.
The new template, `init_template.ansible.tpl`, runs the playbooks with
`ansible-pull`, and needs two values `main.tf` does not pass:
`provisioning_repo` and `provisioning_version`. Since moving day
`csis-sandbox-provisioning` has a repository whose URL can be named, and
since 2026-11-19 `csis-sandbox-terraform` owns its copied files, so the
change is made in the unit itself, not as a patch here. That repository is
private, which the first boot has to be able to clone.

## Clarifications

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A new head node builds itself from the playbooks (Priority: P1)

The operator creates a head node with `csis-sandbox-terraform`, naming the
playbooks' repository and version, and the node's first boot fetches them,
installs the collections, and applies them, with no step by hand.

**Why this priority**: it is the last place the sandbox still runs the old
script.

**Independent Test**: the rendered user data, held to the template, without
AWS; then a node's first boot, in spec 001.

**Acceptance Scenarios**:

1. **Given** the two values, **When** the module is rendered, **Then** the user
   data names the repository and version, and is the template's.
2. **Given** no `provisioning_repo`, **When** a plan is made, **Then** it fails
   with a message naming it.
3. **Given** an empty workspace, **When** a plan is made with the values,
   **Then** it shows the user data naming the repository.

### Edge Cases

- The playbooks' repository is private: a node without a way to authenticate
  cannot clone it, and the first boot must fail visibly, not quietly build
  nothing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `main.tf` MUST render `init_template.ansible.tpl` and pass
  `provisioning_repo` and `provisioning_version`; `variables.tf` MUST gain
  them, with no default for `provisioning_repo`, so a plan without it fails.
  `sandbox_version` stays while the template still clones a repository for
  cloudflow.
- **FR-002**: cloudflow at first boot: [NEEDS CLARIFICATION: keep cloning the
  original `ioos/Cloud-Sandbox`, read only, for cloudflow, as now (default:
  this repository no longer holds cloudflow, and cloudflow's own repository is
  private); or install cloudflow from its own repository at a tag, which needs
  the node to authenticate to it and a line in the template.]
- **FR-003**: How the node authenticates to the private
  `csis-sandbox-provisioning`: [NEEDS CLARIFICATION: a read-only deploy key on
  that repository, its private half put in place outside the repository (for
  example from a secret store the node's role can read); a token; or the
  repository made public. No default: it is the operator's to choose, and the
  key is never in a repository or a variable.]
- **FR-004**: `test_template.py` MUST render the main module with the two
  values and hold the rendered user data to the template; `tofu validate` MUST
  pass; a plan in an empty workspace MUST show the user data naming the
  repository.
- **FR-005**: `csis-sandbox-terraform`'s `DEPLOYMENT.md` MUST say how to set
  the two values, and that `provisioning_repo` is `csis-sandbox-provisioning`'s
  URL and `provisioning_version` one of its tags.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A plan without `provisioning_repo` fails with a message naming
  it.
- **SC-002**: The rendered user data names the repository and version.
- **SC-003**: The root `just test` and `just full-test` pass.

## Assumptions

- `init_template.ansible.tpl` already does the checkout, the collections from
  `requirements.yml` (from Ansible Galaxy) and the plays; only `main.tf` and
  `variables.tf` change, and the authentication FR-003 chooses.

## Dependencies

None to write and test it. Its first real use is a head node's first boot
(spec 001, or after it).

## Out of Scope

Building a node (spec 001).

## Carried From

Stage 21, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-21.md`),
as a pointer for a person reading; this spec stands without it.
