# Implementation Plan: A build cache for RHEL 10, pushed without scripts

**Branch**: `feature/rhel10-build-cache`, in Cloud-Sandbox,
`csis-sandbox-terraform`, `csis-sandbox-provisioning` and `csis-sandbox-ops`
| **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-rhel10-build-cache/spec.md`

## Summary

A new private bucket of the sandbox's own, made by a root module of its own
in `csis-sandbox-terraform`, holds the RHEL 10 build cache. A playbook in
`csis-sandbox-provisioning`, run by hand after a build, pushes the
environment's packages there with the collection's `spack_buildcache_push`,
signed with the site's key, through a policy on the head node's own role.
Once a build has been shown to install from the cache, the playbooks'
defaults switch to it. The old RHEL 8 push script stays in
`csis-sandbox-ops`, its replacement named.

## Technical Context

**Language/Version**: HCL for OpenTofu 1.13.9; YAML (Ansible, ansible-core as
the playbooks pin it); Bash (the catalogue check); Python 3.12 (tests)

**Primary Dependencies**: `hashicorp/aws ~> 6.0` for `build-cache/` (as spec
003's `reaper/`); the main module's providers unchanged; the collection
`infrastructurebuilder.csis_spack` (`spack_buildcache_push`, Spack 1.0 or
later); Spack v1.2.0 on the node

**Storage**: the new S3 bucket; the module's local state

**Testing**: `tofu test` (mocked) and `validate` for `build-cache/` and the
policy; pytest parity, Ansible syntax and lint, and the container push to a
directory in `csis-sandbox-provisioning`; `check-catalogue.sh`; the real push
on a head node

**Target Platform**: AWS, `noaa`, us-east-2; a RHEL 10 head node built as
spec 001 builds one

**Project Type**: a root module, a policy, a playbook, and records

**Performance Goals**: a build from the cache installs most packages from it
instead of compiling (SC-003)

**Constraints**: `ioos-cloud-sandbox` never written to; the existing role not
changed; no credential on the node but the signing key, put in place and
removed by hand; every AWS change on the operator's word

**Scale/Scope**: four repositories; one head node of hours, then the bucket
alone

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Each unit changed in its own repository first; the script stays where it is, only its records change, so no file moves (FR-005) | Pass |
| II. The original reaches the units only by sync | `spack-update-mirror.sh` is unchanged but for a header line; its mapping line stays, so a sync still lands on it | Pass |
| III. Work that spans units is planned here | This spec, four repositories | Pass |
| IV. Acceptance tests run through the Justfile | Every new check behind its unit's `just test` or `just full-test`; the AWS steps are a procedure | Pass |
| V. The operator decides | Four questions asked and recorded; the bucket, the node, every push and removal on the operator's word | Pass |
| VI. Nothing toward `ioos` | `ioos-cloud-sandbox` is read for its public key only | Pass |
| The ATTIC | Not consulted | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/002-rhel10-build-cache/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R8
├── data-model.md
├── quickstart.md
├── contracts/
│   └── push-build-cache.md   # the playbook and build-cache/
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/              # csis-sandbox-terraform
├── build-cache/                         # new root module (research R1)
│   ├── versions.tofu, main.tf, variables.tf, outputs.tf
│   └── tests/build-cache.tftest.hcl
├── main.tf                              # + aws_iam_role_policy.build_cache (count)
├── variables.tf                         # + build_cache_bucket
├── tests/support.py                     # MODULES gains "build-cache"
└── DEPLOYMENT.md                        # the bucket, and build_cache_bucket

exportit/sandbox-provisioning/           # csis-sandbox-provisioning
├── push-build-cache.yml                 # contracts/push-build-cache.md
├── group_vars/all.yml                   # the last step: the defaults (research R7)
├── tests/test_parity.py                 # the playbook's variables = the script's; the defaults
└── tests/container/converge.sh          # push to a directory, twice

exportit/sandbox-ops/                    # csis-sandbox-ops
├── bin/spack-update-mirror.sh           # a header line naming its replacement
├── CATALOGUE.tsv                        # superseded_by filled
└── tests/check-catalogue.sh             # superseded_by names a unit and a path

Cloud-Sandbox (the workshop)
├── exportit/sandbox-terraform.map       # + new build-cache/
├── exportit/REMINDERS.md                # + the managed policies to narrow (research R2)
└── specs/README.md                      # 002's state
```

**Structure Decision**: the bucket in a root module of its own, so that a head
node's removal never touches it; the playbook beside `site.yml`, which builds
what it pushes.

## Order of the work, and of the merges

1. **No AWS:** `build-cache/` and the policy (csis-sandbox-terraform); the
   playbook, its parity and container tests (csis-sandbox-provisioning); the
   header, catalogue and check (csis-sandbox-ops); the map line and reminder
   (Cloud-Sandbox). Acceptance tests in each, then the root's. Merged and
   pushed on the operator's word. Needs spec 001 merged (its `proof/`).
2. **On AWS**, each step on the operator's word: the bucket; a head node
   (spec 001's stages A and B, with `build_cache_bucket`); the push three
   ways; the build from the cache (SC-003).
3. **The defaults** (FR-004), merged in `csis-sandbox-provisioning`, then
   SC-004 on the same node; then the node removed (spec 001's stage E), the
   bucket kept.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| A third root module in the unit | the bucket outlives every head node (FR-002) | a resource in the main module is destroyed with the node |

## For the operator

- **Finding** (research R2): the head node's role already has
  `AmazonS3FullAccess` through the module's default managed policies, so
  today it could write to any bucket, `ioos-cloud-sandbox` included. The
  scoped policy is written for when that list is narrowed; narrowing it is a
  spec of its own, added to `REMINDERS.md`.
- The bucket's name, `csis-sandbox-rhel10-build-cache`, must be free in all of
  S3; if it is taken, the plan says so, and a name is your decision then.
