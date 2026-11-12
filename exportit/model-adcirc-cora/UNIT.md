# model-adcirc-cora

The scripts and templates that run ADCIRC for the CORA reanalysis on a
Cloud Sandbox. They are B. Blanton's (RENCI) system for templated sets
of storm runs: `bin/run_storms.sh` and its helpers, the grids'
templates in `common/`, the run configurations in `configs/`, and a
Pacific example in `pac/`. Beside them are a build recipe for ADCIRC
itself and, in `patches/`, two repair scripts for an installed ADCIRC.
How the run system works is in [README.md](README.md), the original's
own description.

## This is a copy

This directory is a copy of `models/adcirc-cora/` and
`patches/adcirc-cora/` from the Cloud-Sandbox repository, made there.
Every one of those files is here, byte-identical; `patches/adcirc-cora/`
became `patches/`. [../MAP.md](../MAP.md#the-model-units) describes
how this project would be moved to a repository of its own. Do not
edit the copied files here: change the original and run
`just export model-adcirc-cora` at the repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | Three tarballs from `s3://ioos-cloud-sandbox/public/cora-adcirc/` (`getS3packages.sh`, `install-adcirc-cora.sh`): `adcirc_built.tgz`, a built ADCIRC; `cora-runs.tgz`, a run tree laid out like this directory; `2018.ioos_sb.tgz`, the 2018 forcing |
| Builds | ADCIRC, with `buildadcirc.sh`, from a source tree that `ADCIRCHome` names and that nothing here fetches. `padcirc`, `padcswan`, `adcprep` and the utilities go to `$ADCIRCHome/work` |
| Needs from provisioning | `intel_x86_64.impi_2021.12.1`, which `buildadcirc.sh` finds in `../modulefiles`: now in `model-common`. It loads Spack's Intel oneAPI 2023.1 compilers, Intel MPI 2021.12.1, HDF5 and NetCDF by their hashed names. Also `cmake`, `aws` |
| Installs to | `/save/$USER` (`getS3packages.sh` uses `$USERNAME`); `install-adcirc-cora.sh` takes the directory three levels above the one it runs in, which is `/save/<user>` only when it runs inside `<user>/Cloud-Sandbox/models/adcirc-cora` |

## What cloudflow expects from it

`cora_launcher.sh` is given the job's `ProjectHome` and expects there
the layout of this directory: `bin/run_storms.sh`, `common/` (it
writes `common/submit.cloudflow.template` into it), `configs/`,
`TracksToRun/`, and the run directories `ERA5/<grid>/<year>`. The job
also names `ADCIRCHome`, where the executables are. The full table is
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `buildadcirc.sh` loads its module file from `../modulefiles`, which
  is `models/modulefiles/` in Cloud-Sandbox: `model-common` here.
- `patches/reinstall-esmf-netcdf.sh` sources
  `../../scripts/funcs-setup-instance.sh`, the old provisioning script
  that `sandbox-provisioning` replaces.
- `patches/fix4cora.sh` links into one Spack build of
  netcdf-fortran by its hash.

## Working on it

You need `just`, bash 4 or later and `shellcheck`. Nothing is fetched,
built or run.

```sh
just init        # says which bash and shellcheck will be used
just test        # every script parses; shellcheck's findings are as recorded
just full-test   # the same: there is nothing slower to check
just record      # write tests/shellcheck.counts again, after reviewing a change
```

The scripts are copies, so their shellcheck findings are counted, not
fixed: `tests/shellcheck.counts` holds the number per script, and the
test fails when one changes. The four job templates in `common/` hold
placeholders and do not parse as bash; `tests/templates.txt` lists
them, and the test fails if one starts to parse.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
