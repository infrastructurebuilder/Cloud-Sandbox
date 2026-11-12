# model-common

What several model recipes of a Cloud Sandbox share: two environment
module files and four notes.

| File | What it is |
| --- | --- |
| `modulefiles/intel_x86_64.impi_2021.12.1` | The module file `model-adcirc-cora`'s `buildadcirc.sh` loads. It sets the compiler variables and loads Spack's Intel oneAPI 2023.1 compilers, Intel MPI 2021.12.1, HDF5 and NetCDF by their hashed names, then finds NetCDF with `nf-config` and `nc-config` |
| `modulefiles/intel_x86_64.impi_2021.9.0` | Its predecessor, for Intel MPI 2021.9.0, with the NetCDF paths written out for one RHEL 8 Spack tree |
| `TODO` | Open questions about which model files belong in Cloud-Sandbox and which with the models |
| `compilation.notes` | Intel compiler options for AMD EPYC (`hpc6a`, `hpc7a`) |
| `mpiopts.note` | Intel MPI's libfabric settings, for EFA |
| `utils/readme.makedepf90` | Where `makedepf90` comes from |

## This is a copy

This directory is a copy of `models/modulefiles/`, `models/utils/`,
`models/TODO`, `models/compilation.notes` and `models/mpiopts.note`
from the Cloud-Sandbox repository, made there. Every file is here,
byte-identical. [../MAP.md](../MAP.md#the-model-units) describes how
this project would be moved to a repository of its own. Do not edit
the copied files here: change the original and run
`just export model-common` at the repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## Who uses it

`model-adcirc-cora`'s `buildadcirc.sh`, through `../modulefiles`: it
expects to sit next to this directory's `modulefiles/`. cloudflow's
launchers load a module file of the same name,
`intel_x86_64.impi_2021.12.1`, but from the job's
`$SAVEDIR/modulefiles`, which for NECOFS is `model-necofs`'s own,
different file.

## Working on it

You need `just`, bash 4 or later and `shellcheck`. There are no shell
scripts here, so the test only proves that; it runs the same harness
as every model unit.

```sh
just init        # says which bash and shellcheck will be used
just test        # no scripts; the harness itself is clean
just full-test   # the same
```

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
