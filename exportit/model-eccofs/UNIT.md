# model-eccofs

The recipe that fetches, builds and feeds ECCOFS, the ROMS-based East
Coast model, on a Cloud Sandbox. ECCOFS is built from the NOSOFS code
package, so it shares its install with `model-nosofs`. How to run it is
in [README](README), the original's own description.

## This is a copy

This directory is a copy of `models/eccofs/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-eccofs` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/asascience-open/NOSOFS-Code-Package.git`, branch `v3.6.6.dev`; fixed fields from `https://ioos-sandbox-use2.s3.amazonaws.com/public/nosofs/fix`; forcing from `s3://ioos-sandbox-use2/public/eccofs/input` |
| Builds | The code package's `sorc/build.sh` (`setup_eccofs.sh`, `build_eccofs.sh`) |
| Needs from provisioning | Its own `modulefiles/intel_x86_64`, copied into the install: Spack's Intel oneAPI 2023.1 compilers and MKL, Intel MPI 2021.12.1, netcdf-fortran, METIS, libpng by their hashed names, and the NCEP libraries (`bacio`, `bufr`, `g2`, `w3emc`, `w3nco`, `prod-util`, `wgrib2`, `jasper`) |
| Installs to | `$SAVEDIR/nosofs.v3.6.6`, `SAVEDIR` defaulting to `/save/$USER`; forcing to `/com/eccofs/input` |

## What cloudflow expects from it

`fcst_launcher.sh` takes `eccofs` as one of the NOS ROMS models: the
job's `SAVEDIR` is the install, and the launcher runs
`$SAVEDIR/jobs/fcstrun.sh`, which comes from the code package. See
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `restart_date.sh` does `cd ../../cloudflow/utils`: it expects to sit
  in `models/eccofs` of a Cloud-Sandbox checkout, next to cloudflow.
- `setup_eccofs.sh` and `build_eccofs.sh` print the Cloud-Sandbox
  directory two levels up; they use it for nothing else.

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
