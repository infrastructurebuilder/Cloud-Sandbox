# Implementation Plan: sandbox-configs split by owner

**Branch**: `feature/configs-split-by-owner`, in Cloud-Sandbox,
`csis-sandbox-configs`, cloudflow and `csis-sandbox-terraform` | **Date**:
2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-configs-split-by-owner/spec.md`

## Summary

First, in `csis-sandbox-configs`, the 23 descriptions cloudflow cannot read
are repaired where a sibling gives the missing value, or retired to a new
`attic/` with the reason. Then the 51 templates and examples move to
cloudflow's `examples/configs/` with spec 003's `moved` directive, so both
units keep their lineage and a later sync lands in cloudflow. The schema
writer moves with them, so the schema lives beside the code that reads the
descriptions; the configs unit keeps a copy, written and checked by the
workshop. A Terraform output with a cluster-description fragment replaces the
two hand-kept `current.*` files.

## Technical Context

**Language/Version**: Python 3.12 (the schema writer, the tests, the tools);
JSON (the descriptions); HCL for OpenTofu 1.13.9 (the output)

**Primary Dependencies**: spec 003's `moved` directive in
`exportit/tools/export.py`; the units' `uv` environments

**Storage**: N/A

**Testing**: each unit's pytest; `tofu test` for the output; the workshop's
tools tests and `just full-test` (lineage, the sync rehearsal)

**Target Platform**: the local machine; nothing runs on AWS

**Project Type**: data files moved between two repositories, a tool moved,
an output added, the records

**Performance Goals**: N/A

**Constraints**: nothing moves until every file that moves is readable;
lineage of both units unchanged; nothing in the public cloudflow that the
search of R4 has not cleared

**Scale/Scope**: 51 files moved, 23 repaired or retired, one tool moved, one
output; four repositories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Each file has one owner after the split (R1); the schema lives in cloudflow and is copied, written and checked, into the configs unit (R5); each unit changed in its own repository first | Pass |
| II. The original reaches the units only by sync | `moved` keeps both maps' `copy` rules, so lineage holds; a later change to a moved file syncs into cloudflow (spec 003) | Pass |
| III. Work that spans units is planned here | This spec, four repositories | Pass |
| IV. Acceptance tests run through the Justfile | Every check behind a unit's or the root's `just test`; lineage and the rehearsal in `just full-test`; `just configs-schema-check` new | Pass |
| V. The operator decides | Four questions asked and recorded; a file with no evidence for its repair is retired, not guessed | Pass |
| VI. Nothing toward `ioos` | None | Pass |
| The ATTIC | Not consulted (the configs unit's new `attic/` is its own) | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/005-configs-split-by-owner/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R7
├── data-model.md
├── quickstart.md
├── contracts/
│   └── schema-and-move.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-configs/                # csis-sandbox-configs
├── job.configs/, cluster.configs/       # repairs first (R2); then the 51 leave
├── attic/                               # retired files, with their paths
├── schema/                              # the copy of cloudflow's (R5)
└── tests/catalogue.json, tests/test_descriptions.py   # retired: <reason>, only under attic/

exportit/cloudflow/                      # cloudflow
├── examples/configs/{job.configs,cluster.configs}/    # the 51 (R3)
├── examples/configs/catalogue.json
├── schema/jobs.json, schema/clusters.json
├── tools/configs_schema.py              # moved from the workshop
└── tests/test_configs_schema.py, tests/test_examples.py

exportit/sandbox-terraform/              # csis-sandbox-terraform
├── outputs.tf                           # + cluster_description (R6)
├── main.tf, variables.tf                # + data "aws_ami_ids"; + node_table_name
└── tests/cluster_description.tftest.hcl # the keys; writes the fixture

Cloud-Sandbox (the workshop)
├── exportit/sandbox-configs.map         # + 51 moved lines; + new attic/
├── exportit/cloudflow.map               # + new schema/, new tools/configs_schema.py (if not under a new rule)
├── exportit/tools/configs_schema.py     # removed (moved to cloudflow)
├── exportit/tools/tests/                # the fixture against the schema; moved lines against the catalogue
├── Justfile                             # configs-schema copies; + configs-schema-check in test
├── exportit/MAP.md                      # the sandbox-configs section
└── specs/README.md                      # 005's state
```

**Structure Decision**: the examples and the schema with the code that reads
them; the site's files where the site keeps them; one copy of the schema,
checked, where the site's files need it.

## Order of the work, and of the merges

1. **csis-sandbox-configs:** the 23, repaired or retired (R2), with the
   catalogue and its test. Merged and pushed on the operator's word.
2. **Cloud-Sandbox, needs spec 003 merged:** the 51 `moved` lines, generated
   and reviewed.
3. **cloudflow:** R4's search; the 51 files; the schema writer, the schema,
   the tests.
4. **csis-sandbox-configs:** the 51 removed; `schema/` now the copy;
   `current.*` retired.
5. **csis-sandbox-terraform:** the output and its test.
6. **Cloud-Sandbox:** the maps, the Justfile, the tools tests, `MAP.md`; the
   root's `just test` and `just full-test` (lineage, the rehearsal).
7. **Merged and pushed** on the operator's word, the units first.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| A copy of the schema in the configs unit, written and checked by the workshop | the site's files are checked against cloudflow's schema without the configs unit depending on a cloudflow release | a dependency on cloudflow at a tag would hold every schema change until a tag |

## For the operator

- The move puts the 51 files into cloudflow, which is now public. They came
  from the public original, and research R4 searches them before they go in.
- `current.image_id` held an image ID by hand; the new output reads the
  deployment's image by its name, and is empty until `node-image.yml` has made
  one (research R6).
