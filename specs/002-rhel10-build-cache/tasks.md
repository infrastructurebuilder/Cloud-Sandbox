---

description: "Task list for the RHEL 10 build cache"
---

# Tasks: A build cache for RHEL 10, pushed without scripts

**Input**: Design documents from `specs/002-rhel10-build-cache/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 001 merged (its `proof/`)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T040 to T044 are those conditions' tasks. Each task, when checked,
gets a record under it.

**Tests**: included, written first and seen to fail (principle IV; FR-006
names them).

**AWS**: tasks marked **(AWS, asked)** wait for the operator's word.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel
- **[Story]**: US1 (push), US2 (build from the cache), US3 (the scripts)

## Path Conventions

From the Cloud-Sandbox root: `exportit/sandbox-terraform/`,
`exportit/sandbox-provisioning/`, `exportit/sandbox-ops/`, each committed in
its own repository.

---

## Phase 1: Setup

- [X] T001 Start `feature/rhel10-build-cache` with git-flow in `exportit/sandbox-terraform/`, `exportit/sandbox-provisioning/` and `exportit/sandbox-ops/` from their `develop`, each clean and level with its origin
  - Done 2026-11-24: `feature/rhel10-build-cache` started with git-flow in `csis-sandbox-terraform` (from `f07607d`), `csis-sandbox-provisioning` (`3c8d6fb`) and `csis-sandbox-ops` (`8f17e9b`), each clean and level with its origin. Cloud-Sandbox's branch of the same name (its plan and tasks) brought level with `develop` by a merge.
- [X] T002 Run `just init` in the three units and the root `just test`
  - Done 2026-11-24: `just init` in the three units; the root `just test` passed.

---

## Phase 2: Foundational (the bucket and the permission, no AWS)

### Tests first

- [X] T003 [P] Write `exportit/sandbox-terraform/build-cache/tests/build-cache.tftest.hcl` with a mocked `aws`: a plan in an empty workspace adds the bucket, its public access block (all four `true`), ownership controls (`BucketOwnerEnforced`) and encryption (`AES256`), all tagged, named `var.bucket_name`, and changes nothing; the output `mirror_url` is `s3://<bucket_name>/`
  - Done 2026-11-24: `build-cache/tests/build-cache.tftest.hcl`, mocked `aws`: one run asserting the bucket's name and tags, the four public-access settings on it, `BucketOwnerEnforced`, `AES256`, and `mirror_url`. Wrapped by `tests/test_build_cache_module.py`.
- [X] T004 [P] In `exportit/sandbox-terraform/tests/`, add to the main module's `tofu test` (or a new `build_cache.tftest.hcl`): with `build_cache_bucket` unset, no `aws_iam_role_policy.build_cache`; set, one policy allowing exactly `s3:ListBucket` on the bucket and `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on its objects ([data-model.md](data-model.md))
  - Done 2026-11-24: `tests/build_cache.tftest.hcl`: unset, no `aws_iam_role_policy.build_cache`; set, one policy of two statements, `s3:ListBucket` on the bucket and `s3:DeleteObject`, `s3:GetObject`, `s3:PutObject` on its objects, both `Allow`. Wrapped by the same pytest file, with a check that `main.tf` holds no bucket (FR-002).
- [X] T005 Run them and see them fail for the right reason, recording which failed
  - Done 2026-11-24: all three wrappers failed for the right reason: `build-cache/` not initialised (no module); the main module's test "0 passed, 1 failed" (`build_cache_bucket` undeclared); `build-cache/main.tf` missing.

### Implementation

- [X] T006 Write `exportit/sandbox-terraform/build-cache/` (`versions.tofu` with OpenTofu `1.13.9` and `hashicorp/aws ~> 6.0`; `variables.tf` with `bucket_name` default `csis-sandbox-rhel10-build-cache`, `region` default `us-east-2`, `project_tag`; `main.tf`; `outputs.tf`); add it to `tests/support.py`'s `MODULES`, to `just init`, and to the formatting check
  - Done 2026-11-24: `build-cache/` (`versions.tofu` OpenTofu 1.13.9, `hashicorp/aws ~> 6.0`; `variables.tf`; `main.tf`, four resources; `outputs.tf`, `mirror_url`); `build-cache` in `tests/support.py`'s `MODULES` (so it validates and its `versions.tofu` is checked), initialised by `just init`; the formatting check is recursive and takes it in unchanged. The proof's and plan test's copies of the unit leave it out, as they leave out `reaper/`.
