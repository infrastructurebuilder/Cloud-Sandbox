# Implementation Plan: The first boot puts the site's descriptions on the head node

**Branch**: `feature/site-configs-at-first-boot`, in Cloud-Sandbox,
`csis-sandbox-terraform`, `csis-sandbox-configs` and the units whose guides
name the old paths | **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-site-configs-at-first-boot/spec.md`

## Summary

`csis-sandbox-terraform` gains three optional settings, `configs_repo`,
`configs_version` and `configs_secret_arn`. When they are set, the first boot
reads a read-only deploy key from its own Secrets Manager secret into
memory-backed storage, clones `csis-sandbox-configs` at its tag over SSH with
GitHub's pinned host keys, as `$RUNUSER`, into `/save/$RUNUSER/sandbox-configs`,
removes the key, and links the two description directories where the guides'
relative paths land (`/save/$RUNUSER/cloudflow/src/`) and where the old
absolute paths point (`/save/$RUNUSER/Cloud-Sandbox/`). The head node's role
may read that one secret. Unset, the user data is spec 007's, byte for byte.
The guides that name the old paths, and every document that tells someone how
to deploy or run, say that the key is needed. It reuses spec 007's way of
handling a secret on the node, and is built after it.

## Technical Context

**Language/Version**: HCL for OpenTofu 1.13.9 (the main module, its
`hashicorp/aws ~> 3.47`); Bash, in `init_template.ansible.tpl`; Python 3.12
(tests); Markdown (the guides)

**Primary Dependencies**: spec 007's first-boot steps for a secret (the AWS
CLI, a directory under `/run`, `set +x`, a trap, GitHub's pinned host keys,
`GIT_SSH_COMMAND`); AWS Secrets Manager; GitHub deploy keys

**Storage**: the operator's Secrets Manager secret (made outside OpenTofu);
the clone on the EFS volume

**Testing**: `tofu test` with mocked providers; `test_template.py` rendering
the template through `tofu console`; the golden rendering of spec 007 (unset);
a test of how the links resolve; a head node for the real clone

**Target Platform**: RHEL 10 head nodes in the `noaa` account

**Project Type**: an OpenTofu module's first boot, and documentation in several units

**Performance Goals**: none

**Constraints**: the key never in a repository, a variable, a log or the
image; the head node's role may read only the secrets this and spec 007 name;
every AWS step, and the key's making, on the operator's word

**Scale/Scope**: one module and its tests; about ten guides in eight units;
the documents FR-008 lists

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
| --- | --- | --- |
| I. The workshop holds the units | Each unit changed in its own repository first, then recorded here | Pass |
| II. The original reaches the units only by sync | No original file is touched; the guides gain notes in the units that own them | Pass |
| III. Work that spans units is planned here | `csis-sandbox-terraform`, `csis-sandbox-configs`, and the guides' units: planned here | Pass |
| IV. Acceptance tests run through the Justfile | The tests are under each unit's `just test` and `just full-test`; the AWS steps are a procedure | Pass |
| V. The operator decides | Location, credential and links were the operator's; the key, the secret, the tag, the node on the operator's word | Pass |
| VI. Nothing goes toward `ioos` | `csis-sandbox-configs` is the sandbox's own; nothing is pushed toward `ioos` | Pass |
| The ATTIC | Not consulted | Pass |

No violation. Re-checked after the design below: unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/008-site-configs-at-first-boot/
├── spec.md
├── plan.md              # this file
├── research.md          # R1 to R9
├── data-model.md
├── quickstart.md
├── contracts/
│   └── configs-at-first-boot.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code

```text
exportit/sandbox-terraform/                  # csis-sandbox-terraform
├── variables.tf                             # configs_repo, configs_version, configs_secret_arn
├── main.tf                                  # the three passed to the template; aws_iam_role_policy.configs_secret
├── init_template.ansible.tpl                # the configs block, after cloudflow's (research R3, R4)
├── tests/configs.tftest.hcl                 # plans: unset, set, the validations
├── tests/test_template.py                   # the rendering: order, key handling, links
├── tests/test_links.py                      # a program's ../ from the cloudflow link (research R2)
├── DEPLOYMENT.md, README.md                 # the key: making it, the secret, the settings (FR-008)
└── proof/proof.tfvars.example               # the three settings, commented

exportit/sandbox-configs/README.md           # private, read with the key (csis-sandbox-configs)
exportit/sandbox-provisioning/DEPLOYMENT.md  # "What happens at first boot": the clone and its key
exportit/<unit>/<guide>                      # the note of FR-006, ten guides in eight units (research R5)

Cloud-Sandbox (the workshop)
├── exportit/MAP.md                          # the first-boot section
└── specs/README.md                          # 008's state
```

**Structure Decision**: the clone belongs to the first boot, which is
`csis-sandbox-terraform`'s template; the notes belong to the guides' own
units.

## Order of the work, and of the merges

1. **After spec 007 is built**: its secret steps are what this extends.
2. No AWS: the settings, the policy, the template block, the tests; the notes
   in each unit; the documents. Acceptance tests in each, then the root's.
   Merged on the operator's word.
3. The tag of `csis-sandbox-configs` that the first boot clones (research R7),
   on the operator's word.
4. On AWS, each step on the operator's word: the deploy key made by the
   operator and added to `csis-sandbox-configs` as read-only, its secret, a
   head node with the settings, the clone and the links seen there, a search
   of the node for the key, the node removed.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
| --- | --- | --- |
| Links in two places | the guides' relative paths resolve from cloudflow's real directory; the old absolute paths from `Cloud-Sandbox/` | one place serves only one of them (the operator's choice, 2026-11-25) |

## For the operator

- **The deploy key is yours to make** (FR-003): an ed25519 key pair, its
  public half added to `csis-sandbox-configs` as a read-only deploy key, its
  private half put in a new Secrets Manager secret. `DEPLOYMENT.md` will give
  the boxes. No task makes it for you.
- **A new tag of `csis-sandbox-configs`** is needed: `0.0.1` (2026-11-17)
  predates spec 005's split of its files.
