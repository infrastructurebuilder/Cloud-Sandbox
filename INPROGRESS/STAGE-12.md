# Stage 12: the old Spack settings in the login user's scope

*Status:* planned 2026-11-14 on `feature/remaining-plans`, and executed
the same day on "do 12", on `feature/stage-12-user-scope` (cut from
`feature/remaining-plans`, which is not merged yet). Committed locally;
not merged. It found a defect in the collection, fixed there and released
as 0.3.1, which this stage pins. The decision is under [Decisions taken](#decisions-taken),
the result under [Outcome](#outcome). Second in the order of the remaining work
([PLAN.md](../PLAN.md)): it depends on nothing, and it is small.

## Why

The reminder the operator asked for in stage 11
([REMINDERS.md](../exportit/REMINDERS.md)). The script's two
`spack config add` lines have no `--scope`, so a head node built by the
script, or by the playbooks before stage 11, has the install-tree padding
(73) and the Tcl modules setting in the login user's `~/.spack/`. Since
stage 11 the playbooks write them to the site scope. The old copies have
the same values, and the user scope wins over the site scope: they do no
harm until someone changes the site's values, when the login user alone
would keep the old ones.

## What exists

- Stage 11's dump of what the shell roles left
  (`sandbox-provisioning/tests/container/expected-spack-config.json`):
  the user scope holds exactly `config:install_tree:padded_length: 73`
  and `modules:default:enable: [tcl]`, and nothing else.
- `sandbox_users` writes each user's `~/.spack/config.yaml` from a
  template, with `install_tree:root` only; it never wrote the two
  settings. Only the login user (`sandbox_user`) can have them.
- The collection's `spack_config` removes paths with `state: absent`,
  in any scope, and does nothing when they are not there.

## Items

1. **Remove the two paths from the login user's scope when they hold
   what the site scope now holds.** A setting the operator changed by
   hand in the user scope, to a value the site does not have, is a
   choice, not a leftover: it is left, and reported.

   The check reads both scopes with `spack config --scope <s> get --json`
   and compares; the removal is a `config` step with `state: absent` and
   `scope: user`. Both run as the login user.

   **YOUR DECISION (where it lives):**
   - **A step of the `spack` role, for a while** (default): every build
     and every re-run of `site.yml` tidies its own node. The step's
     comment says when it can go (when no head node built before stage
     11 is left), and REMINDERS.md keeps that.
   - **A playbook of its own, run once** on each existing head node
     (`tidy-spack-user-scope.yml`), and not part of `site.yml`.

2. **Tests.**
   - Parity: the step names the two paths the stage 11 dump holds, and
     nothing else.
   - The container test: before the first apply, the login user's scope
     is written as a node built before stage 11 has it, but with one
     setting changed, as if by hand: the padding at 73, as the script
     left it, and the modules setting at `[lmod]` instead of `[tcl]`.
     After the apply: the padding is gone, the modules setting is still
     there and reported, and the second apply changes nothing.

3. **Records:** MAP.md (stage 11's section, the difference now handled),
   REMINDERS.md (the item closed, or, with the default, replaced by "the
   step can go when...").

## Decisions taken

Asked on 2026-11-14: **a step of the `spack` role, for a while**, the
default.

## Out of scope

Other users' `~/.spack/`: they never had the two settings.

## Acceptance

The root `just test` and `just full-test` pass; the container test shows
the matching settings removed, a deliberate one kept, and a second run
with nothing to change.

## Found

- **Spack leaves a mapping it empties behind.** Removing
  `config:install_tree:padded_length`, the only key of `install_tree`,
  leaves `install_tree: {}`; the same at every level tried, by hand,
  against Spack v1.2.0. The collection's `spack_config` 0.3.0 assumed the
  opposite and failed its own check after removing, in this stage's
  container test. The operator chose to fix it in the collection and
  release it with collection stage 4's documentation as **0.3.1**
  (tagged and pushed 2026-11-14), and to move this sandbox's pin to it
  here. The collection's stand-in `spack` had the same wrong model, which
  is why its unit tests had not caught it. The container test's own
  clean-up met the same behaviour, and removes the whole mapping.

## Outcome

- `roles/spack/tasks/user_scope.yml` reads the two settings from the
  login user's and the site's files (no Spack, no shell) and says which
  are leftovers and which were chosen; `main.yml` removes the leftovers
  with a `config` step of state `absent` in the user scope, and reports
  the chosen. Three tasks and the file, each with its `# New:` comment and
  when they can go.
- The pin is 0.3.1, in `requirements.yml` and `units.toml`.
- `tests/test_user_scope.py` applies the task file alone against scope
  files it writes (8 tests); the parity test holds the removal to the
  stage 11 dump's two paths; traceability reads the new step.
- **The container, with the real oneAPI:** the login user's scope is
  written as a head node built before stage 11 has it, with the modules
  setting changed to `[lmod]`. First apply of `site.yml`, 56 changes;
  second, 0; check mode, 0. Afterwards the padding is gone, `[lmod]` is
  kept, and Spack's configuration is as the shell left it, with the
  decided difference.
- `sandbox-provisioning`'s `just test` (452 tests) and `just full-test`
  pass. The root `just test` and `just full-test` pass (2026-11-14; the
  first full run stopped on a TLS error cloning Spack from GitHub inside
  the container, and the second passed): every unit, and all 15
  extraction proofs.

