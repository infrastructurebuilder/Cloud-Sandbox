---

description: "Task list for the playbooks taking the collection's 0.0.3 and its from_mirrors again"
---

# Tasks: The playbooks take the collection's 0.0.3 and its `from_mirrors` again

**Input**: Design documents from `specs/009-collection-from-mirrors/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 002 merged (done, 2026-11-25)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T019 to T023 are those conditions' tasks. Each task, when checked,
gets a record under it: what was done, and the evidence.

**Tests**: included, written first and seen to fail before the code they test
(principle IV; FR-004 and FR-005 name them).

**AWS**: none. The proof on a real node is spec 004's head node (FR-007).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an unfinished task)
- **[Story]**: US1 (the `from_mirrors` steps), US2 (the collection's floor)

## Path Conventions

From the Cloud-Sandbox root; `csis-sandbox-provisioning` is
`exportit/sandbox-provisioning/`, committed in its own repository.

**Order of the stories**: both are P1. US2 goes first: US1's container case
needs 0.0.3 installed, which US2's floor brings.

---

## Phase 1: Setup

- [ ] T001 Start `feature/collection-from-mirrors` with git-flow in `exportit/sandbox-provisioning/` from its `develop`, after checking it is clean and level with its origin
- [ ] T002 Run `just init` in `exportit/sandbox-provisioning/` and record the collection's installed version from `.collections/ansible_collections/infrastructurebuilder/csis_spack/MANIFEST.json` (0.0.2 expected); run the root `just test`

---

## Phase 2: User Story 2 - The playbooks cannot run with the collection that fails (Priority: P1)

**Goal**: `requirements.yml` asks for `>=0.0.3,<0.1.0`, and a checkout holding 0.0.2 gets 0.0.3.

**Independent Test**: `just init` where 0.0.2 is installed leaves 0.0.3 (SC-002).

### Tests first

- [ ] T003 [US2] In `exportit/sandbox-provisioning/tests/test_parity.py`, add a test that `requirements.yml` asks for `infrastructurebuilder.csis_spack` `>=0.0.3,<0.1.0` (data-model.md: "Before `>=0.0.1,<0.1.0`, After `>=0.0.3,<0.1.0`"), its comment saying 0.0.3 is the first to answer Spack's confirmation; and that `amazon.aws` stays `>=9.0.0,<10.0.0`; run it and see it fail for the right reason, recording it

### Implementation

- [ ] T004 [US2] In `exportit/sandbox-provisioning/requirements.yml`, set the floor to `>=0.0.3,<0.1.0` with a comment saying why (research R1); run `just init` and record that the installed version is now 0.0.3, where T002 found 0.0.2 (SC-002); and record, quoting the lines, that the two other installs need nothing more because each installs into a place with no collection yet (FR-002): `csis-sandbox-terraform`'s `init_template.ansible.tpl` runs `ansible-galaxy collection install -r requirements.yml` in a fresh clone at `/opt/sandbox-provisioning`, and `tests/container/converge.sh` does the same in a new container
- [ ] T005 [US2] In `exportit/sandbox-provisioning/docs/LIVE-PROOF.md`, box B3 installs the collections from `requirements.yml` (`ansible-galaxy collection install -r requirements.yml`, as the first boot does) before `site.yml`, so that a node built on 0.0.2 gets 0.0.3 (research R4); the box becomes `v4`, the page's version line at its head says version 4 and what it changed (box B3, for spec 009), and `tests/test_live_proof_form.py` allows `v4`; run `just test`: T003 and the form tests pass

**Checkpoint**: no checkout can apply the playbooks with 0.0.2.

---

## Phase 3: User Story 1 - A head node trusts the mirrors' keys through the collection's own step (Priority: P1)

**Goal**: the three steps are `gpg_key` steps with `from_mirrors: true`, proved in the container against a mirror that publishes a key.

**Independent Test**: the container case of research R2 (SC-003).

### Tests first

- [ ] T006 [P] [US1] In `exportit/sandbox-provisioning/tests/test_parity.py`, make `TRUST_MIRROR_KEYS` `{"kind": "gpg_key", "from_mirrors": True}` with its comment saying the collection answers the prompt since 0.0.3; replace `test_no_step_trusts_mirror_keys_through_the_collections_from_mirrors` with a test that no step of the two roles runs `buildcache keys` through `kind: command`, and that exactly three steps are `TRUST_MIRROR_KEYS`; keep `test_as_steps_carries_out_buildcache_keys_with_yes_to_all` renamed for `from_mirrors` (research R3)
- [ ] T007 [P] [US1] In `exportit/sandbox-provisioning/tests/container/converge.sh`, after the push cases, the case of research R2: as `ec2-user`, `spack gpg create` a throwaway key, read its fingerprint; `push-build-cache.yml` signed (`push_build_cache_unsigned: false`, `spack_key_fingerprint` the throwaway key's, `spack_mirror` a second directory, `spack_environment_dir` the test environment); `spack gpg untrust --signing` the key and check it is not trusted; then `site.yml --tags spack,intel_oneapi` with `spack_site_mirror: true` and `spack_mirror` the signed directory (overriding `tests/container/vars.yml`'s `false`), so that **all three** steps run: the `spack` role's first list (L700) and the site mirror's list (L19, its pinned key from the role's own file, no S3), and `intel_oneapi`'s (L959). It must finish with no prompt and report a change, Spack must trust the throwaway key afterwards (`spack gpg list --trusted`), and a second apply must report `changed=0`; then the mirror (`s3-mirror`, pointed at the directory) removed
- [ ] T008 [US1] Run `just test` and `just full-test` and see T006 and T007 fail for the right reason (the steps are still `command` steps; record what the container case reports), recording which failed

### Implementation

- [ ] T009 [US1] In `exportit/sandbox-provisioning/roles/spack/tasks/main.yml` (the first list, `funcs-setup-instance.sh` L700; the site mirror's list, `spack-pubkey.sh` L19) and `exportit/sandbox-provisioning/roles/intel_oneapi/tasks/main.yml` (`funcs-setup-instance.sh` L959), make each of the three `command` steps `kind: gpg_key` with `from_mirrors: true`, each still saying the script lines it replaces, its comment saying the collection answers Spack's confirmation since 0.0.3 (data-model.md, "The three steps")
- [ ] T010 [US1] Run `just test` and `just full-test` in the unit: T006 and T007 pass, and the container's second apply and check mode still change nothing

**Checkpoint**: no `--yes-to-all` workaround is left; the container proves the steps against a mirror that publishes a key.

---

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T011 [P] In `exportit/MAP.md`, the paragraph that describes the workaround (the `sandbox-provisioning` part, "The three steps that trust the keys the mirrors publish …") says the steps are the collection's `from_mirrors` again, on 0.0.3, since this spec
- [ ] T012 [P] In `specs/004-spack-stack-ufs-coastal/tasks.md`, T017's description (its head node) adds that its `proof.tfvars` sets `provisioning_version` to the tag this spec cuts (0.0.5) or a later one, and that its record says whether the first boot ended `failed=0`, installed from the RHEL 10 cache, and ran the three `from_mirrors` steps with no prompt (spec 009's FR-007, SC-004; research R5)
- [ ] T013 [P] In `specs/README.md`, set 009's state
- [ ] T014 Grep `exportit/sandbox-provisioning/` and `exportit/MAP.md` for `--yes-to-all` used for `buildcache keys`, and for `TRUST_MIRROR_KEYS`' old form: none left (SC-001); `docs/BUILD-CACHE.md`'s `spack gpg trust --yes-to-all` is another command, and stays
- [ ] T015 Commit the unit's work on its branch; record the submodule here; run `just constitution-check`
- [ ] T016 Run the root `just test`
- [ ] T017 Run the root `just full-test`
- [ ] T018 In `specs/009-collection-from-mirrors/spec.md`, an **Outcome** section: the installed version before and after, the container case's result, and that the real-node proof is spec 004's T017, to be linked when its record exists
- [ ] T019 Run `/speckit-converge` on `specs/009-collection-from-mirrors/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T020 Walk `specs/009-collection-from-mirrors/quickstart.md`, steps 1 to 4 each with its evidence; step 5 is spec 004's (done condition 3)
- [ ] T021 On the operator's word only: finish the unit's branch into its `develop` with the version raised to 0.0.5 (`pyproject.toml`, `uv.lock`), tag `0.0.5` and push; in `exportit/cloud-sandbox/units.toml`, sandbox-provisioning 0.0.5, committed in `csis-cloud-sandbox` on a branch, finished and pushed; record their commits; then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T022 Record the release: `csis-sandbox-provisioning` 0.0.5, cut on the operator's word with T021 (done condition 5)
- [ ] T023 Mark the spec **complete**, with the date, only when T001 to T022 are checked (done conditions 1 and 6); its outcome links spec 004's T017 record once it exists

---

## Dependencies & Execution Order

- **Setup (T001, T002)**: needs spec 002 merged (done).
- **US2 (T003 to T005)**: after Setup; before US1 (the container case needs 0.0.3).
- **US1 (T006 to T010)**: after US2; T006 and T007 before T009.
- **Polish**: after US1; T011 to T014 before T015; then T015 to T023 in order.
- **Spec 004** comes after this spec, and its head node is this spec's real-node proof.

### Parallel Opportunities

- T006 and T007 (different files); T011, T012 and T013.

---

## Implementation Strategy

1. The floor (US2): the MVP, without which nothing else is safe.
2. The steps and the container's case (US1).
3. Records, release on the operator's word, and the merge; the real node is spec 004's.

---

## Notes

- The container's throwaway signing key is made and thrown away inside the container; no real key is used.
- Nothing in `ATTIC/` is read for any task.
