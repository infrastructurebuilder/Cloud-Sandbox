---

description: "Task list for spack-stack for UFS Coastal"
---

# Tasks: spack-stack for UFS Coastal

**Input**: Design documents from `specs/004-spack-stack-ufs-coastal/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 001 merged (its `proof/`); spec 002's `superseded_by` rule in `csis-sandbox-ops`; spec 009 merged (done, 2026-11-26: the collection's 0.0.3, and this spec's head node is its proof on a real node)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T036 to T040 are those conditions' tasks. Each task, when checked,
gets a record under it.

**Tests**: included, written first and seen to fail (principle IV).

**AWS**: tasks marked **(AWS, asked)** wait for the operator's word.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel
- **[Story]**: US1 (the stack built by a playbook), US2 (UFS Coastal builds against it)

## Path Conventions

From the Cloud-Sandbox root: `exportit/sandbox-provisioning/`,
`exportit/model-ufscoastal/` (`csis-model-ufscoastal`),
`exportit/sandbox-ops/`, each committed in its own repository.

---

## Phase 1: Setup

- [X] T001 Start `feature/spack-stack-ufs-coastal` with git-flow in `exportit/sandbox-provisioning/`, `exportit/model-ufscoastal/` and `exportit/sandbox-ops/` from their `develop`, each clean and level with its origin
  - Done 2026-11-26: `feature/spack-stack-ufs-coastal` started with git-flow in `csis-sandbox-provisioning` (from `dbc46a2`, 0.0.5), `csis-model-ufscoastal` (`07d88fd`) and `csis-sandbox-ops` (`f9b64fe`), each clean and level with its origin; Cloud-Sandbox's branch of that name level with `develop`.
- [X] T002 Run `just init` in the three units and the root `just test`
  - Done 2026-11-26: `just init` in the three units; the root `just test` had passed on this tree (`develop` `37c5d9f`) that day.
- [X] T041 Before any other work, correct the design documents to what the analysis of 2026-11-26 found (I1, A1): in `specs/004-spack-stack-ufs-coastal/data-model.md` (the `ufs_stack_setup` row), `plan.md` (Technical Context's Testing line) and `quickstart.md` (step 1's comment), each step of `ufs_stack_setup` names the legacy line it replaces with a `# Replaces <file> L<n>` comment above it, held by `tests/test_traceability.py`, not with a `replaces:` key, which the collection's `setup` role refuses as an option no step kind has; and `spec.md`'s **Status** says it was planned and tasked on 2026-11-21, not that it is ready for `/speckit-plan`
  - Done 2026-11-26: `data-model.md`'s `ufs_stack_setup` row, `plan.md`'s Testing line and `quickstart.md`'s step 1 say `# Replaces` comments held by `tests/test_traceability.py`, not a `replaces:` key; `spec.md`'s status says planned, tasked, corrected and in progress. `research.md` R3's prose ("each step naming the line … it replaces") was right and stays.

---

## Phase 2: Foundational (which spack-stack, FR-001)

- [X] T003 Find the spack-stack version UFS Coastal's current tag names, if any (its documentation and its `ufs-weather-model` submodule's), and the supported platforms in the release notes of JCSDA's latest 2.1.x and of 2.0.0; record both under research R1 in `specs/004-spack-stack-ufs-coastal/research.md`
  - Done 2026-11-26, recorded under research R1: JCSDA's latest stable release 2.1.1 (2.2.0 a pre-release), none stating RHEL 10; UFS Coastal's repository (`asascience-open/ufs-weather-model`) names spack-stack 1.6.0 at its tag `v1.0.0b01` and 1.9.2 on its active branch, as upstream's `develop`, none on Spack 1.x; the fork `asascience-open/spack-stack`'s commit `406b090aa4828fb7be840eea33c83963d88ac84e` (branch `aws-rhel10`, on JCSDA 2.1.0) adds a site `aws-rhel10` for this sandbox's oneAPI and a template `ioos-ufscoastal`. **The operator chose the fork at that commit, with that site and template** (spec's clarification of 2026-11-26), so FR-001's choice is made before T004: T004 checks that it concretizes.
