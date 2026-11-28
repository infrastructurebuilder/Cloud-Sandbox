# Data model: spack-stack for UFS Coastal

## The playbook's variables (`ufs-stack.yml`'s `vars`)

| Variable | Default | Notes |
| --- | --- | --- |
| `ufs_stack_repo` | `https://github.com/asascience-open/spack-stack.git` | the fork (FR-001; the operator's choice, 2026-11-26) |
| `ufs_stack_version` | `406b090aa4828fb7be840eea33c83963d88ac84e` | the operator's commit; never a branch (FR-001) |
| `ufs_stack_dir` | `/save/environments/spack-stack-{{ ufs_stack_version }}` | the clone |
| `ufs_stack_env_dir` | `{{ ufs_stack_dir }}/envs/{{ ufs_stack_env_name }}` | the environment |
| `ufs_stack_env_scope` | `env:{{ ufs_stack_env_dir }}` | Spack's name for the environment's own scope, where the `detect` and `config` steps write (FR-004) |
| `ufs_stack_spack` | `{{ ufs_stack_dir }}/spack/bin/spack` | the fork's Spack |
| `ufs_stack_extra_specs` | `[sp@2.5.0]` | added to the template's specs, as the script did (L444) |
| `ufs_stack_env_name` | `aws-ioossb-rhel10` | |
| `ufs_stack_site` | `aws-rhel10` | the fork's site for this sandbox |
| `ufs_stack_template` | `ioos-ufscoastal` | the fork's template: `ufs-weather-model-env` and its pins |
| `ufs_stack_compiler` | `oneapi` | FR-002 |
| `ufs_stack_install` | `true` | `false` stops after concretizing (the container, R6) |
| `ufs_stack_setup` | the list of R3, up to the concretization | each step names the legacy line it replaces in a `# Replaces <file> L<n>` comment above it, held by `tests/test_traceability.py`; no `replaces:` key, which the collection's `setup` role refuses |
| `ufs_stack_after_install` | the meta-modules' steps | the role applied a second time, after `spack_env`, when `ufs_stack_install` is true; it keeps nothing between applications |

The sandbox's `group_vars/all.yml` gives the rest: `sandbox_user`, the oneAPI
versions and modules, `spack_jobs`; and `roles/intel_oneapi/defaults/main.yml`
`intel_oneapi_spack_packages`, declared again in the environment's scope,
since the fork's site names an MPI the sandbox does not have (T008).

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
| `…/install/modulefiles/Core` (or as the release names it) | the meta-modules, `stack-intel-oneapi-compilers` and the rest |
| `/etc/spack` | unchanged (SC-004) |
