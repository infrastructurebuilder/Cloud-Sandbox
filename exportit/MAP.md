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
(the copy exists and is checked against its source), *relocated*
(never used here: nothing leaves this repository).

| Unit | Copy | Source paths | Stage | State |
| --- | --- | --- | ---: | --- |
| `cloudflow` | [cloudflow/](cloudflow/) | `cloudflow/` without `plotting/`; root `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md` | [2](../INPROGRESS/STAGE-2.md) | copied 2026-11-12 |
| `cloudflow-plotting` | [cloudflow-plotting/](cloudflow-plotting/) | `cloudflow/plotting/`, `cloudflow/setup.py`, `cloudflow/plotting_reqs.reference`, `cloudflow/tests/test.plotting.py` | [2](../INPROGRESS/STAGE-2.md) | copied 2026-11-12 |
| cloudflow's documentation | `exportit/cloudflow/docs/` | `docs/source/` | [8](../INPROGRESS/STAGE-8.md) | planned |
| `sandbox-provisioning` | `exportit/sandbox-provisioning/` | `scripts/setup-instance.sh`, `funcs-setup-instance.sh`, `environment-vars.sh`, `create_image.*`, the `scripts/system/` files they install | [3](../INPROGRESS/STAGE-3.md) | planned |
| `sandbox-terraform` | `exportit/sandbox-terraform/` | `terraform/` | [4](../INPROGRESS/STAGE-4.md) | planned |
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
  table.

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

Planned. [Stage 3](../INPROGRESS/STAGE-3.md) fills this section. It is
a translation and not a copy: each function of
`funcs-setup-instance.sh` becomes an Ansible role, and this section
will list function to role, variable to variable and file to file.

## sandbox-terraform

Planned. [Stage 4](../INPROGRESS/STAGE-4.md) fills this section.

## sandbox-models

Planned. [Stage 5](../INPROGRESS/STAGE-5.md) fills this section.

## sandbox-configs

Planned. [Stage 6](../INPROGRESS/STAGE-6.md) fills this section.

## sandbox-ops

Planned. [Stage 7](../INPROGRESS/STAGE-7.md) fills this section.

## cloud-sandbox (the umbrella)

Planned. [Stage 8](../INPROGRESS/STAGE-8.md) fills this section and
closes the map with the order of the relocations.
