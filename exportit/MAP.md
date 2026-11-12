# Relocation map

This directory holds copies of the parts of Cloud-Sandbox that could
live in repositories of their own. Nothing here has been moved: the
original paths are untouched, and no other repository has been
created. This page says, for each unit, where its files come from,
where the copy is, and how the real relocation would be done.

The reasons behind the split are in
[INPROGRESS/ANALYSIS.md](../INPROGRESS/ANALYSIS.md); the work is
staged in [INPROGRESS/TODO.md](../INPROGRESS/TODO.md).

## Units

"State" is one of: *planned* (assigned, nothing copied), *copied*
(the copy exists and is checked against its source), *translated*
(rewritten in another form, with the originals carried beside it and
tests that hold the two together), *relocated* (never used here:
nothing leaves this repository).

| Unit | Copy | Source paths | Stage | State |
| --- | --- | --- | ---: | --- |
| `cloudflow` | [cloudflow/](cloudflow/) | `cloudflow/` without `plotting/`; root `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md` | [2](../INPROGRESS/STAGE-2.md) | copied 2026-11-12 |
| `cloudflow-plotting` | [cloudflow-plotting/](cloudflow-plotting/) | `cloudflow/plotting/`, `cloudflow/setup.py`, `cloudflow/plotting_reqs.reference`, `cloudflow/tests/test.plotting.py` | [2](../INPROGRESS/STAGE-2.md) | copied 2026-11-12 |
| cloudflow's documentation | `exportit/cloudflow/docs/` | `docs/source/` | [8](../INPROGRESS/STAGE-8.md) | planned |
| `sandbox-provisioning` | [sandbox-provisioning/](sandbox-provisioning/) | `scripts/setup-instance.sh`, `funcs-setup-instance.sh`, `environment-vars.sh`, `create_image.*`, four `scripts/system/` files they install | [3](../INPROGRESS/STAGE-3.md) | translated 2026-11-12 |
| `sandbox-terraform` | [sandbox-terraform/](sandbox-terraform/) | `terraform/` | [4](../INPROGRESS/STAGE-4.md) | copied 2026-11-12 |
| `sandbox-models` | `exportit/sandbox-models/` | `models/`, `patches/` | [5](../INPROGRESS/STAGE-5.md) | planned |
| `sandbox-configs` | `exportit/sandbox-configs/` | `job.configs/`, `cluster.configs/` | [6](../INPROGRESS/STAGE-6.md) | planned |
| `sandbox-ops` | `exportit/sandbox-ops/` | the rest of `scripts/`, `misc/`, `jupyterhub/` | [7](../INPROGRESS/STAGE-7.md) | planned |
| `cloud-sandbox` (umbrella) | `exportit/cloud-sandbox/` | `README.md`, `DEPLOYMENT.md`, `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`, `images/`, `TODO`, `.github/`, `LICENSE`, `.gitignore` | [8](../INPROGRESS/STAGE-8.md) | planned |
| not relocated | none | the built HTML under `docs/` (rebuilt from `docs/source/`), `docs/save/` | [8](../INPROGRESS/STAGE-8.md) | planned |

Every tracked top-level path of the repository appears in one row.
`scripts/` is divided file by file between two units; stages 3 and 7
record that division here.

## How a copy is made and checked

Each unit has a mapping file beside this page, `<unit>.map`. It is a
list of directives: `copy <source> <destination>`, `drop <source>`
for a file that is deliberately left behind, `new <path>` for a file
that exists only in the unit, and `covers <path>` to say that every
tracked file under a path must be assigned to some unit. Where two
directives match a file, the longer source wins; that is how
`cloudflow/plotting/` goes to one unit and the rest of `cloudflow/`
to another.

A correction to a copied file is not made by editing the copy. It is a
patch in `<unit>.patches/`, applied after the copy.

[tools/export.py](tools/export.py) reads those files. From the
repository root:

