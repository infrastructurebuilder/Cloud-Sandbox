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

- [X] T001 Start `feature/configs-split-by-owner` with git-flow in `exportit/sandbox-configs/`, `exportit/cloudflow/` and `exportit/sandbox-terraform/` from their `develop`, each clean and level with its origin
  - Done 2026-11-23: `feature/configs-split-by-owner` made in `csis-sandbox-configs`, cloudflow and `csis-sandbox-terraform` from their `develop`, each clean and level with origin; Cloud-Sandbox's branch existed and had `develop` merged in (`ef92426`).
- [X] T002 Run `just init` in the three units and the root `just test`; confirm `exportit/tools/export.py` reads `moved` (spec 003)
  - Done 2026-11-23: the three units' `just init` passed; `export.py` reads `moved` (cloudflow.map's three lines, spec 003); the root `just test` had passed on `develop`'s tree (spec 006's final run).

---

## Phase 2: Foundational (the 23, before anything moves; FR-003)

### Tests first

- [X] T003 In `exportit/sandbox-configs/tests/test_descriptions.py`, add: a `status` of `retired: <reason>` is accepted only for a path under `attic/`, and every file under `attic/` has one; run `just test` and see it pass on today's tree and fail on a test entry that breaks it, recorded
  - Done 2026-11-23: `csis-sandbox-configs` `6c64080`, `6e9b904`: `attic/` and `attic/REASONS.json` in `descriptions.py`, `misplaced_retirements()`, and two tests: the real catalogue keeps the rule, and a test of the rule finds each of its five breaches. 137 passed.

### Implementation

- [X] T004 In `exportit/sandbox-configs`, for each of the 3 `not JSON` site files: fix it when the intended JSON is evident, else move it under `attic/` with `retired: not JSON, <what>`; one commit each, naming the file (research R2)
  - Done 2026-11-23: `ioos.nosofs.cfg` (`dccb859`) and `nosofs.config` (`e4898a9`), a trailing comma each, repaired; `current.system`, the third, is a fragment, not a description: retired at T028 with `current.image_id`.
- [X] T005 For the 6 files `missing table_name` (5 site, the cluster template): add `"table_name": "IOOS-Sandbox-Compute-Nodes"`; one commit
  - Done 2026-11-23: `b1f5328`: `table_name` `IOOS-Sandbox-Compute-Nodes` in `template.ioos` and five site cluster descriptions.
- [X] T006 For each of the 13 files missing other keys: add the key with the value a sibling description of the same model gives, naming the sibling in the commit message; with no sibling, retire it with the reason; one commit each
  - Done 2026-11-23: 9 repaired from sibling evidence: `GRID` `ec95d` in `cora.reanalysis` and `test.cora.ec95d.reanalysis` (their template names that grid; `e2bef04`), `GRID` `hsofs` in `test.cora.reanalysis` (`842e6b9`), `SAVEDIR` `/save/ec2-user` in five ROMS forecasts (cloudflow's own definition, and every sibling's under `/save/<user>/`; read and not used by `romsforecast`; `7250354`), `BUCKET`, `BCKTFLDR`, `FSPEC` in `local.plots` from `liveocean.00z.plots` (`97fc939`). 4 retired with reasons (`f08422e`): `test.hsofs.V2.reanalysis`, `necofs.exp.hot`, `necofs.exp.test`, `secofs.hcst.test`.
- [X] T007 For the template with `JOBTYPE 'XXX_MODEL_EXPERIMENT'`: the JOBTYPE of the model it is for, so the schema reads it; one commit
  - Done 2026-11-23, after asking the operator ("yes" to option A): the template is for a model cloudflow has no class for yet, as the integration guide uses it; it stays as it is and is read as a **new-model template** (`MODEL_CLASS`, a `JOBTYPE` ending in `_EXPERIMENT`, keys an existing experiment type requires). Recorded in the spec's Clarifications and FR-003; `csis-sandbox-configs` `5eeb4b5`.
