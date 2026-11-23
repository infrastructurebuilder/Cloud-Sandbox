# Implementation Plan: The Lambda functions, owned and deployable

**Branch**: `feature/lambda-functions-owner`, in Cloud-Sandbox and in each unit it touches | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-lambda-functions-owner/spec.md`

## Summary

The two zombie-node Lambda functions leave cloudflow's package for
`csis-sandbox-terraform`, where a new root module, `reaper/`, packages them,
schedules them and gives each a role allowed exactly what it calls; nothing is
applied to any account. The terminating role may stop only nodes carrying a
tag that cloudflow now adds to every node it launches, and the report's bucket
becomes a setting. The files move by a new mapping directive, `moved`, which
the export tool learns so that both units keep their lineage and a later sync
carries the original's changes to the functions into their new home.

## Technical Context

**Language/Version**: Python 3.12 (the export tool, cloudflow, the units'
tests); Python 3.13 (the Lambda runtime); OpenTofu 1.13.9 (HCL)

**Primary Dependencies**: `hashicorp/aws ~> 6.0` and `hashicorp/archive ~> 2.0`
for `reaper/` only (research R1); `boto3`/`botocore` (the functions, and
`botocore`'s Stubber in their tests); `git-filter-repo` (the export tool)

**Storage**: the DynamoDB table cloudflow writes (read and pruned by the
functions, unchanged); the report in S3

**Testing**: pytest through each repository's `just test`; `tofu test` with
mocked providers for `reaper/` (research R2); the export tool's tests on
throw-away repositories; the sync rehearsal in Cloud-Sandbox's `just full-test`

**Target Platform**: AWS Lambda (when the operator applies it, later); the
local machine for every test

**Project Type**: an OpenTofu module and two functions in one unit, a small
change in another, and a tool change in the workshop

**Performance Goals**: N/A

**Constraints**: nothing created in any AWS account (FR-003); the unit's main
module and its provider unchanged (research R1); both units' lineage unchanged
(FR-010); no secret or account number in any repository

**Scale/Scope**: three repositories: `csis-sandbox-terraform` (the functions,
their tests, `reaper/`), cloudflow (the functions leave; the tag), Cloud-Sandbox
(`moved` in `export.py`, the maps, a check between units, the records)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Each unit changes in its own repository on `feature/lambda-functions-owner`, merged and pushed there first; the files move by a spec that says how their mapping lines, history and lineage are kept (`moved`); only `csis-sandbox-terraform` needs them, so they move rather than going to a common place | Pass |
| II. The original reaches the units only by sync | `moved` keeps both units' `copy` rules, so lineage holds; a sync carries the original's changes to the functions to their new home, and does not bring them back into cloudflow; the rehearsal gains a scenario for it | Pass |
| III. Work that spans units is planned here | This spec is in Cloud-Sandbox; its tasks say which repository each lands in, units first | Pass |
| IV. Acceptance tests run through the Justfile | Each unit's `just test` and `just full-test`, then the root's; the new `tofu test` runs go behind the unit's `just test`; the tool's tests use throw-away repositories | Pass |
| V. The operator decides | Five questions asked and recorded; nothing applied to AWS; commits local, merged and pushed only on the operator's word; no secret or account number in the module | Pass |
| VI. Nothing toward `ioos` | No remote, push or pull request toward it | Pass |
| The ATTIC | Not consulted; stage 17 was carried into the spec on 2026-11-19 | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/003-lambda-functions-owner/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R8
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── moved-directive.md
│   └── reaper-module.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/          # csis-sandbox-terraform
├── reaper/                          # new root module (research R1)
│   ├── versions.tofu                # OpenTofu 1.13.9; aws ~> 6.0, archive ~> 2.0
│   ├── main.tf                      # functions, packaging, schedule, roles (contracts/reaper-module.md)
│   ├── variables.tf
│   ├── outputs.tf
│   ├── functions/                   # moved from cloudflow (contracts/moved-directive.md)
│   │   ├── lambda_identify_zombies.py   # reads REPORT_BUCKET (FR-009)
│   │   ├── lambda_terminate_zombies.py
│   │   └── lambda.env               # gains REPORT_BUCKET
│   └── tests/
│       └── reaper.tftest.hcl        # mocked providers; enable_reaper false and true
├── tests/
│   ├── support.py                   # MODULES gains "reaper"
│   ├── test_reaper_functions.py     # Stubber: the four cases of User Story 1, the report's bucket
│   └── test_reaper_module.py        # runs `tofu test` in reaper/; validate
└── DEPLOYMENT.md                    # how the guard is switched on

exportit/cloudflow/                  # cloudflow
├── src/cloudflow/cluster/
│   ├── AWSCluster.py                # adds the launch tag (FR-008)
│   └── (the two functions and lambda.env, deleted)
└── tests/
    ├── test_modules.py              # loses the two skipped modules (FR-006)
    └── test_launch_tag.py           # a launch request carries the tag

Cloud-Sandbox (the workshop)
├── exportit/tools/export.py         # the `moved` directive (FR-010)
├── exportit/tools/tests/test_moved.py
├── exportit/tools/tests/test_umbrella.py   # the tag: cloudflow's constant = the module's default
├── exportit/tools/rehearse_sync.py  # a scenario: a change to a moved file
├── exportit/cloudflow.map           # three `moved` lines
├── exportit/sandbox-terraform.map   # `new reaper/`
├── exportit/MAP.md, exportit/REMINDERS.md   # FR-007
└── specs/README.md                  # 003's state
```

**Structure Decision**: the functions sit beside the module that packages them,
in a root module of its own, because the main module's provider is too old for
any runtime AWS still supports, and changing it is not this spec's.

## Order of the work, and of the merges

1. **Cloud-Sandbox, the tool first:** `moved` in `export.py`, with its tests,
   and the rehearsal's new scenario, written so that it runs before any map
   uses the directive (on throw-away repositories).
2. **cloudflow:** the tag in `AWSCluster`, with its test; the two functions and
   `lambda.env` deleted; the import test updated.
3. **csis-sandbox-terraform:** the functions under `reaper/functions/`, their
   `REPORT_BUCKET` change, their tests, the `reaper/` module and its `tofu
   test`, `MODULES`, `DEPLOYMENT.md`.
4. **Cloud-Sandbox, the maps and records:** `cloudflow.map`'s `moved` lines,
   `sandbox-terraform.map`'s `new reaper/`, the check between units for the
   tag, MAP.md, REMINDERS.md (the item closes), `specs/README.md`; the
   submodules record both units' branches.
5. **Acceptance:** each unit's `just test` and `just full-test`, then the root's
   `just test` and `just full-test`. Merged and pushed on the operator's word:
   cloudflow and `csis-sandbox-terraform` first, then Cloud-Sandbox.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| A second provider version in one unit (`reaper/` on `aws ~> 6.0`, the main module on `~> 3.47`) | `~> 3.47` cannot create a Lambda on a supported Python (research R1) | raising the main module three major versions is a change of its own, to a module not yet applied once (spec 001) |

## For the operator

Research R5 records a finding that bears on the fourth clarification:
cloudflow already adds a tag of its own to every node, `ApprovedSubnet =
<the cluster's subnet>`, which the role could require instead, with no
cloudflow change and covering nodes started before this spec. The answer
given stands; the plan uses `csis:launched-by = cloudflow` unless you say
otherwise.
