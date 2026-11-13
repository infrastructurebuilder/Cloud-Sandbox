# Stage 10: the Spack environment through the csis_spack collection

*Status:* planned 2026-11-13 on `feature/stage-10-spack-module`; nothing
executed. It is executed on "do 10", after each **YOUR DECISION** below
has been asked, one at a time.

## Why

After [stage 9](STAGE-9.md), `sandbox-provisioning`'s
`spack_environment` role writes `spack.yaml` from a template but still
calls Spack through three shell tasks. Each hashes something before and
after to say whether it changed, none supports `--check`, and one is
wrong: Spack stamps every module file with the time it wrote it, so the
module-file task reports a change on every run
([MAP.md](../exportit/MAP.md#how-it-was-tested-and-what-was-not)). The
collection `infrastructurebuilder.csis_spack` 0.1.0, built for this,
does the same work as a module, `spack_env`, with Ansible's own change
reporting and check mode, and compares module files without the time.

## What exists

- [roles/spack_environment/tasks/main.yml](../exportit/sandbox-provisioning/roles/spack_environment/tasks/main.yml):
  after the template, "Work out what has to be built"
  (`concretize --force --fresh`, output to `log.concretize`), "Build and
  install the environment" (`install {{ spack_opts }}`, under
  `async: 86400`, `poll: 60`, output to `log.install`) and "Regenerate
  the environment's module files" (`module tcl refresh --delete-tree
  -y`). Each first runs `sandbox_modules_init` and
  `sandbox_load_intel_modules` in bash.
- [requirements.yml](../exportit/sandbox-provisioning/requirements.yml)
  holds `amazon.aws`; `just init` installs it into `.collections/`, and
  the first-boot template runs `ansible-galaxy collection install -r
  requirements.yml` on the head node before `ansible-pull`.
- The collection: `/Volumes/MiniSSD/git/Work/Phase3/ansible-collection-csis-spack`,
  tagged `0.1.0` locally on 2026-11-13. **Nothing of it is pushed:**
  `infrastructurebuilder/ansible-collection-csis-spack` on GitHub is
  still empty.
- The container test applies the `spack` and `intel_oneapi` roles (Spack
  v1.2.0 and oneAPI are there) but not `spack_environment`, because its
  build takes hours.

## Items

1. **Where the collection comes from.** A line in `requirements.yml`,
   so that `just init` and the head node's first boot install it like
   `amazon.aws`.

   **YOUR DECISION (source):**
   - its git repository, pinned to the tag:
     `name: https://github.com/infrastructurebuilder/ansible-collection-csis-spack.git`,
     `type: git`, `version: 0.1.0` (default). This needs the
     collection's `main`, `develop` and tag `0.1.0` pushed first, and the
     head node able to clone the repository, so the repository must be
     public or the node given a credential;
   - Ansible Galaxy, `infrastructurebuilder.csis_spack` `0.1.0`: needs
     the namespace on Galaxy and the collection published there;
   - the built tarball kept in `sandbox-provisioning` (`type: file`):
     needs no network or publishing, but puts a build artefact in the
     repository, renewed by hand on each release.

2. **The three shell tasks become one `spack_env` task**, with the
   traceability comments of all three (`funcs-setup-instance.sh` L812,
   L817, L820-L822):

   ```yaml
   - name: Concretize, build and install the environment, and regenerate its module files (hours, the first time)
     infrastructurebuilder.csis_spack.spack_env:
       path: "{{ spack_environment_dir }}"
       spack: "{{ spack_exe }}"
       install_args: "{{ spack_opts.split() + spack_environment_install_args }}"
       modules: [tcl]
       log_file: "{{ spack_environment_dir }}/log.install"
     environment: "{{ spack_environment_intel_env }}"
     become: true
     become_user: "{{ sandbox_user }}"
     async: "{{ spack_environment_build_timeout }}"
     poll: 60
   ```

   - **The Intel modules** (the collection's decision 3): one task before
     it runs `sandbox_modules_init` and `sandbox_load_intel_modules` in
     bash and prints the environment that results as JSON; the module
     gets it through `environment:`. The module itself runs no shell.
   - `spack_environment_install_args` (default `[]`) is new: what the
     container test sets to `[--fake]`.
   - `spack_environment_modules_root` goes: the module asks Spack for the
     module roots.
   - `log.concretize` is no longer written: the module keeps the
     install's output in `log.install` and the concretization's in its
     result. Listed in `tests/not_carried.yml` with the reason.
   - Check mode now works for the whole role: the module concretizes a
     copy and says what would be installed.

3. **Tests.** The traceability test follows the merged task; the
   parity test holds `spack_opts.split()` to the script's `SPACKOPTS`.
   `ansible-lint` must resolve the collection (installed by `just init`
   into `.collections/`).

   **YOUR DECISION (the container):** apply `spack_environment` in the
   container test too, with `spack_environment_install_args: [--fake]`,
   so that ESMF and PETSc are concretized with the real oneAPI
   compilers and "installed" without compiling, twice, the second run
   changing nothing (default; adds the concretization's time, minutes,
   to `just full-test`); or leave the role out of the container as now.

4. **The umbrella.** `units.toml` gains the collection:
   `ansible-collection-csis-spack`, version `0.1.0`, kind `ansible`,
   step 2, before `sandbox-provisioning` in the order of relocation,
   and `sandbox-provisioning` needs it. It is the first unit with no
   map in `exportit/` (it lives in its own repository), so the umbrella's
   check and the test in `tools` learn a new field, `external = true`,
   for a unit that is not copied.

5. **MAP.md:** the `sandbox-provisioning` section (the tasks, the
   variables, the module-file finding resolved, what the container now
   proves), the collection's section (now used, at 0.1.0), and the order
   of relocations.

## Out of scope

- Pushing or publishing the collection; decision 1 says what each
  source needs, and the push is the operator's to give.
- The `sandbox-ops` mirror scripts. `spack_buildcache_push` can replace
  them; that is a stage of its own, with the mirror's key.
- Changing the collection. If this stage needs it to change, the change
  is made there, released as 0.1.1, and pinned here.

## Acceptance

- The root `just test` and `just full-test` pass.
- With decision 3's default: the container applies `spack_environment`
  twice and the second run reports nothing changed, module files
  included.
