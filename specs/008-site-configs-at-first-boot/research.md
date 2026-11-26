# Research: The first boot puts the site's descriptions on the head node

Each item records a decision, why, and what else was weighed. Written on
2026-11-25, after specs 006 and 007 were planned and 002 was built.

## R1. The settings

**Decision**: three variables in `csis-sandbox-terraform`'s main module, all
default `null`:

- `configs_repo`: the repository in SSH form, validated as
  `git@github.com:<owner>/<repo>.git` or
  `ssh://git@ssh.github.com:443/<owner>/<repo>.git` when set;
- `configs_version`: the tag; required when `configs_repo` is set;
- `configs_secret_arn`: an `arn:aws:secretsmanager:` ARN; required when
  `configs_repo` is set.

A plan with `configs_repo` and without either of the others fails, naming the
missing one. With `configs_repo` unset, the other two are ignored.

**Rationale**: FR-001 and FR-003. A deploy key works only over SSH, so the URL
is checked where the mistake can be seen, before anything is built, as spec
007 does for its `deploy_key` mode.

**Alternatives considered**: one object variable (less readable in a settings
file); a token as a second mode (spec 007 offers one for the playbooks; the
operator chose a deploy key here, and nothing asks for more).

## R2. Where the links go (the clarification of 2026-11-25)

**Decision**: the clone in `/save/$RUNUSER/sandbox-configs`; links named
`job.configs` and `cluster.configs` to its two directories in
`/save/$RUNUSER/cloudflow/src/` and in `/save/$RUNUSER/Cloud-Sandbox/`. In
cloudflow's checkout, the two names are added to `.git/info/exclude`, so that
`git status` there stays clean.

