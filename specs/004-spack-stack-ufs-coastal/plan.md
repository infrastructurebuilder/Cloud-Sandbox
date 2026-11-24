# Implementation Plan: spack-stack for UFS Coastal

**Branch**: `feature/spack-stack-ufs-coastal`, in Cloud-Sandbox,
`csis-sandbox-provisioning`, `csis-model-ufscoastal` and `csis-sandbox-ops`
| **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-spack-stack-ufs-coastal/spec.md`

## Summary

A playbook, `ufs-stack.yml`, replaces the broken `add-ufs-setup.sh`: it clones
a JCSDA spack-stack release (2.1.x if it concretizes on RHEL 10, else 2.0.0,
else the fork at a commit the operator names), creates the `unified-dev`
environment for oneAPI, writes its externals and settings only into its own
scopes, installs it, and sets up the meta-modules, all through the
collection's `setup` role and `spack_env`. UFS Coastal's own files are
brought to the new environment so its build finds what it needs. Proved by
concretizing in the container and building on a head node of its own.

## Technical Context

**Language/Version**: YAML (Ansible); Bash (`setup.sh`); Tcl and Lua (module
files); Python 3.12 (tests)

**Primary Dependencies**: JCSDA spack-stack 2.x (its own Spack, 1.0-based);
the collection `infrastructurebuilder.csis_spack` (`setup` role, `spack_env`);
oneAPI from the `intel_oneapi` role; RHEL 10's GCC 14

**Storage**: the EFS volume, `/save/environments/`

**Testing**: Ansible syntax and lint, and the steps' `replaces:` lines, in
`just test`; the container concretization in `just full-test`; the build on a
head node

**Target Platform**: a RHEL 10 head node built as spec 001 builds one

**Project Type**: a playbook, a model unit's build files, records

**Performance Goals**: N/A (a full build is hours; no cache for spack-stack)

**Constraints**: nothing in `/etc/spack` (FR-004); no GCC toolset (FR-002); a
tag or a named commit, never a branch (FR-001); the node removed at the end
(FR-007)

**Scale/Scope**: four repositories; one head node of several hours

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Each unit changed in its own repository first; the two UFS scripts stay in `csis-sandbox-ops`, marked, so no file moves | Pass |
| II. The original reaches the units only by sync | The scripts' mapping lines stay; `csis-model-ufscoastal` is owned, its changes its own | Pass |
| III. Work that spans units is planned here | This spec | Pass |
| IV. Acceptance tests run through the Justfile | Each check behind a unit's `just test` or `just full-test` | Pass |
| V. The operator decides | Five questions asked and recorded; the fork's commit, if needed, is the operator's; the node on the operator's word | Pass |
| VI. Nothing toward `ioos` | None | Pass |
| The ATTIC | Not consulted | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/004-spack-stack-ufs-coastal/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R9
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ufs-stack-playbook.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-provisioning/           # csis-sandbox-provisioning
├── ufs-stack.yml                        # the playbook (contracts/ufs-stack-playbook.md)
├── group_vars/ufs_stack.yml             # or the playbook's vars: the variables of data-model.md
├── tests/test_ufs_stack.py              # each step names a legacy line; no system scope; the ref is not a branch
└── tests/container/converge.sh          # + concretize ufs-stack.yml (ufs_stack_install: false)

exportit/model-ufscoastal/               # csis-model-ufscoastal
├── README                               # FR-006
├── setup.sh                             # the new setup.sh; no toolset (research R5)
└── modulefiles/{tcl,lua}/ufs_ioossb.intel.*   # the new environment's path and versions (research R7)

exportit/sandbox-ops/                    # csis-sandbox-ops
├── bin/add-ufs-setup.sh, bin/ufs-envars.sh   # a header line naming the replacement
└── CATALOGUE.tsv                        # superseded_by filled

Cloud-Sandbox (the workshop)
└── specs/README.md                      # 004's state
```

**Structure Decision**: the playbook beside `site.yml`, whose environment it
sits beside; UFS Coastal's files in their own unit.

## Order of the work, and of the merges

1. **No AWS:** R1's checks (the release named by UFS Coastal's tag, the
   release notes), recorded; the playbook and its tests; the container
   concretization (which settles 2.1.x or 2.0.0, or sends the choice to the
   operator); `csis-model-ufscoastal`'s files at the chosen release's
   versions, as far as they can be read before a build; the catalogue. Each
   unit's acceptance tests, then the root's. Needs spec 001 merged and spec
   002's catalogue rule (`superseded_by`).
2. **On AWS**, on the operator's word: a head node, the playbook twice, the
   checks, UFS Coastal's configure, the module file's versions corrected from
   the real `module avail` if they differ; removal.
3. **Merged and pushed** on the operator's word: the units first.

## Complexity Tracking

No violation to justify.

## For the operator

- **Finding** (research R5): `csis-model-ufscoastal`'s `setup.sh` loads
  `gcc-toolset-13` because `ar` segfaulted on RHEL 8; RHEL 10 has no such
  toolset, and your answer was no toolset. The line goes; a recurrence is a
  finding.
- **Scope** (research R7): SC-003 needs `setup.sh` and the module files of
  `csis-model-ufscoastal` brought to the new environment, beyond FR-006's
  README. They are that unit's own files.
- If neither 2.1.x nor 2.0.0 concretizes on RHEL 10, the work stops for you to
  name a commit of the fork (FR-001).
