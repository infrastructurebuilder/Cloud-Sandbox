# Cloud-Sandbox: analysis for reconstruction

*Written 2026-11-12 against commit `ca0604a` (the upstream `main` at
pull request 166). This is the survey that [stage 1](COMPLETED/STAGE-1.md)
produced; the stages that act on it are listed in [TODO.md](TODO.md).*

Nothing was executed to write this page: no script was run, no
Terraform was planned, no model was built. Every statement comes from
reading the files, and the section
[What was not examined](#what-was-not-examined) says where the reading
stopped.

## What the repository is

Cloud-Sandbox is one repository that holds seven different kinds of
thing: a Python workflow engine, the shell scripts that turn a bare
RHEL instance into a head node, the Terraform that creates that
instance, build recipes for ocean models, site configuration data,
operator utilities, and documentation. They are versioned together
because the system is *deployed* as a checkout: the head node clones
the whole repository onto its shared EFS volume and everything runs
from that directory.

802 files are tracked. There is no build file that covers the
repository, no test that runs without a live sandbox, no continuous
integration, and no `Justfile`.

## How the parts run together today

1. An operator runs Terraform in [terraform/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform). It
   creates the network, an EFS volume and one head node.
2. The head node's first boot runs
   [terraform/init_template.tpl\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform/init_template.tpl). That
   script installs the EFS client, mounts the volume at `/mnt/efs/fs1`,
   links it as `/save`, clones this repository from
   `github.com/ioos/Cloud-Sandbox` into `/save/ec2-user/Cloud-Sandbox`
   and runs [scripts/setup-instance.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/setup-instance.sh).
3. `setup-instance.sh` installs the system packages, drivers,
   compilers and the Spack-built libraries, then snapshots the head
   node's own root volume and registers it as the machine image that
   compute nodes boot from. The image carries the EFS line in
   `/etc/fstab`, so every compute node mounts the same `/save`, `/com`
   and `/ptmp`.
4. A modeller builds a model under `/save` with a recipe from
   [models/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/models), then picks a cluster description from
   [cluster.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cluster.configs) and a job description from
   [job.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/job.configs).
5. From the checkout's `cloudflow` directory they run
   [workflow_main.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/workflow_main.py) with
   those two files. A Prefect flow starts EC2 compute nodes with boto3,
   records them in a DynamoDB table, runs a launcher shell script that
   calls `mpirun`, optionally plots the output, and terminates the
   nodes. Two Lambda functions read the DynamoDB table and terminate
   nodes that have run longer than an organisation-wide limit.

## Inventory

| Path | Files | What it is | Proposed unit | Stage |
| --- | ---: | --- | --- | --- |
| [cloudflow/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow) | 195 | Python workflow engine, launchers, input templates, notebooks | `cloudflow` | [2](COMPLETED/STAGE-2.md) |
| [setup.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/setup.py), [setup-plotting.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/setup-plotting.sh), [CLOUDFLOW.md\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/CLOUDFLOW.md), [PREFECTv3.md\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/PREFECTv3.md), [LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md) | 5 | Packaging and notes that belong to cloudflow but sit at the root | `cloudflow` | [2](COMPLETED/STAGE-2.md) |
| [scripts/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts) (setup path) | part of 93 | Head-node provisioning: `setup-instance.sh`, its function library, version file, image creation, the `system/` files they install | `sandbox-provisioning` (Ansible) | [3](COMPLETED/STAGE-3.md) |
| [terraform/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform) | 22 | Network, EFS, IAM and head node; the first-boot template | `sandbox-terraform` | [4](COMPLETED/STAGE-4.md) |
| [models/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/models), [patches/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/patches) | 149 | Per-model fetch, build and setup recipes; module files | `sandbox-models` | [5](COMPLETED/STAGE-5.md) |
| [job.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/job.configs), [cluster.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cluster.configs) | 130 | Job and cluster descriptions, many with one site's AWS identifiers | `sandbox-configs` | [6](COMPLETED/STAGE-6.md) |
| [scripts/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts) (the rest), [misc/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/misc), [jupyterhub/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/jupyterhub) | rest of 93, 23, 1 | User management, Spack mirror upkeep, data scrubbing, instance helpers, JupyterHub, Slurm leftovers, notes | `sandbox-ops` | [7](COMPLETED/STAGE-7.md) |
| [docs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/docs), [images/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/images), root `README.md`, `DEPLOYMENT.md`, `CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md`, `TODO`, `LICENSE`, `.gitignore`, `.github/` | 175, 2, 7 | Sphinx sources and their built HTML; the umbrella documents | split across units; a thin umbrella remains | [8](COMPLETED/STAGE-8.md) |

The unit names are proposals. They are the directory names under
[exportit/](../../exportit/) and the repository names used in
[exportit/MAP.md](../../exportit/MAP.md).

## What couples the parts

These are the things that stop a directory from being lifted out as it
stands. Each stage has to cut or declare the ones that touch its unit.

- **C1. The checkout is the installation.** Nothing is installed as a
  package. [workflow_main.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/workflow_main.py#L18)
  adds the parent of the current directory to `sys.path`, so it only
  works when started from inside `cloudflow/`; the cron scripts
  ([cron_nosofs.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/cron_nosofs.sh)) `cd` to
  `$HOME/Cloud-Sandbox/cloudflow` first.
- **C2. Sibling directories by relative path.** Usage text, cron
  scripts and documentation address the configuration as
  `../job.configs/...` and `../cluster.configs/...`. The files are
  passed on the command line, so this is a convention and not an
  import, but every example assumes the monorepo layout.
- **C3. A filesystem contract nobody wrote down.** Launchers and job
  classes assume `/save/<user>` (code and model builds), `/com`
  (results) and `/ptmp` (scratch), all on the EFS volume, and that a
  model was installed where its recipe in `models/` put it
  (`$SAVEDIR/modulefiles`, `HOMEnos`, and so on; see
  [fcst_launcher.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/fcst_launcher.sh)).
- **C4. Files found beside the code.** Job classes read input
  templates from `templates/` next to themselves, and the tasks run
  launcher scripts next to themselves, through
  `os.path.dirname(__file__)`
  ([tasks.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/tasks.py#L27)). This survives
  packaging only if the package carries those files with their
  executable bits.
- **C5. First boot clones the monorepo.**
  [init_template.tpl\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/terraform/init_template.tpl#L55) clones
  `ioos/Cloud-Sandbox` and runs a script by its path inside the clone.
  Terraform, the provisioning scripts and the repository's own URL are
  tied together in one line.
- **C6. Provisioning installs cloudflow's dependencies by hand.**
  `install_python_modules_user` in
  [funcs-setup-instance.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L1210)
  repeats the list in
  [python_minimal_requirements.txt\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/python_minimal_requirements.txt)
  with different version rules (see F4).
- **C7. The machine image is site data.** Image creation writes an
  image id that somebody copies into `cluster.configs/`; those files
  also hold security group, subnet and key names
  ([template.ioos\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cluster.configs/template.ioos)). Terraform
  writes the same identifiers to `deployment_info.txt`. Three units
  share one set of facts with no single owner.
- **C8. A DynamoDB table shared by three programs.**
  [AWSCluster.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/cluster/AWSCluster.py#L390) refuses to
  start without a table name; the two Lambda functions in
  [cloudflow/cluster/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/cluster) and
  [weekly_summary.nu\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/weekly_summary.nu) read the same
  table. The table's shape is defined nowhere but in that code.
- **C9. Documentation reaches into the code tree.**
  [docs/source/conf.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/docs/source/conf.py#L15) inserts seven
  `sys.path` entries that point into `cloudflow/`.
- **C10. One site's names are constants.** The Spack mirror bucket,
  the shell prompt, the project tag, the AWS region and the clone URL
  are written into scripts as `ioos` or `IOOS-Cloud-Sandbox` literals.

## The proposed units

Each unit gets its own stage. "Independent" means the same five things
for every one of them: it has its own README and licence, its own
`Justfile` with the five contract targets, no path that leaves its own
directory, a written statement of what it expects from the other
units, and an entry in [exportit/MAP.md](../../exportit/MAP.md) that says
how the real relocation would be done.

- **cloudflow** ([stage 2](COMPLETED/STAGE-2.md)). An installable Python
  distribution. Expects: a cluster description and a job description
  (files, by path), the filesystem contract of C3, AWS credentials,
  and the DynamoDB table of C8.
- **sandbox-provisioning** ([stage 3](COMPLETED/STAGE-3.md)). Ansible roles and
  playbooks that do what `setup-instance.sh` does. Expects: a RHEL 10
  host with the EFS volume mounted. Provides: the software stack and
  the node image.
- **sandbox-terraform** ([stage 4](COMPLETED/STAGE-4.md)). Expects: an AWS
  account. Provides: the host and the EFS volume, and the identifiers
  of C7.
- **sandbox-models** ([stage 5](COMPLETED/STAGE-5.md); became one unit per
  model, `model-<name>`, and `model-common`). Expects: the compilers
  and modules that provisioning installs. Provides: model executables
  at the paths of C3.
- **sandbox-configs** ([stage 6](COMPLETED/STAGE-6.md)). Data only. Expects: the
  schema that cloudflow reads and the identifiers of C7.
- **sandbox-ops** ([stage 7](COMPLETED/STAGE-7.md)). Operator utilities that are
  neither provisioning nor workflow.
- **Documentation and the umbrella** ([stage 8](COMPLETED/STAGE-8.md)). Each
  unit takes its own pages; what remains of Cloud-Sandbox is a page
  that says which versions of the units make a sandbox.

## setup-instance.sh, step by step

[setup-instance.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/setup-instance.sh) sources
[environment-vars.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/environment-vars.sh) (the versions)
and [funcs-setup-instance.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh) (33
functions, of which it calls 13), turns SELinux enforcement off, runs
the functions below in order, cleans caches, stops the Prefect
service, creates the node image, starts Prefect again and turns
enforcement back on.

"Lands on" matters because the node image captures only the root
volume: what is installed there reaches compute nodes through the
image, and what is installed on EFS reaches them through the mount.

| # | Function | Line | What it does | Lands on | Safe to run twice? |
| ---: | --- | ---: | --- | --- | --- |
| 1 | `setup_paths` | [264\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L264) | Creates `/ptmp` and `/com` on EFS with links, and a directory per user | EFS, root | No: `mkdir /com/$USER` fails the second time |
| 2 | `setup_aliases` | [1518\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L1518) | Aliases and prompt in `.bashrc` and `.tcshrc`, copies `.vimrc` | home | Yes (guarded by `grep`) |
| 3 | `setup_environment` | [20\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L20) | dnf settings, full update, EPEL, about 30 packages, tmux, pip `boto3`, SSM agent, AWS CLI 2.35.13, environment modules, unlimited stack size | root, home | Mostly; appends the `ulimit` line every run |
| 4 | `setup_prefect-server` | [219\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L219) | `prefect` system user, virtual environment in `/opt/prefect`, systemd unit, state under `/save/environments/prefect` | root, EFS | No: `groupadd` and `useradd` fail the second time |
| 5 | `setup_ssh_mpi` | [1340\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L1340) | Key pair for MPI, authorises it, appends about 90 lines of host rules to `/etc/ssh/ssh_config` | home, root | No (see F6) |
| 6 | `install_efa_driver` | [498\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L498) | Kernel headers, EFA installer 1.48.0 in minimal mode, the AWS libfabric package | root | Yes, slowly |
| 7 | `install_fsx_driver` | [1042\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L1042) | Lustre client repository chosen by kernel version, signature check turned off, client packages | root | Yes |
| 8 | `install_python_modules_user` | [1210\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L1210) | pip installs for the login user: Prefect, Dask, paramiko, boto3 and the plotting libraries | root or home | Yes |
| 9 | `install_spack` | [630\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L630) | Clones Spack v1.2.0 to `/save/environments`, shell start-up lines, configuration, compilers, externals, public mirror | EFS, home | Mostly |
| 10 | `install_intel_oneapi_dnf` | [884\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L884) | Intel repository, oneAPI 2024.2 compilers, MKL and MPI 2021.13, module files, Spack externals and providers | root, EFS | Mostly |
| 11 | `create_spack-environment` | [737\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L737) | Spack environment `rhel10-x86_64_v3` | EFS | No: `spack env create` fails if it exists |
| 12 | `build_spack-environment` | [770\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L770) | Adds ESMF 8.9.1 and PETSc, concretises, builds from source, regenerates module files | EFS | Yes; hours on the first run |
| 13 | `configure_optimizations` | [169\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L169) | A `tuned` profile for HPC instance types | root | Yes |
| 14 | image creation | [setup-instance.sh:52\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/setup-instance.sh#L52) | Cleans caches, stops Prefect, runs [create_image.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/create_image.sh) and [create_image.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/create_image.py), starts Prefect | AWS | Makes a new image every run |

Nine other entry scripts source the same function library and call
different subsets: `rhel10-setup.sh` (the same list without Prefect
and tuning), `update-efa.sh` and `upgrade-mpi.sh` (one or two steps on
an existing node), `ufs-setup-instance.sh` and `add-ufs-setup.sh` (a
different compiler stack through spack-stack), and four more. Three of
them (`ufs-setup-instance.sh`, `add-ufs-setup.sh`, `ncdis-setup.sh`)
call functions that are defined nowhere under `scripts/`:
`install_gcc_toolset_yum`, `setup_prefect`, `install_gcc`,
`install_intel_oneapi` and `install_netcdf`.

## Defects and oddities noticed

None of these was fixed. Each is recorded here so that the stage that
touches the file can decide what to do with it.

- **F1. Two `setup.py` files, neither usable.** The root
  [setup.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/setup.py) names the distribution `cloudflow` but lists
  packages as paths (`'cloudflow/cluster'`), names a licence file that
  does not exist (`LICENSE.txt`) and depends on a distribution called
  `plotting`. [cloudflow/setup.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/setup.py) builds that
  `plotting` distribution from a `plotting` directory, while the code
  imports it as `cloudflow.plotting`.
- **F2. Only one `__init__.py`.** `cloudflow/__init__.py` exists and
  is empty; the six sub-packages have none and work as namespace
  packages.
- **F3. An import that depends on the working directory.**
  [tasks.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/tasks.py#L708) imports
  `python_examples` as a top-level module (again at line 743).
- **F4. Three answers to "which Prefect".**
  [environment-vars.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/environment-vars.sh#L3) installs
  3.7.8;
  [python_minimal_requirements.txt\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/python_minimal_requirements.txt)
  and the Miniforge file pin 3.6.29; the root `setup.py` pins nothing.
- **F5. Personal and retired paths in live code.**
  [fcst_launcher.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/workflows/fcst_launcher.sh#L260)
  sets `JOBDIR=/home/mmonim/...`;
  [testscratch.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/services/testscratch.py#L28) reads
  `/home/centos/...`; both cron scripts start
  `./workflows/nosofs_qops.py`, which exists only as
  `workflows/archived/old.nosofs_quasi_ops.py`.
- **F6. `setup_ssh_mpi` is not repeatable.** It runs `ssh-keygen` onto
  a fixed path and appends its host rules to `/etc/ssh/ssh_config`
  each time. A drop-in file with the same rules already exists at
  [scripts/system/etc.ssh.ssh_config.d/sandbox-local-net.conf\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/system/etc.ssh.ssh_config.d/sandbox-local-net.conf)
  and nothing installs it.
- **F7. The EFA mode is right by accident.**
  [Line 540\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L540) sets
  `EFA_MINAMAL`, line 542 tests `EFA_MINIMAL`. The misspelt variable
  is never read, the tested one is never set, so the minimal install
  always runs.
- **F8. No step can fail the run.** Neither the first-boot template
  nor `setup-instance.sh` stops on an error. A failed build still ends
  with a node image being registered.
- **F9. The image script ignores the region it is given.**
  [create_image.sh\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/create_image.sh) works out the region
  from instance metadata;
  [create_image.py\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/create_image.py#L47) uses `us-east-2`
  in three places regardless.
- **F10. The binary cache is switched off.** `SPACK_CACHEONLY=-1`
  adds `--no-cache`, and the lines that would add the project's S3
  mirror in `install_spack` are commented out, so step 12 compiles
  everything.
- **F11. Built documentation is committed.** [docs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/docs) holds
  generated HTML beside its sources.
- **F12. Notebooks are ignored and tracked.** `.gitignore` excludes
  `**/*.ipynb`; 14 notebooks are tracked under
  [cloudflow/notebooks/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cloudflow/notebooks).
- **F13. A command that its own comment says fails.**
  [Line 88\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/blob/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/scripts/funcs-setup-instance.sh#L88),
  `alternatives --set python`.

## What was not examined

- The inside of the model recipes in `models/` and the 44 input
  templates under `cloudflow/job/templates/`.
- The notebooks, the built HTML under `docs/` and the notes under
  `misc/`.
- Terraform beyond the head node's `user_data` and the list of
  resources.
- Whether any of it runs. The dependency list for cloudflow comes
  from parsing its imports, which was done; nothing was imported.

---

\* A link marked with an asterisk opens the file or directory as it was at
commit [`ca0604a`](https://github.com/infrastructurebuilder/Cloud-Sandbox/commit/ca0604a4a27355b330353c7ded8a1ae00a7e24a6)
of this repository: the original project, from which every unit was made,
and every unit's baseline. These files are no longer on `develop`, because
[stage 22](COMPLETED/STAGE-22.md) deleted the originals on 2026-11-19 once
each unit owned its copies.
