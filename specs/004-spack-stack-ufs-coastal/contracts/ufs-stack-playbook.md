# Contract: `ufs-stack.yml`

**Where**: `csis-sandbox-provisioning`, beside `site.yml`, not imported by it;
run by hand on a head node `site.yml` has built.

| Run | Result |
| --- | --- |
| first apply | spack-stack cloned at the ref; the environment created, concretized, installed; meta-modules set up; `module avail` shows them |
| second apply | `changed=0` |
| check mode | lists what would change; changes nothing |
| `ufs_stack_install: false` (the container) | stops after concretizing; the concretization succeeds |
| the ref is a branch | fails before cloning, naming the variable |

Never writes to `/etc/spack`; never installs a GCC toolset.

# Contract: what UFS Coastal reads (`csis-model-ufscoastal`)

- `setup.sh` sources `{{ ufs_stack_dir }}/setup.sh` and loads
  `ufs_ioossb.intel`, which names the new environment's `Core` path and the
  versions it provides.
- Run on the node up to `build.sh`'s CMake configure, it finds every
  dependency (SC-003).
