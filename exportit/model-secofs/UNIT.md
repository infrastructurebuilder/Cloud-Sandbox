# model-secofs

The recipe that fetches, builds and feeds SECOFS, the SCHISM-based
Southeast Coastal Ocean Forecast System, on a Cloud Sandbox. How to run
it is in [README.md](README.md) and
[README.hotstart.md](README.hotstart.md), the original's own
descriptions.

## This is a copy

This directory is a copy of `models/secofs/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-secofs` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/jduckerOWP/schism.git`, branch `v5.13.0_NOS_Sandbox` (`get_schism.sh`); the test case from `s3://ioos-sandbox-use2/public/secofs/` (`get_testcase_inputs.sh`). `fetch_vims_data.sh` downloads a run from VIMS (`ccrm.vims.edu`, with a password) and uploads it to `s3://ioos-sandbox-use2/secofs/input/` |
| Builds | SCHISM with CMake, using `SCHISM.aws.ioos` and `SCHISM.local.build` (`build_schism.sh`) |
| Needs from provisioning | Its own `modulefiles/intel_x86_64`, copied into the install: Intel compilers 2024.2.1, TBB, MKL, Intel MPI 2021.13 under names of the form `intel/compiler/...`, which the Spack tree does not produce, and netcdf-fortran 4.6.2 by its hashed name. Four other module files are kept for other machines (`nos.`, `ioos.`, two `mpi-2021.12.1` variants) |
| Installs to | `/save/$USER/schism` (the module file at its top, executables in `bin/`); the test case to `/com/$USER/secofs`; `combine_hotstarts.sh` works in a run's `outputs/` |

## What cloudflow expects from it

For `secofs`, `fcst_launcher.sh` does `module use $SAVEDIR` and loads
`intel_x86_64` from there, then runs the job's `EXEC`, which the job
configurations set to `$SAVEDIR/bin/pschism_...`. See
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `setup_schism.sh` prints the Cloud-Sandbox directory two levels up;
  it uses it for nothing else.
- `README.md` points at cloudflow's job templates by their path in
  Cloud-Sandbox.

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
test fails when one changes.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
