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
| `cloudflow` | `exportit/cloudflow/` | `cloudflow/`, root `setup.py`, `setup-plotting.sh`, `CLOUDFLOW.md`, `PREFECTv3.md`, `LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md`, `docs/source/` | [2](../INPROGRESS/STAGE-2.md), [8](../INPROGRESS/STAGE-8.md) | planned |
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

Each unit has a mapping file, `exportit/<unit>.map`: one line per
source path and the path it takes inside the unit. A small tool copies
by that file and can check the result: every copied file must be
byte-identical to its source, and every tracked file under the unit's
source paths must be mapped. The check is part of `just test`, so a
change to an original that is not copied again fails the bar.

The mapping file and the tool arrive with
[stage 2](../INPROGRESS/STAGE-2.md).

## How a unit would really be relocated

The same steps for every unit. None of them has been carried out.

1. Create an empty repository for the unit, under the owner that will
   maintain it. Never under `ioos`, and never as a fork of
   `ioos/Cloud-Sandbox`.
2. Make a throw-away clone of this repository and rewrite it with
   `git filter-repo`, driven by the unit's mapping file, so that only
   the unit's paths remain and they sit at their new places. The
   unit's history comes with it. `filter-repo` rewrites the clone it
   runs in and removes that clone's `origin`, which is the safeguard
   against pushing rewritten history back to where it came from.
3. Add the files that exist only in the copy (the unit's README,
   build file, `Justfile`, tests) as one commit on top of that
   history.
4. Add the new repository as the clone's only remote and push.
5. In Cloud-Sandbox, on a feature branch, delete the relocated paths
   and leave a pointer to the new repository.
6. The units that depend on it refer to it by version from then on.

```sh
git clone --no-local /path/to/Cloud-Sandbox /tmp/extract-UNIT
cd /tmp/extract-UNIT
git filter-repo --paths-from-file /path/to/UNIT.filter
git remote -v            # must print nothing
git remote add origin git@github.com:OWNER/UNIT.git
git push -u origin main
```

`UNIT.filter` is the unit's mapping file converted to the directives
that `--paths-from-file` reads: keep this path, and rename it to
that.

## cloudflow

Planned. [Stage 2](../INPROGRESS/STAGE-2.md) fills this section when
it makes the copy.

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