**Rationale**: the guides run `workflow_main.py ../cluster.configs/…
../job.configs/…` from `/save/$RUNUSER/Cloud-Sandbox/cloudflow`, a link to
`/save/$RUNUSER/cloudflow/src/cloudflow` (spec 006). A program's working
directory is the real one, so `..` is `/save/$RUNUSER/cloudflow/src/`. Tried on
2026-11-25 with links at `Cloud-Sandbox/` only: the shell's `ls
../job.configs` and Python's `open('../job.configs/x')` both failed, and
`os.getcwd()` printed the real directory. A test of the unit holds the links to
this (`tests/test_links.py`: a tree like the node's in a temporary directory,
a program opening `../job.configs/<file>` from the cloudflow link).

**Alternatives considered**: changing the guides' commands to absolute paths
(FR-006 keeps them); links in one place only (serves only one kind of path).

## R3. The key on the node

**Decision**: as spec 007's research R3 to R5, with one difference: the
clone runs as `$RUNUSER`, so the directory under `/run` (made with `mktemp
-d`, mode 0700) is handed to `$RUNUSER` before the key is written into it
(mode 0600), and the clone runs as `sudo -u $RUNUSER env GIT_SSH_COMMAND=…
git clone`. Tracing is off from reading the secret until the directory is
removed, which is right after the clone, before the links and the plays; a
`trap` removes it on any earlier exit. The AWS CLI is installed when either
spec 007's access or this clone needs it, unless `aws --version` answers.
GitHub's published host keys are pinned in a known-hosts file in the same
directory; `StrictHostKeyChecking=yes`.

**Rationale**: FR-003, FR-004 and SC-003: the key is in memory-backed storage
for the few seconds of one clone, readable by the one user who clones, never
traced, and gone before an image could be made. The clone as `$RUNUSER`
leaves the files owned by the user who runs the jobs.

**Alternatives considered**: cloning as root and `chown -R` after (the
clone's files briefly root's, and a second step that can fail); reusing spec
007's directory (it is removed after `ansible-pull`, later than this clone
should keep a key).

## R4. Where in the first boot

**Decision**: right after cloudflow's clone and spec 006's `cloudflow` link,
before the playbooks are fetched. A secret that cannot be read, or a clone
that is refused, stops the boot with a line naming what failed ("Fetching the
site's descriptions FAILED"), `exit 1`, before any image (FR-004).

**Rationale**: FR-002 ("after cloudflow and before the plays"); the links need
cloudflow's checkout to exist.

## R5. The guides that name the old paths

**Decision**: each gains a note (FR-006) in its own unit, the commands left as
they are. Found on 2026-11-25 by a search for `../job.configs/` and
`../cluster.configs/`:

| Unit | Guide |
| --- | --- |
| `csis-cloud-sandbox` | `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md` |
| `cloudflow` | `docs/CLOUDFLOW_MODEL_EXECUTION_INSTRUCTIONS.md`, `docs/CLOUDFLOW_PYTHON_MODEL_EXECUTION_INSTRUCTIONS.md` |
| `csis-model-liveocean` | `LIVEOCEAN-MODEL.md`, `README` |
| `csis-model-nosofs` | `NOSOFS-MODELS.md` |
| `csis-model-secofs` | `README.md` |
| `csis-model-ucla-roms` | `README` |
| `csis-model-ufscoastal` | `README` |
| `csis-sandbox-configs` | `README.md` |

The note says: on a head node these paths reach the site's descriptions in
`/save/$RUNUSER/sandbox-configs`, through the links the first boot makes, and
only when the deployment set `configs_repo` and its key (FR-008).

**Rationale**: the spec's "about a dozen guides in six units" was an
estimate; this is the list. A test in each unit is not wanted for one note;
the task that writes them searches again and records the result.

## R6. The node's permission

**Decision**: a second policy on the head node's role,
`aws_iam_role_policy.configs_secret`, `count` on `configs_repo` being set,
allowing `secretsmanager:GetSecretValue` on exactly `configs_secret_arn`,
beside spec 007's `aws_iam_role_policy.provisioning_secret`.

**Rationale**: FR-005: the role reads only the secrets this and spec 007 name.
Two policies, each counted on its own setting, leave spec 007's resource and
tests as they are.

**Alternatives considered**: one policy listing both ARNs (changes spec 007's
resource and its tests for no gain).

## R7. The tag the first boot clones

**Decision**: a new tag of `csis-sandbox-configs` (0.0.2, from its `develop`),
cut on the operator's word before the proof; `configs_version` names it.

**Rationale**: `0.0.1` (2026-11-17) predates spec 005's split: its
`job.configs/` held 9 files, `develop` holds 4, the rest repaired, retired to
`attic/` or moved to cloudflow.

## R8. Tests without AWS

**Decision**: in `csis-sandbox-terraform`:

- `tests/configs.tftest.hcl`, mocked: unset, no `configs_secret` policy and the
  user data spec 007's; set, one policy on that ARN alone; `configs_repo`
  without `configs_version` or `configs_secret_arn` fails naming it; an HTTPS
  `configs_repo` fails saying it must be SSH.
- `tests/test_template.py`: rendered with the three set, in order: the
  cloudflow clone, `set +x`, the directory under `/run` handed to `$RUNUSER`,
  `get-secret-value --secret-id <arn>`, the pinned host keys,
  `StrictHostKeyChecking=yes`, the clone as `$RUNUSER` at the tag into
  `/save/$RUNUSER/sandbox-configs`, the directory removed, `set -x`, the four
  links, the two `exclude` lines, then the playbooks; a `trap`; no
  `accept-new`; the failure line and `exit 1`. Rendered unset: the golden file
  of spec 007's `none` (unchanged, SC-002).
- `tests/test_links.py`: R2's tree; a program opening `../job.configs/<file>`
  from the cloudflow link reads the site's file, and so does the absolute
  `Cloud-Sandbox/job.configs/<file>`.

**Rationale**: FR-007. The real clone, and SC-003's search for the key, need a
head node.

## R9. The proof on AWS

**Decision**: a head node built as spec 001's stages A and B, with the three
settings; the operator makes the key, adds it to `csis-sandbox-configs`, and
puts its private half in a secret, each on the operator's word; then the
clone, the links (a `workflow_main.py --help`-free check: `ls` and a Python
`open` through each path), and a search of the node for the key's text
(`grep -rF` over `/`, `/run`, the cloud-init logs and the EFS volume); then the
node removed (stage E). The secret and the deploy key stay, for the
deployments that follow, unless the operator says otherwise.

**Rationale**: SC-001 and SC-003. Whether this rides another spec's head node
(as spec 009's proof rides spec 004's) is the operator's choice when it comes;
the tasks keep it a step of its own.
