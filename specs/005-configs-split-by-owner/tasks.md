---

description: "Task list for splitting sandbox-configs by owner"
---

# Tasks: sandbox-configs split by owner

**Input**: Design documents from `specs/005-configs-split-by-owner/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md); spec 003 merged (its `moved` directive)

**Done**: by the six conditions of the constitution's Development Workflow
(1.2.0): T040 to T044 are those conditions' tasks. Each task, when checked,
gets a record under it.

**Tests**: included, written first and seen to fail (principle IV; FR-006
names them).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel
- **[Story]**: US1 (cloudflow's examples), US2 (the site's files)

## Path Conventions

From the Cloud-Sandbox root: `exportit/sandbox-configs/`
(`csis-sandbox-configs`), `exportit/cloudflow/`,
`exportit/sandbox-terraform/`, each committed in its own repository; the
maps, the tools and the Justfile are Cloud-Sandbox's.

---

## Phase 1: Setup

- [ ] T001 Start `feature/configs-split-by-owner` with git-flow in `exportit/sandbox-configs/`, `exportit/cloudflow/` and `exportit/sandbox-terraform/` from their `develop`, each clean and level with its origin
- [ ] T002 Run `just init` in the three units and the root `just test`; confirm `exportit/tools/export.py` reads `moved` (spec 003)

---

## Phase 2: Foundational (the 23, before anything moves; FR-003)

### Tests first

- [ ] T003 In `exportit/sandbox-configs/tests/test_descriptions.py`, add: a `status` of `retired: <reason>` is accepted only for a path under `attic/`, and every file under `attic/` has one; run `just test` and see it pass on today's tree and fail on a test entry that breaks it, recorded

### Implementation

- [ ] T004 In `exportit/sandbox-configs`, for each of the 3 `not JSON` site files: fix it when the intended JSON is evident, else move it under `attic/` with `retired: not JSON, <what>`; one commit each, naming the file (research R2)
- [ ] T005 For the 6 files `missing table_name` (5 site, the cluster template): add `"table_name": "IOOS-Sandbox-Compute-Nodes"`; one commit
- [ ] T006 For each of the 13 files missing other keys: add the key with the value a sibling description of the same model gives, naming the sibling in the commit message; with no sibling, retire it with the reason; one commit each
- [ ] T007 For the template with `JOBTYPE 'XXX_MODEL_EXPERIMENT'`: the JOBTYPE of the model it is for, so the schema reads it; one commit
- [ ] T008 Update `tests/catalogue.json`: each repaired file `ok`, each retired file at its `attic/` path with its reason; run `just test`: every file is as catalogued, no `template` or `example` file is unreadable; record the counts (repaired, retired)
- [ ] T009 In `exportit/sandbox-configs.map`, add `new attic/`; commit the unit's work; record the submodule; root `just test`

**Checkpoint**: every file that will move is readable.

---

## Phase 3: User Story 1 - A new site starts from cloudflow's examples (Priority: P1) 🎯 MVP

### Tests first

- [ ] T010 [P] [US1] In `exportit/cloudflow/tests/test_examples.py`, write: every file under `examples/configs/` is read by `schema/jobs.json` or `schema/clusters.json` as its kind says, using the reading rules `csis-sandbox-configs`' `tests/descriptions.py` uses (moved with it); the cluster template has `table_name`; `examples/configs/catalogue.json` lists every file, each `ok`
- [ ] T011 [P] [US1] In `exportit/cloudflow/tests/test_configs_schema.py`, move the workshop's `exportit/tools/tests/test_configs_schema.py`, reading cloudflow's own `src/` and `schema/`
- [ ] T012 [P] [US1] In `exportit/tools/tests/`, write: the 51 `moved` lines of `sandbox-configs.map` are exactly the catalogue's `template` and `example` files, destination `examples/configs/<the same path>`; none names a retired file
- [ ] T013 [US1] Run them and see them fail for the right reason, recording which failed

### Implementation

- [ ] T014 [US1] Generate the 51 `moved` lines from `tests/catalogue.json` with a short script in the workshop (kept as `exportit/tools/moved_lines.py` or run once and recorded), add them to `exportit/sandbox-configs.map`, and review them by hand against the catalogue (research R3)
- [ ] T015 [US1] Search the 51 files for secrets and personal data as the repositories' histories were searched (private keys, AWS keys, tokens, passwords, emails other than placeholders); record the result; anything found stops the move for the operator (research R4)
- [ ] T016 [US1] In `exportit/cloudflow`, add the 51 files under `examples/configs/` as they are after Phase 2, and `examples/configs/catalogue.json`, in one commit naming `csis-sandbox-configs`' commit they came from
- [ ] T017 [US1] In `exportit/cloudflow`, add `tools/configs_schema.py` (from `exportit/tools/`, reading `src/`), `schema/jobs.json` and `schema/clusters.json` written by it, the reading rules from `csis-sandbox-configs/tests/descriptions.py`, and a `just schema` target; run `just test`: T010 and T011 pass
- [ ] T018 [US1] In `exportit/sandbox-configs`, remove the 51 files and their catalogue entries in one commit naming cloudflow's commit; run `just test`
- [ ] T019 [US1] In `exportit/cloudflow.map`, declare cloudflow's new files (`new schema/`, `new tools/`, or the rule the map already has for them) if `just export-check cloudflow` asks; remove `exportit/tools/configs_schema.py` and its test from the workshop
- [ ] T020 [US1] Run `just export-check`, `just export-lineage sandbox-configs cloudflow` and `just sync-rehearse`: both units' lineage holds, and a change to a moved file lands in cloudflow (FR-005)

---

## Phase 4: User Story 2 - The site's own files stay the site's (Priority: P2)

### Tests first

- [ ] T021 [P] [US2] In the root, add `configs-schema-check` to the `Justfile` and to `test`: `exportit/sandbox-configs/schema/` equals cloudflow's `schema/`; see it fail on a changed copy, recorded
- [ ] T022 [P] [US2] Write `exportit/sandbox-terraform/tests/cluster_description.tftest.hcl` with mocked providers: the output `cluster_description` has exactly `platform`, `region`, `subnet_id`, `sg_ids`, `placement_group`, `table_name`, `image_id`; `image_id` is `null` when no image matches; the test writes a sample of the output to `tests/fixtures/cluster_description.json`
- [ ] T023 [P] [US2] In `exportit/tools/tests/`, write: `exportit/sandbox-terraform/tests/fixtures/cluster_description.json`'s keys are read by cloudflow's `schema/clusters.json` (research R7)
- [ ] T024 [US2] Run them and see them fail for the right reason, recording which failed

### Implementation

- [ ] T025 [US2] Change the root `Justfile`'s `configs-schema` to copy cloudflow's `schema/` into `exportit/sandbox-configs/schema/`; add `configs-schema-check` to `test`; run it
- [ ] T026 [US2] In `exportit/sandbox-terraform/`, add `variable "node_table_name"` (default `IOOS-Sandbox-Compute-Nodes`), `data "aws_ami_ids" "node_image"` (owner `self`, name prefix the deployment's image name), and `output "cluster_description"` (research R6); `just test` and `just full-test`: T022 passes
- [ ] T027 [US2] In `exportit/sandbox-terraform/DEPLOYMENT.md`, how to read `cluster_description` (`tofu output -json cluster_description`), and that `image_id` fills after `node-image.yml` and `tofu apply -refresh-only`
- [ ] T028 [US2] In `exportit/sandbox-configs`, retire `cluster.configs/IOOS/current.system` and `current.image_id` to `attic/`, `retired: replaced by csis-sandbox-terraform's output cluster_description`; `just test`
- [ ] T029 [US2] Run the root `just test`: T021 and T023 pass

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T030 [P] In `exportit/MAP.md`, the `sandbox-configs` and cloudflow sections: what moved, what stayed, what was repaired and retired (counts), where the schema lives
- [ ] T031 [P] In `exportit/sandbox-configs/README.md` and cloudflow's `README.md`, where the examples and the schema are now
- [ ] T032 [P] In `specs/README.md`, set 005's state
- [ ] T033 Commit each unit's last changes; record the three submodules here; `just constitution-check`
- [ ] T034 Run the root `just test`
- [ ] T035 Run the root `just full-test`
- [ ] T036 [P] In `specs/005-configs-split-by-owner/spec.md`, an **Outcome** section: the counts (moved 51, repaired, retired, kept 71 less the retired), and SC-001's evidence
- [ ] T037 [P] Close or add `exportit/REMINDERS.md` items this spec touches (the link of spec 006 if the job descriptions were changed here; none otherwise)
- [ ] T038 Re-read [quickstart.md](quickstart.md) against what was run; correct it if a step differed
- [ ] T039 Check that nothing in any unit or the workshop still reads `exportit/tools/configs_schema.py` (`git grep`); record the result
- [ ] T040 Run `/speckit-converge` on `specs/005-configs-split-by-owner/`; record that it appended nothing, or carry out what it appended (done condition 2)
- [ ] T041 Walk `specs/005-configs-split-by-owner/quickstart.md`, recording each command and result (done condition 3)
- [ ] T042 On the operator's word only: finish the three units' branches and push, record their commits, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
- [ ] T043 Record that no release applies, unless the operator asks for one (done condition 5)
- [ ] T044 Mark the spec **complete**, with the date, only when T001 to T043 are checked (done conditions 1 and 6)

---

## Dependencies & Execution Order

- **Setup**: needs spec 003 merged.
- **Foundational (Phase 2)**: before any move; T004 to T007 in any order, then T008, T009.
- **US1**: after Phase 2; T014 and T015 before T016; T016 and T017 before T018; T020 last.
- **US2**: T021 to T023 can start after Phase 2; T025 needs US1's T017 (cloudflow's schema); T028 any time after T026.
- **Polish**: after US1 and US2; T040 to T044 in order.

### Parallel Opportunities

- T010, T011 and T012; T021, T022 and T023; T030, T031, T032, T036, T037.

---

## Implementation Strategy

1. Repairs first, in the unit that owns them: nothing unreadable travels.
2. The move and the schema with cloudflow (US1): the MVP.
3. The site's side (US2): the copy of the schema, the output, `current.*` retired.

---

## Notes

- Nothing in any task touches AWS; the output is read from a plan.
- A repair with no sibling's evidence is a retirement, never a guess.
- Nothing in `ATTIC/` is read for any task.
