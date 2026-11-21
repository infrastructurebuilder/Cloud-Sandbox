# Research: The first boot reads a private playbooks' repository

Each item records a decision, why, and what else was weighed. It builds on
spec 006's plan (`specs/006-first-boot-runs-playbooks/`), whose template this
spec extends.

## R1. How the secret is named, and how a missing one fails the plan

**Decision**: two variables. `provisioning_access`, a string with default
`"none"` and a validation allowing only `none`, `deploy_key` and `token`.
`provisioning_secret_arn`, a string with default `null`, whose validation
requires it to be a Secrets Manager ARN when `provisioning_access` is not
`none` (OpenTofu 1.9 and later let a variable's validation read another
variable; the unit pins 1.13.9).

**Rationale**: an ARN is exact in an IAM policy; a secret's name is not (AWS
appends a random suffix to the ARN, so a policy written from a name needs a
wildcard, which would also match another secret of a similar name). A
validation fails the plan with its own message, which a `tofu test`
`expect_failures` can check without AWS (FR-001, FR-002, SC-004's plan half).

**Alternatives considered**: the secret's name with a `-??????` wildcard in
the policy (wider than FR-004's "that one secret"); one variable holding mode
and secret together (harder to validate and to read in `DEPLOYMENT.md`).

## R2. The node's permission

**Decision**: an `aws_iam_role_policy` on the module's head-node role
(`aws_iam_role.sandbox_iam_role`), with `count = provisioning_access == "none"
? 0 : 1`, allowing `secretsmanager:GetSecretValue` on exactly
`provisioning_secret_arn`. The secret is encrypted with the account's
default key for Secrets Manager, which needs no `kms:Decrypt` grant;
`DEPLOYMENT.md` says so, and that a secret under a key of its own needs that
grant added by the operator.

**Rationale**: FR-004: that one secret, and nothing with `none`. The role is
the one the module creates for each deployment (spec 001's "new role"), so
no existing role changes. The module's managed policies grant no Secrets
Manager action, so this policy is the only path to the secret.

**Alternatives considered**: a managed policy such as
`SecretsManagerReadWrite` (every secret in the account); a resource policy on
the secret instead of the role (the secret is the operator's, outside
Terraform, FR-003).

## R3. Reading the secret on the node

**Decision**: when `provisioning_access` is not `none`, the first boot
installs the AWS CLI v2 with AWS's own installer (as it installs EFS's
utilities with theirs), unless `aws --version` already answers, and reads the
secret with `aws secretsmanager get-secret-value --secret-id <arn> --query
SecretString --output text`, written straight to a file. With `none`, nothing
is installed.

**Rationale**: the playbooks, which would install Python and boto3, have not
run yet; the CLI is the smallest thing that signs the request with the
instance's role. Whether the RHEL 10 image already carries it is checked when
the template is written, and recorded; the `aws --version` test makes the
template right either way.

**Alternatives considered**: `curl` to the Secrets Manager endpoint (needs a
SigV4 signer); fetching the secret in a playbook (the playbooks are what the
secret is needed to fetch).

## R4. Where the credential lives on the node, and for how long

**Decision**: in a directory made with `mktemp -d` under `/run` (memory, not
disk), mode 0700, owned by root; the secret in a file there, mode 0600. The
boot turns tracing off (`set +x`) from reading the secret until it is
removed, and removes the directory right after `ansible-pull` returns,
passing or failing, with a `trap … EXIT` as well, so a failure part-way also
removes it. The node image is made after that removal.

**Rationale**: FR-005 and SC-002: nothing on the node holds the credential
afterwards. The template runs with `set -x`, whose trace goes to the cloud-init
log; any line that expanded the secret would put it there. `/run` is a
`tmpfs`, so the file never reaches the root volume the image is made from.

**Alternatives considered**: an environment variable holding the secret
(inherited by every child process, readable in `/proc` for the process's
lifetime, and printed by `set -x` where it is set); `/root/.ssh` (on disk, and
in the image if removal failed).

## R5. Cloning with a deploy key

**Decision**: the operator gives `provisioning_repo` in SSH form
(`git@github.com:<owner>/<repo>.git`, or
`ssh://git@ssh.github.com:443/<owner>/<repo>.git` where port 22 is closed).
The template writes GitHub's published host keys, for `github.com` and for
`[ssh.github.com]:443`, into a known-hosts file in the same temporary
directory, and sets, for the clone and for `ansible-pull` only,
`GIT_SSH_COMMAND="ssh -i <key> -o IdentitiesOnly=yes -o
UserKnownHostsFile=<file> -o StrictHostKeyChecking=yes"`. A validation fails
the plan if the mode is `deploy_key` and the URL is not in SSH form.

**Rationale**: FR-006: pinned keys, not accepted on first use. `ansible-pull`
runs `git` through Ansible's `git` module, which passes the environment on
when no key file of its own is given, so one setting serves both fetches;
this is checked when the template is written, against Ansible's `git` module
as installed by the boot, and if it does not hold, `ansible-pull` is given
`--private-key` with the same file. The port-443 form is the edge case of a
private subnet whose NAT allows only HTTPS.

**Alternatives considered**: `StrictHostKeyChecking=accept-new` (first use);
rewriting an HTTPS URL to SSH inside the template (surprising; the URL the
operator gives is the one used).

## R6. Cloning with a fine-grained token

**Decision**: `provisioning_repo` stays in HTTPS form. For the clone and for
`ansible-pull` only, git is given a credential helper through the
environment (`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=credential.helper`,
`GIT_CONFIG_VALUE_0` a shell function that prints `username=x-access-token`
and `password=` followed by the token file's contents). The token is read by
the helper when git asks for it; it is never in the URL, a command's
arguments, the environment or `.git/config` (FR-007). A refused clone's log
line says the token may have expired (User Story 3, scenario 3).

**Rationale**: environment-given configuration (git 2.31 and later) applies to
the one command and leaves the checkout's configuration as it was; the helper
reads a file, so the value appears in no process listing.

**Alternatives considered**: `https://x-access-token:<token>@github.com/…`
(the token in the URL, the process list and `.git/config`); `http.extraHeader`
(the token in the environment or the configuration).

## R7. `none` leaves spec 006's boot as it was

**Decision**: the template's new steps are inside `%{ if
provisioning_access != "none" ~}` … `%{ endif ~}` directives, written so that
`none` renders no text at all. A file in the unit's tests,
`tests/golden/first-boot.none.sh`, holds the user data spec 006's template
renders for fixed sample values; the test renders the template with `none`
and the same values and compares the two byte for byte.

**Rationale**: SC-001 and User Story 1: nothing changes for a public
repository. A byte comparison catches a stray blank line from a directive,
which a search for words would not.

**Alternatives considered**: a second template for private repositories (two
first boots to keep in step).
