# Stage 12: the old Spack settings in the login user's scope

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. It is executed on "do 12", after each **YOUR DECISION** below
has been asked, one at a time. Second in the order of the remaining work
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
   - The container test: before the first apply, the two settings are
     written to the login user's scope, as a node built before stage 11
     has them, and one of them a second time with a different value in a
     separate run, to be left alone. After the apply: the matching one
     is gone, the different one is still there and reported, and the
     second apply changes nothing.

3. **Records:** MAP.md (stage 11's section, the difference now handled),
   REMINDERS.md (the item closed, or, with the default, replaced by "the
   step can go when...").

## Out of scope

Other users' `~/.spack/`: they never had the two settings.

## Acceptance

The root `just test` and `just full-test` pass; the container test shows
the matching settings removed, a deliberate one kept, and a second run
with nothing to change.
