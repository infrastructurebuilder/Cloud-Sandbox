# Feature Specification: The playbooks take the collection's 0.0.3 and its `from_mirrors` again

**Feature Branch**: none yet

**Created**: 2026-11-25, on the operator's instruction of that day: "The
Cloud-Sandbox can now raise its pin for the spack ansible collection to 0.0.3
and replace its command workaround with `from_mirrors` … Make a spec to do
that."

**Status**: Built 2026-11-26; outcome below. Clarified 2026-11-25. **Needs spec 002 merged first** (done, 2026-11-25): the workaround it removes
is spec 002's, merged in `csis-sandbox-provisioning` (`2a4980c`), and spec
002's Cloud-Sandbox branch is not merged yet.

**Input**: the collection `infrastructurebuilder.csis_spack` released 0.0.3 on
Ansible Galaxy on 2026-11-25 (its spec 003, "spack_gpg_key trusts the
mirrors' keys without a prompt"). Its `spack_gpg_key` with `from_mirrors:
true` now answers Spack's "Trust key? [y/N]" for each key a mirror publishes,
and it works on Spack 1.0, 1.1 and 1.2. A playbook written for 0.0.2 runs on
it unchanged.

## Why

- **The workaround stands in for a step that now works.** On spec 002's head
  node, 2026-11-24, the playbooks' `from_mirrors` steps stopped at Spack's
  prompt once the new build cache published its signing key: 0.0.2 did not
  answer it. Spec 002 replaced them in `csis-sandbox-provisioning` with the
  collection's generic `command` step, running `spack buildcache keys
  --install --trust --yes-to-all`, in three places:
  - the `spack` role's first list, for `funcs-setup-instance.sh` L700;
  - the `spack` role's site-mirror list, for `spack-pubkey.sh` L19;
  - the `intel_oneapi` role's list, for `funcs-setup-instance.sh` L959.

  The parity tests carry the scripts' command the same way, in one place
  (`TRUST_MIRROR_KEYS` in `tests/test_parity.py`), and hold that no step uses
  `from_mirrors`.
- **The `command` step says less than `from_mirrors` does.** It reports no
  change whatever it trusts (`changes: never`), cannot be previewed, and does
  not check afterwards that the keys are trusted. `from_mirrors` reports the
  keys it newly trusted, and fails if Spack does not trust them afterwards.
- **The range already admits 0.0.3, and that is not enough.** The playbooks
  ask for `>=0.0.1,<0.1.0`, so a fresh install takes 0.0.3. But an existing
  checkout can keep the 0.0.2 it has, which satisfies that range, and with
  0.0.2 the `from_mirrors` steps would stop at the prompt again. The floor has
  to say 0.0.3.

## Clarifications

### Session 2026-11-25

- Q: How should spec 009's change be proved on a real head node? → A: the
  container test now (FR-005), and the proof on spec 004's head node, which
  needs one anyway: 009 goes before 004 in the build order, and 004's first
  boot records that the `from_mirrors` steps ran with no prompt (the
  operator, "C").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A head node trusts the mirrors' keys through the collection's own step (Priority: P1)

A head node's first boot applies the playbooks, and the three steps that trust
the keys the mirrors publish are the collection's `from_mirrors` steps again,
on 0.0.3: they trust the RHEL 10 cache's key and Spack's public cache's keys
with no prompt, and say which keys they trusted.

**Why this priority**: it is the change; the rest makes sure it cannot run on
the collection that fails.

**Independent Test**: the container test, with the site mirror's steps run
against a mirror that publishes a key; then a head node's first boot.

**Acceptance Scenarios**:

1. **Given** the playbooks' checkout with 0.0.3 installed, **When** `site.yml`
   is applied, **Then** the three steps are `from_mirrors` steps, they finish
   with no prompt, and a second apply reports no change from them.
2. **Given** a mirror that publishes a key the node does not trust yet,
   **When** the steps run, **Then** the key is trusted and reported as newly
   trusted.
3. **Given** a node built with the defaults (spec 002's: the RHEL 10 cache on),
   **When** its first boot runs, **Then** it installs from the cache, as spec
   002's fresh node did (19 packages fetched, none built).

### User Story 2 - The playbooks cannot run with the collection that fails (Priority: P1)

Someone who set up the playbooks before 0.0.3 was released runs `just init`,
or a head node's first boot installs the collections, and 0.0.3 is what is
installed, even over an installed 0.0.2.

**Why this priority**: with 0.0.2, the `from_mirrors` steps stop at the prompt
again; the range alone does not prevent that.

**Independent Test**: a checkout with 0.0.2 installed; `just init`; the
installed version is 0.0.3.

**Acceptance Scenarios**:

1. **Given** `requirements.yml`, **When** it is read, **Then** it asks for
   0.0.3 or later, below 0.1.0.
2. **Given** a checkout with 0.0.2 installed, **When** `just init` runs,
   **Then** 0.0.3 is installed in its place.
3. **Given** a head node's first boot, which installs the collections before
   the plays, **When** it runs, **Then** 0.0.3 is what the plays use.

### Edge Cases

- **A head node built before this change** has 0.0.2 under its playbooks'
  checkout; a second apply after the checkout moves to the new commit must
  install 0.0.3 first, or it stops at the prompt. The procedure for applying
  again (`docs/LIVE-PROOF.md`, box B3) says so if the first boot's command
  does not.
- **Galaxy unreachable** when `just init` or the first boot runs: they fail
  visibly, as they do today; nothing falls back to 0.0.2.
- **A later 0.0.x of the collection**: the range keeps taking it, below 0.1.0,
  as it does today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-provisioning`'s `requirements.yml` MUST ask for
  `infrastructurebuilder.csis_spack` `>=0.0.3,<0.1.0`, with a comment saying
  why the floor is 0.0.3.
- **FR-002**: `just init` MUST install the version `requirements.yml` asks
  for over one that is installed already, so that an existing checkout moves
  from 0.0.2 to 0.0.3; and the first boot's installation of the collections
  (`csis-sandbox-terraform`'s first-boot template, and the container test,
  which does the same) MUST do the same, or MUST be shown to install into an
  empty place, where the question does not arise.
- **FR-003**: The three `command` steps spec 002 added MUST become `gpg_key`
  steps with `from_mirrors: true` again, each still saying which script lines
  it replaces, and their comments MUST say the prompt is answered by the
  collection since 0.0.3.
- **FR-004**: The parity tests MUST carry the scripts' `spack buildcache keys
  --install --trust` as the `from_mirrors` step again (`TRUST_MIRROR_KEYS`
  and the test that no step uses `from_mirrors` are removed or inverted), and
  a test MUST hold `requirements.yml`'s floor at 0.0.3.
- **FR-005**: The container test (`just full-test`) MUST exercise a
  `from_mirrors` step against a mirror that publishes a key, as the build
  cache does, so that the prompt would be found there and not on a head node:
  for example, the step run after the container's push to its cache in a
  directory, which publishes the key of a throwaway signing key.
- **FR-006**: The places that describe the workaround MUST describe what
  replaced it: `csis-sandbox-provisioning`'s comments and tests, and
  Cloud-Sandbox's `exportit/MAP.md` where it names the collection's version or
  the workaround.
- **FR-007**: This spec builds no head node of its own. The container test of
  FR-005 is its proof before merging; the proof on a real node is spec 004's
  head node, the next one built, whose first boot, with this spec's release,
  MUST end `failed=0`, install from the RHEL 10 cache, and run the three
  `from_mirrors` steps with no prompt. Spec 004 records it; this spec is
  complete when it is merged, and its outcome links 004's record once it
  exists.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No step of the playbooks runs `spack buildcache keys` through
  the generic `command` step; the three that trust mirrors' keys are the
  collection's own.
- **SC-002**: After `just init` on a checkout that had 0.0.2, the installed
  collection is 0.0.3.
- **SC-003**: The container test applies the playbooks twice with the
  `from_mirrors` steps against a mirror that publishes a key, finishes with no
  prompt, and the second apply changes nothing.
- **SC-004**: Spec 004's head node, the first built with this change, ends its
  first boot `failed=0`, installs the environment from the cache, and runs the
  `from_mirrors` steps with no prompt (FR-007).

## Outcome

Done on 2026-11-26, with no AWS.

| Check | Result |
| --- | --- |
| The installed collection, before and after `just init` (SC-002) | 0.0.2, then 0.0.3 over it |
| The three steps (SC-001) | the collection's `from_mirrors` again; no `command` step runs `buildcache keys` |
| The container's new case, with 0.0.3 (SC-003) | a signed push with a throwaway key published its keys; `site.yml` with that cache as the site mirror trusted the key with no prompt, and a second apply changed nothing |
| The same case, with 0.0.2 pinned for one run | stopped at Spack's "Trust key: … [y/N]" in the `from_mirrors` step: the bug the case is there to catch |
| A real node (SC-004) | spec 004's head node, its T017, to be linked here when its record exists |

Found on the way:

- `units.toml` named the collection 0.0.1, which the playbooks had already
  left for 0.0.2 and which the new floor does not admit; the root test of
  pins said so, and it now names 0.0.3.
- `csis-sandbox-provisioning`'s README still quoted the old range; the
  convergence corrected it.

## Assumptions

- 0.0.3 is on Ansible Galaxy (the collection's spec 003 records the release
  workflow's run and Galaxy listing 0.0.1, 0.0.2 and 0.0.3), and its
  `from_mirrors` behaves as that spec says on Spack 1.2.0, the version the
  playbooks install.
- The change goes out as a new tag of `csis-sandbox-provisioning` (0.0.5),
  named by `units.toml`, on the operator's word, as 0.0.3 and 0.0.4 were.

## Dependencies

- **Spec 002, merged first**: it made the workaround and the defaults this
  spec's head node uses; its Cloud-Sandbox branch must be merged before this
  spec's work starts.
- **The collection's spec 003**, released as 0.0.3 (done, 2026-11-25).
- **Spec 004 comes after this one**: its head node is this spec's proof on a
  real node (FR-007).

## Out of Scope

- Changing the collection (its own repository's work, done).
- Trusting fewer keys: whether a node should trust every key its mirrors
  publish, rather than only pinned ones, is not this spec's question; the
  steps stay what the scripts did.
- The collection's other modules, and its 0.1 series.
