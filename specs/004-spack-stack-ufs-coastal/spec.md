# Feature Specification: spack-stack for UFS Coastal

**Feature Branch**: none yet; `feature/spack-stack-ufs-coastal` when it is
taken up

**Created**: 2026-11-14, as stage 18; carried into this spec 2026-11-19

**Status**: Draft. **Needs spec 001's head node, or one like it,** for its
proof: a real build takes hours.

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

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

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
  then FR-001's other answer, or the spec waits.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Which spack-stack: [NEEDS CLARIFICATION: the release of JCSDA's
  spack-stack that supports RHEL 10 and Spack 1.x, if there is one (default:
  the fork's changes are not described anywhere, and an upstream release is
  what UFS's own instructions name); or the fork, at a commit the operator
  names. The first task is to find what JCSDA has released, and whether UFS
  Coastal's current tag names one.]
- **FR-002**: The compiler: [NEEDS CLARIFICATION: oneAPI, as the script
  (default: the sandbox already installs it, and the setup role's Intel list
  registers it); or a GCC toolset, which is what the broken call was for.]
- **FR-003**: `csis-sandbox-provisioning` MUST gain a playbook,
  `ufs-stack.yml`, not part of `site.yml`: clone spack-stack at the chosen tag;
  the collection's `setup` role with a list (an `environment` step for
  spack-stack's `setup.sh` and the Intel modules, `command` steps for `spack
  stack create env` and `spack stack setup-meta-modules`, `detect` steps for its
  externals, a `config` step for its settings), each step naming the script's
  line it replaces; then `spack_env` for the environment it creates, with
  `refresh_modules: when_needed`.
- **FR-004**: The scope: [NEEDS CLARIFICATION: the environment's own scope and
  the site scope of spack-stack's Spack (default: nothing at the `system` scope,
  which is one node's `/etc/spack`); or `system`, as the script.]
- **FR-005**: `add-ufs-setup.sh` and `ufs-envars.sh` are files of
  `csis-sandbox-ops`; moving them beside their replacement in
  `csis-sandbox-provisioning` moves them between units: [NEEDS CLARIFICATION:
  first, whether both units need them, in which case they go to a common unit
  or a single source instead (constitution 1.1.0, principle I); if only one
  does, how their mapping lines move and both units' lineage is kept, or
  whether they stay in `csis-sandbox-ops`, marked replaced.]
- **FR-006**: `csis-model-ufscoastal`'s README MUST be corrected in that unit,
  which owns its copied files since 2026-11-19.
- **FR-007**: Where it is proved: [NEEDS CLARIFICATION: a head node of its own
  for this spec, removed after (default); or spec 001's node, if it is still
  there.]

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `ufs-stack.yml` applied twice on a head node, the second run
  changing nothing.
- **SC-002**: `module avail` shows spack-stack's meta-modules.
- **SC-003**: UFS Coastal's own build script finds what it needs.

## Assumptions

- The collection's `setup` role and modules are enough to express what the
  script did; anything they cannot is a change to the collection, released
  first.

## Dependencies

- Spec 001 (a head node), or a head node of its own.
- Spec 002 leaves the two spack-stack push scripts to this spec.

## Out of Scope

Building UFS Coastal itself (`csis-model-ufscoastal`'s recipes do that); the
spack-stack build cache.

## Carried From

Stage 18, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-18.md`),
as a pointer for a person reading; this spec stands without it.
