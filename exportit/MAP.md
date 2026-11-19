# Relocation map

This directory holds the parts of Cloud-Sandbox that can live in
repositories of their own, and since **moving day, 2026-11-17**, each of
them does: every unit below is a private repository on
`infrastructurebuilder`, and is kept here as a git submodule at the path
its copy had ([MOVINGDAY.md](MOVINGDAY.md) is the plan and its record).
Since **stage 22, finished 2026-11-19**, the originals are gone from
this repository's `develop`: `cloudflow/`, `scripts/`, `terraform/`,
`models/` and the rest were deleted one unit at a time, and every unit
owns its copied files (its mapping file says `owned`). This repository's
history and its `main`, the copy of the original, still hold them, at
`ca0604a`, which is every unit's baseline. The mapping files stay: they
say where each original file went, and a sync from a later original
(stage 23) is driven by them. This page says, for each unit, where its
files came from, where the unit is, and how it was made.

Much of what follows was written before moving day and says how a
relocation *would* be done; the three sections that describe the method,
the state and the order have been brought up to date, and the units' own
sections are left as the record of how each was made.

The reasons behind the split are in
[SPECS/ANALYSIS.md](../SPECS/ANALYSIS.md); the work is
staged in [SPECS/TODO.md](../SPECS/TODO.md).

## Units

