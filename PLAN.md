# Plans

## The remaining work, in order (2026-11-14)

*Status:* planned 2026-11-14, every item on its own; nothing executed.
Each is a stage, executed on its "do", with its decisions asked one at a
time first. The stage numbers follow this order.

The order is set by what each item needs first; where two items need
nothing of each other, the smaller comes first. Defects that stages 2 to
8 found in the originals and left as they are (cloudflow's missing flows
and cron target, its lint findings, `scrub_liveocean.sh`'s parse error)
are not in it.

| # | Stage | What | Needs first | Size |
| ---: | --- | --- | --- | --- |
| 1 | [collection 4](../ansible-collection-csis-spack/COLL-INPROGRESS/COLL-STAGE-4.md) | `spack_env`: document `async` with check mode (0.3.1) | nothing | minutes |
| 2 | [12](INPROGRESS/STAGE-12.md) | The old Spack settings in the login user's scope on existing head nodes | nothing | small |
| 3 | [13](INPROGRESS/STAGE-13.md) | JupyterHub: an option, part of every build, or removed (a decision, then its work) | nothing; before 15, so the proof covers it | small |
| 4 | [14](INPROGRESS/STAGE-14.md) | Clearing old model output on a timer, in place of the two scrub scripts | nothing; before 15, so the proof covers it | medium |
| 5 | [15](INPROGRESS/STAGE-15.md) | **The live proof on AWS** | 12 to 14 done or dropped; the AWS session | large: hours of a head node |
| 6 | [16](INPROGRESS/STAGE-16.md) | A build cache for RHEL 10, and the mirror-push scripts replaced by `spack_buildcache_push` | 15: a real build to push | medium |
| 7 | [collection 5](../ansible-collection-csis-spack/COLL-INPROGRESS/COLL-STAGE-5.md) | Ansible Galaxy, or the git tag (a decision, then its work) | nothing; before 22, so the source is named once | medium if published |
| 8 | [17](INPROGRESS/STAGE-17.md) | The Lambda functions: an owner, a module, tests (a decision, then its work) | nothing; before 22, step 1 | medium to large |
| 9 | [18](INPROGRESS/STAGE-18.md) | spack-stack for UFS Coastal, in place of the broken `add-ufs-setup.sh` | 15: a head node to build on | large |
| 10 | [19](INPROGRESS/STAGE-19.md) | Relocate all, some, or none (a decision) | 1 to 9, as "a good commit tree" | a decision |
| 11 | [20](INPROGRESS/STAGE-20.md) | `sandbox-configs` split by owner | 19 relocates it | medium |
| 12 | [21](INPROGRESS/STAGE-21.md) | The first boot runs the playbooks (`main.tf`'s two values) | 19 relocates both units; put into use at 22, step 6 | small |
| 13 | [22](INPROGRESS/STAGE-22.md) | The real relocations, eight steps in MAP.md's order | 19, 20, 21 | large |

Standing beside all of them: the parity watch on `main` (the next
section), which, while it lasts, comes before any of these whenever
`origin/main` has moved.

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