- [X] T007 In `exportit/sandbox-terraform/variables.tf` add `build_cache_bucket` (string, default `null`); in `main.tf` add `aws_iam_role_policy.build_cache`, counted on it (research R2)
  - Done 2026-11-24: `build_cache_bucket` (string, `null`) in `variables.tf`; `aws_iam_role_policy.build_cache` in `main.tf`, counted on it, with a comment on `AmazonS3FullAccess`.
- [X] T008 In `exportit/sandbox-terraform/DEPLOYMENT.md`, add the bucket (applied once, on its own; never part of a head node's removal) and `build_cache_bucket`; run the unit's `just test` and `just full-test`: T003 and T004 pass
  - Done 2026-11-24: `DEPLOYMENT.md`: `build_cache_bucket` among the optional settings, and step 9, the bucket (applied once, on its own, never part of a head node's removal; the name a decision if taken). The unit's `just test` 39 passed; `just full-test` 5 slow passed. `csis-sandbox-terraform` `bb724c9`.
- [X] T009 [P] In `exportit/sandbox-terraform.map`, add `new build-cache/`; in `exportit/REMINDERS.md`, add "Narrow the head node's managed policies" (`AmazonS3FullAccess` and the rest, research R2's finding)
  - Done 2026-11-24: `exportit/sandbox-terraform.map` gains `new build-cache/`; `exportit/REMINDERS.md` gains "Narrow the head node's managed policies".

---

## Phase 3: User Story 1 - Push a build to the cache (Priority: P1) 🎯 MVP

**Goal**: `push-build-cache.yml` pushes the environment's packages, signed; again, nothing new.

### Tests first

- [X] T010 [P] [US1] In `exportit/sandbox-provisioning/tests/test_parity.py`, add: the playbook's `mirror` is `spack_mirror` (the script's `SPACK_MIRROR`), its `key` is `spack_key_fingerprint`, ending in the script's `KEY=F525C05B06DCA266`, and its `env` is `spack_environment_dir`; `update_index` true; `force` false
  - Done 2026-11-24: `tests/test_parity.py`: the push's `mirror` is `{{ spack_mirror }}` (the map's `SPACK_MIRROR`), its `key` names `spack_key_fingerprint`, which ends in the script's `F525C05B06DCA266` (held as a constant: the script is `csis-sandbox-ops`' and not in `legacy/`), `env` is `{{ spack_environment_dir }}`, `update_index` true, `force` false; and `site.yml` does not import it.
- [X] T011 [P] [US1] In `exportit/sandbox-provisioning/tests/container/converge.sh`, after the fake install, add: `push-build-cache.yml` with `spack_mirror` a directory and an `unsigned` override, run in check mode (pushes nothing), then for real (`changed`), then again (`changed=0`); and the key-missing case failing with the fingerprint in its message
  - Done 2026-11-24: `tests/container/converge.sh`, after verify: `zlib-ng` fake-installed in the concretized environment as the login user; `push-build-cache.yml` to `/tmp/build-cache`, unsigned, in check mode (must report a change and leave no file), for real (a change, files), again (`changed=0`); then signed with no key in the keyring (must fail, naming the fingerprint).
- [X] T012 [US1] Run them (`just test`, `just full-test`) and see them fail for the right reason, recording which failed
  - Done 2026-11-24: the parity test failed for the right reason (no `push-build-cache.yml`). The container step was not run before the playbook existed. Run after, it failed twice on the test's own assumption, recorded here: Spack refuses to push an environment with any package not installed. The site's environment is only concretized in the container (21 of 24 refused), and a fake install leaves out build-only dependencies (`compiler-wrapper` refused). The test now pushes an environment of its own, `zlib-ng` and `compiler-wrapper` as roots, fake-installed, through `spack_environment_dir`; on a failure it prints that environment's install state.

### Implementation

