# Feature Specification: spack-stack for UFS Coastal

**Feature Branch**: none yet; `feature/spack-stack-ufs-coastal` when it is
taken up

**Created**: 2026-11-14, as stage 18; carried into this spec 2026-11-19

**Status**: Planned and tasked 2026-11-21; tasks corrected by the analysis of
2026-11-26; in progress since 2026-11-26. Specs 001, 002 and 009 merged: this
spec's head node is built with spec 001's module and procedure, and is spec
009's proof on a real node. A real build of spack-stack takes hours.

**Input**: the stage plan of 2026-11-14, carried from the ATTIC on the
operator's instruction of 2026-11-19.

## Why

UFS Coastal builds against spack-stack, a Spack distribution with its own
environments and meta-modules, not against the sandbox's Spack environment.
Today that is `csis-sandbox-ops`' `bin/add-ufs-setup.sh`, with
`ufs-envars.sh`, run by hand on a built head node, and it **fails as
written**: its line 27 calls `install_gcc_toolset_yum`, which the setup
script's library no longer defines. Its versions are RHEL 8's
(`linux-rhel8`, Spack v0.22.5, spack-stack 2.0 from the fork
`asascience-open/spack-stack`). `csis-model-ufscoastal`'s README still points
to `ufs-setup-instance.sh`, which is superseded.

What the functions it calls did (the setup script's `setup_spack-stack` and
`build_spack-stack-environment`, kept in `csis-sandbox-provisioning`'s
`legacy/`): clone the fork, `spack gpg` and a mirror, `spack stack create env
--site linux.default --template unified-dev --name aws-ioossb-rhel8
--compiler=oneapi`, find externals at the system scope, three `config add`,
add `sp`, concretize, install, `module tcl refresh`, `spack stack
setup-meta-modules`.

## Clarifications

### Session 2026-11-21

- Q: Which spack-stack should the playbook build? → A: an upstream JCSDA
  release if one supports RHEL 10 and Spack 1.x; otherwise the fork
  `asascience-open/spack-stack` at a commit the operator names, so the spec
  never waits.
- Q: Which compiler should spack-stack's environment be built with? → A:
  oneAPI, as the script, on RHEL 10's own GCC 14; no GCC toolset.
- Q: Where should spack-stack's settings and externals be written? → A: in
  the environment's own scope and spack-stack's site scope; nothing in
  `system`, and a check shows `/etc/spack` unchanged.
- Q: What happens to `add-ufs-setup.sh`, `ufs-envars.sh` and the two
  spack-stack push scripts? → A: the two UFS scripts stay in
  `csis-sandbox-ops`, marked as replaced by `ufs-stack.yml`; the push scripts
  stay unmarked, for a later cache spec; no mapping line changes.
- Q: What head node should `ufs-stack.yml` be proved on? → A: one of its own,
  built with spec 001's module and procedure, removed at the end, each step
  asked first (spec 001 removes its own node, so that one is not there).

### Session 2026-11-26

