# Stage 9: the Spack environment as a file, and a home for a Spack module

*Status:* planned and executed 2026-11-13, at the operator's request
("this has some urgency across the next several days"), on
`feature/stage-9-spack-yaml`, cut from `feature/attic-stays-home`
because that branch is not merged yet. Committed locally; not merged.
The outcome is under [Outcome](#outcome).

## Why

`sandbox-provisioning`'s `spack_environment` role builds the
environment's `spack.yaml` by calling Spack: `spack env create`, then
`spack config add` once per setting and `spack add` once per spec, each
step comparing checksums of the file before and after to say whether
it changed. That is state kept in bash. A Spack environment is
declared by its `spack.yaml`; written by Ansible from a template, it
has Ansible's own change detection, `--check` and `--diff`, and the
role loses half its shell.

What still has to call Spack (concretize, install, regenerate the
modules, push to the build cache) is the job for an Ansible module.
The operator decided on 2026-11-13 that the module gets a repository
of its own, `infrastructurebuilder/ansible-collection-csis-spack`, as the
collection `infrastructurebuilder.csis_spack` (first named
`ansible-collection-spack` and `infrastructurebuilder.spack`), and is built, tested and
released separately, after the `spack.yaml` work. This stage makes
its place and does the `spack.yaml` work; the module is the next.

## What exists

- [roles/spack_environment/](../../exportit/sandbox-provisioning/roles/spack_environment/):
  the tasks named above; its defaults hold `spack_environment_settings`
  (three `config add` paths) and `spack_environment_specs` (ESMF and
  PETSc).
- [tests/test_parity.py](../../exportit/sandbox-provisioning/tests/test_parity.py)
  holds the two lists to the script's `spack config add` and
  `spack add` lines (`funcs-setup-instance.sh` L754–L806).
- The container test clones Spack v1.2.0 (role `spack`) but does not
  run `spack_environment`: its build takes hours.
- The repository `git@github.com:infrastructurebuilder/ansible-collection-spack.git`
  exists and is empty.

## Items

1. **The collection's folder,** `exportit/ansible-collection-spack/`:
   `galaxy.yml` (namespace `infrastructurebuilder`, name `spack`,
   version 0.1.0), `README.md`, `LICENSE`, a `Justfile` with the five
   targets (`build` makes the collection tarball with
   `ansible-galaxy collection build`; `test` lints and checks the
   metadata), an empty `plugins/modules/`, and its line in
   `units.toml` and the root `Justfile`. It is not a copy of anything,
   so its map lists only new files. Nothing is pushed to its
   repository.

   **YOUR DECISION (licence):** GPL-3.0-or-later, the licence of
   Ansible and of the community collections, whose code a module is
   most likely to borrow from (default); BSD-3-Clause, like the
   sandbox; or Apache-2.0.

2. **`spack.yaml` from a template.** The two tasks "Configure the
   environment" and "Add ESMF and PETSc" become one `template` task
   writing `spack.yaml`, with the traceability comments of both. The
   environment is still created by `spack env create` when it does not
   exist, so that Spack makes its directory, and the template then
   replaces the file. Concretize, install and the module files stay as
   they are, and run when their inputs changed, as today.

   **YOUR DECISION (variables):** one variable,
   `spack_environment_config`, a mapping in the shape of `spack.yaml`
   (`modules`, `concretizer`, `packages`), with the specs beside it
   (default); or keep the three `config add` strings and have the
   template turn them into YAML.

   **YOUR DECISION (ownership):** Ansible owns `spack.yaml` whole: an
   edit made by hand on the head node is overwritten, with a backup
   kept beside it (default); or Ansible sets only its own keys and
   leaves the rest of the file alone.

3. **Proof that the file is the same.** The parity test changes to
   compare the new variables with the script's lines. In addition, the
   container test, which has Spack v1.2.0 already, makes an environment
   the script's way (`env create`, `config add`, `add`) and one from the
   template, and compares what Spack reads from each with
   `spack -e <env> config get`. Nothing is concretized or built.

4. **MAP.md:** a section for the collection, and the `spack.yaml`
   change under `sandbox-provisioning`'s translation notes.

## Decisions taken

Asked one at a time on 2026-11-13, before execution.

0. **Name and namespace** (asked before the plan was written): the
   repository is `ansible-collection-spack`, the collection
   `infrastructurebuilder.spack`. The operator then created the empty
   repository.
   Later the same day the operator renamed them: the repository
   `ansible-collection-csis-spack`, the tooling project
   `ansible-collection-csis-spack`, the collection `csis_spack` (a
   collection name cannot hold a hyphen).
1. **Licence:** GPL-3.0-or-later.
2. **Where the collection is worked on** (raised by the operator during
   the questions): not under `exportit/`, but in its own clone,
   `/Volumes/MiniSSD/git/Work/Phase3/ansible-collection-csis-spack`
   (first cloned as `ansible-collection-spack`). Item 1
   is done there instead: no map, no line in the root `Justfile`, and no
   line in `units.toml` until `sandbox-provisioning` uses it.
3. **Variables:** one mapping, `spack_environment_config`, in the shape
   of `spack.yaml`, with `spack_environment_specs` beside it.
4. **Ownership:** Ansible owns `spack.yaml` whole; a hand edit is
   overwritten, with a backup kept beside it.

## Out of scope

- The module itself, and anything pushed to the collection's
  repository.
- The mirror-push scripts, `spack-pubkey.sh` and the UFS spack-stack
  in `sandbox-ops`; they come with the module.

## Acceptance

- The root `just test` and `just full-test` pass.
- The collection's `just build` makes
  `infrastructurebuilder-spack-0.1.0.tar.gz`.

## Outcome

- The collection: [its own clone](../../../ansible-collection-csis-spack/README.md),
  `infrastructurebuilder.csis_spack` 0.1.0, two local commits on its
  `feature/skeleton`. `just test` (lint, type-check, six metadata tests,
  a build that installs) and `just full-test` (adding `ansible-test
  sanity`, which has no targets yet) pass. Nothing pushed.
- `spack_environment`: one `template` task writes `spack.yaml` from
  `spack_environment_config` and `spack_environment_specs`, in place of
  the two shell tasks. Tests: the parity test reads the script's
  `config add` lines as Spack does; `tests/test_spack_yaml.py` renders
  the template; `sandbox-provisioning`'s `just test` passes (412 tests).
- The container test makes both environments with Spack v1.2.0 and
  compares them; `sandbox-provisioning`'s `just full-test` passes. It
  took four runs, each failure the comparison's, not the role's:
  `spack python -c` takes one statement; `spack add` rewrites specs
  (variants sorted, `%intel-oneapi-compilers` as `%oneapi`); and
  `config add` writes lists in flow style. Each is recorded in
  [MAP.md](../../exportit/MAP.md#the-environments-spackyaml-written-whole-stage-9).
  The comparison was also tried on the local machine against Spack
  v1.2.0, and fails on a changed setting and on a changed spec.
- The root `just test` passes.

