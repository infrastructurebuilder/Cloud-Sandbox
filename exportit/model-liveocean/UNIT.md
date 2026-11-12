# model-liveocean

The recipe that fetches, builds and feeds LiveOcean, the University of
Washington's ROMS forecast for the Salish Sea and the coast of
Washington and Oregon, on a Cloud Sandbox. How to run it is in
[README](README) and [LIVEOCEAN-MODEL.md](LIVEOCEAN-MODEL.md), the
original's own descriptions.

## This is a copy

This directory is a copy of `models/liveocean/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-liveocean` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/asascience/LiveOcean.git` (`main`), the job scripts; then (`get_LO_ROMS.sh`) `parkermac/LO`, `asascience/LO_roms_user`, `parkermac/LO_roms_source_alt` and `myroms/roms` from GitHub; the forcing and the grid from `s3://ioos-sandbox-use2/public/LiveOcean` |
| Builds | ROMS for the `x4b` case in `LO_roms_user/x4b` (`LO_COMPILE.sh`), with `Compilers/Linux-ifort.mk` copied in |
| Needs from provisioning | Its own `modulefiles/intel_x86_64`, copied into the install: Spack's Intel oneAPI 2023.1 compilers, MKL and netcdf-fortran by their hashed names |
| Installs to | `$SAVEDIR/LiveOcean`, `SAVEDIR` defaulting to `/save/$USER`; data to `/com/$USER/liveocean` |

## What cloudflow expects from it

`fcst_launcher.sh` runs `$SAVEDIR/LiveOcean/jobs/fcstrun.sh` for the
`liveocean` application; the job's `SAVEDIR` is the directory *above*
the install. See [the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `setup_LiveOcean.sh` prints the Cloud-Sandbox directory two levels
  up and uses it for nothing else.
- `get_LiveOcean_grid.sh` names its data directory after the directory
  two levels up.

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