FR-001's first task found: JCSDA's latest stable release is 2.1.1
(2026-07-18; 2.2.0 is a pre-release), stating no RHEL 10 support; UFS
Coastal's repository (`asascience-open/ufs-weather-model`) names spack-stack
1.6.0 at its one tag, `v1.0.0b01`, and 1.9.2 on its active branch, as
upstream's `develop` does, none of them on Spack 1.x; and the fork
`asascience-open/spack-stack` has, on its branch `aws-rhel10`, commit
`406b090aa4828fb7be840eea33c83963d88ac84e` (2026-10-05, "ufs weather app -
coastal", on JCSDA's 2.1.0), adding a site `aws-rhel10` that declares this
sandbox's oneAPI 2024.2.1 at `/opt/intel/oneapi` and a template
`ioos-ufscoastal` that builds `ufs-weather-model-env` alone.

- Q: Which spack-stack should the playbook build? → A: the fork at commit
  `406b090aa4828fb7be840eea33c83963d88ac84e`, with its site `aws-rhel10` and
  its template `ioos-ufscoastal` (the operator, 2026-11-26), in place of
  JCSDA 2.1.1's `linux.default` and `unified-dev`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - spack-stack built on a head node by a playbook (Priority: P1)

The operator applies one playbook on a built head node and gets spack-stack's
environment and meta-modules, built; applied again, nothing changes.

**Why this priority**: UFS Coastal cannot be built on today's sandbox without
it, and the script that did it is broken.

**Independent Test**: the playbook applied twice on a head node; `module
avail` after.

**Acceptance Scenarios**:

1. **Given** a built head node, **When** `ufs-stack.yml` is applied, **Then**
   spack-stack's environment is created and built, and `module avail` shows its
   meta-modules.
2. **Given** that node, **When** it is applied again, **Then** nothing changes.
3. **Given** the container, **When** the playbook runs there, **Then** the
   environment concretizes (a fake install cannot build it).

### User Story 2 - UFS Coastal builds against it (Priority: P2)

UFS Coastal's own build script, from `csis-model-ufscoastal`, finds what it
needs.

**Why this priority**: it is what the stack is for.

**Independent Test**: UFS Coastal's build script on that node, up to the
point where it has found its dependencies.

**Acceptance Scenarios**:

1. **Given** the built stack, **When** UFS Coastal's build script runs,
   **Then** it finds every dependency it needs.

### Edge Cases

- No JCSDA release supports RHEL 10 and Spack 1.x when the spec is taken up:
  the fork is used, at the commit the operator names (FR-001); the spec does
  not wait.
- The fork's commit does not build on RHEL 10 either: the spec stops there
  and says so; nothing is patched in the fork without the operator's word.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playbook MUST build JCSDA's spack-stack at a release that
  supports RHEL 10 and Spack 1.x, preferring the one UFS Coastal's current tag
  names. The first task finds what JCSDA has released. If no release fits,
  the playbook MUST build the fork `asascience-open/spack-stack` instead, at a
  commit the operator names, and the spec MUST record which was chosen and
  why. The tag or commit is a variable of the playbook, never a branch.
- **FR-002**: The environment MUST be built with oneAPI, the one the sandbox
  already installs and the setup role's Intel list registers
  (`--compiler=oneapi`, as the script), on RHEL 10's own GCC 14. No GCC
  toolset is installed; the script's `install_gcc_toolset_yum` call is not
  carried over.
- **FR-003**: `csis-sandbox-provisioning` MUST gain a playbook,
  `ufs-stack.yml`, not part of `site.yml`: clone spack-stack at the chosen tag;
  the collection's `setup` role with a list (an `environment` step for
  spack-stack's `setup.sh` and the Intel modules, `command` steps for `spack
  stack create env` and `spack stack setup-meta-modules`, `detect` steps for its
  externals, a `config` step for its settings), each step naming the script's
  line it replaces; then `spack_env` for the environment it creates, with
  `refresh_modules: when_needed`.
- **FR-004**: The playbook's `detect` and `config` steps MUST write to the
  environment's own scope and the site scope of spack-stack's Spack, never to
  the `system` scope (`/etc/spack`), which the sandbox's own Spack shares. The
  proof MUST show `/etc/spack` unchanged by the playbook, and the sandbox's
  environment concretizing as before.
- **FR-005**: `add-ufs-setup.sh` and `ufs-envars.sh` MUST stay in
  `csis-sandbox-ops`, marked as replaced: their headers and `CATALOGUE.tsv`
  name `ufs-stack.yml` in `csis-sandbox-provisioning`, whose variables take
  the versions `ufs-envars.sh` held. Only that unit has them, so nothing moves
  between units and no mapping line changes (constitution, principle I).
  `spack-stack-update-mirror.sh` and `spack-stack-mirror-create.sh` stay as
  they are, unmarked: this spec builds no spack-stack cache, so nothing
  replaces them yet.
- **FR-006**: `csis-model-ufscoastal`'s README MUST be corrected in that unit,
  which owns its copied files since 2026-11-19.
- **FR-007**: The proof MUST run on a head node of this spec's own, built with
  spec 001's Terraform module and procedure, in the same account, region and
  VPC, creating only new resources. At the end everything it created MUST be
  removed, each step asked first, and checked gone, as spec 001's FR-015.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `ufs-stack.yml` applied twice on a head node, the second run
  changing nothing.
- **SC-002**: `module avail` shows spack-stack's meta-modules.
- **SC-003**: UFS Coastal's own build script finds what it needs.
- **SC-004**: `/etc/spack` is as it was before the playbook, and the sandbox's
  own environment concretizes to the same specs.

## Assumptions

- The collection's `setup` role and modules are enough to express what the
  script did; anything they cannot is a change to the collection, released
  first.

## Dependencies

- Spec 001: its Terraform module and procedure, to build this spec's own head
  node (FR-007).
- Spec 002 leaves the two spack-stack push scripts to this spec, which leaves
  them as they are for a later spec on spack-stack's cache (FR-005).
- Spec 009 (2026-11-25, its clarification), merged first: this spec's head
  node is the first built with 009's change, and its first boot is 009's proof
  on a real node; the record of that first boot says whether it ended
  `failed=0`, installed from the RHEL 10 cache, and ran the `from_mirrors`
  steps with no prompt.

## Out of Scope

Building UFS Coastal itself (`csis-model-ufscoastal`'s recipes do that); the
spack-stack build cache.

## Carried From

Stage 18, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-18.md`),
as a pointer for a person reading; this spec stands without it.
