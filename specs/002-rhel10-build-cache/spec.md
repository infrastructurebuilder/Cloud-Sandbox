# Feature Specification: A build cache for RHEL 10, pushed without scripts

**Feature Branch**: none yet; `feature/rhel10-build-cache` when it is taken up

**Created**: 2026-11-14, as stage 16; carried into this spec 2026-11-19

**Status**: Draft. Clarified 2026-11-21; ready for `/speckit-plan`. **Needs
spec 001 first:** it needs a real build to push, and the access the live
proof shows a head node has.

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

### Session 2026-11-21

- Q: Where should the new RHEL 10 build cache go? → A: a new bucket of the
  sandbox's own, made by its Terraform; the existing `ioos-cloud-sandbox`
  bucket and its RHEL 8 cache are not touched (the standing rule: only new
  resources in us-east-2).
- Q: What should be allowed to write to the new cache bucket? → A: the head
  node's new role, made by the sandbox's Terraform, with a policy for the new
  bucket only; the existing role is not touched.
- Q: What should new builds use by default once the RHEL 10 cache exists?
  → A: the defaults stay `spack_cache_only: -1` and `spack_site_mirror: false`
  until SC-003 holds; then, as this spec's last step, they become
  `spack_cache_only: 0` and `spack_site_mirror: true`, at the new bucket.
- Q: Once the playbook has pushed, what happens to `spack-update-mirror.sh`?
  → A: it stays in `csis-sandbox-ops`, marked as replaced; no file moves
  between units, and its mapping line is unchanged.

### Session 2026-11-24

Found at T019: the site's signing key (fingerprint ending `F525C05B06DCA266`)
was kept on its owner's machine, and its private half cannot be obtained.

- Q: Which key signs the new cache? → A: a new key, made for it (the
  operator: "We will have to make a new signing key").
- Q: Where do head nodes get the new key's public half? → A: in
  `csis-sandbox-provisioning`, which the `spack` role puts in place and trusts,
  pinned to its fingerprint; nothing is fetched.
- Q: Where is its private half kept, and how is it made? → A: made on the
  local machine, with no passphrase, and kept with its public half in the
  Keybase team folder `/Volumes/Keybase/team/csimagesystem`, named so that it
  is known what it is, beside a `README.md` saying what it is, what it is used
  for and how to manage it. It is on a head node only while a push runs.
- Made 2026-11-24: RSA 4096, signing only, no expiry, fingerprint
  `8D58116F59406FF3B70812BA065FBB8F66F38D66`, its user ID naming the cache and no person.

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
   new bucket lists this sandbox's packages for RHEL 10, signed with the key
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

**Independent Test**: the script's header and `csis-sandbox-ops`'
catalogue.

**Acceptance Scenarios**:

1. **Given** the playbook has pushed, **When** `spack-update-mirror.sh` is
   retired, **Then** it is still in `csis-sandbox-ops`, its header and
   `CATALOGUE.tsv` name `push-build-cache.yml` as its replacement, and the two
   spack-stack scripts are left for spec 004.

### Edge Cases

- The private key is never in a repository, a variable or an AWS secret; it
  is copied to the node by hand, as a file, for a push, and taken off after
  (FR-007). The signing key is the only secret on the node; S3 access comes
  from the role (FR-003).
- A push aimed at `ioos-cloud-sandbox`, by a setting left at its old default
  or given by mistake, stops before anything is sent (FR-008).
- A push interrupted part-way: running it again pushes what is missing, and
  only that.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-provisioning` MUST gain a playbook,
  `push-build-cache.yml`, run by hand after a build and not by `site.yml`:
  `spack_buildcache_push` for the environment, signed with the key
  `spack_key_fingerprint` names, to `spack_mirror`, with `update_index: true`.
- **FR-002**: The cache MUST go to a new S3 bucket in us-east-2, made by
  `csis-sandbox-terraform` and named with the sandbox's prefix, holding only
  the RHEL 10 cache. `spack_mirror` MUST point at it. The existing
  `ioos-cloud-sandbox` bucket and its RHEL 8 cache MUST NOT be written to or
  changed. The bucket lasts beyond spec 001's proof: it is not among what that
  proof removes at its end, and its own removal is a step asked for by name.
- **FR-003**: The head node MUST write through its new role, the one the
  sandbox's Terraform makes (spec 001), with a policy allowing object writes
  and lists on the new bucket only. No credential is put on the node for the
  push. The existing IAM role (`csis-sandbox-terraform`'s `main.tf`, lines 52
  to 59, as deployed) MUST NOT be changed.
- **FR-004**: The defaults for new builds MUST stay `spack_cache_only: -1` and
  `spack_site_mirror: false` until a build has installed from the new cache
  (SC-003). Then, as this spec's last step, they MUST become
  `spack_cache_only: 0` and `spack_site_mirror: true`, with `spack_mirror` at
  the new bucket, and the tests that hold the defaults MUST change with them.
- **FR-005**: `spack-update-mirror.sh` MUST stay in `csis-sandbox-ops`,
  marked as replaced: its header and `CATALOGUE.tsv` name
  `push-build-cache.yml` in `csis-sandbox-provisioning`. Only that unit needs
  it, so nothing moves between units and its mapping line is unchanged
  (constitution, principle I). `spack-stack-update-mirror.sh` and
  `spack-stack-mirror-create.sh` are spec 004's; `scp-secret.sh` stays as it
  is.
- **FR-006**: Tests MUST hold the playbook's mirror, key and environment to
  the variables the scripts read (parity), check its syntax and lint, and prove
  its push against a mirror in a directory in the container, unsigned. The
  push to S3 is proved by doing it.
- **FR-007**: The cache MUST be signed with the key made for it on 2026-11-24
  (`8D58116F59406FF3B70812BA065FBB8F66F38D66`), not the old site key, whose private half cannot be obtained.
  `spack_key_fingerprint` MUST name it. Its public half MUST be in
  `csis-sandbox-provisioning`, put in place and trusted by the `spack` role
  pinned to that fingerprint, in place of the download from
  `ioos-cloud-sandbox`; tests MUST hold the file's fingerprint to the setting,
  and its user ID to naming no person. Its private half MUST be kept in the
  Keybase team folder `csimagesystem` with a `README.md`, and nowhere else.
- **FR-008**: `push-build-cache.yml` MUST refuse a `spack_mirror` in
  `ioos-cloud-sandbox` before pushing anything (FR-002), and a test MUST show
  it refusing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The new bucket's cache lists this sandbox's packages for RHEL 10,
  and `ioos-cloud-sandbox` is as it was.
- **SC-002**: A second push reports nothing new.
- **SC-003**: A build with the cache turned on installs from it.
- **SC-004**: After SC-003, a build with the defaults alone installs from the
  new cache.

## Assumptions

- A head node from spec 001, or one like it, is there to push from.
- The new bucket is private; the sandbox's nodes read it through their role.

## Dependencies

- Spec 001 (the live proof).
- Spec 004 (spack-stack) decides the two spack-stack scripts.

## Out of Scope

The UFS spack-stack's cache (spec 004).

## Carried From

Stage 16, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-16.md`),
as a pointer for a person reading; this spec stands without it.
