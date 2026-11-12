# model-necofs

The recipes that fetch, build and feed NECOFS, the FVCOM-based
Northeast Coastal Ocean Forecast System, on a Cloud Sandbox: a hindcast
build in `hindcasts/` (the current one) and a tidal, barotropic build
in `tidal_barotropic/`. How to use them is in [README](README), the
original's own description.

## This is a copy

This directory is a copy of `models/necofs/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical, including
`bin/makedepf90`, a built x86-64 executable.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-necofs` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/FVCOM-GitHub/FVCOM.git` at `v4.4.8` (`hindcasts/get_src.sh`); the test case's inputs from `s3://ioos-sandbox-use2/public/necofs` |
| Builds | FVCOM with `hindcasts/hindcasts.make.inc` (`hindcasts/build_necofs.sh`), giving `necofs_fvcom`; the tidal build with `tidal_barotropic/make.inc` |
| Needs from provisioning | Its own `modulefiles/intel_x86_64.impi_2021.12.1`: Spack's Intel oneAPI 2023.1 compilers, PETSc 3.21.1, METIS, netcdf-c and netcdf-fortran by their hashed names |
| Installs to | `/save/$USER/necofs/NECOFS_v2.4/hindcast/FVCOMv4.4.8` (fixed in the scripts); the tidal build expects `/save/patrick/necofs/sorc/tidal_barotropic/FVCOMv4.4.7.1`; inputs to `/com/$SBUSER/necofs/NECOFS_v2.4/hindcast` |

## What cloudflow expects from it

For `necofs`, `necofs_hot` and `necofs_cold`, the launchers load
`intel_x86_64.impi_2021.12.1` from `$SAVEDIR/modulefiles` and run the
job's `EXEC`. The module file is this unit's own: one job
configuration names the `models/necofs` directory of a Cloud-Sandbox
checkout as `SAVEDIR`, the others a copy of it in `/save`. See
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- Through cloudflow: `job.configs/OFS/necofs.hindcast` sets `SAVEDIR`
  to `/save/ec2-user/Cloud-Sandbox/models/necofs`, the place of this
  directory in a checkout.
- `tidal_barotropic/build.sh` builds under one person's directory,
  `/save/patrick`.

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
test fails when one changes. The run scripts in `run/` are `#!/bin/sh`
scripts for PBS; they are checked as shellcheck reads their first line.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
