# Data model: spack-stack for UFS Coastal

## The playbook's variables (`ufs-stack.yml`'s `vars`)

| Variable | Default | Notes |
| --- | --- | --- |
| `ufs_stack_repo` | `https://github.com/asascience-open/spack-stack.git` | the fork (FR-001; the operator's choice, 2026-11-26) |
| `ufs_stack_version` | `406b090aa4828fb7be840eea33c83963d88ac84e` | the operator's commit; never a branch (FR-001) |
| `ufs_stack_dir` | `/save/environments/spack-stack-{{ ufs_stack_version }}` | the clone |
| `ufs_stack_env_dir` | `{{ ufs_stack_dir }}/envs/{{ ufs_stack_env_name }}` | the environment |
| `ufs_stack_env_scope` | `env:{{ ufs_stack_env_dir }}` | Spack's name for the environment's own scope, where the `detect` and `config` steps write (FR-004) |
| `ufs_stack_env_site_scope` | `{{ ufs_stack_env_scope }}:{{ <the real path of ufs_stack_env_dir> }}/site` | the scope of the environment's `site/` directory, which `spack stack create env` fills from the fork's site; Spack names it by the real path (`/save` is a link), which the play finds with `realpath` (0.0.7) |
| `ufs_stack_intel_externals` | the sandbox's oneAPI compilers, classic Fortran and TBB, at their prefixes, `buildable: false`, no `modules` | written with `intel_oneapi_spack_packages` into `ufs_stack_env_site_scope`, each list of externals set exactly, in place of the fork's site's entries, which load Intel's module files (whose `®` Spack cannot read) and name MPI 2021.16 (0.0.7) |
| `ufs_stack_tbb_version` | `2021.13` | oneAPI 2024.2's TBB, as the fork's site names it (0.0.7) |
| `ufs_stack_system_packages` | `binutils-devel`, `git-lfs`, `bash-completion`, `xorg-x11-xauth`, `perl-IPC-Cmd`, `gettext-devel`, `perl`, `zlib-ng-compat-static` | installed with dnf as root before the clone: `install_spack-stack_prereqs`'s six (L309-L314), Perl whole (`FindBin`, for OpenSSL) and zlib's static library (for HDF5's CMake) (0.0.8) |
| `ufs_stack_meta_modules_dir` | `{{ ufs_stack_env_dir }}/modules/Core` | where `spack stack setup-meta-modules` writes; removed when the environment or the MPI module's settings change, which makes the module files again (0.0.9, 0.0.10) |
| `ufs_stack_spack` | `{{ ufs_stack_dir }}/spack/bin/spack` | the fork's Spack |
| `ufs_stack_extra_specs` | `[sp@2.5.0]` | added to the template's specs, as the script did (L444) |
| `ufs_stack_env_name` | `aws-ioossb-rhel10` | |
| `ufs_stack_site` | `aws-rhel10` | the fork's site for this sandbox |
| `ufs_stack_template` | `ioos-ufscoastal` | the fork's template: `ufs-weather-model-env` and its pins |
| `ufs_stack_compiler` | `oneapi` | FR-002 |
| `ufs_stack_install` | `true` | `false` stops after concretizing (the container, R6) |
| `ufs_stack_setup` | the list of R3, up to the concretization | each step names the legacy line it replaces in a `# Replaces <file> L<n>` comment above it, held by `tests/test_traceability.py`; no `replaces:` key, which the collection's `setup` role refuses |
| `ufs_stack_after_install` | the module files' and the meta-modules' steps | the role applied a second time, after `spack_env`, when `ufs_stack_install` is true: `spack module tcl refresh -y --delete-tree` and `spack stack setup-meta-modules`, both guarded by `ufs_stack_meta_modules_dir` (FR-003, amended 2026-11-27); the role keeps nothing between applications |

The sandbox's `group_vars/all.yml` gives the rest: `sandbox_user`, the oneAPI
versions and modules, `spack_jobs`; and `roles/intel_oneapi/defaults/main.yml`
`intel_oneapi_spack_packages`, declared again in the environment's `site/`
scope with `ufs_stack_intel_externals` (T008; moved there in 0.0.7). The
versions are the sandbox's, not `ufs-envars.sh`'s (the playbook's header;
T043).

## The choice of FR-001, recorded

| Field | Value |
| --- | --- |
| source | `JCSDA` release or `fork` |
| ref | the tag or commit |
| why | which of R1's checks it passed, or why the fork |
| date | when chosen |

Recorded in the spec's outcome and in the playbook's defaults' comment.

## What the node has afterwards

| Path | What |
| --- | --- |
| `{{ ufs_stack_dir }}` | spack-stack and its Spack, at the ref |
| `{{ ufs_stack_dir }}/envs/aws-ioossb-rhel10/` | the environment, concretized and installed |
| `{{ ufs_stack_dir }}/envs/aws-ioossb-rhel10/modules/` | the Tcl module files, in spack-stack's hierarchy (`oneapi/2024.2.1/…`, `impi/2021.13/oneapi/2024.2.1/…`) |
| `{{ ufs_stack_dir }}/envs/aws-ioossb-rhel10/modules/Core` | the meta-modules: `stack-intel-oneapi-compilers/2024.2.1`, which offers `stack-intel-oneapi-mpi/2021.13` |
| `/etc/spack` | unchanged (SC-004) |
