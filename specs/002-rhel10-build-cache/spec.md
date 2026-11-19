# Feature Specification: A build cache for RHEL 10, pushed without scripts

**Feature Branch**: none yet; `feature/rhel10-build-cache` when it is taken up

**Created**: 2026-11-14, as stage 16; carried into this spec 2026-11-19

**Status**: Draft. **Needs spec 001 first:** it needs a real build to push,
and the access the live proof shows a head node has.

**Input**: the stage plan of 2026-11-14, carried from the ATTIC on the
operator's instruction of 2026-11-19.

## Why

- **The site's build cache is of no use to today's sandbox:** its index holds
  103 packages, all `rhel8`, built with oneAPI 2023.1.0, Intel 2021.9.0 and gcc
  11.2.1, in the layout of Spack before 1.0. A RHEL 10 head node with Spack
  v1.2.0 builds everything from source, for hours, every time.
- **Pushing to it is three scripts in `csis-sandbox-ops`,** run by hand:
  `spack-update-mirror.sh` (a list of RHEL 8 specs pushed one by one),
  `spack-stack-update-mirror.sh` and `spack-stack-mirror-create.sh` (the same
  for UFS's spack-stack), with `scp-secret.sh` to copy the private signing key
  from the operator's machine. The collection's `spack_buildcache_push` does
  the pushing, and reports only what the mirror gained.
- **The head node may not be allowed to write there:** its IAM role
  (`csis-sandbox-terraform`'s `main.tf`, lines 52 to 59) allows objects in
  `ioos-coastalsb-*puts`, not in `ioos-cloud-sandbox`, the mirror's bucket.

## Clarifications

None asked yet. The questions are the `[NEEDS CLARIFICATION]` markers below,
each with the default the stage proposed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Push a build to the cache (Priority: P1)

After a head node has built the sandbox's Spack environment, the operator runs
one playbook and the cache gains this sandbox's packages for RHEL 10, signed;
run again, it reports nothing new.

**Why this priority**: without a cache every build is hours from source.

**Independent Test**: the push against a mirror in a directory, in the
container, unsigned; then the real push from a head node.

**Acceptance Scenarios**:

1. **Given** a built environment, **When** `push-build-cache.yml` runs in check
   mode, **Then** it lists what would be pushed and pushes nothing.
2. **Given** a built environment, **When** it runs, **Then** the cache at the
   chosen prefix lists this sandbox's packages for RHEL 10, signed with the key
   `spack_key_fingerprint` names.
3. **Given** a push just made, **When** it runs again, **Then** it reports
   nothing new.

### User Story 2 - Build from the cache (Priority: P2)

A new build takes what the cache has and compiles only the rest.

**Why this priority**: it is what the cache is for, once it has been shown to
work.

**Independent Test**: a build with the cache turned on, and how many packages
it installs from the cache.

**Acceptance Scenarios**:

1. **Given** a cache with this sandbox's packages, **When** a build runs with
   the cache turned on, **Then** it installs them from the cache.

### User Story 3 - The scripts retired (Priority: P3)

The three push scripts are no longer the way to push, and the records say
what replaced them.

**Why this priority**: tidying, once the playbook has done a real push.

**Independent Test**: the scripts' new place, and `csis-sandbox-ops`'
catalogue.

**Acceptance Scenarios**:

1. **Given** the playbook has pushed, **When** the scripts are retired,
   **Then** each is either kept beside its replacement with the replacement
   named, or left for spec 004 (the two spack-stack ones).

### Edge Cases

- The private key is never in a repository or a variable; it is put in place
  by hand, as today (`scp-secret.sh` stays).
- A push interrupted part-way: running it again pushes what is missing, and
  only that.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-provisioning` MUST gain a playbook,
  `push-build-cache.yml`, run by hand after a build and not by `site.yml`:
  `spack_buildcache_push` for the environment, signed with the key
  `spack_key_fingerprint` names, to `spack_mirror`, with `update_index: true`.
- **FR-002**: Where the new cache goes: [NEEDS CLARIFICATION: a new prefix
  beside the old one, for example `public/spack/mirror-rhel10/`, so the old
  cache stays for any RHEL 8 node still running (default); or the same prefix,
  replacing it.]
- **FR-003**: Who may write: [NEEDS CLARIFICATION: the head node, with a
  policy for that prefix added to the IAM role in `csis-sandbox-terraform`
  (default); or the operator's own credentials, passed for the one run.]
- **FR-004**: The default for new builds: [NEEDS CLARIFICATION: leave
  `spack_cache_only: -1` and `spack_site_mirror: false` until the cache has
  been shown to work (default); or `spack_cache_only: 0` and
  `spack_site_mirror: true`.]
- **FR-005**: The three scripts are files of `csis-sandbox-ops`. Moving them
  to `csis-sandbox-provisioning` (its `legacy/`, as the stage proposed) moves
  them between units: [NEEDS CLARIFICATION: how their mapping lines move and
  the two units' lineage is kept (constitution, principle I), or whether they
  stay in `csis-sandbox-ops`, marked as replaced.]
- **FR-006**: Tests MUST hold the playbook's mirror, key and environment to
  the variables the scripts read (parity), check its syntax and lint, and prove
  its push against a mirror in a directory in the container, unsigned. The
  push to S3 is proved by doing it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The cache at the chosen prefix lists this sandbox's packages for
  RHEL 10.
- **SC-002**: A second push reports nothing new.
- **SC-003**: A build with the cache turned on installs from it.

## Assumptions

- A head node from spec 001, or one like it, is there to push from.

## Dependencies

- Spec 001 (the live proof).
- Spec 004 (spack-stack) decides the two spack-stack scripts.

## Out of Scope

The UFS spack-stack's cache (spec 004).

## Carried From

Stage 16, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-16.md`),
as a pointer for a person reading; this spec stands without it.
