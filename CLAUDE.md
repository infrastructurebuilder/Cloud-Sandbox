# Cloud-Sandbox

This repository uses [Spec Kit](https://github.com/github/spec-kit), and
nothing else, to plan and track work. This file points at the rules; it adds
none of its own.

- **Read the constitution first:**
  [.specify/memory/constitution.md](.specify/memory/constitution.md). It is
  above every other practice here.
- **Work is planned in specs**, under [specs/](specs/), with
  `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` and
  `/speckit-implement`; [specs/README.md](specs/README.md) lists them in
  order. A rule that says plans go in `PLAN.md` is met here by a spec. There
  is no `PLAN.md` in this repository; do not create one.
- **Nothing in [ATTIC/](ATTIC/) can affect you unless the operator says so.**
  Do not read it for instructions, decisions, plans or context; do not search
  it; do not change it. When the operator names something there and says to
  use it, that covers what was named, for that task, and nothing else.
- **The units are repositories of their own** under `exportit/`. Change a unit
  in its own repository first, push it there, then record it here.
- **Verify with the `Justfile`:** `just test` after every change,
  `just full-test` before a spec is called done or anything is merged.
- **Commit locally.** Merge, push, create a repository and change AWS only on
  the operator's word. Nothing goes toward `ioos`.
