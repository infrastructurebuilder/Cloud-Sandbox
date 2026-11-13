# Plans

## Keeping exportit/ in parity with main (from 2026-11-13)

*Status:* standing, from 2026-11-13 until the operator says otherwise:
for about four to five weeks, until the actual migration. Baseline:
`origin/main` at `ca0604a` (2026-10-30), which `develop` already
contains. No updates on `main` since.

Changes keep arriving on `main` while the units wait to be migrated.
Each time `origin/main` (infrastructurebuilder) has moved past the last
baseline, the changes are carried into [exportit/](exportit/) the same
way the eight stages were made, so that every unit stays a faithful
copy or translation of what is in the repository.

1. **Look.** `git fetch origin`, then
   `git log <baseline>..origin/main`. Nothing new: nothing to do. Only
   `origin` is read; nothing is fetched from or pushed to IOOS.
2. **Merge onto a branch.** `git flow feature start sync-<n>`, then
   `git merge origin/main` on it. `just test` then lists the drift: the
   copy check names every copied file that now differs from its source,
   every new tracked file that no unit takes, and every map line that
   matches nothing any more.
3. **Plan.** `INPROGRESS/SYNC-<n>.md`, in the form of a stage: each
   change on `main`, the unit it lands in, and what it takes (a fresh
   copy, a patch that no longer applies, a new file to assign, a role
   or task to translate again with its traceability). Existing
   decisions stand. Where a change gives a compelling reason to revisit
   one, the plan says so under its own heading, with the decision and
   the reason, and asks rather than changes it; smaller discrepancies
   are listed too.
4. **Execute on "do sync <n>"**: ask each YOUR DECISION singly, carry
   the changes, update [exportit/MAP.md](exportit/MAP.md) and the
   affected `README.md` and `UNIT.md` files, and pass the root `just test`
   and `just full-test`. Commit locally; merge into `develop` and push to
   `origin` only when told. The new baseline is the `main` commit merged.

## Reconstruction into independent units (2026-11-12)

*Status:* all eight stages merged into `develop` 2026-11-12, one
squash commit each, feature branches kept. Nothing has been relocated;
the real relocations wait for the operator.

Cloud-Sandbox is being taken apart into units that could each live in
their own repository: the cloudflow workflow engine, head-node
provisioning (as Ansible playbooks), Terraform, the model recipes, the
job and cluster descriptions, operator utilities, and documentation.
Nothing is moved out of this repository. Each unit is copied into
[exportit/](exportit/), and [exportit/MAP.md](exportit/MAP.md) says
how the real relocation would be done.

The plan is kept as one file per stage, because each is reviewed and
executed on its own:

- [INPROGRESS/ANALYSIS.md](INPROGRESS/ANALYSIS.md): what is in the
  repository and what ties its parts together.
- [INPROGRESS/TODO.md](INPROGRESS/TODO.md): the open stages and the
  standing decisions.
- [INPROGRESS/STAGE-1.md](INPROGRESS/STAGE-1.md) to
  [INPROGRESS/STAGE-8.md](INPROGRESS/STAGE-8.md): the stage plans.
