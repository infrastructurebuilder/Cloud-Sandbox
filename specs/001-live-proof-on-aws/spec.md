# Feature Specification: The live proof on AWS

**Feature Branch**: none yet; `feature/live-proof` when it is taken up

**Created**: 2026-11-14, as stage 15; carried into this spec 2026-11-19

**Status**: **Complete**, 2026-11-24. Run on AWS 2026-11-23; outcome below. It ran in the `noaa`
account in us-east-2, inside the existing IOOS VPC, creating only new
resources (the operator's answer, 2026-11-21); the role there cannot create
a network, so the module is given one.

**Input**: the stage plan of 2026-11-14 ("Make a plan for the live proof"),
carried from the ATTIC on the operator's instruction of 2026-11-19.

## Why

Everything built since the units were made is proved on the local machine
and in an AlmaLinux 10 container. What only a real head node can show is
still not proved:

| Not proved | Why only a head node shows it |
| --- | --- |
| `efa_driver`, `fsx_lustre_client` | kernel modules, built for the running kernel |
| `hpc_tuning` | kernel settings and a `tuned` profile |
| `node-image.yml` | an EBS snapshot and a machine image, through `amazon.aws` |
| Building `spack_environment` | the container only concretizes; a real build takes hours |
| Module files with `refresh_modules: when_needed` | only a real build writes real module files |
| The site mirror's list (off by default) | needs the site's bucket and key |
| Anything on RHEL, or on AWS | the container is AlmaLinux |
| The first-boot script | needs a real EFS volume, and cloud-init |
| Whether the playbooks leave the same node the script did | needs a second node, built the old way |

`csis-sandbox-provisioning/docs/LIVE-PROOF.md` is the procedure, written
before the units had repositories and never run. It is out of date: it
assumes the original `terraform/` and Terraform 1.5.7 (the unit is
`csis-sandbox-terraform`, with OpenTofu 1.13.9, which its `versions.tofu`
requires), copies the playbooks by `tar` without installing the collection
first (its box B2 would fail at the `spack` role), and says nothing of check
mode, the comparison of Spack's configuration, or `refresh_modules`.

What was found while planning, and still holds:

- With the module's default `t3.medium`, `spack_jobs` is 1, and the
  script's `spack_cache_only: -1` compiles everything.
- The site's build cache holds 103 specs, all `rhel8`, built with oneAPI
  2023.1.0, Intel 2021.9.0 and gcc 11.2.1, in the layout of Spack before 1.0:
  its key can be trusted and the mirror added, but it supplies nothing to a
  RHEL 10 build.
- In the `noaa` account (2026-11-15): the role allows IAM roles, instances,
  security groups, EFS, images and key pairs, and denies `ec2:CreateVpc` and
  `ec2:CreateSubnet`. Its state bucket `cloud-sandbox-tfstate` returns 403.
  Only us-east-2's VPC reaches the internet, through a NAT; it is a shared
  account with many running head nodes.

## Clarifications

### Session 2026-11-21

- Q: In which AWS account and region does the proof build its head node, and
  does OpenTofu create its network or use an existing one? → A: the `noaa`
  account in us-east-2, the module given the existing IOOS VPC and a private
  subnet by ID, read only, creating only new resources inside them.
- Q: How does the agent reach the head node in the private subnet? → A: AWS
  Systems Manager Session Manager: the proof's own new role gets
  `AmazonSSMManagedInstanceCore`, the SSM agent is installed at first boot,
  and the agent connects with `aws ssm start-session` (and `ssh` through it);
  nothing is added to the existing bastion. (So the agent runs the boxes:
  FR-007 follows.)
- Q: What size of instance does the head node build on? → A: a
  compute-optimized type with 32 processors or more, for example
  `c6i.8xlarge`, so `spack_jobs` is 31 (first answered 16 processors, changed
  by the operator the same day).
- Q: How do the playbooks reach the head node? → A: by hand, as the first
  boot would: the node boots with the old template minus its last step, the
  unit is copied to it as a git repository over the SSM session, and the
  template's three commands are run there. The real first boot is spec 006's
  to prove.
- Q: Does the build compile everything, or take what Spack's public binary
  cache has? → A: compile everything, `spack_cache_only: -1`, as the script
  does.
- Q: Does the proof apply the site mirror's settings? → A: yes,
  `spack_site_mirror: true` on the proof's node.
- Q: Does the proof also build a second head node the old way, to compare?
  → A: make it a flag, `compare_with_script`, default `false`, which skips it;
  set to `true`, the proof builds the second node with the original methods
  and compares the two. The comparison is to be attempted later.
- Q: Does the proof start a compute node from the image and run a model job?
  → A: no, out of scope: the image's `available` state is the proof; a
  compute-node run becomes a spec of its own later.
- Q: When the proof is over, what happens to the node, its EFS volume, and the
  image and snapshot? → A: all removed, each step asked first; then a check
  shows nothing with the proof's prefix remains and the plan shows the IOOS
  VPC unchanged.
- Q: Now that spec 006 is built before this one, how does the proof's head
  node get its playbooks? → A: by spec 006's real first boot (asked while
  planning, 2026-11-21): the unit's template, with the playbooks' and
  cloudflow's repositories and tags set; the second apply, check mode and the
  comparisons are then run by hand; `node-image.yml` waits for the operator's
  word. This replaces the earlier answer to FR-010 (boot with the old
  template, its last step removed, and the playbooks run by hand).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A head node built by the playbooks on AWS (Priority: P1)

