# Feature Specification: spack-stack for UFS Coastal

**Feature Branch**: none yet; `feature/spack-stack-ufs-coastal` when it is
taken up

**Created**: 2026-11-14, as stage 18; carried into this spec 2026-11-19

**Status**: **Complete**, 2026-11-28. Planned and tasked 2026-11-21; tasks
corrected by the analyses of 2026-11-26 and 2026-11-28; implemented and
proved on a head node of its own 2026-11-27 and 28, released in
`csis-sandbox-provisioning` 0.0.6 to 0.0.10, the node removed; converged;
merged into `develop` here and in its three units. Outcome below.

**Input**: the stage plan of 2026-11-14, carried from the ATTIC on the
operator's instruction of 2026-11-19.

## Why

UFS Coastal builds against spack-stack, a Spack distribution with its own
environments and meta-modules, not against the sandbox's Spack environment.
Today that is `csis-sandbox-ops`' `bin/add-ufs-setup.sh`, with
`ufs-envars.sh`, run by hand on a built head node, and it **fails as
written**: its line 27 calls `install_gcc_toolset_yum`, which the setup
script's library no longer defines. Its versions are RHEL 8's
(`linux-rhel8`, Spack v0.22.5, spack-stack 2.0 from the fork
`asascience-open/spack-stack`). `csis-model-ufscoastal`'s README still points
to `ufs-setup-instance.sh`, which is superseded.

What the functions it calls did (the setup script's `setup_spack-stack` and
`build_spack-stack-environment`, kept in `csis-sandbox-provisioning`'s
`legacy/`): clone the fork, `spack gpg` and a mirror, `spack stack create env
--site linux.default --template unified-dev --name aws-ioossb-rhel8
--compiler=oneapi`, find externals at the system scope, three `config add`,
add `sp`, concretize, install, `module tcl refresh`, `spack stack
setup-meta-modules`.

## Clarifications

### Session 2026-11-21

- Q: Which spack-stack should the playbook build? → A: an upstream JCSDA
  release if one supports RHEL 10 and Spack 1.x; otherwise the fork
  `asascience-open/spack-stack` at a commit the operator names, so the spec
  never waits.
- Q: Which compiler should spack-stack's environment be built with? → A:
  oneAPI, as the script, on RHEL 10's own GCC 14; no GCC toolset.
- Q: Where should spack-stack's settings and externals be written? → A: in
  the environment's own scope and spack-stack's site scope; nothing in
  `system`, and a check shows `/etc/spack` unchanged.
- Q: What happens to `add-ufs-setup.sh`, `ufs-envars.sh` and the two
  spack-stack push scripts? → A: the two UFS scripts stay in
  `csis-sandbox-ops`, marked as replaced by `ufs-stack.yml`; the push scripts
  stay unmarked, for a later cache spec; no mapping line changes.
- Q: What head node should `ufs-stack.yml` be proved on? → A: one of its own,
  built with spec 001's module and procedure, removed at the end, each step
  asked first (spec 001 removes its own node, so that one is not there).

### Session 2026-11-26