| Command | What it does |
| --- | --- |
| `just export [unit]` | Copies by the mapping file and applies the patches |
| `just export-check` | Fails unless every copied file equals its source plus the patches, every file in the unit is either copied or declared new, and every covered file is assigned. Part of `just test` |
| `just export-filter <unit>` | Prints the unit's mapping as directives for `git filter-repo` |
| `just export-prove <unit>` | Runs the extraction below on a throw-away clone and compares the result with the copy. Part of `just full-test` |

So a change to an original that is not copied again fails the bar, and
so does an edit made directly to a copy.

Some originals are tracked although `.gitignore` excludes them (the
notebooks). Their copies have to be added with `git add -f`; the check
says so when one is missing from the index.

## How a unit would really be relocated

The same steps for every unit. None of them has been carried out for
real; steps 2 and 3 are what `just export-prove` rehearses.

1. Create an empty repository for the unit, under the owner that will
   maintain it. Never under `ioos`, and never as a fork of
   `ioos/Cloud-Sandbox`.
2. Make a throw-away clone of this repository and rewrite it with
   `git filter-repo`, driven by the unit's directives, so that only
   the unit's paths remain and they sit at their new places. The
   unit's history comes with it. `filter-repo` rewrites the clone it
   runs in and removes that clone's `origin`, which is the safeguard
   against pushing rewritten history back to where it came from.
3. Check that no remote is left.
4. Apply the unit's patches, one commit each, and add the files that
   exist only in the copy (README, build file, `Justfile`, tests) as a
   further commit.
5. Add the new repository as the clone's only remote and push.
6. In Cloud-Sandbox, on a feature branch, delete the relocated paths
   and leave a pointer to the new repository.
7. The units that depend on it refer to it by version from then on.

```sh
# From the Cloud-Sandbox checkout:
just export-filter UNIT > /tmp/UNIT.paths

git clone --no-local . /tmp/extract-UNIT
cd /tmp/extract-UNIT
uvx git-filter-repo --paths-from-file /tmp/UNIT.paths
git remote -v            # must print nothing
git remote add origin git@github.com:OWNER/UNIT.git
git push -u origin HEAD:main
```

History is followed along the paths the files have today. A
`workflow/` directory existed until 2020-03-31, the day `cloudflow/`
first appears; that first month of history is not carried unless the
path is added to the directives.

## cloudflow

Copied on 2026-11-12 by [stage 2](../INPROGRESS/STAGE-2.md). The
project's own description is
[cloudflow/README.md](cloudflow/README.md).

### Where each file goes

From [cloudflow.map](cloudflow.map): 188 files copied, 2 left behind.

| Source | In the unit | Files |
| --- | --- | ---: |
| `cloudflow/cluster/` | `src/cloudflow/cluster/` | 9 |
| `cloudflow/job/` | `src/cloudflow/job/` | 63 |
| `cloudflow/services/` | `src/cloudflow/services/` | 6 |
| `cloudflow/utils/` | `src/cloudflow/utils/` | 4 |
| `cloudflow/workflows/` | `src/cloudflow/workflows/` | 59 |
| `cloudflow/tests/` except `test.plotting.py` | `legacy-tests/` | 6 |
| `cloudflow/notebooks/` | `notebooks/` | 22 |
| `cloudflow/notes/`, `cloudflow/somenotes/` | `notes/`, `notes/somenotes/` | 5 |
| `cloudflow/docs/`, the three `.md` files in `cloudflow/`, root `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md` | `docs/` | 7 |
| `cloudflow/cron_nosofs.sh`, `cloudflow/cron_rand_nosofs.sh` | `examples/cron/` | 2 |
| `cloudflow/python_minimal_requirements.txt`, `pip_freeze.reference`, `cloudflow_miniforge3_installation.yml` | `requirements/` | 3 |
| root `setup.py`, `setup-plotting.sh` | `legacy/` | 2 |
| `cloudflow/__init__.py` | left behind: empty, and `cloudflow` has to be a namespace (see below) | |
| `cloudflow/README.md` | left behind: empty; the unit has a new README | |

### What is new

