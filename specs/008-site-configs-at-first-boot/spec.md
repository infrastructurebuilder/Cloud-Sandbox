# Feature Specification: The first boot puts the site's descriptions on the head node

**Feature Branch**: `feature/site-configs-at-first-boot`

**Created**: 2026-11-23, on the operator's instruction of that day: option 2
of three, "as a follow up for spec 006"

**Status**: Draft. **Needs specs 006 and 007 first**: 006's first boot, which
this extends, and 007's access to a private repository, which this uses.

**Input**: a finding of spec 005's convergence (2026-11-23). The original
first boot cloned the `ioos/Cloud-Sandbox` monorepo, which held the site's job
and cluster descriptions (`job.configs/`, `cluster.configs/`). Spec 006
replaced that clone with cloudflow's; spec 005 left the site's descriptions in
`csis-sandbox-configs` alone. Nothing now puts them on a new head node, so a
node has cloudflow and its examples but not the descriptions a real run uses
(`cbofs.fcst`, `ioos.nosofs.cfg` and the rest). The operator chose to keep
`csis-sandbox-configs` private and reach it with spec 007's credential, over
making it public or copying the files by hand.

## Why

- **A site's runs need its descriptions on the node:** cloudflow is started
  with a cluster description and a job description
  (`workflow_main.py <cluster> <job>`), and the site's are the ones with its
  account's images, groups and subnets.
- **They stay private:** `csis-sandbox-configs` holds the IOOS account's
  resource IDs, and stays private (the operator's choice).
- **The access already planned is for one repository:** spec 007 lets the
  first boot read a private **playbooks'** repository with a read-only deploy
  key or a fine-grained token (its FR-008: the playbooks' only). This spec
  extends it to the site's descriptions.

## Clarifications

None asked yet.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A new head node has the site's descriptions (Priority: P1)

The operator names the site's descriptions' repository and tag; the node's
first boot clones it, with spec 007's credential, where cloudflow's runs look
for it, and removes the credential afterwards.

**Why this priority**: without it no site run can start on a new node.

**Independent Test**: the rendered user data, without AWS; then a first boot
with the private repository.

**Acceptance Scenarios**:

1. **Given** a configs repository, tag and access set, **When** the module is
   rendered, **Then** the user data clones it after cloudflow, into the place
   the site's runs read it from, and names the credential's secret but holds
   no credential.
2. **Given** that node's first boot, **When** it has finished, **Then** the
   site's descriptions are on the node at that place, at the tag, and no file,
   log or configuration holds the credential.
3. **Given** no configs repository set, **When** the module is rendered,
   **Then** the user data is spec 006's (or 007's) as it was.

### User Story 2 - The run guides say where the descriptions are (Priority: P2)

The guides that start a run (`workflow_main.py ../cluster.configs/… ../job.configs/…`)
name the place this spec puts the site's descriptions.

**Why this priority**: today about a dozen guides in six units name paths of
the old checkout that no longer exist.

**Independent Test**: a search of every unit's guides for the old relative
paths finds none.

### Edge Cases

- The secret cannot be read, or the clone is refused (a revoked key, an expired
  token): the first boot stops visibly, as spec 007's does, before an image is
  made.
- A site with no private descriptions of its own: no configs repository is set,
  and nothing changes.
- The descriptions' `CONFIGTMPL` paths name the old checkout's
  `Cloud-Sandbox/cloudflow/…`: spec 006's link serves them; the place chosen
  here must not break it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-terraform` MUST gain `configs_repo` and
  `configs_version` (a tag), both optional: unset, nothing is cloned and the
  user data is unchanged.
- **FR-002**: When set, the first boot MUST clone the configs repository at its
  tag, as `$RUNUSER`, after cloudflow and before the plays, into
  [NEEDS CLARIFICATION: the place the site's runs read the descriptions from:
  `/save/$RUNUSER/Cloud-Sandbox/` (so `job.configs/` and `cluster.configs/` sit
  beside the `cloudflow` link, and the old `../job.configs/` paths from it keep
  working), or `/save/$RUNUSER/sandbox-configs/`, with the guides changed to
  name it].
- **FR-003**: The clone MUST use spec 007's access: [NEEDS CLARIFICATION: one
  fine-grained token read-only on both private repositories, the playbooks'
  and the descriptions', in one secret; or a second deploy key, the
  descriptions' own (a deploy key reaches one repository), in a second secret;
  or either, as the operator sets]. The credential is read, used and removed as
  spec 007's FR-005 says, and never written anywhere else.
- **FR-004**: A secret that cannot be read, or a refused clone, MUST stop the
  first boot visibly before any image is made.
- **FR-005**: The head node's role MUST be allowed to read only the secrets
  this and spec 007 name.
- **FR-006**: The run guides in every unit that name the old checkout's
  `../job.configs/` and `../cluster.configs/` MUST name the place FR-002
  chooses, each changed in its own unit.
- **FR-007**: Tests MUST render the module with and without the configs
  repository and hold the user data to the template, as specs 006 and 007 do;
  no credential value appears in any rendered output or plan.

### Key Entities

- **The site's descriptions**: `csis-sandbox-configs`' `job.configs/` and
  `cluster.configs/`, at a tag.
- **The credential**: spec 007's deploy key or token, kept in Secrets Manager.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a new head node, `workflow_main.py` can be started with one
  of the site's cluster descriptions and one of its job descriptions, by the
  paths the guides give, with no file copied by hand.
- **SC-002**: With no configs repository set, the user data is unchanged.
- **SC-003**: After the first boot, a search of the node for the credential's
  value finds nothing.
- **SC-004**: A search of every unit's guides for the old checkout's relative
  paths finds none.

## Assumptions

- `csis-sandbox-configs` stays private (the operator's choice, 2026-11-23).
- Spec 007 is built first; this reuses its secret handling and adds a
  second clone to it.
- Proving the private clone needs a head node (spec 001's procedure) and the
  credential made by the operator.

## Dependencies

- Spec 006 (the first boot it extends) and spec 007 (the access it uses).

## Out of Scope

- Making `csis-sandbox-configs` public, or copying descriptions by hand (the
  options not chosen).
- Changing what the descriptions say, beyond paths in the guides.
