# model-ucla-roms

The recipe that fetches and builds UCLA ROMS and its `Rivers_real`
example on a Cloud Sandbox. How to run it is in [README](README), the
original's own description.

## This is a copy

This directory is a copy of `models/ucla-roms/` from the Cloud-Sandbox
repository, made there. Every file is here, byte-identical.
[../MAP.md](../MAP.md#the-model-units) describes how this project would
be moved to a repository of its own. Do not edit the copied files
here: change the original and run `just export model-ucla-roms` at the
repository root.

What is new: this file, `LICENSE`, `Justfile` and `tests/`.

## What the recipe does

| | |
| --- | --- |
| Fetches | `https://github.com/CESR-lab/ucla-roms.git`, its default branch (`setup_uclaroms.sh`); the example's inputs with the repository's own `ci/get_input_files.sh` |
| Builds | The tools in `Tools-Roms/` and the `Rivers_real` example (`compile.sh`, `testcase.sh`) |
| Needs from provisioning | Spack modules, loaded in the scripts themselves from `/mnt/efs/fs1/save/environments/spack/share/spack/modules/linux-rhel8-x86_64`: Intel oneAPI 2023.1 compilers, Intel MPI 2021.9.0, bzip2, lz4, snappy, zstd, c-blosc, netcdf-c and netcdf-fortran, by their hashed names |
| Installs to | `/save/$USER/ucla-roms` (fixed in the scripts) |

## What cloudflow expects from it

`ucla-roms_run.sh` runs the job's `EXEC` in its `MODEL_DIR`; the job
configuration names `/save/ec2-user/ucla-roms/Examples/Rivers_real`
and the `roms` executable in it. See
[the install contract](../MAP.md#the-install-contract).

## Where it reaches outside its directory

Nowhere in its scripts. `README` walks through cloudflow by its path in
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
