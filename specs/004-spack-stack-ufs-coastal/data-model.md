# Data model: spack-stack for UFS Coastal

## The playbook's variables (`ufs-stack.yml`, `group_vars` or its own defaults)

| Variable | Default | Notes |
| --- | --- | --- |
| `ufs_stack_repo` | `https://github.com/JCSDA/spack-stack.git` | the fork's URL if FR-001 falls back |
| `ufs_stack_version` | the release chosen by R1 (a tag), or the operator's commit | never a branch (FR-001) |
| `ufs_stack_dir` | `/save/environments/spack-stack-{{ ufs_stack_version }}` | the clone |
| `ufs_stack_env_name` | `aws-ioossb-rhel10` | |
| `ufs_stack_site` | `linux.default` | |
| `ufs_stack_template` | `unified-dev` | |
| `ufs_stack_compiler` | `oneapi` | FR-002 |
| `ufs_stack_install` | `true` | `false` stops after concretizing (the container, R6) |
| `ufs_stack_setup` | the list of R3 | each step's `replaces:` names the legacy line |

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