FR-001's first task found: JCSDA's latest stable release is 2.1.1
(2026-07-18; 2.2.0 is a pre-release), stating no RHEL 10 support; UFS
Coastal's repository (`asascience-open/ufs-weather-model`) names spack-stack
1.6.0 at its one tag, `v1.0.0b01`, and 1.9.2 on its active branch, as
upstream's `develop` does, none of them on Spack 1.x; and the fork
`asascience-open/spack-stack` has, on its branch `aws-rhel10`, commit
`406b090aa4828fb7be840eea33c83963d88ac84e` (2026-10-05, "ufs weather app -
coastal", on JCSDA's 2.1.0), adding a site `aws-rhel10` that declares this
sandbox's oneAPI 2024.2.1 at `/opt/intel/oneapi` and a template
`ioos-ufscoastal` that builds `ufs-weather-model-env` alone.

- Q: Which spack-stack should the playbook build? → A: the fork at commit
  `406b090aa4828fb7be840eea33c83963d88ac84e`, with its site `aws-rhel10` and
  its template `ioos-ufscoastal` (the operator, 2026-11-26), in place of
  JCSDA 2.1.1's `linux.default` and `unified-dev`.

### Session 2026-11-27

- Q: T020 found that a second apply changes something: `spack_env`'s refresh
  `when_needed` regenerated the module files with `--delete-tree` on every
  run, deleting the meta-modules (the collection's `spack_env` does not
  expand `$env` in spack-stack's module root, and `setup-meta-modules`
  rewrites the Tcl module files, so the refresh could not settle). How should
  the module files be made? → A: with the meta-modules, as two `command`
  steps guarded by the meta-modules' directory, which the play removes
  whenever `spack_env` concretized or installed something; FR-003 is amended,
  and the collection's bug gets a spec of its own in
  `ansible-collection-csis-spack`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - spack-stack built on a head node by a playbook (Priority: P1)

The operator applies one playbook on a built head node and gets spack-stack's
environment and meta-modules, built; applied again, nothing changes.

**Why this priority**: UFS Coastal cannot be built on today's sandbox without
it, and the script that did it is broken.

**Independent Test**: the playbook applied twice on a head node; `module
avail` after.

**Acceptance Scenarios**:

1. **Given** a built head node, **When** `ufs-stack.yml` is applied, **Then**
   spack-stack's environment is created and built, and `module avail` shows its
   meta-modules.
2. **Given** that node, **When** it is applied again, **Then** nothing changes.
3. **Given** the container, **When** the playbook runs there, **Then** the
   environment concretizes (a fake install cannot build it).

### User Story 2 - UFS Coastal builds against it (Priority: P2)

UFS Coastal's own build script, from `csis-model-ufscoastal`, finds what it
needs.

**Why this priority**: it is what the stack is for.

**Independent Test**: UFS Coastal's build script on that node, up to the
point where it has found its dependencies.

**Acceptance Scenarios**:

1. **Given** the built stack, **When** UFS Coastal's build script runs,
   **Then** it finds every dependency it needs.

### Edge Cases

- No JCSDA release supports RHEL 10 and Spack 1.x when the spec is taken up:
  the fork is used, at the commit the operator names (FR-001); the spec does
  not wait.
- The fork's commit does not build on RHEL 10 either: the spec stops there
  and says so; nothing is patched in the fork without the operator's word.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playbook MUST build JCSDA's spack-stack at a release that
  supports RHEL 10 and Spack 1.x, preferring the one UFS Coastal's current tag
  names. The first task finds what JCSDA has released. If no release fits,
  the playbook MUST build the fork `asascience-open/spack-stack` instead, at a
  commit the operator names, and the spec MUST record which was chosen and
  why. The tag or commit is a variable of the playbook, never a branch.
- **FR-002**: The environment MUST be built with oneAPI, the one the sandbox
  already installs and the setup role's Intel list registers
  (`--compiler=oneapi`, as the script), on RHEL 10's own GCC 14. No GCC
  toolset is installed; the script's `install_gcc_toolset_yum` call is not
  carried over.
- **FR-003**: `csis-sandbox-provisioning` MUST gain a playbook,
  `ufs-stack.yml`, not part of `site.yml`: clone spack-stack at the chosen tag;
  the collection's `setup` role with a list (an `environment` step for
  spack-stack's `setup.sh` and the Intel modules, `command` steps for `spack
  stack create env` and `spack stack setup-meta-modules`, `detect` steps for its
  externals, a `config` step for its settings), each step naming the script's
  line it replaces; then `spack_env` for the environment it creates, which
  concretizes and installs it; then `command` steps for `spack module tcl
  refresh` and `spack stack setup-meta-modules`, made again whenever
  `spack_env` concretized or installed something (amended 2026-11-27, see
  Clarifications: it named `spack_env`'s `refresh_modules: when_needed`).
- **FR-004**: The playbook's `detect` and `config` steps MUST write to the
  environment's own scope and the site scope of spack-stack's Spack, never to
  the `system` scope (`/etc/spack`), which the sandbox's own Spack shares. The
  proof MUST show `/etc/spack` unchanged by the playbook, and the sandbox's
  environment concretizing as before.
- **FR-005**: `add-ufs-setup.sh` and `ufs-envars.sh` MUST stay in
  `csis-sandbox-ops`, marked as replaced: their headers and `CATALOGUE.tsv`
  name `ufs-stack.yml` in `csis-sandbox-provisioning`, whose variables take
  the versions `ufs-envars.sh` held. Only that unit has them, so nothing moves
  between units and no mapping line changes (constitution, principle I).
  `spack-stack-update-mirror.sh` and `spack-stack-mirror-create.sh` stay as
  they are, unmarked: this spec builds no spack-stack cache, so nothing
  replaces them yet.
- **FR-006**: `csis-model-ufscoastal`'s README MUST be corrected in that unit,
  which owns its copied files since 2026-11-19.
- **FR-007**: The proof MUST run on a head node of this spec's own, built with
  spec 001's Terraform module and procedure, in the same account, region and
  VPC, creating only new resources. At the end everything it created MUST be
  removed, each step asked first, and checked gone, as spec 001's FR-015.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `ufs-stack.yml` applied twice on a head node, the second run
  changing nothing.
- **SC-002**: `module avail` shows spack-stack's meta-modules.
- **SC-003**: UFS Coastal's own build script finds what it needs.
- **SC-004**: `/etc/spack` is as it was before the playbook, and the sandbox's
  own environment concretizes to the same specs.

## Assumptions

- The collection's `setup` role and modules are enough to express what the
  script did; anything they cannot is a change to the collection, released
  first.

## Dependencies

- Spec 001: its Terraform module and procedure, to build this spec's own head
  node (FR-007).
- Spec 002 leaves the two spack-stack push scripts to this spec, which leaves
  them as they are for a later spec on spack-stack's cache (FR-005).
- Spec 009 (2026-11-25, its clarification), merged first: this spec's head
  node is the first built with 009's change, and its first boot is 009's proof
  on a real node; the record of that first boot says whether it ended
  `failed=0`, installed from the RHEL 10 cache, and ran the `from_mirrors`
  steps with no prompt.

## Out of Scope

Building UFS Coastal itself (`csis-model-ufscoastal`'s recipes do that); the
spack-stack build cache.

## Carried From

Stage 18, planned 2026-11-14, now in the ATTIC (`ATTIC/SPECS/STAGE-18.md`),
as a pointer for a person reading; this spec stands without it.

## Outcome

Implemented 2026-11-26 to 28 by the agent, each merge, release and AWS step on
the operator's word. The tasks' records (T004, T017 to T025) hold each step's
evidence; this is their summary.

**Which spack-stack** (FR-001): the fork `asascience-open/spack-stack` at
`406b090aa4828fb7be840eea33c83963d88ac84e`, with its `aws-rhel10` site and
`ioos-ufscoastal` template, chosen by the operator on 2026-11-26 when no JCSDA
release fitted (2.1.1, the latest, has no RHEL 10 site and none of UFS
Coastal's pins). The fork is unchanged: its site's Intel entries, which name an
MPI the sandbox lacks and load Intel's modules, are overridden in the
environment's own `site/` scope, which `spack stack create env` writes
(Edge Cases).

**Releases**: `csis-sandbox-provisioning` 0.0.6 (the playbook), and 0.0.7 to
0.0.10, each a fix the head node found. Its last changes (a page on building
spack-stack, the playbook's header and a test) stay unreleased on `develop`,
on the operator's word of 2026-11-28. `csis-sandbox-ops` and
`csis-model-ufscoastal` change on their `develop` and cut no release.

**The proof**, on a head node of its own (`c6i.8xlarge`, the noaa account,
us-east-2, the IOOS VPC), removed at the end with nothing left (FR-007):

| Criterion | Evidence |
| --- | --- |
| SC-001 | from 0.0.9's checkout, two applies `changed=0` (T020); 0.0.10's change, applied by hand, `changed=4` then `changed=0` (T023) |
| SC-002 | `stack-intel-oneapi-compilers/2024.2.1`, then `stack-intel-oneapi-mpi/2021.13`, then ESMF 8.8.0, FMS, MAPL, CRTM, HDF5, NetCDF and PIO at T014's versions (T021) |
| SC-003 | UFS Coastal's `setup.sh` loaded its module file and CMake found every dependency; the model then built (`ufs_model`, eight minutes) (T023) |
| SC-004 | `/etc/spack` absent before and after; the sandbox's environment concretizing to the same 36 hashes, its lock unchanged (T018, T022) |

Its first boot was spec 009's proof on a real node: `failed=0`, the
environment from the RHEL 10 cache, the three `from_mirrors` steps with no
prompt (T017).

**The build's time**: the clone of spack-stack, about ten minutes on the node;
the environment, about two hours of compiling (a build by hand, 13:59 to
16:01 UTC with one fix between); the first apply from 0.0.8, 1 h 41 min,
since new system packages had given Spack more externals and 74 packages were
built again; a second apply, two to three minutes.

**Findings**, each with what carries it:

| Finding | Fix |
| --- | --- |
| The account's patch scan (State Manager) ran `dnf clean all` during the first boot's update, which failed | the node replaced; `csis-sandbox-provisioning`'s spec 001 (dnf retries) |
| Spack cannot read the sandbox's Intel module files (a `®` that is not UTF-8), which the fork's site names | 0.0.7: the sandbox's oneAPI declared with no modules |
| RHEL 10's Perl lacks `FindBin`, which OpenSSL's build needs; and `install_spack-stack_prereqs`, which `add-ufs-setup.sh` called, had been missed | 0.0.8: that function's packages and Perl whole |
| HDF5's CMake stops at the system zlib's CMake files without its static library | 0.0.8: `zlib-ng-compat-static` |
| `spack_env` takes `$env/modules` literally and regenerated the module files every run, deleting the meta-modules; with the root found, `setup-meta-modules`' rewrites would keep it from settling | 0.0.9: the module files made with the meta-modules; the collection's spec 014 |
| The module Spack makes for the external MPI sets no `I_MPI_ROOT`, so `use mpi` fails | 0.0.10: set in the stack's MPI module |
| `setup.sh` put `modulefiles/`, not `modulefiles/tcl/`, on the module path | `csis-model-ufscoastal` `e6db006` |
| Check mode on a built node reports changes it would not make (its preview's copy has an empty `$env/install`) | documented; the collection's spec 014, FR-007 |
| The `ar` failure of RHEL 8, the reason for the GCC toolset, did not come back | none needed |

The ones that outlive this spec are in [exportit/REMINDERS.md](../../exportit/REMINDERS.md).

