# Feature Specification: The first boot reads a private playbooks' repository

**Feature Branch**: none yet; `feature/private-playbooks-access` when it is
taken up

**Created**: 2026-11-21, on the operator's instruction of that day

**Status**: Draft. **Needs spec 006 first,** whose first boot this extends.
Nothing waits for it: the playbooks' repository is public, so the first boot
needs no credential today.

**Input**: the operator, 2026-11-21, answering spec 006's question on how a
node reaches the playbooks: "Make csis-sandbox-provisioning public, so this
isn't an issue right now. However, create a spec to make it possible to use
both a read-only deploy key or a fine-grained github token if that's what
someone wants to do in the future."

## Why

- **Today the first boot needs no credential:** `csis-sandbox-provisioning`
  was made public on 2026-11-21, and spec 006's first boot clones it over
  HTTPS anonymously (its FR-003).
- **Someone may not want that:** a site that keeps its own fork of the
  playbooks private, or a later decision to make this one private again,
  leaves a node that cannot clone what it is meant to apply. The first boot
  fails visibly then (spec 006's edge case), but there is no way to make it
  succeed.
- **GitHub offers two read-only ways in, and each suits someone:** a
  **deploy key**, an SSH key added to one repository with read access only,
  which does not expire and reaches nothing else; and a **fine-grained
  personal access token**, limited to named repositories and to reading their
  contents, which can cover several repositories at once but expires and is
  tied to a person's account. The operator chooses; the sandbox supports
  both, and neither is the default.

## Clarifications

### Session 2026-11-21

- Q: Which repositories does the choice cover? → A: the playbooks' only:
  cloudflow's is public too, by the operator's answer to spec 006's FR-002.
- The operator, 2026-11-23: the documentation must note the need for the key
  (or a token) in all the right places, as spec 008's must → FR-011, SC-006.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nothing changes for a public repository (Priority: P1)

An operator who names a public playbooks' repository, as today, sets nothing
new, and the first boot clones it anonymously, exactly as spec 006 left it.

**Why this priority**: it is every node built today; adding a choice must not
change it.

**Independent Test**: the user data rendered with no access mode set,
compared with spec 006's.

**Acceptance Scenarios**:

1. **Given** no access mode is set, **When** the module is rendered, **Then**
   the user data is spec 006's, byte for byte, and no permission to read a
   secret is granted.

### User Story 2 - A private repository read with a deploy key (Priority: P2)

An operator who keeps the playbooks private adds a read-only deploy key to
that repository, keeps the key's private half in a secret of their own, and
names the mode and the secret. The first boot reads the key, clones over
SSH, applies the playbooks, and leaves no copy of the key on the node.

**Why this priority**: a deploy key reaches one repository only and does not
expire, so it is the narrower of the two ways in.

**Independent Test**: the rendered user data for this mode, without AWS; then
one first boot against a private copy of the playbooks.

**Acceptance Scenarios**:

1. **Given** the mode `deploy_key` and a secret, **When** the module is
   rendered, **Then** the user data clones over SSH, trusts only GitHub's
   published host keys, and names the secret but holds no key.
2. **Given** that node's first boot, **When** it has finished, **Then** the
   playbooks were applied, and no file, log or environment on the node holds
   the key.
3. **Given** the mode `deploy_key` and no secret named, **When** a plan is
   made, **Then** it fails with a message naming the missing value.

### User Story 3 - A private repository read with a fine-grained token (Priority: P2)

An operator who would rather use a fine-grained token, read-only on the
repositories the first boot needs, keeps it in a secret of their own and
names the mode and the secret. The first boot reads the token, clones over
HTTPS with it, and leaves no copy of it on the node.

**Why this priority**: one token can cover several private repositories,
which a deploy key cannot.

**Independent Test**: as User Story 2, for this mode.

**Acceptance Scenarios**:

1. **Given** the mode `token` and a secret, **When** the module is rendered,
   **Then** the user data clones over HTTPS and names the secret but holds no
   token.
2. **Given** that node's first boot, **When** it has finished, **Then** the
   playbooks were applied, and the token is in no file, log, URL, process
   argument or git configuration on the node.
3. **Given** an expired or revoked token, **When** the node boots, **Then**
   the first boot fails visibly, its log saying the clone was refused and
   that the token may have expired.

### Edge Cases

- **The secret cannot be read** (wrong name, no permission, another region):
  the first boot fails visibly before cloning, naming the secret, never
  falling back to an anonymous clone.
- **A token that has expired** fails the clone; the log says so (User Story
  3). Renewing it is the operator's, in the secret, with no change to the
  module.
- **The private subnet cannot reach GitHub's SSH port:** the deploy-key mode
  uses GitHub's SSH service on port 443 (`ssh.github.com`) when port 22 is
  closed, or the procedure says which one it uses and why.
- **`ansible-pull` fetches the repository again** after the first clone: it
  uses the same access, and the credential is removed only once it has
  finished, pass or fail.
- **A public repository with a mode set:** the clone succeeds with the
  credential; nothing checks that the repository is private.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `csis-sandbox-terraform` MUST gain a variable for how the first
  boot reaches the playbooks' repository, with three values: `none` (the
  default: an anonymous HTTPS clone, spec 006's), `deploy_key` and `token`.
  Any other value fails the plan with a message listing the three.
- **FR-002**: With `deploy_key` or `token`, a second variable MUST name the
  secret that holds the credential; a plan without it fails with a message
  naming it. With `none`, it is not used.
- **FR-003**: The credential MUST never be in a repository, a variable's
  value, the rendered user data, the Terraform state or plan, or a command
  line. The secret is created and filled by the operator, outside Terraform;
  the module only names it.
- **FR-004**: With `deploy_key` or `token`, the head node's role MUST be
  allowed to read that one secret and no other; with `none`, it MUST gain no
  permission at all.
- **FR-005**: The first boot MUST read the credential just before the clone,
  hold it only in a file readable by root alone (or in memory), use it for
  the clone and for `ansible-pull`, and remove it when they have finished,
  whether they passed or failed.
- **FR-006**: With `deploy_key`, the clone MUST be over SSH, with GitHub's
  published host keys pinned in the template, not accepted on first use.
- **FR-007**: With `token`, the clone MUST be over HTTPS, the token given to
  git through a credential helper or header for that one command, never put
  in the URL or the checkout's configuration.
- **FR-008**: This covers the playbooks' repository (`provisioning_repo`)
  only. Cloudflow's repository is public (spec 006, FR-002) and is cloned
  anonymously whatever the mode; giving it the same choice is a later spec's,
  if it is ever made private again.
- **FR-009**: Tests MUST render the module in each of the three modes and
  hold each user data to the template; show that `none` renders spec 006's
  user data unchanged and grants no permission; show a plan failing for an
  unknown mode and for a missing secret; and show that no credential value
  appears in any rendered output or plan. `tofu validate` MUST pass.
- **FR-010**: `csis-sandbox-terraform`'s `DEPLOYMENT.md` MUST say, for each
  mode, how to make the credential (a read-only deploy key on the repository;
  a fine-grained token with read-only access to its contents and nothing
  else), how to keep it in a secret, how to name it, and how to renew a
  token.
- **FR-011**: Every other document that tells someone how to deploy a sandbox
  or what its first boot does MUST say that a private playbooks' repository
  needs a credential, a read-only deploy key or a fine-grained token, made by
  the operator and kept only in its secret, and that without it the first boot
  stops before applying anything; and that a public one needs none (the
  default). The places, each changed in its own repository:
  - `csis-sandbox-terraform`'s `README.md`, its first-boot section;
  - `csis-sandbox-provisioning`'s `DEPLOYMENT.md`, "What happens at first
    boot", and its `README.md`, "How it is applied";
  - Cloud-Sandbox's `exportit/MAP.md` (the `sandbox-terraform` first-boot
    section) and `specs/README.md`.
  Spec 008, which reads `csis-sandbox-configs` with a deploy key of its own,
  names the same places for that key.

