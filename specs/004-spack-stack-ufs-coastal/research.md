# Research: spack-stack for UFS Coastal

Each item records a decision, why, and what else was weighed. Written on
2026-11-21.

## R1. Which spack-stack (FR-001's first task, begun)

**Decision**: the candidate is JCSDA's latest 2.1.x release (2.1.1 when this
was written), checked in this order when the work starts: (1) the spack-stack
version UFS Coastal's current tag names, if it names one; (2) the release
notes' list of supported platforms, for a generic Linux site
(`linux.default`) on a RHEL-9-or-later system; (3) a concretization of its
`unified-dev` template in the container (R6). If 2.1.x fails (3), 2.0.0; if
both fail, the fork `asascience-open/spack-stack` at the commit the operator
names, per FR-001, recorded with the reason.

**Rationale**: 2.0.0 (released 2026-01-06) moved spack-stack onto Spack 1.0
(compilers as packages, packages in their own repository), which is what
FR-001 asks for; JCSDA had moved on to 2.1.0 by March 2026, and UFS's weather
model is moving to 2.1.x. No release states RHEL 10 support, so the container
concretization is the test. spack-stack carries its own Spack (a submodule);
it is not the sandbox's Spack v1.2.0, and the two do not share an install
tree.

Sources: [spack-stack releases](https://github.com/JCSDA/spack-stack/releases);
[UFS weather model, update to spack-stack 2.1.x](https://github.com/ufs-community/ufs-weather-model/issues/3067);
[GDASApp, upgrade to spack-stack 2.x](https://github.com/NOAA-EMC/GDASApp/issues/2057).

**Alternatives considered**: the fork first (its changes are undescribed);
the `develop` branch (not a release; FR-001 names a tag or a commit).

## R2. Where it is installed

**Decision**: `/save/environments/spack-stack-<version>/` (the clone, with
its submodules), and the environment `aws-ioossb-rhel10` under its `envs/`.
Both paths are variables of the playbook (`ufs_stack_version`,
`ufs_stack_dir`, `ufs_stack_env_name`).

**Rationale**: beside the sandbox's own environments on the EFS volume, as
the old `spack-stack.v2.0` was, and named for RHEL 10, so the old RHEL 8 path
is never mistaken for it.

## R3. The playbook, step by step

**Decision**: `ufs-stack.yml` in `csis-sandbox-provisioning`: `git` clone at
the tag, with `--recurse-submodules`; then the collection's `setup` role with
a list `ufs_stack_setup`, each step naming the line of
`setup_spack-stack`/`build_spack-stack-environment` (in `legacy/`) it
replaces:

| Step kind | What | Replaces |
| --- | --- | --- |
| `environment` | source spack-stack's `setup.sh`; the oneAPI modules | `source setup.sh`; `module load` |
| `command` | `spack stack create env --site linux.default --template unified-dev --name aws-ioossb-rhel10 --compiler oneapi` (`creates:` the env's `spack.yaml`) | the same, `rhel8` |
| `detect` | externals, into the environment's scope (R4) | `spack external find --scope system` |
| `config` | the three settings the script added, into the environment's scope | three `spack config add` |
| `command` | `spack add sp` (unless present) | the same |

then `spack_env` for the environment (`concretize`, `install`,
`refresh_modules: when_needed`), then a `command` step for `spack stack
setup-meta-modules` (`creates:` its `Core` directory).

**Rationale**: FR-003; idempotence comes from the modules (`spack_env`
installs only what is missing; `creates:` guards the two commands), so the
second apply changes nothing (SC-001).

## R4. Scopes

**Decision**: every `detect` and `config` step names the environment's own
scope (`--scope env:aws-ioossb-rhel10` or the module's equivalent), or
spack-stack's site scope where a setting must apply to the whole stack;
never `system`. The proof saves `ls -la --time-style=full-iso /etc/spack` and
the sandbox environment's `spack concretize --fresh` output before the
playbook, and compares after (SC-004).

**Rationale**: FR-004; `/etc/spack` is shared with the sandbox's Spack.

## R5. The compiler

**Decision**: `--compiler oneapi`, the oneAPI the sandbox's `intel_oneapi`
role installs, found by spack-stack's Spack as an external compiler
package; RHEL 10's GCC 14 as its GCC. No toolset (FR-002).

**Finding for the operator**: `csis-model-ufscoastal`'s `setup.sh` sources
`/opt/rh/gcc-toolset-13/enable` before `build.sh`, with a comment that `ar`
segfaulted without it on RHEL 8. RHEL 10 has no `gcc-toolset-13`; the line is
removed in that unit, and if `ar` fails again it is a finding, not a reason
to add a toolset.

## R6. The container

**Decision**: `csis-sandbox-provisioning`'s container test (`just
full-test`) gains a run of `ufs-stack.yml` with a variable that stops after
concretization (`ufs_stack_install: false`), asserting the environment
concretizes (User Story 1, scenario 3). It needs the network to clone
spack-stack, as the container test already does for the collection.

## R7. What UFS Coastal must find (SC-003)

**Decision**: `csis-model-ufscoastal` changes in its own repository:
`README` (FR-006: spack-stack from `ufs-stack.yml`, not
`ufs-setup-instance.sh`); `setup.sh` (the new `setup.sh` path, no toolset,
R5); `modulefiles/tcl/ufs_ioossb.intel.tcl` and
`modulefiles/lua/ufs_ioossb.intel.lua` (the new environment's `Core` path,
and each `module load` at the version the new environment provides, read
from its `module avail`). The proof runs `setup.sh` up to `build.sh`'s
CMake configure, which is where it has found its dependencies.

**Rationale**: SC-003 cannot hold while the module file names the RHEL 8
environment's path and versions; FR-006 names the README, and these files are
the same unit's, owned since 2026-11-19.

## R8. Where it is proved

**Decision**: a head node of its own (FR-007), built with spec 001's
`proof/` files and stages A and B, then `ufs-stack.yml` applied twice, the
checks of SC-001 to SC-004, and removal as spec 001's stage E. If spec 002's
cache is in place by then, `spack_cache_only: 0` shortens the sandbox's own
build; spack-stack's own build has no cache (Out of Scope).

## R9. The scripts

**Decision**: as spec 002's R8: `add-ufs-setup.sh` and `ufs-envars.sh` keep
the status `in-use` in `CATALOGUE.tsv` with `superseded_by` naming
`csis-sandbox-provisioning: ufs-stack.yml`, and a header line each; the two
spack-stack push scripts are left as they are (FR-005).