- [X] T013 [US1] Write `exportit/sandbox-provisioning/push-build-cache.yml` as [contracts/push-build-cache.md](contracts/push-build-cache.md) says: one play, as `sandbox_user`; the keyring check; `spack_buildcache_push` with `env`, `mirror`, `key` (or `unsigned` when a test asks), `update_index: true`, `force: false`; not imported by `site.yml`
  - Done 2026-11-24: `push-build-cache.yml` as the contract says: one play on `sandbox_head` as `sandbox_user`, the role's defaults read as `verify.yml` reads them; the keyring check (`spack gpg list --signing`, run in check mode too) and an assert naming the fingerprint; `spack_buildcache_push` with `env`, `mirror`, `key` (or `unsigned` when `push_build_cache_unsigned`), `update_index: true`, `force: false`. Each task says it is new, and what of the script it replaces. Its header links `docs/BUILD-CACHE.md`, written with it (T037).
- [X] T014 [US1] Add it to the unit's syntax and lint targets; run `just test` and `just full-test`: T010 and T011 pass
  - Done 2026-11-24: in the unit's syntax check; ansible-lint takes it in (production profile, passed); traceability's `PLAYBOOKS` lists it. `just test` 478 passed; `just full-test`: the container applied twice with nothing changed the second time, then the push: check mode a change and no file, the first push 12 files, the second `changed=0`, a signed push without the key stopped naming it. `csis-sandbox-provisioning` `678f8a5`.
- [X] T015 [US1] Commit the three units' work on their branches; record the submodules; run the root `just test` and `just full-test`
  - Done 2026-11-24: the three units' work committed on their branches (`csis-sandbox-terraform` `bb724c9`, `csis-sandbox-provisioning` `678f8a5`, `csis-sandbox-ops` `978bed5`) and recorded here; the root `just full-test` passed (every unit's `just test` and `just full-test` with it, `units.toml` consistent, the sync rehearsal), and the root `just test` after the merge (T016).
- [X] T016 [US1] On the operator's word only: finish the three units' branches into their `develop` and push; record their commits (the AWS steps use them)
  - Done 2026-11-24, on the operator's word ("merge when the full test passes"): the three branches squashed into their `develop` and pushed, each kept and pushed: `csis-sandbox-terraform` `d366c93`, `csis-sandbox-provisioning` `a1744f8`, `csis-sandbox-ops` `bfd2097`. The AWS steps use these.
- [ ] T017 [US1] **(AWS, asked)** In a working copy of `build-cache/` with local state: plan (four additions, nothing else), apply; if the name is taken, stop for the operator's decision
- [ ] T018 [US1] **(AWS, asked)** A head node, as spec 001's tasks T017 to T022 (its stages A and B), with `build_cache_bucket` set in `proof.tfvars`
- [ ] T019 [US1] The signing key's private half copied to the node over the SSM session by the operator and trusted (`spack gpg trust`); `spack gpg list` shows the fingerprint (research R6)
- [ ] T020 [US1] `push-build-cache.yml --check`: lists the packages, pushes nothing (scenario 1)
- [ ] T021 [US1] **(AWS, asked)** `push-build-cache.yml`: pushes; `spack buildcache list` against the mirror shows the environment's packages for `linux-rhel10`, signed (scenario 2, SC-001)
- [ ] T022 [US1] `push-build-cache.yml` again: `changed=0` (scenario 3, SC-002)

---

## Phase 4: User Story 2 - Build from the cache (Priority: P2)

- [ ] T023 [US2] On the same node, a second environment directory with the same `spack.yaml`, installed with `spack_cache_only: 0` and the mirror; the install log's count of packages fetched from the cache recorded (SC-003)
- [ ] T024 [US2] In `exportit/sandbox-provisioning/group_vars/all.yml`, the defaults (research R7): `spack_cache_only: 0`, `spack_site_mirror: true`, `spack_mirror: s3://<the bucket>/`; in `tests/test_parity.py` and `tests/support.py`, the tests that held the old defaults now hold these, each saying where the script differs and why; `just test` and `just full-test`
- [ ] T025 [US2] On the operator's word only: finish that change into the unit's `develop` and push
- [ ] T026 [US2] On the same node, a third environment directory installed with the defaults alone (the merged commit checked out): packages fetched from the cache (SC-004)
- [ ] T027 [US2] The signing key removed from the node (`spack gpg untrust` and the file), then **(AWS, asked)** the node removed as spec 001's tasks T031 to T035 (stage E), the bucket kept and E5's search excluding it by name

---