- [X] T008 Update `tests/catalogue.json`: each repaired file `ok`, each retired file at its `attic/` path with its reason; run `just test`: every file is as catalogued, no `template` or `example` file is unreadable; record the counts (repaired, retired)
  - Done 2026-11-23: `just record`; every change reviewed: 17 now `ok`, 4 retired under `attic/`, the template a new-model template, roles unchanged; 139 passed. The only unreadable left was `current.system` (T028).
- [X] T009 In `exportit/sandbox-configs.map`, add `new attic/`; commit the unit's work; record the submodule; root `just test`
  - Done 2026-11-23: `sandbox-configs.map` gains `new attic/`; recorded here (`64767af`). (The root `just export-check` without `source=` reports the originals' absence since stage 22, as expected; `just export-baselines` is the check that applies.)

**Checkpoint**: every file that will move is readable.

---

## Phase 3: User Story 1 - A new site starts from cloudflow's examples (Priority: P1) 🎯 MVP

### Tests first

- [X] T010 [P] [US1] In `exportit/cloudflow/tests/test_examples.py`, write: every file under `examples/configs/` is read by `schema/jobs.json` or `schema/clusters.json` as its kind says, using the reading rules `csis-sandbox-configs`' `tests/descriptions.py` uses (moved with it); the cluster template has `table_name`; `examples/configs/catalogue.json` lists every file, each `ok`
  - Done 2026-11-23: `exportit/cloudflow/tests/test_examples.py`: the catalogue lists every file; 3 templates and 48 examples; each read by `schema/` through `tools/schema_check.py`, `ok` or, for a template, the new-model template; the cluster template has `table_name`.
- [X] T011 [P] [US1] In `exportit/cloudflow/tests/test_configs_schema.py`, move the workshop's `exportit/tools/tests/test_configs_schema.py`, reading cloudflow's own `src/` and `schema/`
  - Done 2026-11-23: `exportit/cloudflow/tests/test_configs_schema.py`, the workshop's test moved, reading cloudflow's own `src/` and `schema/`.
- [X] T012 [P] [US1] In `exportit/tools/tests/`, write: the 51 `moved` lines of `sandbox-configs.map` are exactly the catalogue's `template` and `example` files, destination `examples/configs/<the same path>`; none names a retired file
  - Done 2026-11-23: `exportit/tools/tests/test_moved_configs.py`: every `moved` line goes to cloudflow at `examples/configs/<the same path>`; the moved files are exactly cloudflow's catalogue, templates and examples; none retired.
- [X] T013 [US1] Run them and see them fail for the right reason, recording which failed
  - Done 2026-11-23: all three failed for the right reason (no `moved` lines; no `schema_check` or `configs_schema` in cloudflow).

### Implementation

- [X] T014 [US1] Generate the 51 `moved` lines from `tests/catalogue.json` with a short script in the workshop (kept as `exportit/tools/moved_lines.py` or run once and recorded), add them to `exportit/sandbox-configs.map`, and review them by hand against the catalogue (research R3)
  - Done 2026-11-23: 51 lines generated from the catalogue's roles (`template`, `example`, outside `attic/`) by a one-off script, run once; 3 templates and 48 examples; reviewed against the catalogue.
- [X] T015 [US1] Search the 51 files for secrets and personal data as the repositories' histories were searched (private keys, AWS keys, tokens, passwords, emails other than placeholders); record the result; anything found stops the move for the operator (research R4)
  - Done 2026-11-23: the 51 searched: no private key, AWS key, token, password or account number; one email, `notme@my.com`, a placeholder; paths under `/save`, `/com`, `/ptmp` of `ec2-user`, and two `/Users/patrick.tripp` paths in `local.plots`, identical in the public original at `ca0604a`: nothing new is made public, and research R4 expected paths. The move went on.
- [X] T016 [US1] In `exportit/cloudflow`, add the 51 files under `examples/configs/` as they are after Phase 2, and `examples/configs/catalogue.json`, in one commit naming `csis-sandbox-configs`' commit they came from
  - Done 2026-11-23: cloudflow `28f0b85`: the 51 under `examples/configs/`, byte for byte (`cmp`), with `catalogue.json`, in one commit naming `csis-sandbox-configs`' commit.
- [X] T017 [US1] In `exportit/cloudflow`, add `tools/configs_schema.py` (from `exportit/tools/`, reading `src/`), `schema/jobs.json` and `schema/clusters.json` written by it, the reading rules from `csis-sandbox-configs/tests/descriptions.py`, and a `just schema` target; run `just test`: T010 and T011 pass
  - Done 2026-11-23: cloudflow `4674943`: `tools/configs_schema.py` (from the workshop, reading `src/`, writing `schema/`), `tools/schema_check.py` (the rules, one place for both units: the plan's "reading rules"), `schema/` (byte for byte the schema `csis-sandbox-configs` had), `just schema`, lint, pyright and pytest over `tools/`. `just test`: 210 passed. Later `1d25070` (the about line) failed the lint and was committed because a pipe hid the exit; `0c88b56` fixes it, `just test` 210 passed, exit 0.
- [X] T018 [US1] In `exportit/sandbox-configs`, remove the 51 files and their catalogue entries in one commit naming cloudflow's commit; run `just test`
  - Done 2026-11-23: `csis-sandbox-configs` `58a2554`: the 51 removed in one commit naming cloudflow's; the test that a template of each kind is here becomes one that none is. 79 files stay (130 less 51).
- [X] T019 [US1] In `exportit/cloudflow.map`, declare cloudflow's new files (`new schema/`, `new tools/`, or the rule the map already has for them) if `just export-check cloudflow` asks; remove `exportit/tools/configs_schema.py` and its test from the workshop
  - Done 2026-11-23: `cloudflow.map` gains `new schema/` and `new tools/`; the workshop's `configs_schema.py` and its test removed; `configs_copy.py` (write and check the copies of the schema and `schema_check.py`) with its tests; `csis-sandbox-configs` reads by the copied rules (`549d672`), the catalogue unchanged. Recorded in `e60f813`.
- [X] T020 [US1] Run `just export-check`, `just export-lineage sandbox-configs cloudflow` and `just sync-rehearse`: both units' lineage holds, and a change to a moved file lands in cloudflow (FR-005)
  - Done 2026-11-23: `just export-baselines` ok; `just export-lineage sandbox-configs cloudflow`: both hold the original at `ca0604a`, filtered; `just sync-rehearse`: 9 of 9, the new "a change to a description moved to cloudflow" carried into cloudflow. The moved-file scenario of spec 003 now checks for a returning file at its old path (it checked the new path in the old unit).

---

## Phase 4: User Story 2 - The site's own files stay the site's (Priority: P2)

### Tests first

- [X] T021 [P] [US2] In the root, add `configs-schema-check` to the `Justfile` and to `test`: `exportit/sandbox-configs/schema/` equals cloudflow's `schema/`; see it fail on a changed copy, recorded
  - Done 2026-11-23: `just configs-schema-check` in the root `test` and `full-test`; `tests/test_configs_copy.py` shows a changed copy failing it.
- [X] T022 [P] [US2] Write `exportit/sandbox-terraform/tests/cluster_description.tftest.hcl` with mocked providers: the output `cluster_description` has exactly `platform`, `region`, `subnet_id`, `sg_ids`, `placement_group`, `table_name`, `image_id`; `image_id` is `null` when no image matches; the test writes a sample of the output to `tests/fixtures/cluster_description.json`
  - Done 2026-11-23: `tests/cluster_description.tftest.hcl` and `tests/fixtures/cluster_description.json` (its keys: platform, region, subnet_id, sg_ids, placement_group, key_name, table_name, image_id), run by `tests/test_plan.py`. **Planned only**: twice I ran it with `command = apply`, and the module's `terraform_data.send_outputs` ran its `local-exec` provisioner, `scp.terraform.output.sh` (a 30-second wait, then an `scp` to a mocked address that failed, exit 255; nothing written); mocked providers do not stop it, nor did an override. The plan cannot show the image found once it exists (the lookup is read at apply in an empty workspace); a test checks the lookup's shape instead, and a real deployment (spec 001) proves it.
- [X] T023 [P] [US2] In `exportit/tools/tests/`, write: `exportit/sandbox-terraform/tests/fixtures/cluster_description.json`'s keys are read by cloudflow's `schema/clusters.json` (research R7)
  - Done 2026-11-23: `exportit/tools/tests/test_cluster_description.py`: every key of the fixture is one cloudflow's AWS cluster schema reads, and the required keys it leaves out are exactly a description's own (`nodeType`, `nodeCount`, `tags`).
- [X] T024 [US2] Run them and see them fail for the right reason, recording which failed
  - Done 2026-11-23: the tofu test failed for the right reason (undeclared output) before T026; T023 passed at once, the fixture being written with it, and would fail on a key the schema does not read; T021's tests passed with `configs_copy.py` written with them.

### Implementation

- [X] T025 [US2] Change the root `Justfile`'s `configs-schema` to copy cloudflow's `schema/` into `exportit/sandbox-configs/schema/`; add `configs-schema-check` to `test`; run it
  - Done 2026-11-23: the root `configs-schema` copies cloudflow's two schema files and `schema_check.py` (`exportit/tools/configs_copy.py write`); `configs-schema-check` in `test` and `full-test`.
- [X] T026 [US2] In `exportit/sandbox-terraform/`, add `variable "node_table_name"` (default `IOOS-Sandbox-Compute-Nodes`), `data "aws_ami_ids" "node_image"` (owner `self`, name prefix the deployment's image name), and `output "cluster_description"` (research R6); `just test` and `just full-test`: T022 passes
  - Done 2026-11-23: `csis-sandbox-terraform` `0d3911c`: `node_table_name` (default `IOOS-Sandbox-Compute-Nodes`), `data "aws_ami_ids" "node_image"` (owner `self`, the deployment's image name), `output "cluster_description"`, with the head node's three security groups (as `current.system` had; research R6 named two) and `key_name` (Terraform knows it; beyond the plan's list). `just test` 32, `just full-test` 3 slow passed.
- [X] T027 [US2] In `exportit/sandbox-terraform/DEPLOYMENT.md`, how to read `cluster_description` (`tofu output -json cluster_description`), and that `image_id` fills after `node-image.yml` and `tofu apply -refresh-only`
  - Done 2026-11-23: `DEPLOYMENT.md`: `tofu output -json cluster_description`, its keys, `image_id` filled by `apply -refresh-only` after the image.
- [X] T028 [US2] In `exportit/sandbox-configs`, retire `cluster.configs/IOOS/current.system` and `current.image_id` to `attic/`, `retired: replaced by csis-sandbox-terraform's output cluster_description`; `just test`
  - Done 2026-11-23: `csis-sandbox-configs` `4a9b4c8`: `current.system` and `current.image_id` under `attic/`, the reason naming the output; every description left is one cloudflow reads (66 site, all `ok`).
- [X] T029 [US2] Run the root `just test`: T021 and T023 pass
  - Done 2026-11-23: the root `just test` passed within T034's run.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T030 [P] In `exportit/MAP.md`, the `sandbox-configs` and cloudflow sections: what moved, what stayed, what was repaired and retired (counts), where the schema lives
  - Done 2026-11-23: `exportit/MAP.md`: `sandbox-configs` (the split, the counts, the schema's place) and cloudflow (what it holds and publishes).
- [X] T031 [P] In `exportit/sandbox-configs/README.md` and cloudflow's `README.md`, where the examples and the schema are now
  - Done 2026-11-23: `csis-sandbox-configs` `79a0437` and cloudflow `c5e4344`: each README says where the examples and the schema are.
- [X] T032 [P] In `specs/README.md`, set 005's state
  - Done 2026-11-23: `specs/README.md`, 005 **in progress** (implemented, not yet merged).
- [X] T033 Commit each unit's last changes; record the three submodules here; `just constitution-check`
  - Done 2026-11-23: the three units' commits recorded here (`b3ccbbd`); `just constitution-check` ran within the root `just test`.
- [X] T034 Run the root `just test`
  - Done 2026-11-23: the root `just test` passed, 16 targets, `configs-schema-check` among them.
- [X] T035 Run the root `just full-test`
  - Done 2026-11-23: the root `just full-test` passed, 16 targets: lineage of every unit, `csis-sandbox-configs` and cloudflow among them; the sync rehearsal 9 of 9; the copies cloudflow's (SC-002).
- [X] T036 [P] In `specs/005-configs-split-by-owner/spec.md`, an **Outcome** section: the counts (moved 51, repaired, retired, kept 71 less the retired), and SC-001's evidence
  - Done 2026-11-23: the spec's **Outcome** section: the counts, the search, the schema's place, the output's extra keys, SC-001.
- [X] T037 [P] Close or add `exportit/REMINDERS.md` items this spec touches (the link of spec 006 if the job descriptions were changed here; none otherwise)
  - Done 2026-11-23: `exportit/REMINDERS.md`: "`sandbox-configs` moved whole" closed (the split is done); spec 006's link reminder stays (the job descriptions still name the old path; this spec changed none of them).
- [X] T038 Re-read [quickstart.md](quickstart.md) against what was run; correct it if a step differed
  - Done 2026-11-23: [quickstart.md](quickstart.md) re-read against what was run: its commands are the ones run; nothing to correct.
- [X] T039 Check that nothing in any unit or the workshop still reads `exportit/tools/configs_schema.py` (`git grep`); record the result
  - Done 2026-11-23: `git grep configs_schema` across the workshop and every unit: only cloudflow's own `tools/` and tests, the records that describe the move, and `MOVINGDAY.md`'s history; the schema's about line, `sandbox-configs.map`'s comment and the tools' type-check list, which still named the old place, were corrected (cloudflow `1d25070`, `0c88b56`; `csis-sandbox-configs` `52b11fb`).
- [X] T040 Run `/speckit-converge` on `specs/005-configs-split-by-owner/`; record that it appended nothing, or carry out what it appended (done condition 2)
  - Done 2026-11-23: `/speckit-converge` appended nothing: converged. Two differences from the design documents, neither actionable and both recorded: the data model says every status in cloudflow's catalogue is `ok`, and one is the new-model template (the operator's answer of 2026-11-23, in the spec); the output carries three security groups and `key_name` where research R6 listed fewer (what `current.system` held, and what a description needs; T026).
- [X] T041 Walk `specs/005-configs-split-by-owner/quickstart.md`, recording each command and result (done condition 3)
  - Done 2026-11-23, each command and result: `just test` in `exportit/sandbox-configs`: 89 passed (every file as catalogued; retired only under `attic/`); in `exportit/cloudflow`: 210 passed (the schema equals the code; the 51 read by it); in `exportit/sandbox-terraform`: 32 passed (the output's keys, the fixture); the root `just test`: passed (`configs-schema-check`, the tools tests across units); the root `just full-test`: passed (lineage of both units; the rehearsal with a moved description).
- [X] T042 On the operator's word only: finish the three units' branches and push, record their commits, then squash Cloud-Sandbox's branch into `develop` and push, with `just submodules-pushed` first (done condition 4)
  - Done 2026-11-23, on the operator's word ("merge and push 005 when the full test passes"), the root `just test` and `just full-test` having passed (16 targets each; the rehearsal 9 of 9): each unit's branch squashed into its `develop` and pushed, the branch kept and pushed: `csis-sandbox-configs` `023e44b`, cloudflow `7bb64ad`, `csis-sandbox-terraform` `50f6b0f`, recorded here; then this branch squashed into Cloud-Sandbox's `develop` from its tree and pushed, with `just submodules-pushed` first.
- [X] T043 Record that no release applies, unless the operator asks for one (done condition 5)
  - Done 2026-11-23: no release applies: the plan names none; each unit's `release` target says nothing is released from it; `exportit/REMINDERS.md` keeps "Releasing from a unit's own repository" open.
- [X] T044 Mark the spec **complete**, with the date, only when T001 to T043 are checked (done conditions 1 and 6)
  - Done 2026-11-23: T001 to T043 checked, each with its record; the spec marked **complete** in its Status line and in `specs/README.md`.

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

---

## Phase 6: Convergence

- [X] T045 In `exportit/cloud-sandbox/CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`, steps 3 and 4 tell a reader to copy `cloud_sandbox_experiment.template` from `Cloud-Sandbox/job.configs` and `template.ioos` from `Cloud-Sandbox/cluster.configs`; both are cloudflow's now, in `examples/configs/job.configs/` and `examples/configs/cluster.configs/`, and the new model's description belongs in the site's own repository (`csis-sandbox-configs`): say so, committed in `csis-cloud-sandbox` on a `feature/configs-split-by-owner` branch and recorded here, per US1/AC2 (contradicts)
  - Done 2026-11-23: `csis-cloud-sandbox` `4bea4ed`, on `feature/configs-split-by-owner` from its `develop` (clean, level with origin): steps 3 and 4 name cloudflow's `examples/configs/job.configs/cloud_sandbox_experiment.template` and `examples/configs/cluster.configs/template.ioos`, and say a site's own descriptions go with its others (`csis-sandbox-configs` for the IOOS deployment). Its step 2 still clones `ioos/Cloud-Sandbox`, outside this task and this spec; left as it is. The unit's `just test` passed.
- [X] T046 In `exportit/model-nosofs/NOSOFS-MODELS.md`, the examples it names (`./Cloud-Sandbox/job.configs/cbofs.00z.fcst`, `cbofs.00z.plots`, and `cluster.configs/ioos.config`, `post.config`) are at paths that no longer exist: point them at cloudflow's `examples/configs/` for the examples (`job.configs/OFS/cbofs.00z.plots` among them) and at `csis-sandbox-configs` for the site's descriptions, committed in `csis-model-nosofs` on a `feature/configs-split-by-owner` branch and recorded here, per US1 (partial)
  - Done 2026-11-23: `csis-model-nosofs` `f6dc025`, likewise branched: the four paths name `csis-sandbox-configs`' `cluster.configs/IOOS/ioos.nosofs.cfg` (the guide's `ioos.config` exists nowhere), its `cluster.configs/post.config` and `job.configs/OFS/cbofs.fcst` (its `cbofs.00z.fcst` exists nowhere), and cloudflow's `examples/configs/job.configs/OFS/cbofs.00z.plots`. The unit's `just test` passed. With T045 and T046 done, every task is checked again, so T044's completion holds.

---

## Phase 7: Convergence

- [X] T047 In `exportit/cloudflow/docs/CLOUDFLOW_MODEL_EXECUTION_INSTRUCTIONS.md` and `docs/CLOUDFLOW_PYTHON_MODEL_EXECUTION_INSTRUCTIONS.md`, the pre-configured job descriptions are said to "reside in `Cloud-Sandbox/cloudflow/job.configs/MODEL_EXPERIMENTS/`" and are edited as `../job.configs/MODEL_EXPERIMENTS/…`; they are cloudflow's own now, in `examples/configs/job.configs/MODEL_EXPERIMENTS/`, while the cluster descriptions the guides name (`cluster.configs/Experiments/…`) stayed with the site (`csis-sandbox-configs`): say where each is, committed in cloudflow on a `feature/configs-split-by-owner` branch and recorded here, per US1 (partial)
  - Done 2026-11-23: cloudflow `f303150`, on its kept `feature/configs-split-by-owner` (the same tree as its `develop`): a note in each run guide that the `MODEL_EXPERIMENTS` job descriptions are cloudflow's `examples/configs/job.configs/MODEL_EXPERIMENTS/`, the `Experiments` cluster descriptions the IOOS site's in `csis-sandbox-configs`, and that the commands' `../job.configs` paths are the old checkout's, to be settled when spec 008 puts the site's descriptions on the node. The commands themselves are left for spec 008 (its FR-006). The unit's `just test`: 210 passed. With it every task is checked again.