The operator creates a head node with `csis-sandbox-terraform`, whose first
boot (spec 006) builds it with `csis-sandbox-provisioning`'s `site.yml`, and
sees it built, built again with nothing changed, and previewed in check mode
with nothing to change.

**Why this priority**: it is what the units were made for, and none of it has
been done on a real node.

**Independent Test**: one head node in a workspace of its own; `site.yml`
applied twice and once in check mode, with its recap kept.

**Acceptance Scenarios**:

1. **Given** a fresh account session and the plan showing only additions,
   **When** the node is created, **Then** OpenTofu reports `0 to change, 0 to
   destroy` before anything is applied.
2. **Given** the node, **When** `site.yml` is applied, **Then** it ends with
   `failed=0`; applied again, every task that changes is listed as a finding.
3. **Given** the built node, **When** check mode runs, **Then** every task that
   would change is listed as a finding.
4. **Given** the built node, **When** Spack's configuration is compared with
   the container's (`tests/container/expected-spack-config.json`), **Then**
   each difference is recorded as a finding, not a failure.

### User Story 2 - An image a compute node can start from (Priority: P2)

The operator runs `node-image.yml` on the built node and gets a machine image
that AWS reports `available`.

**Why this priority**: compute nodes start from it; it is the step the
container cannot take at all.

**Independent Test**: the image's state in `aws ec2 describe-images`.

**Acceptance Scenarios**:

1. **Given** the built node, **When** `node-image.yml` runs, **Then** an image
   and its snapshot exist and the image is `available`.

### User Story 3 - Nothing left behind (Priority: P2)

When the proof is over, everything it created is removed, one step at a time
with the operator's word at each, and the account shows nothing else of it.

**Why this priority**: a forgotten node or image is a bill.

**Independent Test**: list what carries the proof's name tag after removal.

**Acceptance Scenarios**:

1. **Given** the proof's resources, **When** they are removed, **Then** no
   instance, volume, image, snapshot, security group or role of the proof
   remains, and the existing IOOS VPC and its subnets are unchanged.

### Edge Cases

- The session expires during the hours of a build: the build must be
  resumable, or the session refreshed between stages of the procedure.
- The plan shows a change or a destruction: stop; nothing is applied.
- The private subnet has no public address and no internet gateway: the head
  node is reached only through a way in that already exists, and gets its
  packages through the subnet's NAT.
- A second apply changes something because a package was released upstream
  in the meantime (botocore has done it in the container): recorded, and the
  apply repeated, before it is called a finding.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The AWS session MUST be checked first (`aws sts
  get-caller-identity`); if it fails, the work stops and the operator is asked
  to refresh it.
