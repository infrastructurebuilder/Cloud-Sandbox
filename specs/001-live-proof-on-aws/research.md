# Research: The live proof on AWS

Each item records a decision, why, and what else was weighed. It builds on
spec 006's plan (the first boot) and was written on 2026-11-21, after the
operator's answer that this node runs spec 006's real first boot.

## R1. Where the working copy's changes live

**Decision**: a directory of the unit, `csis-sandbox-terraform/proof/`, holds
every file the proof adds to its working copy: `backend_override.tf` (local
state), `proof_override.tf` (the boot's two changes, R3; the SSH rule left
out, R5), `proof.tf` (the flag and, when it is `true`, the second node, R7),
`proof.tfvars.example` (every setting, with the VPC and subnet left to be
filled in), and `ssm-agent.sh`. Stage A copies the unit to a working
directory and these files into it. `proof/` is tested in the unit with
`tofu test` and mocked providers.

**Rationale**: the spec forbids changing the unit's `main.tf` (Out of Scope)
but the edits must be reviewed and repeatable, not typed into a shell.
OpenTofu's override files change a module without editing it. Kept beside
the module they override, they are checked by the same pinned OpenTofu,
where a drift in `main.tf` would break them visibly.

**Alternatives considered**: the edits as `sed` lines in `LIVE-PROOF.md` (the
old page's way; untested, and fragile against every change to `main.tf`);
the files beside `LIVE-PROOF.md` in `csis-sandbox-provisioning` (that unit
has no OpenTofu to test them with).

## R2. Local state and a workspace of its own

**Decision**: `backend_override.tf` sets `terraform { backend "local" {} }`;
stage A runs `tofu init`, then `tofu workspace new live-proof`; every later
box first checks `tofu workspace show` prints `live-proof`.

**Rationale**: FR-003: never a shared bucket (the account's
`cloud-sandbox-tfstate` returns 403 anyway). The workspace check before each
apply or destroy keeps a box from acting on another sandbox.

## R3. The proof's first boot

**Decision**: `proof_override.tf` overrides `local.user_data` (spec 006's
local) with: `ssm-agent.sh` (install and start the SSM agent if `systemctl
is-active amazon-ssm-agent` does not answer), then the unit's rendered
template cut just before its `## Create the node image` section, with the
extra variable of R9, then a line logging that the image is left for stage
C. A `tofu test` asserts the cut
point exists once, that the result contains `ansible-pull` and the cloudflow
install, and not `node-image.yml`.

**Rationale**: the operator's answer (FR-010): the real first boot, with
exactly two changes, the agent first (FR-017) and the image left out
(FR-005). Cutting the rendered text at a section heading keeps every other
byte of the unit's boot; the test makes a renamed heading fail loudly
instead of producing a node that makes an image unasked.

**Alternatives considered**: a `make_node_image` variable in the unit's
template (a change to spec 006 for the proof's sake); a second template for
the proof (a copy to keep in step).

## R4. Reaching the node

**Decision**: the role's managed policies, set in `proof.tfvars`, are the
module's list with `arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore`
added. Your local machine's `session-manager-plugin` is checked in box A1.
The node is reached with `aws ssm start-session --target <id>`; files and
`ssh` go through SSM's `AWS-StartSSHSession` document, with the proof's key
pair, as `ec2-user`. The SSM agent reaches its endpoints through the
subnet's NAT.

**Rationale**: FR-017. The node has no public address (the module makes no
Elastic IP when a subnet is given) and no inbound rule (R5).

## R5. No inbound rule

**Decision**: `proof_override.tf` overrides the network interface's security
groups to the module's base and EFS groups only, so `ssh_ingress` is not
attached; `allowed_ssh_cidr_list` is set to `[]` to satisfy the variable.

**Rationale**: FR-017: no inbound rule is opened. An `ssh_ingress` group with
an empty list would still be a group named for SSH; leaving it unattached
and empty states what is meant. (Whether AWS accepts an ingress rule with no
CIDR is checked by the plan; if not, the override removes the rule.)

## R6. Finding the network, and proving it unchanged

**Decision**: box A3 looks the VPC up by its `Name` tag ("IOOS Cloud Sandbox
VPC") and lists its subnets with their route tables; a private subnet is one
whose default route goes to a NAT gateway. **The decision box** proposes the
private subnet in the module's availability zone (`us-east-2b`), or the first
private subnet if none is there. The IDs go into the working copy's
`proof.tfvars`, never into a repository (FR-006). Before the first apply and
after the last removal, `aws ec2 describe-vpcs`, `describe-subnets` and
`describe-route-tables` for that VPC are saved and compared; the plan must
show only additions (FR-003, FR-008).

**Rationale**: SC-004 asks that the VPC and its subnets be "as they were";
the module never manages them (it reads them as data), so a plan cannot show
them changing, and the before-and-after comparison is the check.

## R7. The flag `compare_with_script`

**Decision**: `proof.tf` declares `variable "compare_with_script"` (bool,
default `false`), set in `proof.tfvars`. When `true`, it adds a second
instance (same type, subnet, groups, role and key), named with the proof's
prefix and `-script`, whose user data is `ssm-agent.sh` followed by the
unit's `init_template.tpl` (spec 006 keeps it) rendered with `sandbox_version
= "ca0604a4a27355b330353c7ded8a1ae00a7e24a6"`, the original at the units'
baseline, and cut before its image step in the same way. Stage D compares the
two nodes. With `false`, nothing is added, stage D's boxes are skipped, and
the last row of the "Not proved" table is recorded as deferred.

**Rationale**: FR-013 and SC-005; the old template already clones the
original and checks out `$BRANCH`, so the baseline commit is reached with no
new script.

## R8. Hours of build, and the session

**Decision**: the build runs inside cloud-init on the node, not in a session
of your local machine, so an expiring AWS session or a closed SSM session
does not stop it. The procedure has a box that reports the boot's progress
(`tail` of `/root/setup.log` and the plays' recap) and can be run again; FR-001's
check opens every stage. Stage B's by-hand runs (second apply, check mode)
are started with `nohup … &` and read back the same way.

## R9. The settings `site.yml` reads

**Decision**: `spack_cache_only` stays `-1`, the playbooks' default (FR-011).
`spack_site_mirror` is turned on (FR-012) by the same override as R3: in the
rendered boot, `ansible-pull`'s `--extra-vars "sandbox_user=` becomes
`--extra-vars "spack_site_mirror=true sandbox_user=`. Stage B's by-hand runs
pass the same extra variable. `spack_jobs` follows from the 32 processors
(31), with no setting.

**Rationale**: no change to the unit's template or playbooks. An extra
variable given as `key=value` is the string `"true"`; the `spack` role's
condition is checked, when `proof/` is written, to read it as true (it does if
it tests the value's truth or applies `| bool`), and the `tofu test` asserts
the replaced text appears exactly once.

**Alternatives considered**: a `group_vars` file placed in the checkout
before `ansible-pull` (the checkout does not exist when the proof's first
lines run); turning the mirror on only in the second apply (the second apply
would then change things by design, hiding real findings).

## R10. Removal

**Decision**: stage E, each box asked first: `tofu destroy` (instances, EFS,
groups, role, key pair, interface); the image and snapshot by ID; then a
search with `aws resourcegroupstaggingapi get-resources` for the proof's
`Project` tag and `describe-images`/`describe-snapshots --owners self` for
its prefix, both empty; then R6's comparison of the VPC.

**Rationale**: FR-015 and SC-004.
