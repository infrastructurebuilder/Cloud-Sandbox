# Implementation Plan: The first boot runs the playbooks

**Branch**: `feature/first-boot-runs-playbooks`, in Cloud-Sandbox and in
`csis-sandbox-terraform` | **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-first-boot-runs-playbooks/spec.md`

## Summary

`main.tf` stops rendering the old first-boot script and renders
`init_template.ansible.tpl`, passing four new values: where the playbooks and
cloudflow are, and at which tag. The first boot then clones both from their
own public repositories with no credential, applies the playbooks, installs
cloudflow for the login user, and makes the image; nothing of the original
`ioos/Cloud-Sandbox` is cloned any longer. A link at the old checkout's path
keeps the site's job descriptions working. Everything is proved without AWS:
the template rendered, and a plan of the module with mocked providers.

## Technical Context

**Language/Version**: HCL for OpenTofu 1.13.9 (the module); Bash (the
template); Python 3.12 (the unit's tests)

**Primary Dependencies**: the module's providers as they are (`hashicorp/aws
~> 3.47`, `random`, `local`), unchanged; pytest, ruff and pyright through the
unit's `uv` environment

**Storage**: N/A (the template writes to the node's EFS volume and log)

**Testing**: pytest through the unit's `just test` (`test_template.py`) and
`just full-test` (the plan without a value); `tofu test` with mocked
providers (research R4)

**Target Platform**: a RHEL 10 head node's first boot (put to use by spec
001); the local machine for every test

**Project Type**: an OpenTofu module and its first-boot template, in one unit

**Performance Goals**: N/A

**Constraints**: no AWS call in any test; no credential anywhere (FR-003); no
repository of the original cloned (FR-002); the module's providers unchanged

**Scale/Scope**: one unit, `csis-sandbox-terraform` (`main.tf`,
`variables.tf`, the template, its tests, `DEPLOYMENT.md`, the Justfile); in
Cloud-Sandbox, `exportit/REMINDERS.md` and `specs/README.md`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | The change is made in `csis-sandbox-terraform`'s own repository on the same branch, merged and pushed there first, then recorded here; no file moves between units; the job descriptions and cloudflow's scripts are left to their owners (research R3) | Pass |
| II. The original reaches the units only by sync | `init_template.tpl`, a copy of the original's, stays unchanged so a sync still lands on it (research R5); the unit is `owned`, so its edited files are its own | Pass |
| III. Work that spans units is planned here | This spec; its tasks name the repository each lands in, the unit first | Pass |
| IV. Acceptance tests run through the Justfile | The new tests run behind the unit's `just test` and `just full-test`, then the root's; the rendering a person reads is a Justfile target (`render-first-boot`) | Pass |
| V. The operator decides | Two questions asked and recorded; cloudflow's repository made public on the operator's word (2026-11-21), its history checked first; nothing applied to AWS; merges and pushes on the operator's word | Pass |
| VI. Nothing toward `ioos` | The first boot stops cloning from it; no remote or push toward it | Pass |
| The ATTIC | Not consulted; stage 21 was carried into the spec on 2026-11-19 | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/006-first-boot-runs-playbooks/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R6
├── data-model.md        # the variables, and what the boot makes on the node
├── quickstart.md
├── contracts/
│   └── first-boot.md    # the template's inputs and order
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/              # csis-sandbox-terraform
├── main.tf                              # local.user_data renders init_template.ansible.tpl with the four values
├── variables.tf                         # + provisioning_repo, provisioning_version, cloudflow_repo, cloudflow_version; - sandbox_version
├── init_template.ansible.tpl            # cloudflow from its own repository; the link; the install; the header
├── init_template.tpl                    # unchanged (research R5)
├── Justfile                             # + render-first-boot
├── DEPLOYMENT.md                        # the four values, and which tags to use (FR-005)
└── tests/
    ├── support.py                       # template_variables() reads local.user_data
    ├── test_template.py                 # the main module's template, its placeholders, the order
    ├── test_plan.py                     # slow: a plan without provisioning_repo fails, naming it
    └── firstboot.tftest.hcl             # tofu test, mocked providers: the planned user data

Cloud-Sandbox (the workshop)
├── exportit/REMINDERS.md                # + remove the compatibility link when nothing needs it
└── specs/README.md                      # 006's state
```

**Structure Decision**: the whole change is inside the unit; the workshop only
records it. `tests/` is declared `new` in `sandbox-terraform.map`, so the new
test files need no mapping change.

## Order of the work, and of the merges

1. **csis-sandbox-terraform:** the variables, `local.user_data`, the
   template's cloudflow steps, the tests (failing first, then passing), the
   Justfile target, `DEPLOYMENT.md`; its `just test` and `just full-test`.
2. **Cloud-Sandbox:** the reminder, the spec's state, the submodule's new
   commit; the root's `just test` and `just full-test`.
3. **Merged and pushed** on the operator's word: the unit first, then
   Cloud-Sandbox.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| A compatibility link at the old checkout's path | 20-odd job descriptions and several cloudflow scripts name `/save/ec2-user/Cloud-Sandbox/cloudflow/…` (research R3) | editing them is three more units' work, and the job descriptions are spec 005's |

## For the operator

- Cloudflow's repository was made public on 2026-11-21, so FR-002's "before
  that" step is done.
- All four new values are required (research R1); `DEPLOYMENT.md` will name
  today's tags, `csis-sandbox-provisioning` `0.0.1` and cloudflow `1.6.0b0`.
