# Stage 11: Spack set up through the csis_spack collection, at 0.3.0

*Status:* executed 2026-11-14 on `feature/stage-11-csis-spack-0.3.0`, on
the operator's "do coll 3". Committed locally; not merged.

## The plan is in the collection's repository

This stage was planned as **stage 3 of the Ansible collection**
`infrastructurebuilder.csis_spack`, because it is where the collection's
0.2.0 and 0.3.0 are proved on the machine they were written for. The plan,
with what exists, the items, and how each decision changes them, is
`COLL-INPROGRESS/COLL-STAGE-3.md` in
`git@github.com:infrastructurebuilder/ansible-collection-csis-spack.git`
(in a clone beside this one:
[../../ansible-collection-csis-spack/COLL-INPROGRESS/COLL-STAGE-3.md](../../ansible-collection-csis-spack/COLL-INPROGRESS/COLL-STAGE-3.md)).

Every change it makes is in this repository, under this repository's
rules. This file holds what this repository needs to know without the
other: what was decided, what was done, and what was found.

## What it does

`sandbox-provisioning` moves its pin of the collection from 0.1.0 to
0.3.0, and the shell that set Spack up in its `spack` and `intel_oneapi`
roles becomes lists of steps for the collection's `setup` role. See
[MAP.md](../exportit/MAP.md#spack-set-up-through-the-collection-stage-11).

## Decisions taken

Asked one at a time on 2026-11-14, before execution.

1. **`refresh_modules` in `spack_environment`:** `when_needed`. A second
   run touches no module file; differs from the script, and says so.
2. **Where the lists live:** in the roles' tasks files, as `vars:` of the
   `include_role` task, each step with its own `# Replaces` comment.
3. **The two settings' scope:** the **site** scope. The script's two
   `spack config add` lines have no `--scope` and so wrote to the login
   user's `~/.spack`.
4. **A side-by-side proof:** a recorded comparison with what the shell
   roles left in the container.
5. **`spack-pubkey.sh`:** a third list in the `spack` role, off by
   default (`spack_site_mirror`).
6. **How this repository records it:** as this stage, pointing to the
   collection's plan.

Asked during execution (2026-11-14): a reminder for the two settings
that stay in the login user's scope on head nodes built before this
stage. It is in [REMINDERS.md](../exportit/REMINDERS.md).

## What differs from the plan

- **`spack-pubkey.sh` is in `sandbox-provisioning/legacy/`, not the
  attic.** The plan sent it to the attic as superseded. The scripts a
  role replaces are kept in `legacy/`, where the traceability and parity
  tests read them (as stage 7's were); the attic is for what nothing
  reads. Its row left `sandbox-ops/CATALOGUE.tsv` and joined no other.
- **`spack_key` stays in `group_vars`.** The plan removed it. The script
  exports it, and `test_parity.py` holds every exported variable to the
  script; nothing uses it now.
- **The site-scope decision is not in `tests/not_carried.yml`.** The
  plan put it there. That file is for lines that are not carried, and
  L672-L673 are carried, by a step that names them; the difference is in
  the step's comment and in MAP.md.
- **The site mirror goes to the site scope** as well. The script's
  `mirror add` has no `--scope` either; the same decision was applied.
- **Externals are compared by package name** in the side-by-side proof,
  not by version: the versions detection finds are the container
  image's, and would fail the comparison when the image is rebuilt. The
  versions the roles state themselves are checked against the variables.

## Found

- **`spack config add` without `--scope` writes to the user scope.** The
  shell roles' result, dumped from the container before they were
  replaced, shows it: the padding and the Tcl modules in the user scope,
  nothing in the site scope's `config` and `modules`.
- **Detection does not remove.** The stage 3 record that the two
  `compiler find` steps undo each other is corrected in MAP.md.
- **`spack_environment` could not run in check mode.** Ansible refuses a
  task that is both asynchronous and in check mode, and the build task
  is asynchronous. Stage 10 claimed check mode for the role without
  running it. The task is synchronous when previewing; the container
  test now runs the preview.
- **The key at the site mirror's address** has the fingerprint of the key
  kept in `sandbox-ops/keys/` (fetched and compared on 2026-11-14).

## Outcome

- The pin is 0.3.0 in `requirements.yml` and `units.toml`.
- `spack`: six steps replace the shell task; a second list of three, for
  the site mirror, is applied only when `spack_site_mirror` is true.
  `intel_oneapi`: four steps replace three shell tasks. No task of either
  role runs Spack through a shell; a test holds that.
- `spack_environment`: `refresh_modules: when_needed`; the build task is
  synchronous in check mode.
- `sandbox-provisioning`'s `just test`: ansible-lint at the production
  profile, pyright, 437 tests (traceability, with steps read like tasks;
  parity, with the script's commands written as steps).
- **The container, with the real oneAPI** (root `just full-test`,
  2026-11-14): the collection installed from its tag; first apply of
  `site.yml`, 55 changes; second, 0; the three roles once more in check
  mode, 0 changes and no failure; what Spack was told is as the shell
  roles left it (28 packages with externals, the providers, the mirror),
  with the padding and the Tcl modules in the site scope.
- Extraction: `sandbox-provisioning` gives the same 26 files with 19
  commits of history, `sandbox-ops` the same 15 with 14.
- The root `just test` and `just full-test` pass.

## Out of scope

As the plan's: `spack_buildcache_push` for the `sandbox-ops` mirror
scripts, the UFS spack-stack, removing the old settings from the login
user's scope on existing head nodes, applying the site mirror's list
against the real bucket, and the live proof on AWS.
