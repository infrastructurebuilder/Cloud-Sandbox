# Research: A build cache for RHEL 10, pushed without scripts

Each item records a decision, why, and what else was weighed. Written on
2026-11-21, after specs 001, 006 and 007 were planned.

## R1. Where the bucket is made

**Decision**: a new root module of `csis-sandbox-terraform`, `build-cache/`,
with its own state (local, like the proof's, unless the operator names a
backend later) and provider `hashicorp/aws ~> 6.0` (as spec 003's `reaper/`,
its research R1). It makes one private bucket: public access blocked on all
four settings, ownership enforced (no ACLs), default encryption (SSE-S3),
versioning off, tagged with the sandbox's prefix. Its name is a variable,
default `csis-sandbox-rhel10-build-cache`; it carries no account number.

**Rationale**: FR-002: the bucket outlives any head node, so it cannot be in
the head node's workspace, which spec 001's removal destroys. A root module of
its own is applied and removed on its own, by name. The provider is the one
spec 003 settled for new root modules in this unit.

**Alternatives considered**: a resource in the main module (destroyed with
the node); a bucket made by hand (not reviewable or repeatable); the account
number in the name for uniqueness (no account number in a repository).

## R2. The head node's write permission

**Decision**: the main module gains `build_cache_bucket` (string, default
`null`). When it is set, an `aws_iam_role_policy` on the head node's role
allows `s3:ListBucket` on the bucket and `s3:GetObject`, `s3:PutObject` and
`s3:DeleteObject` on its objects, and nothing else. When `null`, no policy.

**Rationale**: FR-003: the node's own role, the new bucket only, no
credential on the node. `DeleteObject` is needed by `spack buildcache
update-index`, which replaces the index.

**Finding for the operator**: the module's default `managed_policies` already
attach `AmazonS3FullAccess` to the head node's role (its `variables.tf` has a
`TODO: limit this`). While that stands, the scoped policy grants nothing new;
it is written so that it is enough once the managed list is narrowed, which
is not this spec's work. It is recorded in `exportit/REMINDERS.md`.

## R3. The playbook

**Decision**: `push-build-cache.yml` in `csis-sandbox-provisioning`, one play
on the head node, as `sandbox_user`, with the collection's
`spack_buildcache_push` module: `env: "{{ spack_environment_dir }}"` (the
`spack_environment` role's own variable), `mirror: "{{ spack_mirror }}"`,
`key: "{{ spack_key_fingerprint }}"`, `update_index: true`, `force: false`.
It asserts first that the key is in Spack's keyring (`spack gpg list`), and
fails with a message naming the fingerprint if not. It is not imported by
`site.yml`.

**Rationale**: FR-001. The module pushes only what the mirror lacks and
reports a change only for that, so the second run reports nothing (SC-002),
and an interrupted push is finished by running it again (the edge case). Its
check mode asks the mirror and pushes nothing (scenario 1).

**Alternatives considered**: a role (one task does not need one); pushing from
`site.yml` (FR-001: by hand, after a build).

## R4. Tests without AWS

**Decision**: in `csis-sandbox-provisioning`:

- `test_parity.py` gains a case: the playbook's mirror, key and environment
  are the variables `spack-update-mirror.sh` reads (`SPACK_MIRROR`, the key
  `F525C05B06DCA266`, the environment), through the existing variable map in
  `tests/support.py`.
- The container test (`tests/container/converge.sh`, in `just full-test`)
  pushes the environment it concretized to a mirror in a directory,
  `unsigned: true`, after a fake install of one small package, then runs the
  playbook again and asserts `changed=0`. Syntax and lint as for the other
  plays.

**Rationale**: FR-006. The container concretizes and fakes installs; a push
of a fake-installed package to a directory exercises the module's path end to
end without S3 or a key.

## R5. Where the proof runs

**Decision**: on a head node of this spec's own, built with spec 001's
`proof/` files and procedure (its stages A, B and E), with the settings of
spec 001 and `build_cache_bucket` set. After the push (User Story 1), the same
node proves User Story 2: a second environment directory, the same
`spack.yaml`, installed with `spack_cache_only: 0` and the mirror, counting
the packages installed from the cache. After the defaults change (FR-004),
SC-004 is proved there again with the defaults alone. Then everything but the
bucket is removed.

**Rationale**: spec 001 removes its node at its end (its FR-015), so this
spec cannot use it; one node for the three proofs keeps the hours of
compilation to one build. A second environment directory on the same node is
a fresh build as far as Spack is concerned.

**Alternatives considered**: a second head node for User Story 2 (another
node, for the same answer).

## R6. The signing key

**Decision**: the cache is signed with the site's existing key (fingerprint
`22DC0120263F329AE5C9DA08F525C05B06DCA266`), whose private half the operator
copies to the node by hand over the SSM session, as `scp-secret.sh` does
today over SSH, and imports with `spack gpg trust`; the procedure removes it
from the node before the node is removed.

**Rationale**: FR-001 names that key; nodes already trust it by that
fingerprint (`spack_site_mirror`), so the new cache needs no new trust.

**Superseded 2026-11-24** (spec's session 2026-11-24, FR-007): the private
half of that key cannot be obtained; it was kept on its owner's machine
(`scp-secret.sh` copied it from there). A new key was made for the cache,
`8D58116F59406FF3B70812BA065FBB8F66F38D66` (RSA 4096, signing, no expiry, no passphrase, its user ID naming the
cache). Its public half ships in `csis-sandbox-provisioning`'s `spack` role,
which copies it to `spack_key` (the path the script downloaded to) and trusts
it pinned to `spack_key_fingerprint`; nodes no longer fetch a key from
`ioos-cloud-sandbox`. Its private half is in the Keybase team folder
`csimagesystem`, with a README, and is copied to a node as a file for a push
(`scp` through a Session Manager tunnel, so that it is not pasted into a
session whose input may be logged) and removed with `spack gpg untrust
--signing` after.

## R7. The defaults switch

**Decision**: the last task changes `group_vars/all.yml`:
`spack_cache_only: 0`, `spack_site_mirror: true`, and `spack_mirror:
s3://csis-sandbox-rhel10-build-cache/` (or the name used); and the tests that
hold the old defaults (`test_parity.py`'s `spack_site_mirror` case and the
variable map's comments) change with them, each saying the script's value
differs and why.

**Rationale**: FR-004. The key is no longer fetched (R6, superseded): the
`spack` role trusts the new key from its own file whether or not the defaults
have switched.

## R8. The scripts

**Decision**: `spack-update-mirror.sh`'s header gains a line naming
`push-build-cache.yml` as its replacement. In `CATALOGUE.tsv` its row keeps
the status `in-use` (the file is still in the unit, and `check-catalogue.sh`
allows only `in-use` there; `superseded` and `dead` belong in the umbrella's
attic) and fills the existing `superseded_by` column with
`csis-sandbox-provisioning: push-build-cache.yml`. `check-catalogue.sh` gains
one rule: a `superseded_by` value, when present, names a unit and a path. The
file and its mapping line stay (FR-005).

**Rationale**: FR-005, with the catalogue's own column for exactly this; the
status vocabulary is the unit's, and "kept, marked as replaced" is `in-use`
with a replacement named.