"State" is one of: *planned* (assigned, nothing copied), *copied*
(the unit's files are checked against their sources), *translated*
(rewritten in another form, with the originals carried beside it and
tests that hold the two together), *relocated* (a private repository of
its own on `infrastructurebuilder`, kept here as a submodule),
*owned* (its originals deleted here; its copies are its own, and its
lineage alone holds it to the original). Every unit was relocated on
2026-11-17 and is owned since 2026-11-19.

| Unit | Copy | Source paths | Stage | State |
| --- | --- | --- | ---: | --- |
| `cloudflow` | [cloudflow/](cloudflow/) | `cloudflow/` (plotting included since 2026-11-13); root `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md` | [2](../SPECS/COMPLETED/STAGE-2.md) | copied 2026-11-12; relocated 2026-11-17 as `cloudflow` |
| cloudflow's documentation | [cloudflow/docs/sphinx/](cloudflow/docs/sphinx/) | `docs/source/` and the files that built it | [8](../SPECS/COMPLETED/STAGE-8.md) | copied 2026-11-12; relocated with cloudflow |
| `sandbox-provisioning` | [sandbox-provisioning/](sandbox-provisioning/) | `scripts/setup-instance.sh`, `funcs-setup-instance.sh`, `environment-vars.sh`, `create_image.*`, four `scripts/system/` files they install | [3](../SPECS/COMPLETED/STAGE-3.md) | translated 2026-11-12; relocated 2026-11-17 as `csis-sandbox-provisioning` |
| `sandbox-terraform` | [sandbox-terraform/](sandbox-terraform/) | `terraform/` | [4](../SPECS/COMPLETED/STAGE-4.md) | copied 2026-11-12; relocated 2026-11-17 as `csis-sandbox-terraform` |
| `model-<name>`, eight of them, and `model-common` | [model-adcirc-cora/](model-adcirc-cora/) and the others in [the model units](#the-model-units) | `models/`, `patches/` | [5](../SPECS/COMPLETED/STAGE-5.md) | copied 2026-11-12; relocated 2026-11-17 as `csis-model-<name>` and `csis-model-common` |
| `sandbox-configs` | [sandbox-configs/](sandbox-configs/) | `job.configs/`, `cluster.configs/` | [6](../SPECS/COMPLETED/STAGE-6.md) | copied 2026-11-12; relocated 2026-11-17 as `csis-sandbox-configs`, whole |
| `sandbox-ops` | [sandbox-ops/](sandbox-ops/) | the 15 files of `scripts/` and `misc/` still in use that `sandbox-provisioning` does not take: 14 operator tools and the Spack mirror's public key (16 until stage 11 took `spack-pubkey.sh`) | [7](../SPECS/COMPLETED/STAGE-7.md) | copied 2026-11-12; relocated 2026-11-17 as `csis-sandbox-ops` |
| `cloud-sandbox` (umbrella) | [cloud-sandbox/](cloud-sandbox/) | `README.md`, `DEPLOYMENT.md`, `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`, `images/sandbox-stack.png`, `TODO`, `.github/`, `LICENSE`, `.gitignore`; the attic: the superseded and dead files of `scripts/` and `misc/` | [8](../SPECS/COMPLETED/STAGE-8.md) | copied 2026-11-12; attic since 2026-11-13; relocated 2026-11-17 as `csis-cloud-sandbox` |
| not relocated | none | the built HTML under `docs/` (rebuilt from `docs/source/`), `docs/save/`; this work's own `SPECS/`, `PLAN.md`, `Justfile` | [8](../SPECS/COMPLETED/STAGE-8.md) | dropped 2026-11-12, each with its reason in a mapping file |

Every tracked top-level path of the repository appears in one row.
`scripts/` is divided file by file between three units
(`sandbox-provisioning`, `sandbox-ops`, and the umbrella's attic);
stages 3 and 7 record that division here.

## How a copy is made and checked

Each unit has a mapping file beside this page, `<unit>.map`. It is a
list of directives: `copy <source> <destination>`, `drop <source>`
for a file that is deliberately left behind, `new <path>` for a file
that exists only in the unit, and `covers <path>` to say that every
tracked file under a path must be assigned to some unit. Where two
directives match a file, the longer source wins; that is how
`cloudflow/README.md` is dropped while the rest of `cloudflow/` is
copied.

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

Since moving day a unit's directory is a submodule, and nothing of this
changes: the mapping files and the patches are here, `just export`
writes into the submodule's working directory, and the check reads the
unit's files from the unit's own repository. What is new is where the
result is committed: in the unit's repository, after which this
repository records the unit's new commit (`git add exportit/<unit>`).
`just submodules-check`, part of `just test`, fails when a unit is not
checked out; `just submodules-pushed` fails when this repository records
a commit that is not yet on the unit's remote.

Since stage 22's step 0 (2026-11-18), the acceptance tests no longer read
the originals in the working tree, which stage 22 deletes: `just test`
runs `just export-baselines` (each unit against the original at its
baseline, read from this repository's history) in place of
`just export-check`, and `just full-test` runs `just export-lineage` (the
original at each unit's baseline, filtered, is a commit of the unit's
own history) in place of `just export-prove`. A unit whose originals are
deleted carries `owned` in its map: it owns its copied files, the
baseline check passes it by, and the lineage check alone holds it to the
original.

Some originals are tracked although `.gitignore` excludes them (the
notebooks). Their copies have to be added with `git add -f`; the check
says so when one is missing from the index.

## How a unit would really be relocated

**Carried out for all fifteen units on 2026-11-17, except step 6.** The
exact commands, with the gate after each, are the seven boxes of
[MOVINGDAY.md](MOVINGDAY.md#the-method-for-one-unit). What was planned
here, and what was done:

1. Create an empty repository for the unit, under the owner that will
   maintain it. Never under `ioos`, and never as a fork of
   `ioos/Cloud-Sandbox`. **Done:** private, on `infrastructurebuilder`,
   named `csis-<unit>` (`cloudflow` under its own name).
2. Make a throw-away clone of this repository and rewrite it with
   `git filter-repo`, driven by the unit's directives, so that only
   the unit's paths remain and they sit at their new places. The
   unit's history comes with it. `filter-repo` rewrites the clone it
   runs in and removes that clone's `origin`, which is the safeguard
   against pushing rewritten history back to where it came from.
   **Done.**
3. Check that no remote is left. **Done, as a gate.**
4. Apply the unit's patches, one commit each, and add the files that
   exist only in the copy (README, build file, `Justfile`, tests) as a
   further commit. **Done;** the result was compared with the copy,
   file for file, before anything was pushed.
5. Add the new repository as the clone's only remote and push.
   **Done:** `main`, `develop` and the first tag, by name; the rewritten
   copies of this repository's other branches and tags stayed behind.
6. In Cloud-Sandbox, on a feature branch, delete the relocated paths
   and leave a pointer to the new repository. **Done by
   [stage 22](../SPECS/STAGE-22.md), one unit at a time,
   2026-11-18 and 19,** after moving day had replaced each copy under
   `exportit/` with a submodule. The pointer is the submodule, and the
   root `README.md`.
7. The units that depend on it refer to it by version from then on.
   **Not yet:** no unit installs another from its repository.
   `units.toml` names each repository and its version.

The original sketch of the commands, kept for the record:

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

Copied on 2026-11-12 by [stage 2](../SPECS/COMPLETED/STAGE-2.md). The
project's own description is
[cloudflow/README.md](cloudflow/README.md).

### Where each file goes

From [cloudflow.map](cloudflow.map). Plotting was a unit of its own,
`cloudflow-plotting`, until 2026-11-13, when the operator folded it
back (see [Plotting, folded back](#plotting-folded-back)); the table is
as it is now.

| Source | In the unit | Files |
| --- | --- | ---: |
| `cloudflow/cluster/` | `src/cloudflow/cluster/` | 9 |
| `cloudflow/job/` | `src/cloudflow/job/` | 63 |
| `cloudflow/plotting/` | `src/cloudflow/plotting/` | 7 |
| `cloudflow/__init__.py` (empty) | `src/cloudflow/__init__.py` | 1 |
| `cloudflow/services/` | `src/cloudflow/services/` | 6 |
| `cloudflow/utils/` | `src/cloudflow/utils/` | 4 |
| `cloudflow/workflows/` | `src/cloudflow/workflows/` | 59 |
| `cloudflow/tests/` | `legacy-tests/` | 7 |
| `cloudflow/notebooks/` | `notebooks/` | 22 |
| `cloudflow/notes/`, `cloudflow/somenotes/` | `notes/`, `notes/somenotes/` | 5 |
| `cloudflow/docs/`, the three `.md` files in `cloudflow/`, root `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md` | `docs/` | 7 |
| `cloudflow/cron_nosofs.sh`, `cloudflow/cron_rand_nosofs.sh` | `examples/cron/` | 2 |
| `cloudflow/python_minimal_requirements.txt`, `pip_freeze.reference`, `cloudflow_miniforge3_installation.yml`, `plotting_reqs.reference` | `requirements/` | 4 |
| root `setup.py`, `setup-plotting.sh` | `legacy/` | 2 |
| `cloudflow/setup.py` | `legacy/plotting-setup.py`, renamed because `legacy/setup.py` is the root one | 1 |
| `cloudflow/README.md` | left behind: empty; the unit has a new README | |

### What is new

`README.md`, `LICENSE` (a copy of the repository's), `pyproject.toml`,
`uv.lock`, `Justfile`, `.python-version` and `tests/`.

`pyproject.toml` replaces both `setup.py` files. Its dependencies
include plotting's (matplotlib, netCDF4, numpy, Pillow, pyproj), since
`workflows/job_tasks.py` imports `cloudflow.plotting` when it is
loaded, and an `hlfs` extra for `plotting/hlfs.py`. It names the
distribution `cloudflow`, version `1.6.0b0` (the root `setup.py` said
`1.6.0b`), and registers a `cloudflow` command that runs
`workflow_main.py`'s `main`. Its dependencies are what the code
imports; the lower bounds are the versions in
`python_minimal_requirements.txt`.

### Decisions that shaped it

- **Layout:** the package is under `src/`.
- **Plotting is part of the package**, as `cloudflow.plotting`, the way
  the code imports it. Stage 2 made it a second distribution sharing a
  `cloudflow` namespace; the operator folded it back on 2026-11-13.
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
  read; [stage 6](../SPECS/COMPLETED/STAGE-6.md) writes that schema down.
- **`sandbox-provisioning`:** a shared filesystem with `/save`, `/com`
  and `/ptmp`; Intel MPI and the modules the launchers load; a Prefect
  server; and Python with cloudflow installed. Today provisioning
  installs cloudflow's dependencies from its own list; after a
  relocation it would install the `cloudflow` distribution.
- **The model units:** model executables and module files where the
  launcher scripts look for them; [the install
  contract](#the-install-contract) lists every such path.
- **`sandbox-terraform`:** the security groups, subnet, key name and
  placement group that a cluster description names.
- **AWS:** credentials, and a DynamoDB table named in the cluster
  description. `AWSCluster` refuses to start without it; the two
  Lambda functions and `scripts/weekly_summary.nu` read the same
  table. The table is made by hand and its name is configuration
  (operator, 2026-11-12).

### Extraction

`just export-prove cloudflow` passed on 2026-11-12: the rewritten
clone held the same 188 files, with 112 commits of history; with
plotting and the documentation folded in, on 2026-11-13, 240 files and
114 commits (the
repository had 176 before this work). `just export-filter cloudflow` prints the 56 directives.

Afterwards Cloud-Sandbox would delete `cloudflow/` and the five root
files, `scripts/funcs-setup-instance.sh` would install the
distribution instead of a hand-kept list, and `docs/source/conf.py`
would document the installed package
([stage 8](../SPECS/COMPLETED/STAGE-8.md)).

The name `cloudflow` has not been checked against any package index.
Nothing is published.

### Plotting, folded back

From stage 2 to 2026-11-13 `cloudflow/plotting/` was a unit of its own,
`cloudflow-plotting`, by the operator's decision then: a second
distribution, version 0.3.1, that installed `cloudflow.plotting` into a
`cloudflow` namespace it shared with this one. On 2026-11-13 the
operator folded it back. The reasons: the code only ever imports it as
`cloudflow.plotting`; the workflows import it whenever they load, so
cloudflow could not run without it; and the second distribution's
model, `cloudflow/setup.py`, is close to an orphan. That file builds a
distribution called `plotting`, with a top-level `plotting` package that
no code imports. Only `setup-plotting.sh` installs it, and the root
`setup.py` lists it as a requirement.

What changed:

- `cloudflow/plotting/`, `cloudflow/plotting_reqs.reference` and
  `cloudflow/tests/test.plotting.py` are copied into this unit;
  `cloudflow/setup.py` goes to `legacy/plotting-setup.py`, renamed so
  that it does not overwrite the root `setup.py` in `legacy/`.
- `cloudflow/__init__.py`, left out while `cloudflow` was a namespace,
  is copied again: the package is a regular one, as in the original.
- The one plotting correction, the missing `ClientError` import in
  `hlfs.py`, is now `cloudflow.patches/09-hlfs-import-clienterror.patch`.
- Plotting's dependencies and its `hlfs` extra are cloudflow's; its
  tests are `tests/test_plotting.py`; the wheel test builds one wheel
  and checks that plotting is in it. Two more outward references are
  counted: `plot_roms.py` and `plot_fvcom.py` change `sys.path` when
  they load.
- `exportit/cloudflow-plotting/`, its map and its patch directory are
  gone, and so is its line in the umbrella's `units.toml`.

## sandbox-provisioning

Translated on 2026-11-12 by [stage 3](../SPECS/COMPLETED/STAGE-3.md). The
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

Stage 7 added the users and JupyterHub as two more roles: 16 more
files (15 under `scripts/`, 2 of them as role files, and
`jupyterhub/README.md` as `docs/JUPYTERHUB.md`), described in
[the ops section](#sandbox-ops). The other 69 files under `scripts/`
are in `sandbox-ops`. That includes
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
| `spack` | `install_spack`, 630-704 | 10 tasks, with 9 steps in two lists since stage 11 (9 tasks before) |
| `intel_oneapi` | `install_intel_oneapi_dnf` and `add_spack_site_external`, 884-963 and 708-733 | 5 tasks, with 4 steps in one list since stage 11 (7 tasks before) |
| `spack_environment` | `create_spack-environment` and `build_spack-environment`, 737-766 and 770-826 | 6 (8 before stage 9, 7 before stage 10) |
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
[stage 4](../SPECS/COMPLETED/STAGE-4.md) owns that change. It still clones
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
- **The two `compiler find` steps undo each other.** *(Corrected
  2026-11-14: they do not; see
  [stage 11](#spack-set-up-through-the-collection-stage-11).)* As
  recorded in stage 3: run without the Intel modules, the
  `install_spack` step removes the Intel compilers that
  `install_intel_oneapi_dnf` registered; that function then adds them
  back; the `spack` role loads the Intel modules when they exist, so a
  second run changes nothing. Tried again with the real oneAPI and Spack
  v1.2.0, detection never removes anything: without the modules it finds
  no Intel compiler and leaves the registered ones alone. What stage 3
  saw change between runs was the order in which Spack wrote
  `packages.yaml`, not what it said.

### How it was tested, and what was not

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| Syntax, `ansible-lint` production profile, `shellcheck`, `ruff`, `pyright` | `just test` | pass |
| Traceability and parity with the scripts (310 tests) | `just test` | pass |
| Eight roles (all but the four below) applied with `ansible-pull` to an AlmaLinux 10 container, twice; the second run must change nothing; the result is checked | `just full-test` | pass: 49 changes, then 0 |
| `spack_environment`'s `spack.yaml` (stage 9): an environment made with the script's commands and one written by the role's template, side by side with the real Spack v1.2.0, give the same manifest and the same merged `concretizer`, `modules` and `packages` | `just full-test` | pass (2026-11-13) |
| `spack_environment` through `spack_env` (stage 10), with `spack_environment_state: concretized`: ESMF and PETSc concretized with the real oneAPI and Spack v1.2.0, 36 packages, Intel's compilers and MPI among them; the second run changes nothing | `just full-test` | pass (2026-11-13) |
| `efa_driver`, `fsx_lustre_client`, `hpc_tuning`, `node-image.yml`, and building `spack_environment` and its module files | nowhere (the build and the module files are proved by the collection's own tests against the real Spack) | **not proved**: kernel modules, hours of compiling, kernel settings and AWS |
| Anything on RHEL, or on AWS | nowhere | **not proved** |
| The first-boot script | nowhere | **not proved**: it needs a real EFS volume |
| Whether the playbook leaves the same node the script does | nowhere | **not proved** |

[docs/LIVE-PROOF.md](sandbox-provisioning/docs/LIVE-PROOF.md) is the
procedure that would settle the last four rows. It costs a head node
for several hours. It has not been run either.

One guess in the untested roles is marked where it is made, and a second
was until stage 10. The
`efa_driver` role reads the installer's record in
`/opt/amazon/efa_installed_packages` to skip a second install; if the
record's form differs, the installer simply runs every time, as in the
script. The `spack_environment` role reports a change in module files
by hashing Spack's default module directory; if the files are
elsewhere, it reports no change but still regenerates them.

**That second guess is wrong the other way too** (found 2026-11-13 while
testing the `infrastructurebuilder.csis_spack` collection against the
real Spack v1.2.0): Spack writes into every module file the time it
wrote it (`## Module file created by spack (...) on 2026-11-13
11:00:30.218360`). Every refresh therefore changes every file, and the
role's "Regenerate the environment's module files" task reports a
change on every run, so a second run of `site.yml` is never "nothing
changed" once the environment is built. The collection's `spack_env`
module leaves that line out when it compares module trees. Since stage 10
the role uses the module, and the shell task is gone.

### The environment's spack.yaml, written whole (stage 9)

Until stage 9 the `spack_environment` role made the environment's
`spack.yaml` as the script does: `spack env create`, then one
`spack config add` per setting and one `spack add` per spec, each step
hashing the file before and after to say whether it changed. Now, by
the operator's decisions of 2026-11-13:

- **The file is a template.** `spack env create` still makes the
  environment when it is missing; then one `template` task writes
  `spack.yaml` whole, from two variables, and keeps the previous file
  beside it. Ansible reports the change itself, and `--check` and
  `--diff` work on it. The task replaces the script's L754-L762 and
  L775-L806, as the two shell tasks did.
- **`spack_environment_config`** replaces `spack_environment_settings`:
  a mapping in the shape of `spack.yaml` instead of three
  `config add` paths. It also holds `view: true` and
  `concretizer: unify: true`, which `spack env create` writes into a new
  file and the script keeps; without them the template's file would
  not be the script's.
- **Ansible owns the file.** An edit made by hand on the head node is
  overwritten; the backup is the only trace of it.

What is proved: `tests/test_parity.py` reads the script's three
`config add` lines as Spack does and holds the mapping to them;
`tests/test_spack_yaml.py` renders the template and holds it to the two
variables; and the container test makes both environments with the real
Spack and compares them (table above). Concretizing, building and the
module files are unchanged and run as before.

Found by that comparison: `spack add` does not store a spec as it is
typed but as Spack prints it. The script's
`esmf@8.9.1+pnetcdf+mpi ... %intel-oneapi-compilers@2024.2.1` lands in
its `spack.yaml` as `esmf@8.9.1+mpi+pnetcdf ... %oneapi@2024.2.1`:
variants sorted, and the compiler under its short name. The template
writes the specs as the role states them, so the two files differ in
text; the test compares the specs as Spack parses them, where they are
the same. The configuration sections hold the same data, but not the
same text: `spack config add` writes a list in flow style
(`[target=x86_64_v3]`) and the template in block style, so
`spack config get` prints them differently. The test compares what
Spack reads as data, not as text.

What is left for a module is what has to call Spack: concretize,
install, regenerate module files, push to a build cache. That is
[the collection](#ansible-collection-csis-spack-outside-this-repository)'s.

### Spack through the collection (stage 10)

By [stage 10](../SPECS/COMPLETED/STAGE-10.md), 2026-11-13, the role's three
shell tasks after the template (concretize, install, regenerate the
module files) are one task of the collection's `spack_env` module,
naming the script's L812, L817 and L820-L822 as the three did:

- **The Intel modules:** a task before it loads them once in bash, as
  the script's shell has them loaded, and hands the module only what
  that changed in the environment, through `environment:`. The module
  runs no shell.
- **Change and check mode:** a change is a new `spack.lock`, a spec
  installed, or module files that differ, leaving out the time Spack
  writes into them. `--check` concretizes a copy and says what would be
  installed.
- **New:** `spack_environment_state` (default `installed`; the container
  test sets `concretized`). Gone: `spack_environment_modules_root`, since
  the module asks Spack for its module roots, and `log.concretize`,
  which the module does not write.
- **The collection** comes from `requirements.yml`, at the tag `0.1.0` of
  its repository. `ansible-pull` installs no collections, so the
  first-boot template in `sandbox-terraform` now fetches the playbooks,
  installs `requirements.yml`, and then runs `ansible-pull`; the
  container test does the same.
- **Not proved in the container:** the build. Spack's fake installs leave
  `python-venv` without the `python3` that the rest of the ESMF and PETSc
  tree needs, so the container concretizes only.

### Spack set up through the collection (stage 11)

By [stage 11](../SPECS/COMPLETED/STAGE-11.md), 2026-11-14, planned as the
collection's stage 3, the shell that set Spack up is gone from the
`spack` and `intel_oneapi` roles. Each role hands a list of steps to the
`setup` role of `infrastructurebuilder.csis_spack` 0.3.0, applied as the
login user. The lists are in the roles' tasks files, where the shell
was, and each step names the lines of the script it replaces.

| Role | The script's lines | Now |
| --- | --- | --- |
| `spack` | L672-L673, L680, L691, L692, L699, L700: two `config add`, `compiler find`, `external find` twice, `mirror add`, `buildcache keys` | six steps: `config`, `detect` three times, `mirror`, `gpg_key` |
| `intel_oneapi` | L919-L937: load the modules, `compiler find`. L709-L732, L941-L955: two externals appended to `packages.yaml` by a here-document, five `config add`. L959: `buildcache keys` | four steps: `environment`, `detect` with `require`, `config` with one mapping (`intel_oneapi_spack_packages`), `gpg_key` |
| `spack` (new, off) | `spack-pubkey.sh` L8-L19, run by hand until now: fetch and trust the site mirror's key, `mirror add s3-mirror`, `buildcache keys` | three steps, applied only when `spack_site_mirror` is true |

What is different from the script, on purpose, each noted where it is:

- **The two settings are in the site scope.** The script's two
  `spack config add` lines have no `--scope`, so the install-tree padding
  and the Tcl modules were in the login user's `~/.spack`, and only that
  user had them. They are now in the site scope with everything else
  (the operator's decision). A head node built earlier also has the old
  copies in the user scope, which wins over the site scope. Since
  [stage 12](../SPECS/COMPLETED/STAGE-12.md) the `spack` role removes them
  where they hold what the site scope holds, and leaves, and reports,
  any value someone changed (`tasks/user_scope.yml`, then a `config` step
  of state `absent` in the user scope). Its tasks can go once no head
  node built before stage 11 is left ([REMINDERS.md](REMINDERS.md)).
- **A missing compiler is a failure.** Run without the Intel modules,
  `compiler find` finds nothing and says nothing, and the script goes on.
  The `detect` step requires `intel-oneapi-compilers` at `oneapi_version`.
- **A changed external is corrected.** The here-document skipped any
  package whose name was already in the file.
- **Module files** are regenerated when needed, not on every run
  (`refresh_modules: when_needed` in `spack_environment`; 0.2.0 of the
  collection changed its default, and the role now says which it wants).
- **The site mirror's key is trusted by its fingerprint**
  (`spack_key_fingerprint`), which is the key kept in
  `sandbox-ops/keys/` and what the address served on 2026-11-14. The
  script trusts whatever it downloads. The mirror goes to the site
  scope; the script's `mirror add` has no `--scope` either.

Gone with the shell: `spack_config_json` and `spack_fingerprint` (the
hash of Spack's whole configuration through `spack python -c`),
`intel_oneapi_spack_externals`, `intel_oneapi_spack_providers` and
`intel_oneapi_spack_packages_file`. `spack_key` stays, unused, because
the script exports it and every exported variable is held to the script.
`spack-pubkey.sh` moved from `sandbox-ops/bin/` to this unit's `legacy/`,
like the other scripts a role replaces; it does not go to the attic,
because the tests read it.

How it is held:

- **Traceability:** `tests/test_traceability.py` reads a step's comment
  as it reads a task's. Every line of `install_spack`,
  `install_intel_oneapi_dnf`, `add_spack_site_external` and
  `spack-pubkey.sh` that does something is replaced by a task or a step
  that names it, or is in `tests/not_carried.yml`.
- **Parity:** `tests/test_parity.py` reads the script's Spack commands
  and writes them as steps (two `config add` in a row are one `config`
  step; nothing else differs), and holds each list to them, in order.
- **In the container, with the real oneAPI:** the roles are applied
  twice from a fresh clone of Spack; the second run changes nothing, and
  a third pass of the three roles in check mode finds nothing to change.
  `tests/container/expected-spack-config.json` is what the shell roles
  left in this container's site and user scopes, dumped just before they
  were replaced; `compare-spack-config.py` holds what the new roles
  leave to it, as data, with the one decided difference stated in the
  script. Externals are compared by package name, because their versions
  are the image's; the versions the roles state themselves are checked
  against the variables.
- **Not proved:** the site mirror's list, which needs the site's bucket.
  Its first application is the live proof on AWS.

Found by the check-mode pass: **`spack_environment` could not be
previewed at all.** Its build task is asynchronous, for a build of
hours, and Ansible refuses a task that is both asynchronous and in
check mode; stage 10 said the role had check mode and had not run it.
The task is now synchronous when previewing, which builds nothing.

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

Copied on 2026-11-12 by [stage 4](../SPECS/COMPLETED/STAGE-4.md). The
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
[init_template.ansible.tpl](sandbox-terraform/init_template.ansible.tpl). Stage 8 added
[DEPLOYMENT.md](sandbox-terraform/DEPLOYMENT.md), the Terraform part of
the root `DEPLOYMENT.md`, and the screenshot it shows, copied from
`images/` to `docs/images/`.

### The first-boot template

Written in stage 3 and moved here in stage 4, because it is rendered by
Terraform's `templatefile()`. By the operator's decision it sits beside
the copied `init_template.tpl` and `main.tf` is not changed. The README
gives the change that would switch over: two variables,
`provisioning_repo` and `provisioning_version`, and the new file name
in the head node's `user_data`.
[tests/test_template.py](sandbox-terraform/tests/test_template.py)
renders both templates through `tofu console` (`terraform console` until 2026-11-13): the old one with
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

The operator chose, in stage 4, `terraform` at 1.9.8 through tfenv, and
to validate what can be validated and count the rest. On 2026-11-13 the
operator switched the unit to OpenTofu at its latest release, 1.13.9:
the licence question in `DEPLOYMENT.md` (Terraform after 1.5.7 is not
open source) decided it. `just init` fetches that version into the
unit's `.tofu/`, checked against the release's checksums, and the tests
run only that copy. No test plans, applies or calls AWS.

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| OpenTofu 1.13.9 is what runs | `just test` | pass (2026-11-13) |
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
- OpenTofu 1.13.9 and Terraform 1.9.8 both validate both modules and
  name the same nine unformatted files; OpenTofu 1.12 accepted
  `variables.tf`.
- Both modules now require OpenTofu 1.13.9, in a new `versions.tofu`
  each (2026-11-13, the operator's request). Not in `main.tf`:
  OpenTofu ignores `required_version` in `.tf` files and enforces it
  only in `.tofu` files, which a test proves by changing the version in
  a copy and watching `tofu init` refuse it. Terraform does not read
  `.tofu` files, so this guards against the wrong OpenTofu, not against
  Terraform.
- The policy files are not used by the module, which attaches six AWS
  managed policies, `AmazonEC2FullAccess` among them.

### What a real relocation would change

- Extract with `just export-filter sandbox-terraform`.
- Make the two-variable change from the README and point
  `provisioning_repo` at the relocated `sandbox-provisioning`.
- Decide where the site's settings and backend file live: they would
  no longer sit in a shared repository.
- In Cloud-Sandbox: delete `terraform/`; the root `DEPLOYMENT.md` goes
  to the umbrella's `history/` ([stage 8](../SPECS/COMPLETED/STAGE-8.md)).

## The model units

Copied on 2026-11-12 by [stage 5](../SPECS/COMPLETED/STAGE-5.md). By the
operator's decision there is one unit per model, and a ninth,
`model-common`, for what several of them share. Each unit's own
description is its `UNIT.md`: two of the models already have a
`README.md` of their own, so the new file needed another name, and all
nine use the same one.

### Where the files go

Every model directory goes, unchanged, to the root of its unit. The
counts are of shell scripts (a `#!` line naming `sh` or `bash`, or a
name ending in `.sh`) and of shellcheck 0.11.0's findings in them.

| Unit | Mapping file | Source | Files | Scripts | Findings |
| --- | --- | --- | ---: | ---: | ---: |
| [model-adcirc-cora](model-adcirc-cora/UNIT.md) | [map](model-adcirc-cora.map) | `models/adcirc-cora/`; `patches/adcirc-cora/` to `patches/` | 57 | 15 | 647 |
| [model-eccofs](model-eccofs/UNIT.md) | [map](model-eccofs.map) | `models/eccofs/` | 13 | 6 | 31 |
| [model-liveocean](model-liveocean/UNIT.md) | [map](model-liveocean.map) | `models/liveocean/` | 10 | 6 | 52 |
| [model-necofs](model-necofs/UNIT.md) | [map](model-necofs.map) | `models/necofs/` | 17 | 7 | 100 |
| [model-nosofs](model-nosofs/UNIT.md) | [map](model-nosofs.map) | `models/nosofs/` | 9 | 5 | 42 |
| [model-secofs](model-secofs/UNIT.md) | [map](model-secofs.map) | `models/secofs/` | 16 | 7 | 39 |
| [model-ucla-roms](model-ucla-roms/UNIT.md) | [map](model-ucla-roms.map) | `models/ucla-roms/` | 4 | 3 | 19 |
| [model-ufscoastal](model-ufscoastal/UNIT.md) | [map](model-ufscoastal.map) | `models/ufscoastal/` | 17 | 4 | 13 |
| [model-common](model-common/UNIT.md) | [map](model-common.map) | `models/modulefiles/`, `models/utils/`, `models/TODO`, `models/compilation.notes`, `models/mpiopts.note` | 6 | 0 | 0 |
| | | | **149** | **53** | **943** |

New in each unit: `UNIT.md`, `LICENSE` (a copy of the repository's),
`Justfile` and `tests/`. No patches: the copies are byte-identical,
and by the operator's decision their findings are counted, not fixed.

### What each recipe fetches, needs and installs

The detail, with the scripts that do each step, is in each `UNIT.md`.

| Model | Fetches from | Needs from provisioning | Installs to |
| --- | --- | --- | --- |
| adcirc-cora | `s3://ioos-cloud-sandbox/public/cora-adcirc/`: a built ADCIRC, a run tree, the 2018 forcing. ADCIRC's source is not fetched | `model-common`'s module file: Spack's oneAPI 2023.1, Intel MPI 2021.12.1, HDF5, NetCDF; `cmake` | `/save/$USER`; ADCIRC to `$ADCIRCHome/work` |
| eccofs | GitHub `asascience-open/NOSOFS-Code-Package` (`v3.6.6.dev`); fixed fields and forcing from `ioos-sandbox-use2` | its own module file: oneAPI 2023.1, MKL, Intel MPI 2021.12.1, NetCDF, METIS, libpng, NCEP libraries | `/save/$USER/nosofs.v3.6.6`, shared with nosofs |
| liveocean | GitHub `asascience/LiveOcean`, `parkermac/LO`, `asascience/LO_roms_user`, `parkermac/LO_roms_source_alt`, `myroms/roms`; data from `ioos-sandbox-use2` | its own module file: oneAPI 2023.1, MKL, netcdf-fortran | `/save/$USER/LiveOcean` |
| necofs | GitHub `FVCOM-GitHub/FVCOM` (`v4.4.8`); inputs from `ioos-sandbox-use2` | its own module file: oneAPI 2023.1, PETSc 3.21.1, METIS, NetCDF | `/save/$USER/necofs/NECOFS_v2.4/hindcast/FVCOMv4.4.8` |
| nosofs | GitHub `asascience-open/NOSOFS-Code-Package` (`v3.6.6.dev`); fixed fields from `ioos-sandbox-use2` or NCO `nwprod` | its own module file: as eccofs, plus parallel-netcdf and ParallelIO | `/save/$USER/nosofs.v3.6.6` |
| secofs | GitHub `jduckerOWP/schism` (`v5.13.0_NOS_Sandbox`); inputs from `ioos-sandbox-use2`, and from VIMS with a password | its own module file: Intel 2024.2.1, MKL, Intel MPI 2021.13 under `intel/...` names that Spack does not make, netcdf-fortran 4.6.2 | `/save/$USER/schism` |
| ucla-roms | GitHub `CESR-lab/ucla-roms`, default branch | Spack modules loaded in the scripts: oneAPI 2023.1, Intel MPI 2021.9.0, compression libraries, NetCDF | `/save/$USER/ucla-roms` |
| ufscoastal | GitHub `asascience-open/ufs-weather-model`, default branch, recursive; inputs from `s3://ioos-transfers/` | spack-stack 2.0 in `/save/environments/spack-stack.v2.0`; `gcc-toolset-13` | `/save/$USER/ufs-weather-model` |

Three recipes follow a branch head (`ucla-roms`, `ufscoastal`,
`liveocean`'s five repositories), so two builds a month apart need not
be the same model.

### The install contract

What cloudflow's launchers, in `cloudflow/workflows/`, expect to find
where a model was installed. The job's configuration names the
install (`SAVEDIR`, `EXEC`, `MODEL_DIR`, `ProjectHome`); the launcher
then looks inside it. Each row is one path a launcher uses, as the
launcher writes it. A check in
[tools/tests/test_model_units.py](tools/tests/test_model_units.py)
reads the launchers and fails if one uses a path that has no row here,
or if a row names a path no launcher uses any more.

| Launcher | Path | What must be there | Put there by |
| --- | --- | --- | --- |
| `fcst_launcher.sh` | `$SAVEDIR` | NOS ROMS and FVCOM models: the code package install; `secofs`: the directory holding the module file `intel_x86_64` (`module use -a $SAVEDIR`) | `model-nosofs`, `model-eccofs` (`nosofs.v3.6.6`); `model-secofs` (`/save/$USER/schism`) |
| `fcst_launcher.sh` | `$HOMEnos/jobs` | The code package's job scripts. `HOMEnos` is `$SAVEDIR`, `$SAVEDIR/LiveOcean` or `$SAVEDIR/WRF-ROMS-Coupled` | the code package, through `model-nosofs` and `model-eccofs`; `LiveOcean` through `model-liveocean` |
| `fcst_launcher.sh` | `$JOBDIR/fcstrun.sh` | The forecast script, `JOBDIR` being `$HOMEnos/jobs` | as the row above |
| `fcst_launcher.sh` | `$SAVEDIR/LiveOcean` | The clone of `asascience/LiveOcean`; `SAVEDIR` is the directory above it | `model-liveocean` |
| `fcst_launcher.sh` | `$SAVEDIR/WRF-ROMS-Coupled` | A coupled WRF-ROMS install for `wrfroms` | **nobody**: there is no recipe in the repository |
| `fcst_launcher.sh` | `$SAVEDIR/modulefiles` | `intel_x86_64.impi_2021.12.1`, for `necofs` | `model-necofs`: its own `modulefiles/`, in a checkout or a copy |
| `fcst_launcher.sh` | `$EXEC` | The model executable, by absolute path: `secofs` `$SAVEDIR/bin/pschism_...`, `necofs` `necofs_fvcom`; `adnoc` and `nyh-hindcast` default to a `roms` on `PATH` | `model-secofs`, `model-necofs`; the `TT` models by hand |
| `fcst_launcher.sh` | `$JOBDIR/fcstrun_adcirc_cluster.sh` | For `adcircofs`, with `JOBDIR` set to one person's home directory, `/home/mmonim/Cloud-Sandbox/cloudflow/workflows` | **nobody**: the script is not in the repository |
| `simple_launcher.sh` | `$SAVEDIR/modulefiles` | `intel_x86_64.impi_2021.12.1`, for `necofs_hot` and `necofs_cold` | `model-necofs` |
| `simple_launcher.sh` | `$EXEC` | `necofs_fvcom` or the tidal build's executable | `model-necofs` |
| `cora_launcher.sh` | `$PROJHOME` | The job's `ProjectHome`: the run tree, laid out like `model-adcirc-cora` | `model-adcirc-cora` (`cora-runs.tgz` from S3) |
| `cora_launcher.sh` | `$PROJHOME/TracksToRun` | The directory of `<year>.trk` files; the launcher touches one | `model-adcirc-cora` |
| `cora_launcher.sh` | `$PROJHOME/ERA5` | The run directories, `ERA5/<grid>/<year>` | `model-adcirc-cora` (`cora-runs.tgz`) |
| `cora_launcher.sh` | `$JOBDIR/common/submit.cloudflow.template` | `JOBDIR` is `$PROJHOME`; the launcher writes cloudflow's template here | `model-adcirc-cora` (`common/`) |
| `ufs_launcher.sh` | `$SAVEDIR/ufs-weather-model/tests` | The UFS regression tests, with `rt.sh` | `model-ufscoastal` |
| `ufs_launcher.sh` | `/save/$USER` | The default `SAVEDIR` | `model-ufscoastal`'s default too |
| `experiment_launcher.sh` | `$MODEL_DIR` | The experiment's run directory, passed on to a `*_run.sh` script | by hand: the job configuration |
| `experiment_launcher.sh` | `$EXEC` | The executable, passed on | by hand: the job configuration |
| `adcirc_basic_run.sh` | `$MODEL_DIR` | An ADCIRC run directory | by hand |
| `adcirc_basic_run.sh` | `$EXEC/adcprep` | `EXEC` here is a *directory* holding `adcprep` | an ADCIRC build: by hand, or `model-adcirc-cora`'s `buildadcirc.sh` |
| `adcirc_basic_run.sh` | `$EXEC/padcirc` | `padcirc`, in the same directory | as the row above |
| `fcstrun_adcirc_florence.sh` | `$PHOME/adcprep` | `PHOME` is `/save/adcirc-cg/work` | **nobody**: an old install |
| `fcstrun_adcirc_florence.sh` | `$PHOME/padcirc` | as the row above | **nobody** |
| `fcstrun_adcirc_florence.sh` | `/save/adcirc-cg/work` | An ADCIRC build | **nobody** |
| `fcstrun_adcirc_florence.sh` | `/save/adcirc-florence-input` | The Florence inputs | **nobody** |
| `fcstrun_adcirc_florence.sh` | `/save/adcirc-florence/tidalSpinup/fort.68.nc` | A tidal spin-up | **nobody** |
| `fcstrun_adcirc_florence.sh` | `/save/adcirc-ClusterRPS/fcst_adcirc_log.txt` | Where its log goes | **nobody** |
| `roms_basic_run.sh` | `$MODEL_DIR` | A ROMS run directory | by hand |
| `roms_basic_run.sh` | `$EXEC` | A ROMS executable | by hand |
| `ucla-roms_run.sh` | `$MODEL_DIR` | `/save/$USER/ucla-roms/Examples/Rivers_real` in the job configuration | `model-ucla-roms` |
| `ucla-roms_run.sh` | `$EXEC` | Its `roms` executable | `model-ucla-roms` (`testcase.sh`) |
| `schism_basic_run.sh` | `$MODEL_DIR` | A SCHISM run directory | by hand |
| `schism_basic_run.sh` | `$EXEC` | A SCHISM executable | by hand, or `model-secofs` |
| `fvcom_basic_run.sh` | `$MODEL_DIR` | An FVCOM run directory | by hand |
| `fvcom_basic_run.sh` | `$EXEC` | An FVCOM executable | by hand, or `model-necofs` |
| `dflowfm_basic_run.sh` | `$MODEL_DIR` | A D-Flow FM run directory | by hand |
| `dflowfm_basic_run.sh` | `$EXEC` | `dflowfm` | by hand: no recipe |
| `wrf_hydro_basic_run.sh` | `$MODEL_DIR` | A WRF-Hydro run directory | by hand |
| `wrf_hydro_basic_run.sh` | `$EXEC` | `wrf_hydro_NoahMP.exe` | by hand: no recipe |
| `model_basic_run.sh` | `$MODEL_DIR` | A run directory (the template for new models) | by hand |
| `python_basic_run.sh` | `$EXEC` | A Python interpreter, not a model | provisioning, or by hand |
| `python_mpi_basic_run.sh` | `$EXEC` | A Python interpreter with `mpi4py` | provisioning, or by hand |

Not in the table, because they belong to provisioning and not to a
model: seven `*_basic_run.sh` scripts and `ucla-roms_run.sh` load
Spack modules by hashed name from
`/mnt/efs/fs1/save/environments/spack.v0.22.5/share/spack/modules/linux-rhel8-x86_64`,
and `python_mpi_basic_run.sh` loads two more.

### Found

- **Module names carry Spack's build hashes** (`-3rbcwfi`,
  `-6nra3z4`, `-aimw7vu`, ...), in every model module file, in
  `model-common`, and in nine of cloudflow's run scripts. Three different hashes of
  the same oneAPI 2023.1 compiler are in use. `sandbox-provisioning`
  builds with Spack 1.2 on RHEL 10 and enables Tcl modules with
  Spack's default naming, so its hashes and its `linux-rhel10-...`
  paths will match none of them. A rebuilt sandbox needs either
  module names without hashes (a Spack modules projection), or every
  module file rewritten. This is the main thing that ties the model
  units to one particular sandbox.
- **Five setup scripts cannot create the directory they install into.**
  `mkdir -p $SAVEDIR | echo "Can not create $SAVEDIR"; exit 1` (in
  `eccofs/setup_eccofs.sh`, `liveocean/setup_LiveOcean.sh`,
  `nosofs/setup_nosofs.sh`, `nosofs/build_nosofs.sh`,
  `ufscoastal/setup.sh`) pipes instead of `||`, so when `SAVEDIR` is
  missing the script creates it, prints the error and exits 1 anyway.
  A second run works.
- **Recipes that assume their place in a Cloud-Sandbox checkout:**
  `adcirc-cora/buildadcirc.sh` (`../modulefiles`, now
  `model-common`), `adcirc-cora/install-adcirc-cora.sh` (installs three
  levels up), `eccofs/restart_date.sh` (`cd ../../cloudflow/utils`),
  `patches/adcirc-cora/reinstall-esmf-netcdf.sh` (sources
  `../../scripts/funcs-setup-instance.sh`, which provisioning
  replaces), and cloudflow's `job.configs/OFS/necofs.hindcast`, whose
  `SAVEDIR` is `.../Cloud-Sandbox/models/necofs`. After a split each
  needs a path given to it instead.
- **Installs with no recipe:** `WRF-ROMS-Coupled`, D-Flow FM,
  WRF-Hydro, the `TT` models, and the Florence ADCIRC run, and the
  `adcircofs` script in one person's home directory.
- **Paths fixed to one person:** `necofs/tidal_barotropic/build.sh`
  builds in `/save/patrick/...`; many job configurations name
  `/save/patrick` ([stage 6](../SPECS/COMPLETED/STAGE-6.md)).
- `liveocean/get_LO_ROMS.sh` defaults to `/save/$USER/liveocean`, and
  the rest of the recipe to `/save/$USER/LiveOcean`; it works only when
  `setup_LiveOcean.sh` exports `MODEL_DIR` first.
- `necofs/bin/makedepf90` is a built executable, tracked in git;
  `utils/readme.makedepf90` says where its source is.
- Four job templates in `adcirc-cora/common/` hold placeholders and do
  not parse as bash; they are recorded as templates.

### How they are checked

Every model unit runs the same harness,
`tests/check-scripts.sh`, and a check in the `tools` unit holds the
nine copies identical. Nothing is fetched, built or run.

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| The harness has no shellcheck findings | each unit's `just test` | pass, 9 units |
| Every script passes `bash -n`, and the 4 templates still fail it | each unit's `just test` | pass: 53 scripts |
| shellcheck's findings per script are as recorded in `tests/shellcheck.counts` | each unit's `just test` | pass: 943 findings |
| The harness finds a syntax error, a changed count, an unlisted script and a template that parses | `tools`' `just test` | pass |
| Every launcher path has a row in the install contract | `tools`' `just test` | pass: 42 rows |
| Extraction with history | root `just full-test` | the same files in all nine; 2 to 8 commits of history each (`model-secofs` 8, `model-eccofs` 7, `model-nosofs` 6, `model-liveocean` 5, `model-adcirc-cora` and `model-necofs` 4, `model-common` 3, `model-ucla-roms` and `model-ufscoastal` 2) |

The counts depend on shellcheck's version: the file records 0.11.0,
and another version fails the check with a message to review and
re-record, rather than with 53 differences.

### What a real relocation would change

- Extract each with `just export-filter model-<name>`; `model-common`
  first, since `model-adcirc-cora` uses it.
- Give each recipe its install directory and module path as
  arguments, in place of its place in a checkout (the list above).
- Settle module naming with `sandbox-provisioning` (the first finding)
  before the first build on a rebuilt sandbox.
- Pin the three recipes that follow a branch head.
- In Cloud-Sandbox: delete `models/` and `patches/`, and point the job
  configurations at installs, not at a checkout
  ([stage 6](../SPECS/COMPLETED/STAGE-6.md)).

## sandbox-configs

Copied on 2026-11-12 by [stage 6](../SPECS/COMPLETED/STAGE-6.md). The
project's own description is
[sandbox-configs/README.md](sandbox-configs/README.md).

### Where its files go

From [sandbox-configs.map](sandbox-configs.map): all 130 files of
`job.configs/` (80) and `cluster.configs/` (50), unchanged, under the
same directory names. By the operator's decisions the copies keep
their identifiers, and the templates and examples stay in the same
unit as the site data. No patches.

New: `README.md`, `LICENSE`, `Justfile`, `pyproject.toml`, `uv.lock`,
`.python-version`, `schema/` and `tests/`.

### The schema

[schema/jobs.json](sandbox-configs/schema/jobs.json) and
[schema/clusters.json](sandbox-configs/schema/clusters.json) name, for
each of the 17 `JOBTYPE`s and the two platforms, every key cloudflow
reads, whether it is required, optional or conditional, and the line
that reads it. They are written from the code, not by hand:
[tools/configs_schema.py](tools/configs_schema.py) reads
`JobFactory.py` and `ClusterFactory.py` for the dispatch and each
class's `parseConfig()` for the keys, with Python's own parser. Two
cases needed care, and each has a test: `table_name` is read under
`if 'table_name' in cfDict` whose `else` raises, so it is required;
`EXPNAME` is guarded the same way but only for LiveOcean, so it is
conditional. `just configs-schema` writes the files again; the tools
tests fail when they differ from what the code reads, or when a line
named no longer reads its key.

### What the files are

Every file is catalogued in
[tests/catalogue.json](sandbox-configs/tests/catalogue.json) with its
kind (job, cluster, other), its role and whether cloudflow can read
it; the unit's test fails when any of that changes.

| Role | Files |
| --- | ---: |
| template (named so, or holding placeholders) | 3 |
| site (an AWS identifier, or a path in one person's directory) | 71 |
| example (anything else that is a description) | 48 |
| helper scripts, notes, pointers | 8 |

### Where the cluster values come from

This gives C7 of [ANALYSIS.md](../SPECS/ANALYSIS.md) its owners:
`region`, `key_name`, `sg_ids`, `subnet_id` and `placement_group` come
from `sandbox-terraform`'s outputs; `image_id` from
`sandbox-provisioning`'s `node-image.yml`; `table_name` from the
operator (made by hand, supplied as configuration); the rest from the
person who writes the description. The README has the table.

### Found

- **23 of the 122 descriptions cannot be read by today's cloudflow.**
  Three are not JSON: two have a trailing comma
  (`IOOS/ioos.nosofs.cfg`, `IOOS/nosofs.config`) and
  `IOOS/current.system` is a fragment. Six cluster descriptions lack
  `table_name`, which `AWSCluster` now insists on, **among them
  `cluster.configs/template.ioos`, the template a new site copies**.
  The four CORA job descriptions lack `GRID`; six forecast and
  hindcast descriptions lack `SAVEDIR`; three experiments lack keys
  their class reads. The catalogue gives each.
- **The site data describes many deployments, not one.** The 40 AWS
  cluster descriptions name 19 different images, 13 sets of security
  groups, 8 subnets and 13 placement groups. Only 4 agree on all four
  with `IOOS/current.system`, the hand-kept copy of the latest
  deployment's values. The rest point at resources that may no longer
  exist; nothing here can tell, since nothing is checked against AWS.
- `IOOS/current.system` and `IOOS/current.image_id` are read by
  nothing; they are notes in the shape of data.
- Two files, `IOOS/liveocean.ioos` and `noaa.cora.config`, hold the
  name of another description, as a symbolic link would; cloudflow
  would try to read them as JSON and fail.
- Three key names are in use: `ioos-sandbox`, `rsa_sandbox_key`, and
  one named after a person.

### How it is checked

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| Every file is as catalogued: kind, role, readable or why not | `just test` | pass, 130 files |
| Every schema key names a line of cloudflow's code | `just test` | pass |
| The schema is what the code reads, and each line named reads its key | `tools`' `just test` | pass |
| Extraction with history | root `just full-test` | the same 130 files, with 4 commits of history |

### What a real relocation would change

- Extract with `just export-filter sandbox-configs`.
- Split it by owner, now that the catalogue says which file is which:
  the 3 templates and 48 examples could travel with cloudflow, the 71
  site files belong to the site that runs them.
- Repair or retire the 23 unreadable descriptions, and add
  `table_name` to the template first.
- Have Terraform write a complete cluster-description fragment
  (with `region` and `table_name`) instead of `current.system` being
  kept by hand.
- Move the schema writer into cloudflow, so that the schema is
  published with the code that reads it.
- In Cloud-Sandbox: delete `job.configs/` and `cluster.configs/`, and
  update the paths in the documentation
  ([stage 8](../SPECS/COMPLETED/STAGE-8.md)).

## sandbox-ops

Done on 2026-11-12 by [stage 7](../SPECS/COMPLETED/STAGE-7.md). The
project's own description is
[sandbox-ops/README.md](sandbox-ops/README.md).

### What the stage did with the 108 files left over

After stage 3, 108 files of `scripts/`, `misc/` and `jupyterhub/` had no
unit. Each was read and marked in use, superseded or dead, with the
evidence (`sandbox-ops/CATALOGUE.tsv` and
`cloud-sandbox/attic/CATALOGUE.tsv` keep the reading for the 92 that are
not provisioning's). Then:

| Files | Went to | Why |
| ---: | --- | --- |
| 8 | `sandbox-provisioning`, role `sandbox_users`, playbook `users.yml` | the user tools and their `sudoers` files: operator's decision 1 |
| 8 | `sandbox-provisioning`, role `jupyterhub`, playbook `jupyterhub.yml` | the JupyterHub install, its files, and its README: decision 1 |
| 16 | `sandbox-ops/bin/`, `keys/` | tools still in use |
| 26 | `cloud-sandbox/attic/superseded/` | replaced by something named in the catalogue |
| 50 | `cloud-sandbox/attic/dead/` | no longer apply |

With this, the copy check covers every tracked file under `scripts/`,
`misc/` and `jupyterhub/`: the [sandbox-ops.map](sandbox-ops.map) says
`covers` for all three, `sandbox-provisioning.map` takes its part, and
[cloud-sandbox.map](cloud-sandbox.map) takes the attic.

### The attic stays with the original repository

Stage 7 copied the 76 superseded and dead files into `sandbox-ops/attic/`
(decision 2). On 2026-11-13 the operator decided that the attic does not
travel with the code: it stays with the original repository. The
original repository is what the umbrella `cloud-sandbox` is once the
units have left, so the attic moved there, whole and unchanged:
`cloud-sandbox/attic/<status>/<original path>`, with the 76 rows of the
catalogue in `cloud-sandbox/attic/CATALOGUE.tsv` and a description in
[cloud-sandbox/attic/README.md](cloud-sandbox/attic/README.md).

- `sandbox-ops` keeps the 16 tools in use and their 16 rows. Its
  catalogue check now refuses a superseded or dead row: those belong in
  the attic. Its shellcheck record lost the attic's 36 scripts: 14
  scripts and 70 findings remain, the one that does not parse
  (`scrub_liveocean.sh`) among them.
- The umbrella's `just test` checks the attic with
  `tests/check_attic.py`: every file has one row, every row a file, and
  each file sits at `attic/<status>/<original path>`. The attic's
  scripts are not shellchecked: nothing runs them.
- `patrick.gitconfig` is in the attic, at
  `attic/dead/scripts/system/patrick.gitconfig`, as it already was in
  `sandbox-ops`. It has always been in the original repository; staying
  there adds nothing to it, and it no longer travels anywhere.

### The two new roles

Both are translations in the manner of stage 3: the originals are in
`sandbox-provisioning/legacy/`, every task names the lines it replaces,
and every line that does something is either replaced or listed in
`tests/not_carried.yml` with the reason. A new test,
`tests/test_ops_parity.py`, renders each template with the role's
defaults and compares it with the file it replaces:
`jupyterhub_config.py` (1244 lines) and the nginx file come out byte for
byte; the two `sudoers` files and the users' shell lines match once the
originals' one person is given as a variable. The container test now
applies `users.yml` and `jupyterhub.yml` too, twice, checks the result,
and removes the test user again.

What the roles do differently from the scripts, on purpose, each noted
above its task:

- **Users:** the user list is a variable kept with the site's
  settings, not a CSV file; the security group is a variable (the
  script names one site's group) and the step needs AWS, so it is
  skipped unless a group is named; the AMI prompt at the end of
  `add-users.py` is `node-image.yml`; the Spack path comes from
  `group_vars` (the script's own TODO); each user's Spack configuration
  belongs to the user (the script hands `.bashrc` to them twice and
  leaves the Spack file root's); `authorized_keys` is the user's, mode
  0600, without the empty line the script adds for a user with no key.
- **Lustre rules:** one person's four `sudoers` lines become a template
  for a list of users, installed as `/etc/sudoers.d/sandbox-modelers`
  and checked with `visudo`. sudo skips any file in `/etc/sudoers.d`
  whose name contains a dot, which both original names do. cloudflow
  needs these rules: `FSxScratchDisk.py` mounts with `sudo`.
- **JupyterHub:** of the two install scripts, the conda one is
  translated, because the service file, the run script and the README
  describe it. Its configuration is written to `/etc/jupyterhub/`,
  where they read it (the script writes `/opt/jupyterhub/`), and the
  run script is put where the service runs it (the script never puts
  it anywhere). conda comes from Miniforge, not the script's Miniconda 23.1
  (whose download address has no host): with Miniconda's solver the
  script's conda-forge install had not finished after 25 minutes, and
  the operator chose Miniforge, with conda-forge as the only channel. conda is called by its path as the owner of `/opt/conda`
  (the script's `conda activate` cannot work in a script, and its
  `chown ec2-user/ec2-user` changes nothing). Ownership and modes under `/opt/conda` are set with
  `find`, which touches only what is not so yet: Ansible's recursive
  `file` checked every file on each run and took 25 minutes in the
  container. nginx is enabled, and started only when the certificates
  exist. `setenforce 0` is not carried.

### Found

- **Nothing installed JupyterHub before this stage.** Neither install
  script is called by the setup, and neither could have run as it was
  (a download address with no host, files copied where nothing reads
  them). The role is the first install that works, in the container.
  Whether a site wants it is its own decision; `jupyterhub.yml` is not
  part of `site.yml`. **Decided (operator, 2026-11-14, stage 13):** it
  stays an option. Since stage 13 the role has no defaults for what only
  a site can say (server name, OAuth callback, certificate and key, the
  administrators and the address map) and refuses to install anything
  until they are given; the README says what a site supplies, and that
  opening 443 is the site's.
- **One tool in use does not parse:** `scrub_liveocean.sh` never closes
  the `if` at L88. It is recorded, and the test fails if it is fixed or
  if another script breaks.
- **`add-ufs-setup.sh` calls `install_gcc_toolset_yum` (L27)**, which
  `funcs-setup-instance.sh` no longer defines, so the UFS add-on fails as
  written. `models/ufscoastal/README` still points to
  `ufs-setup-instance.sh`, which is superseded.
- **The mirror tools carry RHEL 8 versions:** `spack-update-mirror.sh`
  lists gcc 11.2.1 and oneAPI 2023.1.0; `ufs-envars.sh` names Spack
  v0.22.5 and `linux-rhel8`.
- **Personal data in the tree:** `scripts/system/patrick.gitconfig`
  (a name and an address), the mirror key's user id (a work address),
  and three `sudoers` files that name accounts. They are copied as they
  are, like everything else. `patrick.gitconfig` is in the attic, which
  stays with the original repository, so it leaves with no unit.
- 16 of the 50 dead files are Slurm and munge: unit files, a
  configuration and notes from before the sandbox used cloudflow's own
  nodes.

### How it is checked

| Check | Where | Result on 2026-11-12 |
| --- | --- | --- |
| The catalogue and the files agree; every file is in use (2026-11-13) | `sandbox-ops`' `just test` | pass, 16 files |
| 14 scripts parse, except the one recorded; 70 shellcheck findings as recorded (2026-11-13; before the attic moved, 50 scripts and 559 findings) | `sandbox-ops`' `just test` | pass |
| The attic and its catalogue agree; each file sits where its status says (2026-11-13) | `cloud-sandbox`' `just test` | pass, 76 files: 26 superseded, 50 dead |
| Every task of the two roles names its lines; every line is replaced or explained | `sandbox-provisioning`'s `just test` | pass |
| The templates write the original files | `sandbox-provisioning`'s `just test` | pass |
| `users.yml` and `jupyterhub.yml` applied twice in the container, the second run changing nothing; the user removed again | `sandbox-provisioning`'s `just full-test` | pass; the hub answers on port 8000. *(2026-11-14, stage 13: from stage 7 until then, the full test's checks of these two were skipped without failing, because the list of plays was cut at its first space; fixed, and the test now fails if a check is skipped. They pass.)* |
| Extraction with history | root `just full-test` | `sandbox-ops`: the same 16 files, with 14 commits (2026-11-13; 92 files and 22 commits with the attic); `cloud-sandbox`, attic included: 84 files, 62 commits; `sandbox-provisioning`: 25 files, 19 commits |

### What a real relocation would change

- Extract with `just export-filter sandbox-ops`. The attic is not in
  it: it stays with the original repository (2026-11-13).
- Point the mirror tools at `sandbox-provisioning`'s `group_vars`
  instead of sourcing `environment-vars.sh`, and update their versions.
- Fix or retire `scrub_liveocean.sh` and `add-ufs-setup.sh`.
- In Cloud-Sandbox: move the attic's 76 files to
  `attic/<status>/<original path>` with `git mv`, so that they keep their
  history there, then delete what is left of `scripts/`, `misc/` and
  `jupyterhub/` ([stage 8](../SPECS/COMPLETED/STAGE-8.md)).

## cloud-sandbox (the umbrella)

Made on 2026-11-12 by [stage 8](../SPECS/COMPLETED/STAGE-8.md). By the
operator's decision, Cloud-Sandbox does not disappear: it becomes a
small repository that says what a sandbox is made of, at which versions,
and in which order. Its own description is
[cloud-sandbox/README.md](cloud-sandbox/README.md).

### Where its files go

From [cloud-sandbox.map](cloud-sandbox.map):

| Source | In the umbrella |
| --- | --- |
| `LICENSE`, `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`, `.github/ISSUE_TEMPLATE.md` | the same paths |
| `images/sandbox-stack.png` | `images/` |
| `README.md`, `DEPLOYMENT.md`, `TODO`, `.gitignore` | `history/` (`.gitignore` as `history/gitignore`, so that its monorepo patterns do not hide the umbrella's files) |
| `images/AWS-Key-pairs-screen.png` | not here: `sandbox-terraform/docs/images/`, beside the text that shows it |
| the 76 superseded and dead files of `scripts/` and `misc/` | `attic/superseded/` and `attic/dead/`, under their original paths (2026-11-13; see [the sandbox-ops section](#the-attic-stays-with-the-original-repository)) |

New: `README.md`, `units.toml`, `Justfile`, `tests/`, and
`attic/README.md` and `attic/CATALOGUE.tsv`.

[units.toml](cloud-sandbox/units.toml) is the umbrella's substance: each
unit's name, the version that goes into a sandbox, its kind, the step at
which it is applied, its place in the order of relocation, and the units
it needs. The umbrella's own test holds it consistent (each unit is
relocated after what it needs); a test in `tools` holds it to the
repository (every mapped unit is listed, and a unit with a
`pyproject.toml` has that version).

The map also says `covers ./`: every tracked file of the repository must
now be taken or dropped by some unit, and `just test` fails on one that
is not. On 2026-11-12 all 814 tracked files outside `exportit/` are
accounted for.

### DEPLOYMENT.md, split

By the operator's decision the split is written, as two new documents:
[sandbox-terraform/DEPLOYMENT.md](sandbox-terraform/DEPLOYMENT.md) (the
original's lines 1–183, 209–221, 239–261, 272–274 and 281–304) and
[sandbox-provisioning/DEPLOYMENT.md](sandbox-provisioning/DEPLOYMENT.md)
(lines 184–238 and 262–279), each saying where it comes from and where
it departs from the original. The original stays whole in the umbrella's
`history/`.

### The documentation

By the operator's decision only the Sphinx sources travel:
`docs/source/` and the files that built it go to
`cloudflow/docs/sphinx/`; the 129 files of committed HTML and build output and the older
copy in `docs/save/` are dropped as rebuilt. One patch,
`cloudflow.patches/08-sphinx-conf-installed-packages.patch`, makes
`conf.py` document the installed packages instead of reaching into the
repository's directories. `just docs` in the cloudflow export builds it,
and `just full-test` there checks the build.

### Found

- **Three documentation pages are for modules that no longer exist**
  (`nodeInfo`, `nosofs_qops`, `run_adnoc`). The build is held to exactly
  those three.
- **The `@task` work-around is no longer needed.** `sedtasks.sh` comments
  out every `@task` in the source tree before a build, because autodoc
  could not document decorated tasks then. With today's Prefect the
  tasks are documented as they are (`workflows/tasks.html` lists them).
- **The root README has six broken links:** `PREFECTV3.md` (the file is
  `PREFECTv3.md`, so the link only works on a case-insensitive disk),
  `ZOMBIE_JOB_CHECKLIST.md` (it is under `cloudflow/`), and the READMEs
  of four models, which are named `README`, without `.md`.
- **DEPLOYMENT.md has gone stale against Terraform:** it names
  `allowed_ssh_cidr`, which the module replaced with
  `allowed_ssh_cidr_list`; its login example uses `centos`, the module
  says `ec2-user`. It asks for Terraform 1.5.7, the last open-source
  version, while stage 4 tests with 1.9.8. The split documents correct
  the first two. The third the operator settled on 2026-11-13:
  OpenTofu 1.13.9.

## ansible-collection-csis-spack (outside this repository)

Begun on 2026-11-13 by [stage 9](../SPECS/COMPLETED/STAGE-9.md). The Ansible
collection `infrastructurebuilder.csis_spack` is new code, not a copy of
anything in Cloud-Sandbox, so by the operator's decision it is not under
`exportit/`: it lives in its own repository from the start,
`git@github.com:infrastructurebuilder/ansible-collection-csis-spack.git`,
worked on in a clone beside this one
(`../ansible-collection-csis-spack`). The operator renamed the repository and the collection
from `ansible-collection-spack` and `spack` the same day; a collection
name cannot hold a hyphen, hence `csis_spack`. It needs no relocation, and nothing in
this file's copy check covers it.

- **What it is for:** the steps of `spack_environment` that have to call
  Spack (concretize, install, regenerate module files, push to the build
  cache), as a module with Ansible's change reporting and check mode,
  in place of shell tasks that hash files before and after.
- **State:** 0.0.1, published on Ansible Galaxy and tagged in its
  repository on 2026-11-19. On that day the collection withdrew its earlier
  tags, 0.1.0 to 0.3.1, and released all they held as 0.0.1. What was 0.3.1
  fixed what the sandbox's stage 12 found: Spack leaves a mapping it empties behind, and
  `spack_config` now removes the emptied mapping itself. Eight modules, a `setup` role and
  two filters, tested against a stand-in for Spack and against the real
  Spack v1.2.0, and passing `ansible-test sanity`. It names no package,
  compiler, mirror or path of any site; the sandbox's own lists are one
  of its examples. It plans its work with Spec Kit, in its own workspace;
  publishing to Galaxy was its spec 001.
- **How `sandbox-provisioning` uses it** (since [stage 10](../SPECS/COMPLETED/STAGE-10.md)):
  a line in `requirements.yml`. Until 2026-11-19 it named the repository
  at a tag: `0.3.0` since [stage 11](../SPECS/COMPLETED/STAGE-11.md),
  `0.3.1` since [stage 12](../SPECS/COMPLETED/STAGE-12.md). Since then it
  names the collection on Ansible Galaxy, `infrastructurebuilder.csis_spack`,
  in the range `>=0.0.1,<0.1.0`. It is installed into `.collections/` by
  `just init`, by the container test, and by the head node's first boot
  before `site.yml` runs. `units.toml` lists it as the one `external`
  unit, at 0.0.1, with `sandbox-provisioning` needing it; a test in
  `tools` holds that version inside the range `requirements.yml` gives,
  or equal to the tag it names.

## Syncing from the original

Added by [stage 23](../SPECS/STAGE-23.md), 2026-11-18, so that the
original repository's later changes can still reach the units once
their originals are deleted from Cloud-Sandbox.

- **Each unit has a baseline**, in
  [units.toml](cloud-sandbox/units.toml): the commit of the original
  its copied files are, with its patches. All fifteen began at
  `ca0604a`. `just export-baselines` checks every unit against the
  original as it was at its own baseline, read from this repository's
  history, or from a clone given as `source=`.
- **The export tool reads the originals from elsewhere** when told:
  `--source <clone>` (a clean checkout of the original) and
  `--at <commit>`, for every command. The mapping files and the patches
  are always read here. `local` directives name this repository's own
  files (`SPECS/`, `PLAN.md`, the `Justfile`, `.gitmodules`): dropped
  here, and a problem if an original ever has one.
- **`just export-sync <unit> <clone> <branch>`** carries the original's
  commits since the unit's baseline into the unit's repository. The
  clone is filtered with the unit's directives, as the unit's first
  extraction was; that gives the unit's existing history the same
  commit IDs, so only the new upstream commits are new to it, and they
  are merged onto `feature/<branch>` from the unit's `develop`, with
  their authors and dates. The baseline in `units.toml` then moves.
  Nothing is pushed.

What the maps decide, and what they leave:

| The original's change | What a sync does |
| --- | --- |
| A copied file changed | carried, with its commit |
| A new file inside a directory a unit copies whole | carried |
| A new file that no map claims | stops: "not assigned to any unit"; a map line decides where it goes |
| A file a map names, deleted | stops: the map line "matches no tracked file"; the map is changed |
| A change to a patched file that the patch survives | carried, the correction kept |
| A change to a patched file that the patch does not survive | stops on the merge's conflict, the unit left as it was; the patch is written again here |
| A changed original that a unit translates (`sandbox-provisioning`) | carried, and reported: its parity tests say where the translation no longer holds |
| A file only this repository may have (`local`) | stops |

`just sync-rehearse`, part of `just full-test`, runs one sync of each
kind against throw-away clones of the real units: on 2026-11-18 all
seven did as the table says, with the carried commits keeping their
author.

## The order of the real relocations

**Where this stands since moving day (2026-11-17):** every unit below has
its repository, so the first half of every step is done, in an order
that did not have to be this one, because nothing was deleted and no
unit names another by repository yet. What is left of each step is its
last column: deleting the unit's original paths from Cloud-Sandbox, with
what that breaks. That order still matters, and is the order below.

A unit moves after every unit it names by version, so that it can name a
version that exists. `units.toml` holds this order; the steps below
follow it. Each is the method under
[How a unit would really be relocated](#how-a-unit-would-really-be-relocated);
"Cloud-Sandbox after" says what the original repository holds once the
step is done.

| Step | Unit | What it needs first | Cloud-Sandbox after |
| ---: | --- | --- | --- |
| 1 | `cloudflow` (**originals deleted, stage 22 step 1, 2026-11-19**) | nothing | `cloudflow/`, the root `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, the Miniforge guide and `docs/` gone. The launchers no longer sit next to `models/`; the job descriptions that name `/save/<user>/Cloud-Sandbox/...` paths have to change (step 4) |
| 2 | `model-common` (**originals deleted, stage 22 step 2, 2026-11-19**) | nothing | `models/modulefiles/`, `models/utils/` and the three notes gone; `adcirc-cora`'s `../modulefiles` no longer resolves in the original |
| 3 | the eight `model-<name>` units (**originals deleted, stage 22 step 3, 2026-11-19**) | `model-common` (ADCIRC only) | `models/` and `patches/` gone |
| 4 | `sandbox-configs` (**originals deleted, stage 22 step 4, 2026-11-19**) | `cloudflow` (its schema is cloudflow's) | `job.configs/` and `cluster.configs/` gone. Before it moves, split it by owner, as its section says: templates and examples to cloudflow, site data to the site |
| 5 | `sandbox-provisioning` (**originals deleted, stage 22 step 5, 2026-11-19**) | `ansible-collection-csis-spack`, which is in its own repository already | `scripts/setup-instance.sh`, its library, `environment-vars.sh`, `create_image.*`, the user and JupyterHub scripts and their `scripts/system/` files, and `jupyterhub/` gone. The original's `terraform/` still boots the old way |
| 6 | `sandbox-terraform` (**originals deleted, stage 22 step 6, 2026-11-19**) | `sandbox-provisioning` (the first-boot template names its repository and version) | `terraform/` gone. Make the two-variable change in its README at this step, pointing at step 5's repository |
| 7 | `sandbox-ops` (**originals deleted, stage 22 step 7, 2026-11-19**) | `sandbox-provisioning` (its tools read the versions there) | the attic's 76 files moved to `attic/`, which stays; the rest of `scripts/` and `misc/` gone |
| 8 | `cloud-sandbox` (**originals deleted, stage 22 step 8, 2026-11-19**) | every unit | the repository itself becomes the umbrella: what is left is replaced by the umbrella's files, on a branch, and `units.toml` is filled with the repositories made in steps 1–7 |

The machinery of this work does not move: `exportit/`, `SPECS/`,
`PLAN.md` and the root `Justfile` are deleted in step 8, and the
umbrella gets its own `Justfile`.

The repositories exist and are pushed (2026-11-17); not one original
path has been deleted. `just full-test` goes on rehearsing the extraction
of every unit on throw-away clones, which now proves that a unit's
repository could be made again from the originals and the mapping.
