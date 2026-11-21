# Research: The first boot runs the playbooks

Each item records a decision the plan rests on, why, and what else was
weighed. Read on 2026-11-21 from the units as they are on `develop`.

## R1. The four variables, and which have defaults

**Decision**: `variables.tf` gains `provisioning_repo`, `provisioning_version`,
`cloudflow_repo` and `cloudflow_version`, all four `type = string`,
`nullable = false` and **without a default**. `sandbox_version` is removed.

**Rationale**: FR-001 asks for no default on `provisioning_repo`, so that a
plan without it fails. The same reason holds for the other three: a version
cannot be guessed (each unit's tags are its own: `csis-sandbox-provisioning`
is at `0.0.1`, cloudflow at `1.6.0b0`), and a repository URL with a default
would be the one value a site forgets to change. Four required values, named
in one place (`DEPLOYMENT.md`, FR-005), are simpler than two required and two
defaulted.

**Alternatives considered**: a default for `cloudflow_repo`, the public
`https://github.com/infrastructurebuilder/cloudflow.git` (convenient, but a
site with its own fork would build from ours without noticing); keeping
`sandbox_version` (it named the original's branch, which is no longer cloned).

## R2. How cloudflow is put on the node

**Decision**: the first boot clones cloudflow at `cloudflow_version` into
`/save/$RUNUSER/cloudflow` (on the EFS volume, where the old checkout was),
over HTTPS with no credential, in the place where the template cloned
`ioos/Cloud-Sandbox`. After `site.yml` has succeeded, and before the node
image, it installs it for `$RUNUSER` with `python3 -m pip install --user
--no-deps --editable /save/$RUNUSER/cloudflow`.

**Rationale**:

- The unit is an installable package (`pyproject.toml`, the `cloudflow`
  command, `cloudflow.workflows.workflow_main:main`); the original was a
  directory run from its checkout. An editable install keeps one copy, on
  EFS, which compute nodes mount at the same path, and gives the command.
- `--no-deps`: the playbooks' `python_user_env` role already installs
  cloudflow's dependencies for `$RUNUSER` (prefect, dask, boto3 and the rest),
  pinned there; pip resolving them again could move a pin.
- After `site.yml`, because pip and that environment come from the plays.

**Alternatives considered**: a plain (non-editable) install (two copies of the
code, the installed one and the checkout the scripts are run from); cloning
only, no install (no `cloudflow` command, and the package not importable
outside its directory); a new playbook role for cloudflow (FR-002 puts it in
the template; a role is a change to `csis-sandbox-provisioning` that this spec
does not need).

## R3. What still names the old checkout's path

**Decision**: the first boot makes one compatibility link,
`/save/$RUNUSER/Cloud-Sandbox/cloudflow` → `/save/$RUNUSER/cloudflow/src/cloudflow`,
and nothing else is edited by this spec. Removing the link, once nothing
needs it, is a `REMINDERS.md` item.

**Rationale**: the spec's edge case asks for every reference in the template,
the playbooks and the cluster descriptions to be changed or listed. Searched
on 2026-11-21:

| Where | What | Outcome |
| --- | --- | --- |
| `init_template.ansible.tpl` | the clone of `ioos/Cloud-Sandbox` into `/save/$RUNUSER/Cloud-Sandbox` | **changed** (R2) |
| `csis-sandbox-provisioning` (roles, plays, `group_vars`) | none outside `legacy/` | nothing to change |
| `csis-sandbox-configs`' `cluster.configs/` | only tag values (`Project: IOOS-Cloud-Sandbox`, `Name: CORA-Cloud-Sandbox-node`), no path | nothing to change |
| `csis-sandbox-configs`' `job.configs/` | `CONFIGTMPL` paths such as `/save/ec2-user/Cloud-Sandbox/cloudflow/job/templates/…` (and some under other users' homes) | **stays**: the site's files (spec 005); the link makes the `ec2-user` ones resolve |
| cloudflow's scripts and examples | `$HOME/Cloud-Sandbox/cloudflow` in `run_liveocean.sh`, `liveocean_fallback.sh`, `examples/cron/`; a developer's path in `fcst_launcher.sh` | **stays**: cloudflow's own files, changed in cloudflow when it is next worked on; the link serves the `/save` form |
| model READMEs (`liveocean`, `ucla-roms`) | instructions that `cd` into `Cloud-Sandbox/cloudflow` | **stays**: documentation of those units |

The link works because the unit keeps the original's layout under
`src/cloudflow/` (`job/templates/`, `workflows/`, `cluster/`), which is where
the old `Cloud-Sandbox/cloudflow/` paths pointed.

**Alternatives considered**: editing the job descriptions and cloudflow's
scripts here (three more units for a "small" spec, and the job descriptions
are spec 005's to move and repair); no link (every `ec2-user` job description
breaks on the first new node).

## R4. A plan without AWS

**Decision**: two kinds of test, both without credentials.

1. `tests/firstboot.tftest.hcl`, run by `tofu test` with `mock_provider`
   blocks for `aws`, `random` and `local` and `command = plan`: the four
   values given, it asserts that the rendered user data names both
   repositories and both versions, contains `ansible-pull`, and does not name
   `ioos/Cloud-Sandbox`. The rendered text is a `local` (`local.user_data`),
   which `main.tf`'s `user_data` uses, so the assertion reads exactly what the
   instance is given.
2. A pytest, in the slow tests, that copies the module to a temporary
   directory with an override file giving it a `local` backend, runs
   `tofu init` (providers from the plugin cache) and `tofu plan -input=false`
   without `provisioning_repo`, and asserts a non-zero exit whose message names
   the variable (SC-001). OpenTofu checks required variables before it
   configures a provider, so no AWS call is made.

**Rationale**: `tofu test` ignores the S3 backend and can mock providers (spec
003 used the same, research R2 there), so the plan of acceptance scenario 3 is
a real plan of the real module. A missing required variable is an error of the
run, not a check `expect_failures` can catch, so it needs a plain `tofu plan`.

**Alternatives considered**: asserting on `aws_instance.head_node.user_data`
(the AWS provider 3.x stores a hash of user data; under a mock the value
passes through, but the test would then depend on that difference); a
validation block on `provisioning_repo` (an empty string is not "missing";
FR-001 asks for the plan to fail without the value).

## R5. `init_template.tpl`

**Decision**: it stays, unchanged and unused by `main.tf`. Its test changes
from "main.tf renders this template" to "this template still renders with the
values it names", and the header of `init_template.ansible.tpl` says which one
`main.tf` uses.

**Rationale**: it is a copied file of the original (`copy terraform/ ./`); a
later sync carries the original's changes to it, and a reader comparing the
two templates sees what changed. Deleting it is a choice for when the
original's own first boot is retired.

**Alternatives considered**: deleting it (loses the comparison, and the
sync would bring it back as a change to a file the unit no longer has).

## R6. A first boot that cannot clone

**Decision**: each clone (cloudflow, the playbooks) is checked as the
playbooks' clone already is (`if ! … then echo "… FAILED …" >> ~/setup.log;
exit 1`), naming what could not be fetched, before anything is applied.

**Rationale**: the edge case asks that the first boot fail visibly rather than
build nothing. The template already does this for the playbooks; the
cloudflow clone, today a bare `git clone`, gets the same.
