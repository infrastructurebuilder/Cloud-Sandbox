# Implementation Plan: The live proof on AWS

**Branch**: `feature/live-proof`, in Cloud-Sandbox, `csis-sandbox-terraform`
and `csis-sandbox-provisioning` | **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-live-proof-on-aws/spec.md`

## Summary

A head node is built on AWS, in the `noaa` account's existing IOOS VPC, by
spec 006's real first boot, with two changes made by override files of the
proof's own: the SSM agent first, and the image left for the operator's
word. The agent then runs the rest by hand over Session Manager: a second
apply, check mode, the Spack and module-file comparisons, JupyterHub, the
image, and the removal of everything, each AWS step asked first. The
procedure (`LIVE-PROOF.md` v2) and the override files are written and tested
on your local machine first; the run's results settle the "Not proved" table.

## Technical Context

**Language/Version**: HCL for OpenTofu 1.13.9 (the module and `proof/`);
Bash (the boot, the procedure's boxes); YAML (the plays, unchanged); Python
3.12 (tests)

**Primary Dependencies**: `csis-sandbox-terraform` at its tag, with spec
006 merged; `csis-sandbox-provisioning` and cloudflow at their tags, public;
the collection `infrastructurebuilder.csis_spack` from Galaxy; on your local
machine the AWS CLI and the Session Manager plugin

**Storage**: local OpenTofu state in the working copy; the logs on your local
machine (not committed, FR-006)

**Testing**: `tofu test` with mocked providers for `proof/`; a check of
`LIVE-PROOF.md`'s box form in `csis-sandbox-provisioning`'s tests; the run
itself is the proof

**Target Platform**: AWS, `noaa` account, us-east-2; a RHEL 10 head node of
32 processors

**Project Type**: a procedure, the override files it uses, and one real run

**Performance Goals**: the build in as few hours as 31 jobs allow (FR-009)

**Constraints**: nothing existing in us-east-2 changed (FR-005, FR-008); no
inbound rule, nothing added to the bastion (FR-017); every AWS change on the
operator's word; logs and identifiers never committed; the unit's `main.tf`
not edited (Out of Scope)

**Scale/Scope**: `csis-sandbox-terraform` (`proof/`, its tests),
`csis-sandbox-provisioning` (`docs/LIVE-PROOF.md` v2, a test of its form),
Cloud-Sandbox (`exportit/MAP.md`'s table, `exportit/REMINDERS.md`, the spec's
outcome, `specs/README.md`); one run of several hours

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | `proof/` in `csis-sandbox-terraform` and the page in `csis-sandbox-provisioning`, each merged and pushed in its own repository first; the override files live once, beside the module they override (research R1) | Pass |
| II. The original reaches the units only by sync | The comparison node reads the original at `ca0604a` from GitHub at boot, only when the flag is `true`; nothing of the original enters a unit | Pass |
| III. Work that spans units is planned here | This spec, its tasks naming each repository | Pass |
| IV. Acceptance tests run through the Justfile | `proof/`'s `tofu test` behind the unit's `just test`; the page's form behind `csis-sandbox-provisioning`'s; the run is a procedure, not a target, because it needs an account and the operator's word | Pass |
| V. The operator decides | Every apply, image, destroy and removal asked first; the subnet a decision box; the session checked first and refreshed only by the operator | Pass |
| VI. Nothing toward `ioos` | Read-only clone of the original by the comparison node, only with the flag; nothing pushed | Pass |
| The ATTIC | Not consulted; stage 15 carried into the spec on 2026-11-19 | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/001-live-proof-on-aws/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R10
├── data-model.md        # the settings, what is created, the findings
├── quickstart.md
├── contracts/
│   └── live-proof-procedure.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/              # csis-sandbox-terraform
└── proof/                               # copied into the working copy by box A2 (research R1)
    ├── backend_override.tf              # local state (R2)
    ├── proof_override.tf                # local.user_data: SSM agent + the unit's boot, cut before the image, with the site mirror (R3, R9); the interface's groups (R5)
    ├── proof.tf                         # compare_with_script and the -script node (R7)
    ├── proof.tfvars.example             # every setting of data-model.md, VPC and subnet blank
    ├── ssm-agent.sh                     # install and start the agent if absent (R4)
    └── tests/proof.tftest.hcl           # mocked: the boot's changes, the flag both ways, no ingress
exportit/sandbox-terraform/tests/support.py   # proof/ listed among the directories tofu tests

exportit/sandbox-provisioning/           # csis-sandbox-provisioning
├── docs/LIVE-PROOF.md                   # version 2 (contracts/live-proof-procedure.md)
└── tests/test_live_proof_form.py        # every box numbered, versioned, placed; checks last; decisions bold

Cloud-Sandbox (the workshop)
├── exportit/sandbox-terraform.map       # + new proof/
├── exportit/MAP.md                      # the "Not proved" rows, settled (SC-003)
├── exportit/REMINDERS.md                # + the deferred comparison (FR-018)
├── specs/001-live-proof-on-aws/spec.md  # its outcome: the findings' summary
└── specs/README.md                      # 001's state
```

**Structure Decision**: the proof's files sit with what they act on: the
OpenTofu overrides in the OpenTofu unit, the procedure with the playbooks it
proves (FR-002). The run's results come home to the workshop.

## Order of the work, and of the merges

1. **Written and tested, no AWS:** `proof/` and its `tofu test`
   (csis-sandbox-terraform); `LIVE-PROOF.md` v2 and its form test
   (csis-sandbox-provisioning); `REMINDERS.md` (Cloud-Sandbox). Each unit's
   and the root's acceptance tests. Merged and pushed on the operator's word.
   Needs spec 006 merged first.
2. **The run**, on the operator's word and a fresh `noaa` session: stages A
   to E, the agent running each box and stopping at every gate.
3. **The results:** the findings in the spec's outcome, `MAP.md`'s table,
   `specs/README.md`; findings that need fixing become specs of their own.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| Override files that cut and edit the rendered boot | the real first boot with exactly two changes (FR-010) | a variable in the unit's template is a change to spec 006 for the proof's sake |
| A second instance behind a flag | FR-013, off by default | a separate procedure for stage D would duplicate stage A |

## For the operator

- The run is several hours of a 32-processor node (about $1.36 an hour for a
  `c6i.8xlarge`), plus EFS and the image while they stand; stage E removes
  them.
- The subnet is your decision in box A3; the default is the private subnet in
  the module's availability zone.
