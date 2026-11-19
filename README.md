# Cloud-Sandbox: the workshop

This repository was the IOOS Cloud Sandbox, in one piece. It has since
been taken apart into fifteen units, each a private repository of its
own on `infrastructurebuilder`, and what is left here is the workshop
where they are held together:

- **[exportit/](exportit/)**: the fifteen units, each kept as a git
  submodule at the path its copy had (`exportit/cloudflow`,
  `exportit/sandbox-provisioning`, ...); one mapping file per unit
  (`exportit/<unit>.map`), saying which file of the original went where;
  cloudflow's corrections (`exportit/cloudflow.patches/`); and the tools
  that check the units and carry changes into them
  (`exportit/tools/`).
- **[exportit/MAP.md](exportit/MAP.md)**: the record of every unit,
  where its files came from, and how it was made.
- **[specs/](specs/)**: the work that spans units, planned with Spec Kit,
  one directory per spec; [specs/README.md](specs/README.md) lists them in
  the order they are to be taken up. This repository's rules are its
  constitution, [.specify/memory/constitution.md](.specify/memory/constitution.md).
- **[ATTIC/](ATTIC/)**: what was retired when the planning moved to Spec Kit
  on 2026-11-19: `PLAN.md`, and the stage plans that came before, with the
  analysis of the original repository (`ATTIC/SPECS/`). History for a person
  reading; nothing there is a rule.
- **[Justfile](Justfile)**: the entry point for everything below.

The original files are no longer on `develop`. They were deleted, one
unit at a time, by stage 22 (2026-11-18 and 19), once each unit owned
them. They are still in this repository's history, and on its `main`
branch, which is a copy of the original project; every unit's baseline,
the commit of the original it was made from, is `ca0604a`.

## The units

Which units make a sandbox, at which versions, in which order, is in the
umbrella's [units.toml](exportit/cloud-sandbox/units.toml): cloudflow
(the workflow engine), the model recipes (`csis-model-*`),
`csis-sandbox-configs`, `csis-sandbox-provisioning` (the Ansible that
builds a head node), `csis-sandbox-terraform` (the OpenTofu that creates
one), `csis-sandbox-ops`, and the umbrella itself, `csis-cloud-sandbox`.
The Ansible collection `infrastructurebuilder.csis_spack` has its own
public repository and is installed from Ansible Galaxy.

Each unit plans its own work with Spec Kit, under a constitution whose
shared part is kept here (`exportit/tools/constitution/`). Work that
spans units is planned here, as a stage.

## Getting started

You need `git`, `just` and `uv`, and access to the fifteen private
repositories. Clone with the submodules, then set up every unit:

```sh
git clone --recurse-submodules git@github.com:infrastructurebuilder/Cloud-Sandbox.git
cd Cloud-Sandbox
just init
```

A clone made without `--recurse-submodules` gets its units with
`just init` too.

## The acceptance tests

| Target | What it checks |
| --- | --- |
| `just test` | every unit is checked out; every unit not yet owned is the original at its baseline plus its patches (all are owned now); the shared constitution is the same in every unit; each unit's own lint, type-check and fast tests |
| `just full-test` | everything in `just test`; each unit's history holds the original at its baseline (what a sync depends on); a rehearsal of a sync of each kind; each unit's own slow tests, the container test of `sandbox-provisioning` among them |

## Changing a unit

A unit is changed in its own repository, in `exportit/<unit>`, on a
feature branch there. When it is merged into the unit's `develop` and
pushed, this repository records the new commit (`git add
exportit/<unit>`), and is pushed after it, never before:
`just submodules-pushed` says whether every recorded commit is on its
remote.

## Carrying changes from the original

When the original project changes, a clean local clone of it is given to
the sync, one unit at a time:

```sh
just export-sync <unit> <path to the clone> sync-<n>
```

It merges the original's commits since the unit's baseline onto
`feature/sync-<n>` in the unit's repository, with their authors, and
moves the unit's baseline. What the mapping files cannot decide (a new
file no map claims, a deleted file a map names, a conflict with the
unit's own changes) stops it, and the unit is left as it was. The parity
watch, in the constitution's principle II, says when and how a sync is
planned: as a spec.

Nothing from this work goes toward `ioos/Cloud-Sandbox`: no push, no
pull request, no remote.
