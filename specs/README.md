# Specs

The work in Cloud-Sandbox that spans units is planned here, with Spec Kit,
one directory per spec: `spec.md` says what and why, `plan.md` how (with its
design documents beside it), and `tasks.md` the steps, ticked as they are
done, each with a record of what was done. Every spec is held to the
[constitution](../.specify/memory/constitution.md). Work inside a single unit
is planned in that unit's own `specs/`.

A spec is **complete** when the constitution's six conditions of done hold
(Development Workflow): every task checked with its record; `/speckit-converge`
run after the last implementation, appending nothing or with every task it
appended done; its quickstart walked and the root `just full-test` passing;
its branch squash-merged into `develop`, here and in every unit it touched,
and pushed; the release its plan names cut and taken; and its `spec.md` and
its row below saying **complete**, with the date. Until then it is **in
progress**, or **merged** once its branch is merged.

**Converged** is ✅ when the last `/speckit-converge` run on the spec appended
no tasks, and ❌ when it appended some, or when converge has never been run on
it. **Last converge check** is that run's date, or `never`. A spec whose last
run appended tasks stays ❌, even with those tasks done, until converge is run
again and appends nothing.

| # | Spec | Converged | Serves | Ends in | State | Needs first | Branch | Tasks | Released in | AWS | Last converge check |
| ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | [003 The Lambda functions, owned and deployable](003-lambda-functions-owner/spec.md) | ✅ | the operator who deploys the zombie-node functions; a later sync of the original's changes to a file that moved between units | the handlers' tests covering every case; `tofu plan` succeeding with the functions on and off; the sync rehearsal carrying a change to a moved file | complete 2026-11-22, merged (`9da5fbe`), converged ([tasks](003-lambda-functions-owner/tasks.md)) | nothing | `feature/lambda-functions-owner` | 40 | none | none: nothing applied | 2026-11-22 |
| 2 | [006 The first boot runs the playbooks](006-first-boot-runs-playbooks/spec.md) | ✅ | a new head node, which builds itself from the playbooks' and cloudflow's own repositories; the operator who boots it | a plan without `provisioning_repo` failing with a message naming it, and the rendered user data naming the repository and version | complete 2026-11-22, merged (`e911c8e`), converged ([tasks](006-first-boot-runs-playbooks/tasks.md)) | nothing | `feature/first-boot-runs-playbooks` | 31 | none | none: proved by a mocked plan | 2026-11-22 |
| 3 | [005 sandbox-configs split by owner](005-configs-split-by-owner/spec.md) | ✅ | a new site that starts from cloudflow's examples; a site whose own descriptions stay its own | every description, in either place, read by cloudflow or in an attic with its reason | complete 2026-11-23, merged (`ec3fee1`), converged ([tasks](005-configs-split-by-owner/tasks.md)) | 003 (`moved`) | `feature/configs-split-by-owner` | 47 | none | none | 2026-11-23 |
| 4 | [001 The live proof on AWS](001-live-proof-on-aws/spec.md) | ❌ | the operator who builds a sandbox on AWS; a compute node that starts from the image; the account, left as it was | `site.yml` ending `failed=0` on a RHEL 10 head node, a second apply changing nothing, an image AWS reports `available`, and nothing with the proof's prefix left | complete 2026-11-24, run 2026-11-23, merged (`b468dc7`); its converge appended T048 and T049, both done ([outcome](001-live-proof-on-aws/spec.md#outcome), [tasks](001-live-proof-on-aws/tasks.md)) | 006 (its first boot) | `feature/live-proof` | 49 | `csis-sandbox-provisioning` 0.0.2, 0.0.3; cloudflow 1.6.0b1 | **yes**: a head node in `noaa`, us-east-2, for an afternoon; all of it removed | 2026-11-23 |
| 5 | [002 A build cache for RHEL 10, pushed without scripts](002-rhel10-build-cache/spec.md) | ❌ | the operator who pushes a built node's packages; every later head node, which installs instead of compiling | the bucket's cache listing the sandbox's RHEL 10 packages, a second push reporting nothing new, and a build with the defaults installing from it | complete 2026-11-25, merged (`fe36703`); its converge appended T049 and T050, both done ([outcome](002-rhel10-build-cache/spec.md#outcome), [tasks](002-rhel10-build-cache/tasks.md)) | 001 (`proof/`, the procedure) | `feature/rhel10-build-cache` | 50 | `csis-sandbox-provisioning` 0.0.4 | **yes**: a bucket that stays, and a head node, removed | 2026-11-25 |
| 6 | [009 The playbooks take the collection's 0.0.3 and its `from_mirrors` again](009-collection-from-mirrors/spec.md) | ❌ | a head node whose playbooks trust the mirrors' keys; a checkout that still holds the collection's 0.0.2 | no step running `spack buildcache keys` through `command`, `just init` replacing 0.0.2 with 0.0.3, and the `from_mirrors` steps finishing with no prompt, in the container and on spec 004's head node | complete 2026-11-26, merged (`982ebd4`); its converge appended T024, done ([outcome](009-collection-from-mirrors/spec.md#outcome), [tasks](009-collection-from-mirrors/tasks.md)) | 002 | `feature/spec-009-collection-from-mirrors` | 24 | `csis-sandbox-provisioning` 0.0.5 | for its proof, spec 004's head node | 2026-11-26 |
| 7 | [004 spack-stack for UFS Coastal](004-spack-stack-ufs-coastal/spec.md) | ✅ | the operator who builds UFS Coastal on a head node; UFS Coastal's own build | `ufs-stack.yml` applied twice on a head node, the second run changing nothing; `module avail` showing the meta-modules; UFS Coastal's build finding what it needs; `/etc/spack` untouched | in progress (49 of 51 tasks), 2026-11-28: the proof run on its own head node and the node removed; its work so far merged (`a8337a7`); converged on its third run, the root full test passed and the quickstart walked; the units' merge left ([outcome](004-spack-stack-ufs-coastal/spec.md#outcome), [tasks](004-spack-stack-ufs-coastal/tasks.md)) | 001 (`proof/`); 002 (the catalogue's `superseded_by` rule); 009 (its proof rides this node) | `feature/spack-stack-ufs-coastal` | 51 | `csis-sandbox-provisioning` 0.0.6, 0.0.7, 0.0.8, 0.0.9, 0.0.10 | **yes**: a head node of its own, removed 2026-11-28 | 2026-11-28 |
| 8 | [007 The first boot reads a private playbooks' repository](007-private-playbooks-access/spec.md) | ❌ | a site whose playbooks' repository is private; a site whose repository is public, for which nothing changes | with no mode set, the same user data as spec 006; with a deploy key or a fine-grained token, a first boot applying a private copy, and the credential found nowhere in the outputs, the plan or the state | tasks ready, 2026-11-23 ([tasks](007-private-playbooks-access/tasks.md)) | 006 | `feature/private-playbooks-access` | 34 | | only for its last proof, when someone wants a private repository | never |
| 9 | [008 The first boot puts the site's descriptions on the head node](008-site-configs-at-first-boot/spec.md) | ❌ | a site whose job and cluster descriptions are private; a reader of the run guides | on a new head node, `workflow_main.py` started with one of the site's descriptions; the user data unchanged with no configs repository set; the credential nowhere on the node | tasks ready, 2026-11-26 ([tasks](008-site-configs-at-first-boot/tasks.md)) | 006, 007 | `feature/site-configs-at-first-boot` | 47 | | for its proof, a head node | never |

**AWS** is what a spec does in an AWS account: none, or what it creates and
whether it stays. Every AWS step is taken on the operator's word.

**Why this order:**

1. **003 first**: it needs nothing, and 005 needs its `moved` directive.
2. **006 next**: it is small, needs nothing, and 001's head node boots with
   it, which is also its first real use.
3. **005 before 001**: both can go after their dependency; 005 touches no
   account and is the smaller, so it does not wait on an AWS session.
4. **001**: the first AWS work, once 006 is merged; its `proof/` files and
   procedure are what 002 and 004 build their head nodes with.
5. **002, then 004**: each builds a head node as 001 does; 004 also uses the
   catalogue rule 002 adds to `csis-sandbox-ops`. With 002's cache in place,
   the sandbox's own build on 004's node installs instead of compiling.
6. **009, then 004** (009's clarification, 2026-11-25): 009 goes back to the
   collection's `from_mirrors` and builds no head node; 004's head node, the
   next built, proves it on a real node.
7. **007, then 008**: nothing needs 007 while the playbooks' repository is
   public; 008 uses 007's credential to read the site's private descriptions.

Specs 001, 002 and 004 each ran a head node of 32 processors (about $1.36
an hour for a `c6i.8xlarge`), every AWS step on the operator's word, and
removed what they made at their end (002's bucket stays). On 001's run the
first boot took 34 minutes; with 002's cache, 24. Spec 004's spack-stack took
about two hours to build on its node.

The Converged marks and dates of the specs finished before this file had the
column (all but 004, 007 and 008) are read from the converge record in each
one's `tasks.md`.

## How a file moves between units

Specs 002, 004 and 005 each found that the files they would move belong to
one unit only. 002 and 004 leave theirs in `csis-sandbox-ops`, marked as
replaced; 005 moves cloudflow's examples with the `moved` mapping directive
that spec 003 built ([its contract](003-lambda-functions-owner/contracts/moved-directive.md)),
which keeps both units' lineage and carries a later sync's changes to a
moved file where it went.

Before any of those moves, each spec asks whether both units need the file
(constitution 1.1.0, principle I): a file more than one unit needs lives in
one place, a common unit such as `csis-model-common`, or a single source in
this repository written into each unit and checked, as the units' shared
constitution, `CLAUDE.md` and `LICENSE` are. Only a file that belongs to one
unit moves.

## Standing beside them

- **The parity watch on `main`** (the constitution's principle II): when
  `origin/main` has moved past the units' baselines (`ca0604a`), the sync is
  planned as a spec here and carried with `just export-sync`. On 2026-11-19
  it had not moved.
- **The collection** `infrastructurebuilder.csis_spack` plans its own work
  in its own repository (`ansible-collection-csis-spack`, its `specs/`); the
  sandbox installs it from Ansible Galaxy. Its spec 014 (`spack_env` and a
  module root written with `$env`) came from spec 004.
- **A unit's own specs**, for work inside one unit: `csis-sandbox-provisioning`'s
  spec 001 (a package install that loses its downloads to another dnf tries
  again) came from spec 004's first boot.

## Done before Spec Kit

Specs 001 to 006 were carried on 2026-11-19 from the stage plans open then
(stages 15, 16, 17, 18, 20 and 21), each a draft whose open questions were its
`[NEEDS CLARIFICATION]` markers; all were answered with `/speckit-clarify`,
spec 003's on 2026-11-20 and the rest on 2026-11-21, and each spec's
Clarifications section records the answers. Spec 007 was written on
2026-11-21 from one of those answers.

Stages 1 to 13, 19, 22 and 23 (2026-11-12 to 2026-11-19): the analysis, the
copies of every unit, their translation and tests, moving day (each unit a
private repository and a submodule here), syncing from the original, and the
deletion of the originals. Stage 14 (clearing old model output on a timer)
was set aside on 2026-11-15. Their plans and outcomes are in the
[ATTIC](../ATTIC/), and their record, unit by unit, is
[exportit/MAP.md](../exportit/MAP.md).