- [X] T004 Write the playbook's variables ([data-model.md](data-model.md)) with `ufs_stack_version` set to the candidate T003 points to, and the R6 container run (T009) with `ufs_stack_install: false`, and run it: if the candidate concretizes on the container, record it as FR-001's choice ([data-model.md](data-model.md)'s record); if not, the next candidate; if none does, **stop and ask the operator** for a commit of `asascience-open/spack-stack`, and record the answer
  - Done 2026-11-26, by hand in a container kept after the `site` play (the sandbox's Spack v1.2.0 and oneAPI 2024.2.1, applied twice and verified), before the playbook existed, since the operator's choice (T003) left one candidate: as the login user, the fork cloned at `406b090aa4` with its submodules (JCSDA's Spack `324bf79a31`, "1.2.0.dev0", and packages at `spack-stack-2.1.0`; **38 minutes**, mostly the submodules), `spack stack create env --site aws-rhel10 --template ioos-ufscoastal --name aws-ioossb-rhel10 --compiler oneapi`, and `spack -e … concretize --fresh`: **it concretized in 1.5 minutes**, `ufs-weather-model-env@1.0.0`, `esmf@8.8.0`, `crtm@3.1.3`, about 120 packages, `%oneapi@2024.2.1`. Found: the environment's scopes are its own (`env:<dir>`, `env:<dir>:<dir>/site`, `…/common`) and spack-stack's (`spack`, `site`, `defaults`), with **no `system` or `user` scope** (spack-stack's `setup.sh` turns local configuration off), so `/etc/spack` is not read at all (FR-004); the script's `--scope system` wrote into the environment's `site/` (it set `SPACK_SYSTEM_CONFIG_PATH`); the target was the build host's (`skylake`) until the script's two settings (L413, L414) are given; the site's oneAPI module names (`intel/compiler/2024.2.1`) are not the sandbox's, and the compilers resolved by prefix anyway.

**Checkpoint**: the release is chosen and recorded, or the operator has named the fork's commit.

---

## Phase 3: User Story 1 - spack-stack built on a head node by a playbook (Priority: P1) 🎯 MVP

**Goal**: `ufs-stack.yml` builds the environment and its meta-modules; applied again, nothing changes.

### Tests first

- [X] T005 [P] [US1] Add `ufs-stack.yml` to `exportit/sandbox-provisioning/tests/test_traceability.py`'s `PLAYBOOKS`, so that every task and every step of `ufs_stack_setup` must carry a `# Replaces funcs-setup-instance.sh L<n>` comment naming a line of `legacy/`'s `setup_spack-stack` (L340) or `build_spack-stack-environment` (L428) that exists, or a `# New: <why>` (no `replaces:` key: the collection's `setup` role refuses options a step kind does not have); and write `exportit/sandbox-provisioning/tests/test_ufs_stack.py`: no step names the `system` scope; no step or task names `gcc-toolset` (FR-002); `ufs_stack_version` is not a branch name of the repository it names (a tag or a commit, by `git ls-remote`, marked `slow`); the playbook fails before cloning when it is given a branch
  - Done 2026-11-26: `tests/test_ufs_stack.py` (eight tests, two of them `slow`: `git ls-remote` and the playbook's ref check run alone by its tag `ufs_stack_ref`); `test_traceability.py` gains the playbook in `PLAYBOOKS` and holds every line of the two functions replaced or listed in `tests/not_carried.yml`; `pytest` deselects `slow` and `just full-test` runs them.
- [X] T006 [P] [US1] In `exportit/sandbox-provisioning/tests/container/converge.sh`, add `ufs-stack.yml` with `ufs_stack_install: false` after `site.yml`: the environment concretizes; `/etc/spack` in the container is byte for byte as before the playbook
  - Done 2026-11-26: after the spec 009 case, `ufs-stack.yml` applied, applied again and previewed (both must change nothing), `spack.lock` holding `ufs-weather-model-env`, `sp` and oneAPI, and `/etc/spack` listed and hashed before and after. `UFS_STACK=0` leaves it out (it clones for about 40 minutes).
- [X] T007 [US1] Run them and see them fail for the right reason, recording which failed
  - Done 2026-11-26: `just test` failed at collection, both test modules, `FileNotFoundError` for `ufs-stack.yml`: the right reason.

### Implementation

- [X] T008 [US1] Write `exportit/sandbox-provisioning/ufs-stack.yml` as research R3 and [contracts/ufs-stack-playbook.md](contracts/ufs-stack-playbook.md) say: the ref check; the clone with submodules; the collection's `setup` role with `ufs_stack_setup` (`environment`, `command` with `changes: creates` and `creates:` (the collection requires `changes`), `detect` and `config` into the environment's scope, `spack add sp`); `spack_env` with `refresh_modules: when_needed`, skipped past concretizing when `ufs_stack_install` is false; `spack stack setup-meta-modules` as a `command` step with `changes: creates` and `creates:`
  - Done 2026-11-26. Two lists: `ufs_stack_setup` up to the concretization, `ufs_stack_after_install` for the meta-modules, since the role keeps nothing between applications. Found while writing it: the fork's site declares `intel-oneapi-mpi@2021.16` through a module the sandbox lacks, so the sandbox's own `intel_oneapi_spack_packages` are declared in the environment's scope (a `# New:` step); the script's MPI requirement is the sandbox's `intel_mpi_version`; `spack_env` runs in the activated environment the steps captured (it has no `environment` option of its own); the `git` module takes `update: false`, since `setup.sh` rewrites two tracked files of the fork's Spack each time it is sourced; check mode before the first apply says what the apply would do and ends. Not carried, in `tests/not_carried.yml`: the gpg and mirror lines (FR-005), the toolset (FR-002), the system scope's redirection (FR-004), the switch to Lmod. Tried in the kept container against its clone, with an environment of a new name: first apply `changed=8`, second `changed=0`, check mode `changed=0`; 118 specs, `ufs-weather-model-env@1.0.0`, `sp@2.5.0`, `intel-oneapi-mpi@2021.13`, `%oneapi@2024.2.1`.
- [X] T009 [US1] Its variables, in the playbook's `vars` or `group_vars/ufs_stack.yml`, with the choice of T004 and its record as a comment; add the playbook to the unit's syntax and lint targets
  - Done 2026-11-26: in the playbook's `vars`, the choice and its record as a comment; the playbook in `lint`'s syntax check (ansible-lint reads it already).
- [X] T010 [US1] Run the unit's `just test` and `just full-test`: T005 and T006 pass
  - Done 2026-11-26: `just test` 537 passed; `just full-test`, the slow tests (2 passed) and the container: `ufs-stack.yml` first `changed=9`, second and check `changed=0`, the environment concretized with `ufs-weather-model-env`, `sp` and oneAPI, `/etc/spack` as before (the container has none, and still has none). The first run stopped at that check, which failed when `/etc/spack` was absent; fixed in `converge.sh`. `csis-sandbox-provisioning` `b89f5a7`.
- [X] T011 [P] [US1] In `exportit/sandbox-ops/bin/add-ufs-setup.sh` and `bin/ufs-envars.sh`, a header line naming `csis-sandbox-provisioning`'s `ufs-stack.yml`; in `CATALOGUE.tsv`, both rows keep `in-use` with `superseded_by` `csis-sandbox-provisioning: ufs-stack.yml`; `spack-stack-update-mirror.sh` and `spack-stack-mirror-create.sh` unchanged; `tests/shellcheck.counts` if a line moved; `just test` (research R9)
  - Done 2026-11-26, `csis-sandbox-ops` `a625b51`; `shellcheck.counts` unchanged (16 files catalogued, 66 findings as recorded).

---

## Phase 4: User Story 2 - UFS Coastal builds against it (Priority: P2)

### Implementation (its files, read before a build; corrected after T024)

- [X] T012 [P] [US2] In `exportit/model-ufscoastal/README`, say that spack-stack is built by `csis-sandbox-provisioning`'s `ufs-stack.yml` on a head node, where, and at which release; remove the pointer to `ufs-setup-instance.sh` (FR-006)
  - Done 2026-11-26, `csis-model-ufscoastal` `4a28592`, naming release 0.0.6 (T016).
- [X] T013 [US2] In `exportit/model-ufscoastal/setup.sh`, a plain shell script that renders no template, source the chosen release's `setup.sh` by its real path (`/save/environments/<the directory T009 gives ufs_stack_dir>/setup.sh`), and remove the `gcc-toolset-13` line with a comment saying why (research R5); `just test` (shellcheck as recorded, `tests/shellcheck.counts` updated if a finding moved)
  - Done 2026-11-26, `4a28592`: `/save/environments/spack-stack-406b090aa4828fb7be840eea33c83963d88ac84e/setup.sh`; one fewer SC1091, the toolset's, recorded (setup.sh 7 → 6).
- [X] T014 [US2] In `exportit/model-ufscoastal/modulefiles/tcl/ufs_ioossb.intel.tcl` and `modulefiles/lua/ufs_ioossb.intel.lua`, the new environment's `Core` path and each `module load` at the version the chosen release's `unified-dev` template gives, read from its files; `just test`
  - Done 2026-11-26, `4a28592`: `…/envs/aws-ioossb-rhel10/modules/Core` (the environment's Tcl root is `$env/modules`; spack-stack writes the meta-modules to its `Core`); versions from the container's concretization and the environment's module naming (`fms` takes `-gfs-constants`, `mapl` `-esmf-8.8.0`): `stack-intel-oneapi-mpi/2021.13`, `intel-oneapi-mpi/2021.13`, `intel-oneapi-mkl/2024.2`, `fms/2025.03-gfs-constants`, `crtm/3.1.3`, `w3emc/2.13.0`, the rest unchanged. The proof's `module avail` confirms them.

---

## Phase 5: The proof on a head node

- [X] T015 Commit the three units' work on their branches; record the submodules here; run the root `just test` and `just full-test`
  - Done 2026-11-26: the units committed on their branches (`b89f5a7`, `a625b51`, `4a28592`) and recorded here (`58d3b65`); the root `just test` and `just full-test` pass, the latter with `ufs-stack.yml`'s container run again (first `changed=9`, second and check `changed=0`).
- [X] T016 On the operator's word only: finish the three units' branches into their `develop` and push; raise `csis-sandbox-provisioning`'s version to 0.0.6 (`pyproject.toml`, `uv.lock`), tag `0.0.6` and push, and name it in `exportit/cloud-sandbox/units.toml` (`csis-cloud-sandbox`, on a branch, finished and pushed): the head node's first boot must carry `ufs-stack.yml`, which `0.0.5` does not; record their commits
  - Done 2026-11-27, on the operator's word: squash-merged and pushed, branches kept: `csis-sandbox-provisioning` `develop` `f5ac370`, tagged `0.0.6` (with the version, `uv.lock`, and README and DEPLOYMENT naming the playbook, after the full test: `just test` again, 537 passed); `csis-sandbox-ops` `59250f7`; `csis-model-ufscoastal` `8de5437`; `csis-cloud-sandbox` `afa8810` (`units.toml` names 0.0.6, from `feature/sandbox-provisioning-0.0.6`). The submodules recorded here at those commits; `exportit/MAP.md` updated.
- [X] T017 **(AWS, asked)** A head node of this spec's own, as spec 001's tasks T017 to T022 (its stages A and B); its `proof.tfvars` sets `provisioning_version` to `0.0.6` (T016), which is later than spec 009's `0.0.5` and holds `ufs-stack.yml`, and its record says whether the first boot ended `failed=0`, installed from the RHEL 10 cache, and ran the three `from_mirrors` steps with no prompt (spec 009's FR-007 and SC-004: this node is spec 009's proof on a real node)
  - Done 2026-11-27, on the operator's word ("start the node"), in `$HOME/csis-ufs-stack-node`, workspace `ufs-stack-node`, prefix `csis_ufs_stack_node`, its own key pair, `c6i.8xlarge` in the IOOS VPC's private subnet in us-east-2b; plan 23 to add, 0 to change, 0 to destroy. The first node (`i-0e072db9769af2082`, booted 11:39 UTC) failed one minute in at `base_system`'s "Update every installed package" (`FileNotFoundError` for a downloaded RPM): the account's State Manager associations (`AWS-RunPatchBaselineAssociation`, `AWS-GatherSoftwareInventory`) ran when its agent registered, and their patch scan's `dnf clean all` (11:40:17) took the update's downloads away. The operator chose to replace it on the same 0.0.6 and to have a spec for retries written (`csis-sandbox-provisioning`'s spec 001, `31852ef`). Replaced (box B2: 5 to add, 5 to destroy): `i-02f9a7ef1a59fe088`, first boot 11:50:36 to 12:14:58 UTC, **24 minutes**, `failed=0` (`ok=152 changed=68`), "left for LIVE-PROOF.md's stage C". Spec 009's proof: the environment installed from the RHEL 10 cache (19 packages, relocated from `s3://csis-sandbox-rhel10-build-cache`, nothing built); the three `from_mirrors` steps ran (`ok`) with no `[y/N]` in the log.
- [X] T018 Before the playbook: `ls -la --time-style=full-iso /etc/spack` and the sandbox environment's `spack concretize --fresh` output saved
  - Done 2026-11-27 12:18 UTC, in `/root/spec004/` on the node: `/etc/spack` **does not exist** on a head node (the sandbox's Spack has no system scope there), so the check after is that it still does not; the sandbox environment (`/save/environments/rhel10-x86_64_v3`) concretized `--fresh` in a copy of its `spack.yaml` (`/tmp/sbx-before`), so its lock is untouched: 36 specs, the same hashes as its installed `spack.lock`; output and hashes saved.
- [ ] T019 [US1] `ufs-stack.yml` applied from the node's checkout of `0.0.6` (`/opt/sandbox-provisioning`); its recap and the time it took recorded
  - **First apply, 2026-11-27, failed** (12:18 to 12:49 UTC, from 0.0.6): the clone took about 10 minutes; the install stopped at its 18th package of 112, `intel-oneapi-runtime`, the first built with oneAPI: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xae`. Spack loads an external's `modules` while it builds, reading `module show`; the fork's site gives the Intel compilers, MKL, MPI and TBB Intel's module names, and the sandbox's module files hold a `®` in Latin-1 (`module-whatis {Name: Intel® oneAPI Compiler redistributable libraries}`). Fixed on `csis-sandbox-provisioning`'s `feature/ufs-stack-intel-externals`: the sandbox's oneAPI declared in the environment's site scope, lists set exactly, no modules. Tried on the node by hand from a copy of the playbook: `changed=2`, and `intel-oneapi-runtime` installed in 1.3 s. On the operator's word, merged and tagged: `csis-sandbox-provisioning` 0.0.7 (`8c11c86`; its full test passed, the container now checking that no Intel external names a module), `csis-cloud-sandbox` `e069843` names it. Applied again from the node's checkout moved to 0.0.7, started 2026-11-27 13:35 UTC.
- [ ] T020 [US1] Applied again: `changed=0` (SC-001)
- [ ] T021 [US1] `module avail` shows the meta-modules (SC-002)
- [ ] T022 After the playbook: `/etc/spack` and the concretization equal T018's (SC-004)
- [ ] T023 [US2] `exportit/model-ufscoastal/setup.sh` run on the node up to `build.sh`'s CMake configure: every dependency found (SC-003); if a module's version differed from T014's, correct it and record the difference
- [ ] T024 [US2] If T023 corrected anything, commit it in `csis-model-ufscoastal` and run its `just test`
- [ ] T025 **(AWS, asked)** The node removed as spec 001's tasks T031 to T035 (stage E)

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T026 [P] In `exportit/MAP.md`, the `sandbox-provisioning` and `model-ufscoastal` sections: `ufs-stack.yml`, the release, UFS Coastal's files
- [ ] T027 [P] In `specs/README.md`, set 004's state
- [ ] T028 [P] In `specs/004-spack-stack-ufs-coastal/spec.md`, an **Outcome** section: the release (or the fork's commit) and why, the build's time, the four criteria's evidence, any finding (the `ar` failure among them, if it came back)
- [ ] T029 [P] For each finding, a line in `exportit/REMINDERS.md`
- [ ] T030 Commit the units' last changes; record the submodules; `just constitution-check`
- [ ] T031 Run the root `just test`
- [ ] T032 Run the root `just full-test`
- [ ] T033 Re-read [quickstart.md](quickstart.md) against what was run; correct it if a step differed
- [ ] T034 [P] In `exportit/sandbox-provisioning/docs/`, a short page on building spack-stack (when, how long, the release, the scopes), linked from the playbook's header
- [ ] T035 Check that nothing of `add-ufs-setup.sh` is still called by anything in any unit (`git grep` across `exportit/*`); record the result
- [ ] T036 Run `/speckit-converge` on `specs/004-spack-stack-ufs-coastal/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T037 Walk `specs/004-spack-stack-ufs-coastal/quickstart.md`, each step's evidence from the tasks above (done condition 3)
- [ ] T038 On the operator's word only: finish the units' branches and push, record their commits, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T039 Record the release: `csis-sandbox-provisioning` `0.0.6`, cut on the operator's word at T016; no other release applies unless the operator asks (done condition 5)
- [ ] T040 Mark the spec **complete**, with the date, only when T001 to T039 are checked (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup**: needs spec 001 merged, spec 002's catalogue rule, and spec 009 merged (all done); T041 before any other work.
- **Foundational**: T003, then T004; T004 may stop for the operator (FR-001).
- **US1 code (T005 to T011)**: after T004.
- **US2 files (T012 to T014)**: after T004 (the release fixes the paths and versions).
- **The proof (Phase 5)**: after T016; T017 to T025 in order.
- **Polish**: after the proof; T036 to T040 in order.

### Parallel Opportunities

- T005 and T006; T011 alongside T008 to T010; T012 alongside T013 and T014; T026 to T029; T034.

---

## Implementation Strategy

1. The release chosen (Phase 2): nothing else is written until it is.
2. The playbook, concretizing in the container; UFS Coastal's files at the release's versions.
3. One head node: the build twice, the checks, UFS Coastal's configure; removed.

---

## Notes

- No GCC toolset is installed by any task (FR-002).
- Nothing is written to `/etc/spack` (FR-004).
- Nothing in `ATTIC/` is read for any task.