`README.md`, `LICENSE` (a copy of the repository's), `pyproject.toml`,
`uv.lock`, `Justfile`, `.python-version` and `tests/`.

`pyproject.toml` replaces both `setup.py` files. It names the
distribution `cloudflow`, version `1.6.0b0` (the root `setup.py` said
`1.6.0b`), and registers a `cloudflow` command that runs
`workflow_main.py`'s `main`. Its dependencies are what the code
imports; the lower bounds are the versions in
`python_minimal_requirements.txt`.

### Decisions that shaped it

- **Layout:** the package is under `src/`.
- **Plotting is a second distribution.** Both install into one
  `cloudflow` namespace, because the copied code says
  `from cloudflow.plotting import ...`. A namespace shared by two
  distributions cannot have an `__init__.py`, which is why the empty
  one is left behind.
- **The Lambda functions stay in the package**, in
  `src/cloudflow/cluster/`, as today.

### Corrections made in the copy

`ruff` found 13 undefined names in the copied code. The operator chose
to correct them. Each correction is a patch in
[cloudflow.patches/](cloudflow.patches/); nothing else in the copied
files differs from the originals.

| Patch | File | What was wrong | Correction |
| --- | --- | --- | --- |
| 01 | `cluster/AWSCluster.py` | `except WaiterError` with no import | Import it from `botocore.exceptions` |
| 02 | `job/ADCIRCReanalysis.py` | `{APP}` in an error message | `{self.APP}` |
| 03 | `job/ROMSHindcast.py` | `{this.configfile}` | `{self.configfile}` |
| 04 | `services/NFSScratchDisk.py` | `{mountpath}` in a warning | `{self.mountpath}` |
| 05 | `workflows/tasks.py` | `raise ... from e` where no exception is in scope | The `from e` is removed |
| 06 | `workflows/workflow_main.py` | `postconf`, never assigned, passed to two flows | `conf`, the cluster description from the command line. A judgement: it is the only description available there. See defect 1 below |
| 07 | `workflows/archived/old.scratch_mount_flows.py` | `storage_service` and `notebook` used without being set; `result` used after both branches return | The assignment its sibling function already has; the commented-out placeholder restored; the unreachable lines removed. This file is Prefect 1 code that cannot be imported |

### Defects found and left as they are

These are in the originals and therefore in the copy. They are
recorded so that the real relocation can deal with them.

1. `workflow_main.py` calls `flows.reanalysis_flow`, `flows.plot_flow`
   and `flows.diff_plot_flow`. None of the three exists in `flows.py`,
   so the job types `adcircreanalysis`, `plotting` and `plotting_diff`
   fail.
2. Four modules cannot be imported. `utils/testutils.py` imports
   `modelUtil` as a top-level module; `workflows/scripts/random_ofs.py`
   reads `/com/nos/current.fcst` when loaded; the two Lambda functions
   read their settings from the environment when loaded. The list and
   the reasons are in
   [cloudflow/tests/test_modules.py](cloudflow/tests/test_modules.py).
3. Both cron scripts start `./workflows/nosofs_qops.py`, which exists
   only as `workflows/archived/old.nosofs_quasi_ops.py`.
4. 651 `ruff` findings remain in the copied Python (664 before the
   corrections), and it is not type-checked. `just test` holds the
   copied code to: compiles, imports, no undefined names.
5. The tests ran against Prefect 3.9.2, the newest that satisfies the
   lower bound. The requirement files pin 3.6.29 and the provisioning
   scripts install 3.7.8. Every module imports under 3.9.2; no flow
   was run.

### What would have to change for real independence

The copied code still assumes it sits in a Cloud-Sandbox checkout.
[cloudflow/tests/outward_references.json](cloudflow/tests/outward_references.json)
counts every such place per file, and a test fails if one is added.

| Kind | Count | What to do |
| --- | --- | --- |
| `sys.path` changed when a module is imported | 36 in 30 files | Delete; an installed package needs none |
| Configuration addressed as `../job.configs`, `../cluster.configs` | 8 in 5 files | Take paths as given; document the two file formats in `sandbox-configs` |
| `Cloud-Sandbox` by name, in paths and comments | 11 in 8 files | Replace with the package's own location or a setting |
| A person's home directory | 4 in 3 files | `fcst_launcher.sh` sets `JOBDIR=/home/mmonim/...`; `testscratch.py` reads `/home/centos/...`; remove |
| `from python_examples import ...` in `tasks.py` | 2 | Import it as `cloudflow.workflows.python_examples` |
| `push_pyEnv` uploads `../dist/*.tar.gz` | 1 | Decide how compute nodes get the package; today they get a hand-built source distribution |
| Links inside the copied documents | not counted | `CLOUDFLOW.md` points at `./cloudflow/docs/...`; fix after the move |

### What it expects from the other units

- **`sandbox-configs`:** a cluster description and a job description,
  as JSON files, by path. The keys are whatever `cluster/` and `job/`
  read; [stage 6](../INPROGRESS/STAGE-6.md) writes that schema down.
- **`sandbox-provisioning`:** a shared filesystem with `/save`, `/com`
  and `/ptmp`; Intel MPI and the modules the launchers load; a Prefect
  server; and Python with cloudflow installed. Today provisioning
  installs cloudflow's dependencies from its own list; after a
  relocation it would install the `cloudflow` distribution.
- **`sandbox-models`:** model executables and module files where the
  launcher scripts look for them.
- **`sandbox-terraform`:** the security groups, subnet, key name and
  placement group that a cluster description names.
- **AWS:** credentials, and a DynamoDB table named in the cluster
  description. `AWSCluster` refuses to start without it; the two
  Lambda functions and `scripts/weekly_summary.nu` read the same
  table. The table is made by hand and its name is configuration
  (operator, 2026-11-12).

### Extraction

`just export-prove cloudflow` passed on 2026-11-12: the rewritten
clone holds the same 188 files, with 112 commits of history (the
repository had 176 before this work). `just export-filter cloudflow` prints the 56 directives.

Order matters once: extract `cloudflow-plotting` first, or at least
publish it first, because cloudflow depends on it. In
`pyproject.toml` the dependency is a relative path
(`../cloudflow-plotting`); at a real relocation it becomes a version.

Afterwards Cloud-Sandbox would delete `cloudflow/` and the five root
files, `scripts/funcs-setup-instance.sh` would install the
distribution instead of a hand-kept list, and `docs/source/conf.py`
would document the installed package
([stage 8](../INPROGRESS/STAGE-8.md)).

The name `cloudflow` has not been checked against any package index.
Nothing is published.

## cloudflow-plotting

Copied on 2026-11-12 by [stage 2](../INPROGRESS/STAGE-2.md). The
project's own description is
[cloudflow-plotting/README.md](cloudflow-plotting/README.md).

From [cloudflow-plotting.map](cloudflow-plotting.map): 10 files.

| Source | In the unit | Files |
| --- | --- | ---: |
| `cloudflow/plotting/` | `src/cloudflow/plotting/` | 7 |
| `cloudflow/tests/test.plotting.py` | `legacy-tests/test.plotting.py` | 1 |
| `cloudflow/plotting_reqs.reference` | `requirements/plotting_reqs.reference` | 1 |
| `cloudflow/setup.py` | `legacy/setup.py` | 1 |

New: `README.md`, `LICENSE`, `pyproject.toml`, `uv.lock`, `Justfile`,
`.python-version` and `tests/`. `pyproject.toml` replaces
`cloudflow/setup.py`, which built a distribution called `plotting`,
version 0.3.1, from a directory that the code never imported under
that name. The new distribution is `cloudflow-plotting`, the same
version, and provides `cloudflow.plotting`.

One correction, in
[cloudflow-plotting.patches/](cloudflow-plotting.patches/):
`plotting/hlfs.py` catches `ClientError` without importing it; the
import is added.

Left as it is: `hlfs.py` is an exported notebook that runs
`main('hlfs.config')` when it is imported, so it is a script and not a
module. What it imports is the `hlfs` extra. `legacy-tests/test.plotting.py`
imports `plotting`, the old name, and needs model output under `/com`.

It expects nothing from the other units. `cloudflow` depends on it.

`just export-prove cloudflow-plotting` passed on 2026-11-12: the same
10 files, with 14 commits.

## sandbox-provisioning

Translated on 2026-11-12 by [stage 3](../INPROGRESS/STAGE-3.md). The
project's own description is
[sandbox-provisioning/README.md](sandbox-provisioning/README.md).

This unit is not a copy of anything. It is Ansible that does what
`scripts/setup-instance.sh` does. The scripts it replaces travel with
it, unchanged, so that every task can name the lines it replaces and
the tests can compare the two.

### Where its files come from

From [sandbox-provisioning.map](sandbox-provisioning.map): 9 files.

| Source | In the unit |
| --- | --- |
| `scripts/setup-instance.sh`, `funcs-setup-instance.sh`, `environment-vars.sh`, `create_image.sh`, `create_image.py` | `legacy/`, unchanged, as the reference the tests read |
| `scripts/system/tmux.conf` | `roles/base_system/files/tmux.conf` |
| `scripts/system/.vimrc` | `roles/user_shell/files/vimrc` |
| `scripts/system/prefect-server.service` | `roles/prefect_server/files/prefect-server.service` |
| `scripts/system/profile.d.zippy_efa.sh` | `roles/efa_driver/files/zippy_efa.sh` |

Three role files are text that the script writes with `tee` or
`echo`: `mpi_ssh/files/sandbox-local-net.conf`,
`intel_oneapi/files/oneAPI.repo` and `hpc_tuning/files/tuned.conf`. A
test requires each to equal the script's lines byte for byte.

The other 84 files under `scripts/` stay with `sandbox-ops`
([stage 7](../INPROGRESS/STAGE-7.md)). That includes
`scripts/system/etc.ssh.ssh_config.d/sandbox-local-net.conf`, which
nothing installs and whose rules differ from the script's.

### Function to role

`site.yml` imports the roles in the order `setup-instance.sh` calls
the functions; a test checks the order.

| Role | Function, lines of `funcs-setup-instance.sh` | Named tasks and blocks |
| --- | --- | ---: |
| `sandbox_paths` | `setup_paths`, 264-299 | 5 |
| `user_shell` | `setup_aliases`, 1518-1560 | 3 |
| `base_system` | `setup_environment`, 20-165 | 29 |
| `prefect_server` | `setup_prefect-server`, 219-260 | 10 |
| `mpi_ssh` | `setup_ssh_mpi`, 1340-1443 | 5 |
| `efa_driver` | `install_efa_driver`, 498-589 | 13 |
| `fsx_lustre_client` | `install_fsx_driver`, 1042-1079 | 4 |
| `python_user_env` | `install_python_modules_user`, 1210-1249 | 1 |
| `spack` | `install_spack`, 630-704 | 9 |
| `intel_oneapi` | `install_intel_oneapi_dnf` and `add_spack_site_external`, 884-963 and 708-733 | 7 |
| `spack_environment` | `create_spack-environment` and `build_spack-environment`, 737-766 and 770-826 | 8 |
| `hpc_tuning` | `configure_optimizations`, 169-214 | 4 |
| `node-image.yml` | `setup-instance.sh` 52-75, `create_image.sh`, `create_image.py` | 14 |

Every task carries `# Replaces <script> L<n>` or `# New: <why>`.
[tests/test_traceability.py](sandbox-provisioning/tests/test_traceability.py)
fails if a task has neither, if the lines it names lie outside its
role's function, or if a line of the scripts that does something is
neither replaced nor listed with its reason in
[tests/not_carried.yml](sandbox-provisioning/tests/not_carried.yml)
(ten entries).

### Variable to variable

[group_vars/all.yml](sandbox-provisioning/group_vars/all.yml) holds
each of the 21 variables that `environment-vars.sh` exports, under a
lower-case name, with the script's name in a comment.
[tests/test_parity.py](sandbox-provisioning/tests/test_parity.py) runs
the script in `bash` and the playbook's variables through
`ansible-playbook`, and compares the results. It covers every version,
the build-job count for 1, 2, 3, 8 and 96 processors, the three cache
settings, the pip list, both dnf package lists, the Intel modules,
Spack's externals, providers, settings and specs, and the Lustre
repository edits for three kernels.

Values the script takes from its surroundings became variables too:
the login user (`sandbox_user`, `ec2-user`), the EFS mount and
directories, and the prompt's site name.

### The script's accidents, and what was done with each

The operator chose to keep the script's behaviour, accidents
included, and to write each one down.

| What the script does | Here |
| --- | --- |
| Sets `EFA_MINAMAL`, tests `EFA_MINIMAL`, so the minimal EFA install always runs | `efa_driver_minimal: true`; both branches are translated |
| `SPACK_CACHEONLY=-1`, so Spack never uses binary caches and compiles everything | `spack_cache_only: -1` |
| Exports `SPACK_MIRROR`, `SPACK_KEY_URL`, `SPACK_KEY`; nothing uses them | Kept as variables; nothing uses them |
| Updates every package and builds the drivers without a reboot | The same; the `efa_driver` role prints a warning when the running kernel is not the newest installed |
| Turns off the Lustre repository's signature check | The same |
| Installs a Prefect server that does not start (FastAPI too new) | **Corrected:** `fastapi<0.155` (operator's decision) |
| `alternatives --set python`, which its own comment says fails | Run, with failure allowed |
| Writes the module search path into `/etc/environment-modules/modulespath` before the package that owns that file is installed, "only once" | The same order and the same once; the write may fail as it does in the script, and the container test reports whether the line arrived. In the container it did not |
| Edits `/etc/dnf.conf` | The same file. It does not exist on AlmaLinux 10, where the edit does nothing; this was not checked on RHEL |
| Its tcsh guard can never match, so the aliases are appended on every run; `ulimit`, ssh rules and the authorised key are also appended every run | Each line written once |
| A second `spack mirror add spack-public` with no scope, which always stops with "already exists" on Spack v1.2.0 | Not carried; reason in `not_carried.yml` |
| `tuned-adm profile network-latency`, then its own profile thirty lines later | Only the second switch |
| `create_image.py` uses region `us-east-2` whatever the node's region | Not carried: `node-image.yml` uses the node's own region (decision 5) |
| `create_image.py` snapshots every attached volume and uses the first | Only the root volume |
| A failed step still ends with a node image registered | Stops at the first failure; SELinux is turned back on and the Prefect server restarted in any case |

### What it expects

From **sandbox-terraform**: a RHEL 10 x86_64 head node, the EFS volume
mounted at `/mnt/efs/fs1` with `/save` linked to it, the IAM role
that allows snapshots and image registration (today
`AmazonEC2FullAccess`), and the `ami_name` and project tag. The
playbook checks the operating system and the mount, and stops if
either is wrong.

Provides: what the script provides. The software under `/save` (Spack,
the environment, module files) reaches compute nodes through the EFS
mount; everything else through the node image.

### The first-boot script

[init_template.ansible.tpl](sandbox-terraform/init_template.ansible.tpl)
(written in stage 3, moved to the Terraform unit in stage 4) is
`terraform/init_template.tpl` with its last step replaced. It
installs `ansible-core`, runs `ansible-pull` against the provisioning
repository at a version, then runs `node-image.yml`. It stops before
the image if the playbook fails. Terraform would have to pass two more
values, `provisioning_repo` and `provisioning_version`;
[stage 4](../INPROGRESS/STAGE-4.md) owns that change. It still clones
Cloud-Sandbox, because cloudflow runs from that checkout.

### Found while testing

- **The script's Prefect server does not start today.** `pip install
  prefect==3.7.8` brings in FastAPI 0.162. The server of Prefect 3.7.8
  fails at import with any FastAPI from 0.155 on (`Body() got an
  unexpected keyword argument 'min_items'`); 0.139 to 0.154 work. The
  unit's systemd file restarts it every five seconds without end. This
  is the script's behaviour on any node built now. By the operator's
  decision (2026-11-12) the role installs Prefect with
  `fastapi<0.155`: the one deliberate departure from the script,
  undone by setting `prefect_server_extra_requirements: []`.
- **On Spack v1.2.0, `spack-public` already exists** in Spack's
  defaults, as a source-only mirror. The script's add creates a binary
  mirror of the same name in the site scope, which takes precedence.
- **The two `compiler find` steps undo each other.** Run without the
  Intel modules, the `install_spack` step removes the Intel compilers
  that `install_intel_oneapi_dnf` registered; that function then adds
  them back. The script does this on every second run. The `spack`
  role loads the Intel modules when they exist, so a second run
  changes nothing.

### How it was tested, and what was not

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| Syntax, `ansible-lint` production profile, `shellcheck`, `ruff`, `pyright` | `just test` | pass |
| Traceability and parity with the scripts (310 tests) | `just test` | pass |
| Eight roles (all but the four below) applied with `ansible-pull` to an AlmaLinux 10 container, twice; the second run must change nothing; the result is checked | `just full-test` | pass: 49 changes, then 0 |
| `efa_driver`, `fsx_lustre_client`, `spack_environment`, `hpc_tuning`, `node-image.yml` | nowhere | **not proved**: kernel modules, hours of compiling, kernel settings and AWS |
| Anything on RHEL, or on AWS | nowhere | **not proved** |
| The first-boot script | nowhere | **not proved**: it needs a real EFS volume |
| Whether the playbook leaves the same node the script does | nowhere | **not proved** |

[docs/LIVE-PROOF.md](sandbox-provisioning/docs/LIVE-PROOF.md) is the
procedure that would settle the last four rows. It costs a head node
for several hours. It has not been run either.

Two guesses in the untested roles are marked where they are made. The
`efa_driver` role reads the installer's record in
`/opt/amazon/efa_installed_packages` to skip a second install; if the
record's form differs, the installer simply runs every time, as in the
script. The `spack_environment` role reports a change in module files
by hashing Spack's default module directory; if the files are
elsewhere, it reports no change but still regenerates them.

### What a real relocation would change

- Create the repository, extract with `just export-filter
  sandbox-provisioning`, and keep `legacy/` until the live proof has
  been run, then delete it with the tests that read it.
- In Cloud-Sandbox: replace `terraform/init_template.tpl` with the
  first-boot script, pass the two new values, and delete the five
  scripts and the nine sibling entry scripts that are now tags.
- The nine sibling scripts are not translated. Three of them call
  functions that exist nowhere.

`just export-prove sandbox-provisioning` passed on 2026-11-12: the
nine source files, with 15 commits of history.

## sandbox-terraform

Copied on 2026-11-12 by [stage 4](../INPROGRESS/STAGE-4.md). The
project's own description is
[sandbox-terraform/README.md](sandbox-terraform/README.md).

### Where its files go

From [sandbox-terraform.map](sandbox-terraform.map): all 22 files of
`terraform/`, unchanged, to the root of the unit. The copy tool
learned to place a directory at a unit's root (`copy terraform/ ./`)
for this; the extraction directive is `terraform/==>`.

By the operator's decision everything is kept, including the example
settings and the old copies; the README sorts them into module,
examples, policies, helpers, sketch and history. `mysettings.tfvars`
holds placeholders already (addresses like `72.0.162.256`, a dummy
key). `config.s3.tfbackend` names one site's state bucket,
`cloud-sandbox-tfstate`.

New: `README.md`, `LICENSE`, `Justfile`, `pyproject.toml`, `uv.lock`,
`.python-version`, `tests/`, and
[init_template.ansible.tpl](sandbox-terraform/init_template.ansible.tpl).

### The first-boot template

Written in stage 3 and moved here in stage 4, because it is rendered by
Terraform's `templatefile()`. By the operator's decision it sits beside
the copied `init_template.tpl` and `main.tf` is not changed. The README
gives the change that would switch over: two variables,
`provisioning_repo` and `provisioning_version`, and the new file name
in the head node's `user_data`.
[tests/test_template.py](sandbox-terraform/tests/test_template.py)
renders both templates through `terraform console`: the old one with
the five values `main.tf` passes, the new one with those five plus the
two new ones, and it fails if either new value is left out. So the
change in the README is complete, as far as the template goes.

### What it provides: the interface

The values a cluster description for cloudflow needs, and where each
comes from:

| Key in a cluster description | Comes from |
| --- | --- |
| `region` | `var.preferred_region` |
| `key_name` | `var.key_name`; output `key_name` |
| `sg_ids` | the three security groups `base_sg`, `ssh_ingress`, `efs_sg`; output `aws_security_groups` |
| `subnet_id` | the head node's subnet; output `aws_subnet` |
| `placement_group` | output `aws_placement_group` |
| `image_id` | not Terraform: `node-image.yml` in `sandbox-provisioning`, on the head node |
| `table_name` | configuration: an existing table, made by hand, named by the operator (see below) |
| `nodeType`, `nodeCount`, `tags`, `vm_retry_delay`, `vm_max_retries`, `platform` | the person who writes the description |

Today the first four reach a cluster description by hand: Terraform
writes them as a JSON fragment into `deployment_info.txt`, and
`scp.terraform.output.sh` copies that file to the head node.

**Found:** nothing in the repository creates the DynamoDB table that
`AWSCluster` refuses to start without, or deploys the two Lambda
functions that terminate nodes left running. The role is given
`AmazonDynamoDBFullAccess_v2`; the table and the functions are made by
hand.

**Decided (operator, 2026-11-12):** the table stays made by hand and
is *supplied as configuration*. This unit does not create it; a split
passes its name in, the same way as `key_name`. What a real split
should add is a variable for the table name, so that the IAM policy
can be narrowed from `AmazonDynamoDBFullAccess_v2` to that one table,
and an output that carries the name into the cluster description
beside the other four values. The Lambda functions still have no
owner.

It expects nothing from the other units. `sandbox-provisioning` runs on
the node it creates.

### How it is checked

The operator chose `terraform`, at 1.9.8 through tfenv, and to
validate what can be validated and count the rest. No test plans,
applies or calls AWS.

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| Terraform 1.9.8 is what runs | `just test` | pass |
| The root module and `remote-state/` validate | `just test` | pass |
| `fmt -check` would rewrite exactly the nine recorded files | `just test` | pass |
| Both templates render with what `main.tf` passes, the new one with two more values | `just test` | pass |
| `pipeline/` and `modules/` still fail to validate, for the recorded reason | `just full-test` | pass |
| Extraction with history | `just full-test` | the same 22 files, with 44 commits |

Things noticed and left as they are:

- The root module pins the AWS provider to `~> 3.47` (it resolves to
  3.76.1, the last 3.x). `remote-state/` pins nothing and gets 6.x.
- `random` and `local` are used but not declared in
  `required_providers`.
- OpenTofu 1.12 accepts `variables.tf` as formatted; Terraform 1.9.8
  does not. Both validate both modules.
- The policy files are not used by the module, which attaches six AWS
  managed policies, `AmazonEC2FullAccess` among them.

### What a real relocation would change

- Extract with `just export-filter sandbox-terraform`.
- Make the two-variable change from the README and point
  `provisioning_repo` at the relocated `sandbox-provisioning`.
- Decide where the site's settings and backend file live: they would
  no longer sit in a shared repository.
- In Cloud-Sandbox: delete `terraform/` and update `DEPLOYMENT.md`
  ([stage 8](../INPROGRESS/STAGE-8.md)).

## sandbox-models

Planned. [Stage 5](../INPROGRESS/STAGE-5.md) fills this section.

## sandbox-configs

Planned. [Stage 6](../INPROGRESS/STAGE-6.md) fills this section.

## sandbox-ops

Planned. [Stage 7](../INPROGRESS/STAGE-7.md) fills this section.

## cloud-sandbox (the umbrella)

Planned. [Stage 8](../INPROGRESS/STAGE-8.md) fills this section and
closes the map with the order of the relocations.
