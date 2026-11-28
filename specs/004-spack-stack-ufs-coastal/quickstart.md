# Quickstart: checking spack-stack for UFS Coastal

## 1. Without AWS (your local machine)

```sh
cd exportit/sandbox-provisioning && just test        # syntax, lint, the steps' # Replaces comments
just full-test                                     # + the container concretizes ufs-stack.yml
cd ../model-ufscoastal && just test                # setup.sh's shellcheck as recorded
cd ../sandbox-ops && just test                     # the catalogue
cd ../.. && just test && just full-test
```

## 2. On AWS (a head node of its own; hours; operator's word at every step)

The container test in section 1 takes about an hour and a half: it clones
spack-stack (38 minutes) and concretizes. The node's checkout must be at
`csis-sandbox-provisioning` **0.0.10 or later**: 0.0.6 to 0.0.9 do not build
the stack on a head node (spec 004's T019 to T023). Each step's evidence is
in T017 to T025's records in [tasks.md](tasks.md).

1. A head node, as spec 001's stages A and B.
2. Before: `/etc/spack`'s listing and the sandbox environment's concretization
   saved.
3. `ufs-stack.yml` applied, which builds for about two hours on a
   `c6i.8xlarge` (the first apply on spec 004's node took 1 h 41 min, after a
   build by hand had found the last of the system packages); then applied again:
   `changed=0` (SC-001).
4. `module avail` shows the meta-modules (SC-002).
5. `csis-model-ufscoastal`'s `setup.sh`, up to the CMake configure: every
   dependency found (SC-003). On spec 004's node it went on to build the model
   (`ufs_model`, eight minutes), from `csis-model-ufscoastal` `e6db006`.
6. After: `/etc/spack` and the concretization as before (SC-004).
7. Removal, as spec 001's stage E.
