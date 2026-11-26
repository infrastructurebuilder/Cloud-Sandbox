# Research: The playbooks take the collection's 0.0.3 and its `from_mirrors` again

Each item records a decision, why, and what else was weighed. Written on
2026-11-25.

## R1. How an existing checkout gets 0.0.3

**Decision**: raise `requirements.yml`'s floor to `>=0.0.3,<0.1.0`, and change
nothing in `just init`'s command (`ansible-galaxy collection install -r
requirements.yml -p .collections`).

**Rationale**: tried on 2026-11-25 with the unit's `ansible-galaxy` (core
2.16.20, as on RHEL 10), into a scratch collections path holding 0.0.2:

| Install, 0.0.2 installed | Result |
| --- | --- |
| `>=0.0.1,<0.1.0` (today) | "Nothing to do": 0.0.2 stays |
| `>=0.0.3,<0.1.0` | 0.0.3 installed in its place |
| either, with `--upgrade` | the newest in the range (0.0.3) |
| `>=0.0.3,<0.1.0`, 0.0.3 installed | skipped, nothing to do |

The unit's own `.collections` held 0.0.2 that day, the case FR-002 names. A
head node's first boot installs into a new checkout, and the container test
into a new container, so neither has an older collection to replace.

**Alternatives considered**: `--upgrade` in `just init` (takes every later
0.0.x unasked, which a pinned floor is there to prevent); `--force` (installs
again every time, and reports it).

## R2. The container's case that 0.0.2 would fail

**Decision**: after the container's existing push cases, as the login user:
make a throwaway signing key (`spack gpg create`), push the small test
environment **signed** with it to a second mirror in a directory (the
playbook, with `spack_key_fingerprint` set to the throwaway key's), which
publishes the key there, as the S3 push did; take the key off the keyring
(`spack gpg untrust --signing`); add that directory as a mirror in the site
scope; then apply `site.yml --tags spack,intel_oneapi`. The `from_mirrors`
steps must finish with no prompt, report the key as trusted, and Spack must
trust it afterwards; applied again, they report no change. Then the mirror is
removed.

**Rationale**: the prompt appeared only against a mirror that publishes a key
(spec 002's T023). The container's push to a directory is unsigned and
publishes none, so today's container test cannot see the prompt. A signed
push publishes one; the playbook's own push does it, so the case also
exercises the signed path in the container, which spec 002 found untested.

**Alternatives considered**: a mirror written by hand with a key file in it
(depends on Spack's layout, which the push writes for us); only the
collection's own integration test (it proves the module, not the playbooks'
steps).

## R3. The parity tests

**Decision**: `TRUST_MIRROR_KEYS` becomes `{"kind": "gpg_key",
"from_mirrors": True}` (the scripts' `buildcache keys --install --trust`,
carried by the collection's own step again); the test that no step uses
`from_mirrors` becomes the test that no step runs `buildcache keys` through
`command`; a new test holds `requirements.yml`'s floor at 0.0.3, saying why.

**Rationale**: FR-004. One constant carries the scripts' command in every
comparison, so the change is made once.

## R4. A head node built before the change

**Decision**: `docs/LIVE-PROOF.md`'s box B3 (apply again by hand) installs the
collections from `requirements.yml` before the plays, as the first boot does;
its version is raised.

**Rationale**: a node whose checkout is moved to the new commit keeps the
0.0.2 its first boot installed; with it, the `from_mirrors` steps would stop
at the prompt (spec's Edge Cases).

## R5. The proof on spec 004's head node

**Decision**: spec 004's T017 (its head node, as spec 001's stages A and B)
gains in its description that the record says whether the first boot ended
`failed=0`, installed from the RHEL 10 cache, and ran the three `from_mirrors`
steps with no prompt (the log has the steps' names and results). Spec 004 is
not started, so its task is changed rather than added to.

**Rationale**: the clarification (option C). Spec 009 is complete when it is
merged; its outcome links 004's record once it exists.
