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

### Session 2026-11-23

- Q: Where on the head node should the first boot put the site's description
  files? → A: clone into `/save/$RUNUSER/sandbox-configs`, and link
  `/save/$RUNUSER/Cloud-Sandbox/job.configs` and `…/cluster.configs` to it, so
  the old paths keep working; the guides gain a note saying where the files
  are.
- Q: Which credential should the first boot use to read the private
  `csis-sandbox-configs`? → A: a read-only deploy key on that repository,
  in a Secrets Manager secret of its own.
- The operator, the same day: the documentation must note the need for the
  key (or a token) in all the right places → FR-008, SC-005.

### Session 2026-11-25

Found while planning: the guides run `workflow_main.py ../cluster.configs/…
../job.configs/…` from inside `/save/$RUNUSER/Cloud-Sandbox/cloudflow`, which
is a link to `/save/$RUNUSER/cloudflow/src/cloudflow` (spec 006). A program
resolves `..` from its real directory, so those paths land in
`/save/$RUNUSER/cloudflow/src/` (tried: with links at
`Cloud-Sandbox/job.configs` only, the shell's `ls ../job.configs` and a
program's `open('../job.configs/x')` both fail).

- Q: Where should the links to the site's descriptions go? → A: in both
  places: `/save/$RUNUSER/cloudflow/src/job.configs` and `…/cluster.configs`,
  where the guides' relative paths land (inside cloudflow's checkout, kept out
  of its git status), and `/save/$RUNUSER/Cloud-Sandbox/job.configs` and
  `…/cluster.configs`, for the old absolute paths (the operator, "Both
  places").

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

**Independent Test**: every unit's guide that names the old relative paths
carries the note of FR-006.

### Edge Cases

- The secret cannot be read, or the clone is refused (a revoked key, an expired
  token): the first boot stops visibly, as spec 007's does, before an image is
  made.
- A site with no private descriptions of its own: no configs repository is set,
  and nothing changes.
- The descriptions' `CONFIGTMPL` paths name the old checkout's
  `Cloud-Sandbox/cloudflow/…`: spec 006's link serves them; the place chosen
  here must not break it.
- A head node booted on an EFS volume an earlier node used (added by the
  analysis of 2026-11-28; spec 001's open reminder about `/save` on a kept
  volume is the same pattern): `/save/$RUNUSER/sandbox-configs` may be there
  already. A clone of the configs repository at `configs_version` is kept as
  it is, and the links are made again; a clone at another tag, or anything
  else at that path, stops the first boot before the plays, naming the path
  and what it found. Nothing on the volume is overwritten (FR-002).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-terraform` MUST gain `configs_repo` and
  `configs_version` (a tag), both optional: unset, nothing is cloned and the
  user data is unchanged.
- **FR-002**: When set, the first boot MUST clone the configs repository at its
  tag, as `$RUNUSER`, after cloudflow and before the plays, into
  `/save/$RUNUSER/sandbox-configs`, and MUST link its two directories,
  `job.configs` and `cluster.configs`, in two places: in
  `/save/$RUNUSER/cloudflow/src/`, where the guides' relative paths
  (`../job.configs/…`, run from the cloudflow link) land, kept out of
  cloudflow's git status; and in `/save/$RUNUSER/Cloud-Sandbox/`, beside spec
  006's `cloudflow` link, for the old absolute paths. A test MUST show a
  program opening `../job.configs/…` from the cloudflow link reaching the
  site's file. On a volume that already holds that directory, the first boot
  MUST keep a clone at the tag and stop on anything else, as the Edge Cases
  say.
- **FR-003**: The clone MUST use a read-only deploy key on the configs
  repository, its private half in a Secrets Manager secret of its own, named to
  the module (`configs_secret_arn`), read, used and removed as spec 007's
  FR-005 says (in memory-backed storage, with tracing off, removed before the
  image), over SSH with GitHub's pinned host keys (spec 007's FR-006). It is
  never written anywhere else.
- **FR-004**: A secret that cannot be read, or a refused clone, MUST stop the
  first boot visibly before any image is made.
- **FR-005**: The head node's role MUST be allowed to read only the secrets
  this and spec 007 name.
- **FR-006**: The run guides in every unit that name the old checkout's
  `../job.configs/` and `../cluster.configs/` MUST gain a note that, on a head
  node, those paths reach the site's descriptions in
  `/save/$RUNUSER/sandbox-configs` through the links of FR-002, each changed in
  its own unit; their commands stay as they are. On 2026-11-25 they are ten
  guides in eight units (the plan's research R5 lists them).
- **FR-007**: Tests MUST render the module with and without the configs
  repository and hold the user data to the template, as specs 006 and 007 do;
  no credential value appears in any rendered output or plan.
- **FR-008**: Every document that tells someone how to deploy a sandbox, what
  its first boot does, or how to start a run MUST say that reading
  `csis-sandbox-configs` needs a credential: the read-only deploy key of FR-003,
  made by the operator, its private half in its own Secrets Manager secret,
  never in a repository or a variable; and that a private playbooks'
  repository needs its own credential, spec 007's deploy key or fine-grained
  token. Without the key, the site's descriptions are not on the node. The
  places, each changed in its own repository:
  - `csis-sandbox-terraform`'s `DEPLOYMENT.md`: the settings (`configs_repo`,
    `configs_version`, `configs_secret_arn`), how to make the key, add it to
    the repository as read-only, put it in the secret and replace it; beside
    spec 007's section on the playbooks' credential;
  - `csis-sandbox-terraform`'s `README.md`, its first-boot section;
  - `csis-sandbox-configs`' `README.md`: the repository is private, and head
    nodes read it with that key;
  - `csis-sandbox-provisioning`'s `DEPLOYMENT.md`, "What happens at first
    boot": the clone of the site's descriptions, and its key;
  - the run guides of FR-006: their note says the descriptions are there only
    when the deployment set `configs_repo` and its key;
  - Cloud-Sandbox's `exportit/MAP.md` (the `sandbox-terraform` first-boot
    section) and `specs/README.md`.

### Key Entities

- **The site's descriptions**: `csis-sandbox-configs`' `job.configs/` and
  `cluster.configs/`, at a tag.
- **The credential**: a read-only deploy key on `csis-sandbox-configs`, its
  private half in a Secrets Manager secret of its own (`configs_secret_arn`),
  separate from spec 007's credential for the playbooks' repository (FR-003).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a new head node, `workflow_main.py` can be started with one
  of the site's cluster descriptions and one of its job descriptions, by the
  paths the guides give, with no file copied by hand.
- **SC-002**: With no configs repository set, the user data is unchanged.
- **SC-003**: After the first boot, a search of the node for the credential's
  value finds nothing.
- **SC-004**: Every unit's guide that names the old checkout's relative paths
  carries the note of FR-006, and those paths resolve on a new head node.
- **SC-005**: Each place FR-008 lists says the key is needed, and how it is
  made and kept; a search of them for `configs_secret_arn` or "deploy key"
  finds each one.

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
