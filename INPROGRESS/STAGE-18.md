# Stage 18: spack-stack for UFS Coastal

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. It is executed on "do 18", after each **YOUR DECISION** below
has been asked, one at a time. Ninth in the order of the remaining work
([PLAN.md](../PLAN.md)): the largest of the independent stages, and its
proof needs a real head node, so it comes after the live proof (stage
15).

## Why

UFS Coastal builds against spack-stack, a Spack distribution with its
own environments and meta-modules, not against the sandbox's Spack
environment. Today that is `sandbox-ops/bin/add-ufs-setup.sh` with
`ufs-envars.sh`, run by hand on a built head node, and it **fails as
written**: L27 calls `install_gcc_toolset_yum`, which
`funcs-setup-instance.sh` no longer defines (stage 7). Its versions are
RHEL 8's (`linux-rhel8`, Spack v0.22.5, spack-stack 2.0 from the fork
`asascience-open/spack-stack`). `models/ufscoastal/README` still points
to `ufs-setup-instance.sh`, which is superseded.

What the functions it calls do (`funcs-setup-instance.sh`
`setup_spack-stack`, L340-L421, and `build_spack-stack-environment`,
L428-L478): clone the fork, `spack gpg` and a mirror, `spack stack create
env --site linux.default --template unified-dev --name aws-ioossb-rhel8
--compiler=oneapi`, find externals at the system scope, three `config
add`, add `sp`, concretize, install, `module tcl refresh`, `spack stack
setup-meta-modules`.

## Items

1. **YOUR DECISION (which spack-stack):** the release of JCSDA's
   spack-stack that supports RHEL 10 and Spack 1.x, if there is one when
   the stage runs (default: the fork's changes are not described
   anywhere, and an upstream release is what UFS's own instructions
   name); or the fork, at a commit the operator names. The first step of
   the stage is to find out what JCSDA has released for RHEL 10 and
   Spack 1.x, and whether UFS Coastal's current tag names one.

2. **YOUR DECISION (the compiler):** oneAPI, as the script (default:
   the sandbox already installs it, and the setup role's Intel list
   already registers it); or a GCC toolset, which is what the broken
   `install_gcc_toolset_yum` was for.

3. **A playbook, `ufs-stack.yml`,** not part of `site.yml`, applied on a
   built head node:
   - clone spack-stack at the chosen tag (Ansible's `git`);
   - the collection's `setup` role with a list: an `environment` step for
     spack-stack's own `setup.sh` and the Intel modules, then `command`
     steps for `spack stack create env` (`changes: creates`, its
     directory) and `spack stack setup-meta-modules` (`changes: always`),
     `detect` steps for its externals, a `config` step for its settings,
     each step naming the script's line;
   - `spack_env` for the environment it creates, with
     `refresh_modules: when_needed`.

   **YOUR DECISION (the scope):** the environment's own scope and the
   site scope of spack-stack's Spack (default: nothing at the `system`
   scope, which is one node's `/etc/spack`); or `system`, as the script.

4. **`add-ufs-setup.sh` and `ufs-envars.sh`** move to
   `sandbox-provisioning/legacy/` with the two functions accounted for,
   line by line; `models/ufscoastal`'s copy (`model-ufscoastal`) gets its
   README corrected by a patch, or noted in MAP.md if it stays a byte
   copy.

5. **Proof:** the container concretizes (fake installs cannot build it,
   as stage 11 found); a head node builds it. **YOUR DECISION (the
   build):** on the live proof's node if it is still there, or a head
   node of its own for the stage (default: a node of its own, removed
   after); the build is hours.

## Out of scope

Building UFS Coastal itself (`model-ufscoastal`'s recipes do that); the
spack-stack build cache (stage 16 covers the sandbox's own environment).

## Acceptance

`ufs-stack.yml` applied twice on a head node, the second run changing
nothing; `module avail` shows spack-stack's meta-modules; UFS Coastal's
own build script finds what it needs.