## Phase 5: User Story 3 - The scripts retired (Priority: P3)

### Tests first

- [X] T028 [P] [US3] In `exportit/sandbox-ops/tests/check-catalogue.sh`, add the rule that a `superseded_by` value, when present, names a unit and a path (`<unit>: <path>`); run `just test`: it passes on today's catalogue (no values yet), then fails on a test value of the wrong form, recorded
  - Done 2026-11-24: `tests/check-catalogue.sh`: a `superseded_by` value, when present, must match `<unit>: <path>`. `just test` passed on today's catalogue (no values); on a scratch copy of the unit, the value `push-build-cache.yml` was refused ("superseded_by is not '<unit>: <path>'"), and `csis-sandbox-provisioning: push-build-cache.yml` accepted.

### Implementation

- [X] T029 [US3] In `exportit/sandbox-ops/bin/spack-update-mirror.sh`, add a header line naming `csis-sandbox-provisioning`'s `push-build-cache.yml` as its replacement; in `CATALOGUE.tsv`, its row keeps `in-use` and gains `superseded_by` `csis-sandbox-provisioning: push-build-cache.yml` (research R8); update `tests/shellcheck.counts` if the header moved a finding's line; `just test`
  - Done 2026-11-24: `bin/spack-update-mirror.sh`'s header names `push-build-cache.yml`; its catalogue row keeps `in-use` and gains `superseded_by` `csis-sandbox-provisioning: push-build-cache.yml`; shellcheck's counts are per file, unchanged. `just test` passed.
- [X] T030 [US3] In `exportit/sandbox-ops/README.md`, the script's row says it is replaced, and by what; the two spack-stack scripts are left for spec 004
  - Done 2026-11-24: `README.md`'s row says it is replaced, and by what; the two spack-stack scripts left for spec 004. `just full-test` passed. `csis-sandbox-ops` `978bed5`.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T031 [P] In `exportit/MAP.md`, the cache: the bucket, the playbook, the defaults, the script replaced
- [ ] T032 [P] In `specs/README.md`, set 002's state
- [ ] T033 Commit the units' last changes on their branches; record the submodules; `just constitution-check`
- [ ] T034 Run the root `just test`
- [ ] T035 Run the root `just full-test`
- [ ] T036 In `specs/002-rhel10-build-cache/spec.md`, an **Outcome** section: the date, how many packages were pushed, how many the second build fetched, the third; no identifiers
- [X] T037 [P] In `exportit/sandbox-provisioning/docs/`, a short page on pushing the cache (when, the key by hand, the check mode first), linked from the playbook's header
  - Done 2026-11-24, with T013: `exportit/sandbox-provisioning/docs/BUILD-CACHE.md` (when to push, the key by hand and off again, check mode first, a fully installed environment), linked from the playbook's header.
- [ ] T038 [P] For any finding of the run, a line in `exportit/REMINDERS.md`
- [ ] T039 Re-read [quickstart.md](quickstart.md) against what was run; correct it if a step differed
- [ ] T040 Run `/speckit-converge` on `specs/002-rhel10-build-cache/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T041 Walk `specs/002-rhel10-build-cache/quickstart.md`, each step's evidence from the tasks above (done condition 3)
- [ ] T042 On the operator's word only: finish the units' branches and push, record their commits, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T043 Record that no release applies, unless the operator asks for one (done condition 5)
- [ ] T044 Mark the spec **complete**, with the date, only when T001 to T043 are checked (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup, Foundational**: need spec 001 merged.
- **US1**: after Phase 2; T016 before any AWS task; T017 to T022 in order.
- **US2**: after US1, on the same node; T024 and T025 before T026.
- **US3**: independent of the AWS steps; can run alongside Phase 2.
- **Polish**: after US2 and US3; T040 to T044 in order.

### Parallel Opportunities

- T003 and T004; T010 and T011; T028 alongside Phase 2; T031, T032, T037, T038.

---

## Implementation Strategy

1. Phase 2 and US1's code merged; US3 alongside.
2. One head node: push, then build from the cache, then the defaults.
3. The node removed, the bucket kept.

---

## Notes

- The signing key's private half is never in a repository, a variable or a log; the operator puts it on the node and the procedure takes it off.
- `ioos-cloud-sandbox` is never written to.
- Nothing in `ATTIC/` is read for any task.
