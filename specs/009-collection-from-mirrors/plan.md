# Implementation Plan: The playbooks take the collection's 0.0.3 and its `from_mirrors` again

**Branch**: `feature/collection-from-mirrors` in `csis-sandbox-provisioning`;
this plan on `feature/spec-009-collection-from-mirrors` in Cloud-Sandbox
| **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-collection-from-mirrors/spec.md`

## Summary

`csis-sandbox-provisioning` asks for `infrastructurebuilder.csis_spack`
`>=0.0.3,<0.1.0`, so that a checkout holding 0.0.2 gets 0.0.3 (an install
against the new floor replaces it; against today's range it does not,
[research R1](research.md)). Its three `command` steps that run `spack
buildcache keys --install --trust --yes-to-all` become `gpg_key` steps with
`from_mirrors: true` again, and the parity tests carry the scripts' command as
that step. The container test gains a case that 0.0.2 would fail: a mirror in
a directory that publishes a key, which the `from_mirrors` steps must trust
with no prompt. The change is released as 0.0.5; spec 004's head node is its
proof on a real node.

## Technical Context

**Language/Version**: YAML (Ansible, ansible-core 2.16, as RHEL 10 ships and
the unit's tools pin); Bash (the container test); Python 3.12 (tests)

**Primary Dependencies**: `infrastructurebuilder.csis_spack` 0.0.3 from
Ansible Galaxy (its `spack_gpg_key` answers Spack's confirmation); Spack
v1.2.0

**Storage**: none

**Testing**: pytest (parity, traceability, the floor), ansible-lint, the
container test (`just full-test`); the real node is spec 004's

**Target Platform**: RHEL 10 head nodes; the AlmaLinux 10 container

**Project Type**: a dependency change in a playbook repository

**Performance Goals**: none

**Constraints**: the steps must behave as the scripts' command does (trust
what the mirrors publish); nothing is applied to AWS by this spec

**Scale/Scope**: one unit (`csis-sandbox-provisioning`), three steps, one
requirement, and records in Cloud-Sandbox

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | The change is made in `csis-sandbox-provisioning` first, then recorded here | Pass |
| II. The original reaches the units only by sync | No original file is touched; the steps still name the script lines they replace | Pass |
| III. Work that spans units is planned here | One unit, and Cloud-Sandbox's records and spec 004's task: planned here | Pass |
| IV. Acceptance tests run through the Justfile | The new checks are under the unit's `just test` and `just full-test` | Pass |
| V. The operator decides | The proof's place was the operator's ("C"); the merge and the release on the operator's word | Pass |
| VI. Nothing goes toward `ioos` | Nothing is pushed toward it; Galaxy is read | Pass |
| The ATTIC | Not consulted | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/009-collection-from-mirrors/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R5
├── data-model.md        # the requirement, the three steps, before and after
├── quickstart.md
├── contracts/
│   └── trust-steps.md   # what the three steps and the requirement promise
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-provisioning/              # csis-sandbox-provisioning
├── requirements.yml                        # >=0.0.3,<0.1.0, and why
├── roles/spack/tasks/main.yml              # two steps: funcs L700, spack-pubkey.sh L19
├── roles/intel_oneapi/tasks/main.yml       # one step: funcs L959
├── tests/test_parity.py                    # TRUST_MIRROR_KEYS back to from_mirrors; the floor
├── tests/container/converge.sh             # a mirror that publishes a key (research R2)
├── pyproject.toml, uv.lock                 # version 0.0.5
└── docs/LIVE-PROOF.md                      # box B3: the collections installed again (research R4)

exportit/cloud-sandbox/units.toml           # sandbox-provisioning 0.0.5 (csis-cloud-sandbox)

Cloud-Sandbox (the workshop)
├── exportit/MAP.md                         # the workaround's paragraph: from_mirrors, 0.0.3
├── specs/004-spack-stack-ufs-coastal/tasks.md   # T017's record: the from_mirrors steps (research R5)
└── specs/README.md                         # 009's state
```

**Structure Decision**: the change stays in the one unit that has the steps;
nothing moves between units.

## Order of the work, and of the merges

1. Tests first in the unit (the floor, the parity of the steps, the
   container's mirror that publishes a key), seen to fail.
2. The requirement, the three steps, the procedure's box; `just test` and
   `just full-test`.
3. On the operator's word: merge, raise the version to 0.0.5, tag and push;
   `units.toml` names it.
4. The records here, spec 004's task, the converge; on the operator's word,
   merge Cloud-Sandbox's branch. The spec is complete then (FR-007); its
   outcome links spec 004's record when that exists.

## Complexity Tracking

None.

## For the operator

- The floor alone moves an existing checkout to 0.0.3 (research R1). `just
  init` needs no `--upgrade`, which would also take every later 0.0.x on its
  own; a later release is taken by raising the floor again, on purpose.
- The container's new case makes a throwaway signing key inside the container
  and throws it away with the container; no real key is involved.
