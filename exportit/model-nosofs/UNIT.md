# model-nosofs

The recipe that fetches and builds the NOS Operational Forecast
Systems, the ROMS models (`cbofs`, `ciofs`, `dbofs`, `gomofs`, `tbofs`,
`wcofs`) and the FVCOM ones (`leofs`, `lmhofs`, `loofs`, `lsofs`,
`ngofs2`, `sscofs`, `sfbofs`), from the NOSOFS code package, on a
Cloud Sandbox. How to run them is in [README](README) and
[NOSOFS-MODELS.md](NOSOFS-MODELS.md), the original's own descriptions.

## This is a copy

This directory is a copy of `models/nosofs/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-nosofs` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/asascience-open/NOSOFS-Code-Package.git`, branch `v3.6.6.dev`, with its submodules; fixed fields from `https://ioos-sandbox-use2.s3.amazonaws.com/public/nosofs/fix` (`get_fixfiles_s3.sh`). `get_ops_fixfiles_nwprod.sh` takes them from NCO's `nwprod` instead and uploads them to that bucket; `save_fixfiles_s3.sh` uploads an install's |
| Builds | The code package's `sorc/build.sh` (`setup_nosofs.sh`, `build_nosofs.sh`) |
| Needs from provisioning | Its own `modulefiles/intel_x86_64` (and an older `ioos-sb.intel_x86_64`), copied into the install: Spack's Intel oneAPI 2023.1 compilers and MKL, netcdf-fortran, METIS, libpng, parallel-netcdf and ParallelIO by their hashed names, and the NCEP libraries |
| Installs to | `$SAVEDIR/nosofs.v3.6.6`, `SAVEDIR` defaulting to `/save/$USER`; fixed fields to its `fix/` |

## What cloudflow expects from it

For every NOS ROMS and FVCOM model, `fcst_launcher.sh` takes the job's
`SAVEDIR` as the install and runs `$SAVEDIR/jobs/fcstrun.sh`, from the
code package. See [the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `setup_nosofs.sh` and `build_nosofs.sh` print the Cloud-Sandbox
  directory two levels up; they use it for nothing else.
- `NOSOFS-MODELS.md` walks through cloudflow and the configuration
  directories of Cloud-Sandbox by their paths there.

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
