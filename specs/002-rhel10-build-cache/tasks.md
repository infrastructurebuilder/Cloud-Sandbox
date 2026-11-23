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

- [ ] T001 Start `feature/rhel10-build-cache` with git-flow in `exportit/sandbox-terraform/`, `exportit/sandbox-provisioning/` and `exportit/sandbox-ops/` from their `develop`, each clean and level with its origin
- [ ] T002 Run `just init` in the three units and the root `just test`

---

## Phase 2: Foundational (the bucket and the permission, no AWS)

### Tests first

- [ ] T003 [P] Write `exportit/sandbox-terraform/build-cache/tests/build-cache.tftest.hcl` with a mocked `aws`: a plan in an empty workspace adds the bucket, its public access block (all four `true`), ownership controls (`BucketOwnerEnforced`) and encryption (`AES256`), all tagged, named `var.bucket_name`, and changes nothing; the output `mirror_url` is `s3://<bucket_name>/`
- [ ] T004 [P] In `exportit/sandbox-terraform/tests/`, add to the main module's `tofu test` (or a new `build_cache.tftest.hcl`): with `build_cache_bucket` unset, no `aws_iam_role_policy.build_cache`; set, one policy allowing exactly `s3:ListBucket` on the bucket and `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on its objects ([data-model.md](data-model.md))
- [ ] T005 Run them and see them fail for the right reason, recording which failed

### Implementation

- [ ] T006 Write `exportit/sandbox-terraform/build-cache/` (`versions.tofu` with OpenTofu `1.13.9` and `hashicorp/aws ~> 6.0`; `variables.tf` with `bucket_name` default `csis-sandbox-rhel10-build-cache`, `region` default `us-east-2`, `project_tag`; `main.tf`; `outputs.tf`); add it to `tests/support.py`'s `MODULES`, to `just init`, and to the formatting check
- [ ] T007 In `exportit/sandbox-terraform/variables.tf` add `build_cache_bucket` (string, default `null`); in `main.tf` add `aws_iam_role_policy.build_cache`, counted on it (research R2)
- [ ] T008 In `exportit/sandbox-terraform/DEPLOYMENT.md`, add the bucket (applied once, on its own; never part of a head node's removal) and `build_cache_bucket`; run the unit's `just test` and `just full-test`: T003 and T004 pass
- [ ] T009 [P] In `exportit/sandbox-terraform.map`, add `new build-cache/`; in `exportit/REMINDERS.md`, add "Narrow the head node's managed policies" (`AmazonS3FullAccess` and the rest, research R2's finding)

---

## Phase 3: User Story 1 - Push a build to the cache (Priority: P1) 🎯 MVP

**Goal**: `push-build-cache.yml` pushes the environment's packages, signed; again, nothing new.

### Tests first

- [ ] T010 [P] [US1] In `exportit/sandbox-provisioning/tests/test_parity.py`, add: the playbook's `mirror` is `spack_mirror` (the script's `SPACK_MIRROR`), its `key` is `spack_key_fingerprint`, ending in the script's `KEY=F525C05B06DCA266`, and its `env` is `spack_environment_dir`; `update_index` true; `force` false
- [ ] T011 [P] [US1] In `exportit/sandbox-provisioning/tests/container/converge.sh`, after the fake install, add: `push-build-cache.yml` with `spack_mirror` a directory and an `unsigned` override, run in check mode (pushes nothing), then for real (`changed`), then again (`changed=0`); and the key-missing case failing with the fingerprint in its message
- [ ] T012 [US1] Run them (`just test`, `just full-test`) and see them fail for the right reason, recording which failed

### Implementation

- [ ] T013 [US1] Write `exportit/sandbox-provisioning/push-build-cache.yml` as [contracts/push-build-cache.md](contracts/push-build-cache.md) says: one play, as `sandbox_user`; the keyring check; `spack_buildcache_push` with `env`, `mirror`, `key` (or `unsigned` when a test asks), `update_index: true`, `force: false`; not imported by `site.yml`
- [ ] T014 [US1] Add it to the unit's syntax and lint targets; run `just test` and `just full-test`: T010 and T011 pass
- [ ] T015 [US1] Commit the three units' work on their branches; record the submodules; run the root `just test` and `just full-test`
- [ ] T016 [US1] On the operator's word only: finish the three units' branches into their `develop` and push; record their commits (the AWS steps use them)
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

- [ ] T028 [P] [US3] In `exportit/sandbox-ops/tests/check-catalogue.sh`, add the rule that a `superseded_by` value, when present, names a unit and a path (`<unit>: <path>`); run `just test`: it passes on today's catalogue (no values yet), then fails on a test value of the wrong form, recorded

### Implementation

- [ ] T029 [US3] In `exportit/sandbox-ops/bin/spack-update-mirror.sh`, add a header line naming `csis-sandbox-provisioning`'s `push-build-cache.yml` as its replacement; in `CATALOGUE.tsv`, its row keeps `in-use` and gains `superseded_by` `csis-sandbox-provisioning: push-build-cache.yml` (research R8); update `tests/shellcheck.counts` if the header moved a finding's line; `just test`
- [ ] T030 [US3] In `exportit/sandbox-ops/README.md`, the script's row says it is replaced, and by what; the two spack-stack scripts are left for spec 004

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T031 [P] In `exportit/MAP.md`, the cache: the bucket, the playbook, the defaults, the script replaced
- [ ] T032 [P] In `specs/README.md`, set 002's state
- [ ] T033 Commit the units' last changes on their branches; record the submodules; `just constitution-check`
- [ ] T034 Run the root `just test`
- [ ] T035 Run the root `just full-test`
- [ ] T036 In `specs/002-rhel10-build-cache/spec.md`, an **Outcome** section: the date, how many packages were pushed, how many the second build fetched, the third; no identifiers
- [ ] T037 [P] In `exportit/sandbox-provisioning/docs/`, a short page on pushing the cache (when, the key by hand, the check mode first), linked from the playbook's header
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
