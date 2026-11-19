# Feature Specification: The live proof on AWS

**Feature Branch**: none yet; `feature/live-proof` when it is taken up

**Created**: 2026-11-14, as stage 15; carried into this spec 2026-11-19

**Status**: Draft. **Blocked:** it needs an AWS account in which a VPC and a
subnet can be created. The `noaa` profile's role denies both (checked
2026-11-15, read-only), and the operator is finding another account.

**Input**: the stage plan of 2026-11-14 ("Make a plan for the live proof"),
carried from the ATTIC on the operator's instruction of 2026-11-19.

## Why

Everything built since the units were made is proved on the local machine
and in an AlmaLinux 10 container. What only a real head node can show is
still not proved:

| Not proved | Why only a head node shows it |
| --- | --- |
| `efa_driver`, `fsx_lustre_client` | kernel modules, built for the running kernel |
| `hpc_tuning` | kernel settings and a `tuned` profile |
| `node-image.yml` | an EBS snapshot and a machine image, through `amazon.aws` |
| Building `spack_environment` | the container only concretizes; a real build takes hours |
| Module files with `refresh_modules: when_needed` | only a real build writes real module files |
| The site mirror's list (off by default) | needs the site's bucket and key |
| Anything on RHEL, or on AWS | the container is AlmaLinux |
| The first-boot script | needs a real EFS volume, and cloud-init |
| Whether the playbooks leave the same node the script did | needs a second node, built the old way |

`csis-sandbox-provisioning/docs/LIVE-PROOF.md` is the procedure, written
before the units had repositories and never run. It is out of date: it
assumes the original `terraform/` and Terraform 1.5.7 (the unit is
`csis-sandbox-terraform`, with OpenTofu 1.13.9, which its `versions.tofu`
requires), copies the playbooks by `tar` without installing the collection
first (its box B2 would fail at the `spack` role), and says nothing of check
mode, the comparison of Spack's configuration, or `refresh_modules`.

What was found while planning, and still holds:

- With the module's default `t3.medium`, `spack_jobs` is 1, and the
  script's `spack_cache_only: -1` compiles everything.
- The site's build cache holds 103 specs, all `rhel8`, built with oneAPI
  2023.1.0, Intel 2021.9.0 and gcc 11.2.1, in the layout of Spack before 1.0:
  its key can be trusted and the mirror added, but it supplies nothing to a
  RHEL 10 build.
- In the `noaa` account (2026-11-15): the role allows IAM roles, instances,
  security groups, EFS, images and key pairs, and denies `ec2:CreateVpc` and
  `ec2:CreateSubnet`. Its state bucket `cloud-sandbox-tfstate` returns 403.
  Only us-east-2's VPC reaches the internet, through a NAT; it is a shared
  account with many running head nodes.

## Clarifications

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A head node built by the playbooks on AWS (Priority: P1)

The operator creates a head node with `csis-sandbox-terraform`, and builds it
with `csis-sandbox-provisioning`'s `site.yml`, as the first boot would, and
sees it built, built again with nothing changed, and previewed in check mode
with nothing to change.

**Why this priority**: it is what the units were made for, and none of it has
been done on a real node.

**Independent Test**: one head node in a workspace of its own; `site.yml`
applied twice and once in check mode, with its recap kept.

**Acceptance Scenarios**:

1. **Given** a fresh account session and the plan showing only additions,
   **When** the node is created, **Then** OpenTofu reports `0 to change, 0 to
   destroy` before anything is applied.
2. **Given** the node, **When** `site.yml` is applied, **Then** it ends with
   `failed=0`; applied again, every task that changes is listed as a finding.
3. **Given** the built node, **When** check mode runs, **Then** every task that
   would change is listed as a finding.
4. **Given** the built node, **When** Spack's configuration is compared with
   the container's (`tests/container/expected-spack-config.json`), **Then**
   each difference is recorded as a finding, not a failure.

### User Story 2 - An image a compute node can start from (Priority: P2)

The operator runs `node-image.yml` on the built node and gets a machine image
that AWS reports `available`.

**Why this priority**: compute nodes start from it; it is the step the
container cannot take at all.

**Independent Test**: the image's state in `aws ec2 describe-images`.

**Acceptance Scenarios**:

1. **Given** the built node, **When** `node-image.yml` runs, **Then** an image
   and its snapshot exist and the image is `available`.

### User Story 3 - Nothing left behind (Priority: P2)

When the proof is over, everything it created is removed, or kept by the
operator's choice, and the account shows nothing else of it.

**Why this priority**: a forgotten node or image is a bill.

**Independent Test**: list what carries the proof's name tag after removal.

**Acceptance Scenarios**:

1. **Given** the proof's resources, **When** they are removed, **Then** no
   instance, volume, image, snapshot, security group or role of the proof
   remains, unless kept by decision.

### Edge Cases

- The session expires during the hours of a build: the build must be
  resumable, or the session refreshed between stages of the procedure.
- The plan shows a change or a destruction: stop; nothing is applied.
- A second apply changes something because a package was released upstream
  in the meantime (botocore has done it in the container): recorded, and the
  apply repeated, before it is called a finding.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The AWS session MUST be checked first (`aws sts
  get-caller-identity`); if it fails, the work stops and the operator is asked
  to refresh it.