- **FR-002**: `LIVE-PROOF.md` MUST be brought up to date, as its version 2,
  before it is run, in the repository's step form (numbered and versioned
  boxes, a check as the last line of its box, a time estimate on any box over
  thirty seconds, every choice a bold decision with its default, "your local
  machine" and "the head node" named in every step). This is a change in
  `csis-sandbox-provisioning`.
- **FR-003**: Stage A of the page MUST use a working copy of
  `csis-sandbox-terraform` and its pinned OpenTofu, in a workspace and a
  settings file of its own, with state kept locally, never in a shared
  bucket; and MUST stop unless the plan shows only additions.
- **FR-004**: Stage B MUST start from what the first boot did (the checkout,
  `ansible-galaxy collection install -r requirements.yml` from Ansible Galaxy,
  then `site.yml`, read from the boot's log), then run by hand a second apply,
  check mode, the Spack configuration comparison, and the module-file check
  (every module file under the environment's root has the time it had after
  the first apply).
- **FR-005**: Nothing MUST be created, changed or removed on AWS without the
  operator's word at that step (`tofu apply`, `tofu destroy`,
  `node-image.yml`, image and snapshot removal). Existing resources in
  `us-east-2` MUST NOT be changed.
- **FR-006**: The logs MUST NOT be committed: they hold the node's addresses
  and the account's identifiers. Their summary goes in this spec's outcome.
- **FR-007**: The agent MUST run the boxes: the local machine's in its shell,
  the head node's over an SSM session (FR-017), reading each result before the
  next, and stopping to ask at every gate, every decision box, and every box
  that creates, changes or removes something on AWS.
- **FR-017**: The head node MUST be reached only through AWS Systems Manager
  Session Manager: the proof's new IAM role carries the managed policy
  `AmazonSSMManagedInstanceCore`; the SSM agent is installed at first boot if
  the image lacks it; the node reaches SSM's endpoints through the subnet's
  NAT; the procedure uses `aws ssm start-session`, and `ssh` and `scp` through
  it. Your local machine MUST have the Session Manager plugin, and the
  procedure checks for it first. No inbound rule is opened, and nothing is
  added to the existing bastion.
- **FR-008**: The proof MUST run in the `noaa` account, region us-east-2. The
  working copy's settings MUST give the module the existing "IOOS Cloud
  Sandbox VPC" and one of its private subnets (the ones that reach the
  internet through the NAT) by ID, as `vpc_id` and `subnet_id`, so the module
  reads them and creates no network. Every resource the proof creates (its
  security groups, EFS volume and mount target, network interface, instance,
  IAM role, key pair, image and snapshot) MUST be new, carry the proof's name
  prefix, and be the only thing it changes; the plan MUST show no change and
  no destruction of anything that exists.
- **FR-009**: The head node MUST be a compute-optimized instance with 32
  processors or more, for example `c6i.8xlarge`, set in the working copy's
  settings file, so that `spack_jobs` is 31 and the build takes as few hours
  as it can. It can be made smaller afterwards, as `DEPLOYMENT.md` describes.
- **FR-010**: The playbooks MUST reach the node by spec 006's first boot: the
  unit's `init_template.ansible.tpl`, rendered with `provisioning_repo`,
  `provisioning_version`, `cloudflow_repo` and `cloudflow_version`, clones
  both public repositories with no credential and applies `site.yml`. The
  proof's working copy changes the rendered boot in two ways only: the SSM
  agent installed first (FR-017), and the node image left out, so that
  `node-image.yml` runs by hand on the operator's word (FR-005). The second
  apply, check mode and the comparisons (FR-004) run by hand on the node. This
  node is the first real use of spec 006's first boot, and proves it.
- **FR-011**: The Spack build MUST compile everything, `spack_cache_only: -1`,
  as the script does: it is the only way to prove the build, and the site's
  own cache holds only RHEL 8 packages.
- **FR-012**: The proof MUST apply the site mirror's settings,
  `spack_site_mirror: true`: the key trusted by the fingerprint
  `spack_key_fingerprint` names, and the mirror added. With FR-011 the build
  reads no binary cache, so the mirror cannot change what is built.
