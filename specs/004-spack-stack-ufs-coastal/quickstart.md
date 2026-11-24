# Quickstart: checking spack-stack for UFS Coastal

## 1. Without AWS (your local machine)

```sh
cd exportit/sandbox-provisioning && just test        # syntax, lint, the steps' replaces: lines
just full-test                                     # + the container concretizes ufs-stack.yml
cd ../model-ufscoastal && just test                # setup.sh's shellcheck as recorded
cd ../sandbox-ops && just test                     # the catalogue
cd ../.. && just test && just full-test
```

## 2. On AWS (a head node of its own; hours; operator's word at every step)

1. A head node, as spec 001's stages A and B.
2. Before: `/etc/spack`'s listing and the sandbox environment's concretization
   saved.
3. `ufs-stack.yml` applied; then applied again: `changed=0` (SC-001).
4. `module avail` shows the meta-modules (SC-002).
5. `csis-model-ufscoastal`'s `setup.sh`, up to the CMake configure: every
   dependency found (SC-003).
6. After: `/etc/spack` and the concretization as before (SC-004).
7. Removal, as spec 001's stage E.
