# Implementation Plan: The first boot reads a private playbooks' repository

**Branch**: `feature/private-playbooks-access`, in Cloud-Sandbox and in
`csis-sandbox-terraform` | **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/007-private-playbooks-access/spec.md`

## Summary

The module gains a choice of how the first boot reaches the playbooks'
repository: `none`, the default, which leaves spec 006's boot byte for byte as
it was; `deploy_key`; and `token`. With either of the last two, the operator
names a Secrets Manager secret they made themselves, the head node's role may
read that one secret, and the first boot reads the credential into memory-backed
storage with tracing off, uses it for the playbooks' clone and `ansible-pull`,
and removes it before the image is made. Everything but a real private clone
is proved without AWS.

## Technical Context

**Language/Version**: HCL for OpenTofu 1.13.9; Bash (the template); Python 3.12
(the unit's tests)

**Primary Dependencies**: the module's providers as they are (`aws ~> 3.47`);
on the node, the AWS CLI v2 (research R3), OpenSSH and git 2.31 or later
(RHEL 10's)

**Storage**: AWS Secrets Manager, one secret the operator makes; `/run` on the
node, for the length of the clone

**Testing**: `tofu test` with mocked providers (`tests/access.tftest.hcl`);
pytest (`test_template.py`, the golden file); the real proof by hand
(quickstart, step 2)

**Target Platform**: a RHEL 10 head node's first boot; the local machine for
every automatic test

**Project Type**: an OpenTofu module and its first-boot template, in one unit

**Performance Goals**: N/A

**Constraints**: the credential in no repository, variable value, rendered
user data, state, plan, command line, log or image (FR-003, FR-005); `none`
unchanged (SC-001); no existing AWS resource changed

**Scale/Scope**: `csis-sandbox-terraform` (`variables.tf`, `main.tf`, the
template, tests, `DEPLOYMENT.md`); in Cloud-Sandbox, `specs/README.md`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Changed in `csis-sandbox-terraform` first, on the same branch, then recorded; nothing moves between units | Pass |
| II. The original reaches the units only by sync | Only the unit's own files change (`init_template.ansible.tpl` is `new`, the rest `owned`) | Pass |
| III. Work that spans units is planned here | This spec | Pass |
| IV. Acceptance tests run through the Justfile | `tofu test` and pytest behind the unit's `just test`; the AWS proof is a procedure, not a target, because it needs a private repository and an account | Pass |
| V. The operator decides | The secret and the private copy are made on the operator's word; no secret anywhere in a repository; nothing applied by this spec | Pass |
| VI. Nothing toward `ioos` | None | Pass |
| The ATTIC | Not consulted | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/007-private-playbooks-access/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R7
├── data-model.md        # the variables, the secret, the policy, the boot's steps
├── quickstart.md
├── contracts/
│   └── access-modes.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/              # csis-sandbox-terraform
├── variables.tf                         # + provisioning_access, provisioning_secret_arn; provisioning_repo's validation
├── main.tf                              # + aws_iam_role_policy.provisioning_secret (count); the two values to the template
├── init_template.ansible.tpl            # the %{ if } steps: CLI, secret, known hosts, GIT_SSH_COMMAND or helper, removal
├── DEPLOYMENT.md                        # each mode: making the credential, the secret, renewing a token
└── tests/
    ├── access.tftest.hcl                # the three modes and the three failures, mocked
    ├── golden/first-boot.none.sh        # spec 006's rendered user data, for the byte comparison
    └── test_template.py                 # + the golden comparison; the order of the credential steps

Cloud-Sandbox (the workshop)
└── specs/README.md                      # 007's state
```

**Structure Decision**: the same unit and files as spec 006, which this spec
extends; it is taken up after 006 is merged, on a branch from it.

## Order of the work, and of the merges

1. **csis-sandbox-terraform:** the golden file from spec 006's template first
   (so `none` is pinned before anything changes); the variables and their
   validations, with `tofu test` cases failing first; the policy; the template
   steps; `DEPLOYMENT.md`; the checks of research R3 and R5 against a RHEL 10
   image's packages and Ansible's `git` module, recorded in research.md.
2. **Cloud-Sandbox:** the spec's state, the submodule's commit; the root's
   acceptance tests.
3. **Merged and pushed** on the operator's word, the unit first.
4. **The proof on AWS** (quickstart, step 2) when someone wants a private
   repository; until then the spec is merged, not complete (the constitution's
   states).

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| Template directives that render nothing for `none` | SC-001: today's boot unchanged | a second template would have to be kept in step with the first |
| Installing the AWS CLI at first boot | the secret is needed before the playbooks run (research R3) | the playbooks are what the secret fetches |

## For the operator

- The proof on AWS needs a private repository; making one, even a copy, is a
  repository created on your word. Until someone needs the private path, the
  spec can stay merged without that proof.