- **FR-002**: `LIVE-PROOF.md` MUST be brought up to date, as its version 2,
  before it is run, in the repository's step form (numbered and versioned
  boxes, a check as the last line of its box, a time estimate on any box over
  thirty seconds, every choice a bold decision with its default, "your local
  machine" and "the head node" named in every step). This is a change in
  `csis-sandbox-provisioning`.
- **FR-003**: Stage A of the page MUST use a working copy of
  `csis-sandbox-terraform` and its pinned OpenTofu, in a workspace and a
  settings file of its own, with state kept locally, never in a shared
  bucket; and MUST stop unless the plan shows only additions.
- **FR-004**: Stage B MUST end with exactly what the first-boot template does:
  the checkout, `ansible-galaxy collection install -r requirements.yml` (from
  Ansible Galaxy), then the plays; then a second apply, check mode, the Spack
  configuration comparison, and the module-file check (every module file
  under the environment's root has the time it had after the first apply).
- **FR-005**: Nothing MUST be created, changed or removed on AWS without the
  operator's word at that step (`tofu apply`, `tofu destroy`,
  `node-image.yml`, image and snapshot removal). Existing resources in
  `us-east-2` MUST NOT be changed.
- **FR-006**: The logs MUST NOT be committed: they hold the node's addresses
  and the account's identifiers. Their summary goes in this spec's outcome.
- **FR-007**: Who runs the boxes: [NEEDS CLARIFICATION: the agent runs them,
  the local machine's in its shell and the head node's over `ssh`, stopping at
  every gate, decision and AWS change (default); or the operator runs them from
  the page and brings back the logs.]
- **FR-008**: The account and its network: [NEEDS CLARIFICATION: which account
  and region; whether the module creates its network there, or is given an
  existing VPC and subnet by ID, read only. No default: the `noaa` account
  cannot create a network.]
- **FR-009**: The instance type for the build: [NEEDS CLARIFICATION: a
  compute-optimised type with sixteen processors or more, so `spack_jobs` is
  fifteen and the build takes hours, not a day (default); or the settings
  file's own type.]
- **FR-010**: How the playbooks reach the node: [NEEDS CLARIFICATION: by hand,
  as the first boot would: the node boots with the old template, its last step
  removed, and the three commands of `init_template.ansible.tpl` are run by
  hand (default); or by the real first boot, with `provisioning_repo` naming
  `csis-sandbox-provisioning`, which is private and needs a deploy key or a
  token on the node (see spec 006).]
- **FR-011**: The Spack build: [NEEDS CLARIFICATION: `spack_cache_only: -1`,
  compiling everything, as the script does (default); or `0`, taking what
  Spack's public binary cache has.]
- **FR-012**: The site mirror's list: [NEEDS CLARIFICATION: applied on the
  proof's node, `spack_site_mirror: true` (default); or left off.]
- **FR-013**: A second node built the old way: [NEEDS CLARIFICATION: skipped
  (default: the container already holds Spack's configuration to the
  script's); or built, the only direct evidence for the last row of the table
  above.]
- **FR-014**: A compute node from the image: [NEEDS CLARIFICATION: out of
  scope (default: it needs a cluster description, the DynamoDB table and
  cloudflow); or one compute node started with cloudflow and the smallest
  model job run.]
- **FR-015**: At the end: [NEEDS CLARIFICATION: the node, the EFS volume, the
  image and its snapshot removed, each step asked first (default); or the node
  kept for a look, billed while it stands.]
- **FR-016**: JupyterHub, kept as an option (stage 13), MUST be applied and
  checked on the node as the container test checks it, the hub answering on
  its port.

### Key Entities

- **The proof's workspace**: an OpenTofu workspace and settings file of its
  own, with local state, holding everything the proof creates.
- **The findings**: every task that changed on a second apply or in check
  mode, every Spack configuration difference, every row of the table above
  proved or not.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `site.yml` ends `failed=0` on a RHEL 10 head node; its second
  apply and its check-mode run change nothing, or each change is a recorded
  finding.
- **SC-002**: `node-image.yml` makes an image AWS reports `available`.
- **SC-003**: Every row of the "Not proved" table is marked proved, with the
  date and what was seen, or left not proved with the reason, in
  `exportit/MAP.md`.
- **SC-004**: After removal, nothing of the proof remains in the account but
  what the operator chose to keep.

## Assumptions

- An account that can create a network, or a VPC and subnet the operator
  names, will be available; nothing here starts until it is.
- The build cache is no help (the site's holds only RHEL 8 packages), so the
  build is from source unless FR-011 says otherwise.

## Dependencies

- Done: the units and their repositories (moving day); the collection on
  Galaxy; JupyterHub kept as an option (stage 13).
- Specs 002 (the RHEL 10 build cache) and 004 (spack-stack) need this one's
  head node, or one like it.

## Out of Scope

- Changing `main.tf` of `csis-sandbox-terraform` in the unit itself: the
  working copy is edited, never the unit (spec 006 changes the unit).
- Running a model, unless FR-014 says so.
- Fixing what the proof finds: a finding becomes a spec of its own, in the
  unit it concerns.

## Carried From

Stage 15, planned 2026-11-14 and paused 2026-11-15, now in the ATTIC
(`ATTIC/SPECS/STAGE-15.md`), as a pointer for a person reading; this spec
stands without it.
