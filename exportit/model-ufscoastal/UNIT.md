# model-ufscoastal

The recipe that fetches and builds the UFS Coastal application of the
UFS weather model, and runs its regression tests, on a Cloud Sandbox.
How to use it is in [README](README), the original's own description.

## This is a copy

This directory is a copy of `models/ufscoastal/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-ufscoastal` at
the repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/asascience-open/ufs-weather-model.git`, its default branch, with its submodules (`setup.sh`); the regression tests' inputs from `s3://ioos-transfers/UFS_coastal_app/` (`get_input_data.sh`) |
| Builds | The `CSTLR` application with the model's `build.sh --platform=ioossb --compiler=intel` |
| Needs from provisioning | spack-stack 2.0 at `/save/environments/spack-stack.v2.0`, environment `aws-ioossb-rhel8`, through `modulefiles/tcl/ufs_ioossb.intel.tcl` (Intel oneAPI 2024.2.1, Intel MPI 2021.13, ESMF 8.8.0, MAPL, FMS and the NCEP libraries), and `gcc-toolset-13`. The Lua files are for other machines (Hercules, WCOSS2) |
| Installs to | `$SAVEDIR/ufs-weather-model`, `SAVEDIR` defaulting to `/save/$USER`; inputs to `/com/ufs-weather-model/RT/NEMSfv3gfs/input-data-20250507` |

## What cloudflow expects from it

`ufs_launcher.sh` runs the regression tests in
`$SAVEDIR/ufs-weather-model/tests`, with its own copy of
`rt_ioossb.conf`, and writes to `/com/ufs-weather-model/RT`. See
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

- `README` points at `scripts/ufs-setup-instance.sh` of Cloud-Sandbox,
  which installs spack-stack.
- `setup.sh` and `testing_rt.sh` print the Cloud-Sandbox directory two
  levels up; they use it for nothing else.

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