- **FR-013**: The proof MUST have a flag, `compare_with_script`, in its
  settings (the working copy's settings file, read by the procedure), whose
  default is `false`:
  - `false` (now): stage D is skipped, and the last row of the "Not proved"
    table stays not proved, recorded as deferred by this flag;
  - `true` (later): stage D builds a second head node in the same way as the
    first (same type, subnet, SSM access), but set up by the original methods:
    the original `setup-instance.sh` and its library at `ca0604a`, taken from
    this repository's history, run as the old first-boot template ran them;
    then the two nodes are compared (installed packages, users, services,
    Spack's configuration and environment, module files), each difference a
    finding; the second node is removed with the first (FR-015).
  The procedure MUST say what the flag does, and that it is off by default.
- **FR-018**: `exportit/REMINDERS.md` MUST gain an item: the comparison with a
  node built the old way, deferred by `compare_with_script` defaulting to
  `false`, to be attempted later by setting it to `true`.
- **FR-014**: The proof MUST NOT start a compute node from the image or run a
  model: the image AWS reports `available` is the proof of `node-image.yml`. A
  compute node started by cloudflow from the image, running a model job, is a
  spec of its own, to be written later.
- **FR-015**: At the end, everything the proof created MUST be removed, each
  step asked first (FR-005): the node (and the second node, if
  `compare_with_script` was `true`), the EFS volume, and the image and its
  snapshot, with the security group and role it made. Nothing is kept for a
  look. A check MUST then list what carries the proof's prefix and find
  nothing, and a plan of the existing IOOS VPC MUST show no change.
- **FR-016**: JupyterHub, kept as an option (stage 13), MUST be applied and
  checked on the node as the container test checks it, the hub answering on
  its port.

### Key Entities

- **The proof's workspace**: an OpenTofu workspace and settings file of its
  own, with local state, holding everything the proof creates.
- **The findings**: every task that changed on a second apply or in check
  mode, every Spack configuration difference, every row of the table above
  proved or not.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `site.yml` ends `failed=0` on a RHEL 10 head node; its second
  apply and its check-mode run change nothing, or each change is a recorded
  finding.
- **SC-002**: `node-image.yml` makes an image AWS reports `available`.
- **SC-003**: Every row of the "Not proved" table is marked proved, with the
  date and what was seen, or left not proved with the reason, in
  `exportit/MAP.md`.
- **SC-004**: After removal, nothing carrying the proof's prefix remains in the
  account, and the existing IOOS VPC and its subnets are as they were.
- **SC-005**: With `compare_with_script` left `false`, the procedure skips
  stage D and records the last row as deferred; with it `true`, stage D runs
  and every difference between the two nodes is listed.

## Assumptions

- The `noaa` session is fresh when the proof starts, and lasts or is refreshed
  between its stages.
- The build cache is no help (the site's holds only RHEL 8 packages), so the
  build is from source unless FR-011 says otherwise.

## Dependencies

- Done: the units and their repositories (moving day); the collection on
  Galaxy; JupyterHub kept as an option (stage 13).
- Spec 006 (the first boot runs the playbooks), merged first: its first boot
  is the one this node runs (FR-010).
- Specs 002 (the RHEL 10 build cache) and 004 (spack-stack) need this one's
  head node, or one like it.

## Out of Scope

- Changing `main.tf` of `csis-sandbox-terraform` in the unit itself: the
  working copy is edited, never the unit (spec 006 changes the unit).
- Running a model, or starting a compute node from the image (FR-014).
- Fixing what the proof finds: a finding becomes a spec of its own, in the
  unit it concerns.

## Outcome

Run on 2026-11-23 by the agent, box by box, from `LIVE-PROOF.md` version 2,
each AWS step on the operator's word; the procedure then corrected as
version 3 (`csis-sandbox-provisioning`). The tasks' records (T017 to T035)
hold each box's result; the logs stay on the operator's machine (FR-006).

**The node.** `c6i.8xlarge` (32 processors, so `spack_jobs` 31) on RHEL 10.2,
in the IOOS VPC's private subnet in `us-east-2b`, with
`csis-sandbox-provisioning` 0.0.3 and cloudflow 1.6.0b1. Its first boot,
spec 006's, ran in **34 minutes**: Spack compiled five packages (ESMF 8.9.1,
in 7 minutes, PETSc, HDF5, netCDF-C and parallel-netCDF), the system giving
Python, GCC and Intel's compilers and MPI. The procedure had said hours.

| Check | Result |
| --- | --- |
| The plan (A4) | 22 to add, 0 to change, 0 to destroy |
| The first boot (B2) | `failed=0`, at the third boot (findings 1 and 2) |
| The second apply (B3) | `failed=0`, 2 changed (findings 3 and 4) |
| Check mode (B4) | 0 to change |
| Spack's configuration (B5) | 5 differences (finding 5) |
| Module files (B6) | none rewritten |
| JupyterHub (B7) | answers `200`, with test settings (finding 6) |
| The image (C1, C2) | made, `available`, one snapshot (SC-002) |
| Stage D | skipped, `compare_with_script = false` (SC-005) |
| Removal (E1 to E5) | 22 destroyed; the image and snapshot deleted; nothing with the prefix found by each resource's own call; the VPC, subnets and route tables as they were (SC-004; finding 9) |

**The findings.** Each one that needs fixing is in `exportit/REMINDERS.md`,
to become a spec of its own in the unit it concerns (Out of Scope); the
procedure's are fixed in its version 3.

1. **A path RHEL 10 lacks** (`csis-sandbox-provisioning`). "Silence the
   subscription-manager dnf plugin" edited
   `/etc/dnf/pluginconf.d/subscription-manager.conf`, carried from the
   script's L34; RHEL 10 has `/etc/dnf/plugins/`. The script's `sed` failed
   unnoticed; the container test turns the task off. The first boot stopped
   there. **Fixed** in 0.0.3, on the operator's choice: the right path, edited
   only if it exists.
2. **A kept EFS volume gets no `/save`** (`csis-sandbox-terraform`). The node
   replaced to boot 0.0.3, on the same volume, stopped at cloudflow's clone:
   the first boot makes the `/save` link only on a new volume. The proof went
   on with a new volume (the operator's choice); the bug is a reminder.
3. **The update** changed on the second apply: eleven packages released
   since the first. Upstream; check mode then found nothing to change.
4. **The subscription-manager plugin** changed again on the second apply: the
   first apply's update, after the task, upgraded subscription-manager, and
   the file said `enabled=1` again. Check mode then found it unchanged. A
   reminder.
5. **Spack's configuration** differs from the container's in the site's
   mirror (the proof turns it on) and in four externals RHEL 10.2 has and the
   container lacks (`bison`, `flex`, `gettext`, `openssl`). Expected; no fix.
6. **JupyterHub's box** gave none of the six settings only a site can give,
   and the role refused, as it should. Run with the container test's values;
   the box now names them.
7. **The drivers' kernel** (`csis-sandbox-provisioning`): the update installed
   RHEL 10.3's kernel without a reboot, and the EFA and Lustre drivers were
   installed for the running 10.2 kernel. Whether they load on the image's
   kernel is not proved. A reminder.
8. **OpenTofu and the SSO profile**: the AWS provider cannot read the `noaa`
   profile's single sign-on session, which the CLI can; every OpenTofu box
   now exports the session's temporary credentials first.
9. **Removal's checks**: the tagging index still listed four deleted
   resources minutes after; a route table's associations come back in no
   fixed order; other users change the subnets' free-address counts. Box E4
   now asks each resource by its own call, and box E5 sorts and sets the
   counts aside.

**The "Not proved" table.** In `exportit/MAP.md`: RHEL and AWS, the first
boot, the drivers' and the tuning profile's installation, the build, the
module files and the image are proved; that the drivers load on the image's
kernel is not (finding 7); the comparison with a node built the old way is
deferred by the flag (FR-018). The site mirror's list is applied.

## Carried From

Stage 15, planned 2026-11-14 and paused 2026-11-15, now in the ATTIC
(`ATTIC/SPECS/STAGE-15.md`), as a pointer for a person reading; this spec
stands without it.