### Key Entities

- **Access mode**: `none`, `deploy_key` or `token`; one per head node.
- **Credential**: a deploy key's private half or a fine-grained token; made
  and renewed by the operator, kept only in the secret.
- **Secret**: holds one credential; created by the operator, named to the
  module, readable by the head node's role alone.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With no mode set, a new head node is built exactly as spec 006
  builds it: the same user data, and no permission to read any secret.
- **SC-002**: With each of the two modes, a first boot against a private
  copy of the playbooks applies them, and afterwards no file, log or
  configuration on the node holds the credential.
- **SC-003**: A search of the rendered outputs, the plan and the state for
  the credential's value finds nothing, in both modes.
- **SC-004**: A first boot with an unreadable secret or a refused credential
  stops before applying anything and says why in its log.
- **SC-006**: Each place FR-010 and FR-011 list says a private playbooks'
  repository needs a deploy key or a token, and how it is made and kept.
- **SC-005**: The root `just test` and `just full-test` pass.

## Assumptions

- The secret is kept in AWS Secrets Manager, in the head node's region, and
  is a new resource with the sandbox's prefix: nothing existing in the
  account is changed (the operator's standing rule).
- The first boot can read the secret before the playbooks run: the template
  installs, or the image already has, the AWS CLI by then.
- Proving the two modes needs a private copy of the playbooks' repository;
  making one is a repository created on the operator's word, removed after.

## Dependencies

- Spec 006: the first boot that clones `provisioning_repo`.
- Spec 001's head node role, which FR-004 extends.

## Out of Scope

- Making `csis-sandbox-provisioning` private again: it is public since
  2026-11-21, and this spec only makes a private repository possible.
- GitHub Apps and SSH certificates; credentials for anything other than
  cloning at first boot.
- Rotating credentials automatically.
