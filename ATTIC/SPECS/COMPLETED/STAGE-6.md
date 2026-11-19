# Stage 6: job and cluster descriptions as an independent unit

*Status:* executed and merged into `develop` 2026-11-12. The decisions are
under [Decisions taken](#decisions-taken); the result under
[Outcome](#outcome).

## Why

[job.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/job.configs) and
[cluster.configs/\*](https://github.com/infrastructurebuilder/Cloud-Sandbox/tree/ca0604a4a27355b330353c7ded8a1ae00a7e24a6/cluster.configs) are data, not code. cloudflow
reads them by a path given on the command line. Many of them carry
one site's AWS identifiers (image id, security groups, subnet, key
name), so they are that site's configuration and have a different
owner and a different rate of change from the software (C2 and C7 in
[ANALYSIS.md](../ANALYSIS.md)).

## What exists

80 files under `job.configs/` (46 of them under `OFS/`) and 50 under
`cluster.configs/` (32 under `IOOS/`). Most are JSON descriptions;
there is a template for each kind, and a few files are something else
(two helper scripts, a Python test, notes, a file holding the current
image id).

## Items

1. Write down the schema: every key that cloudflow reads from a job
   description and from a cluster description, taken from the code,
   and which keys are required.
2. Classify each file: a template or example that any site can use,
   or one site's live configuration.
3. Copy both directories to `exportit/sandbox-configs/` through a
   mapping file.

   **YOUR DECISION (identifiers):** copy the files as they are, with
   the identifiers in them (default), or replace identifiers with
   placeholders in the copies.

   **YOUR DECISION (one unit or two):** examples and site data
   together (default), or examples travel with cloudflow and only
   site data forms this unit.
4. Add `README.md`, `LICENSE` and a `Justfile` (`test` = every
   description parses as JSON and has the required keys for its
   kind).
5. Say which values come from Terraform's outputs and which from the
   node image, so that C7 has an owner.
6. The configs section of [MAP.md](../../../exportit/MAP.md).

## Decisions taken

1. **Identifiers:** the copies keep them, byte-identical; no patches.
2. **One unit or two:** one unit; templates, examples and site data
   together, sorted by the catalogue.

## Out of scope

Changing any description. Validating identifiers against AWS.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under both directories; every key in the
schema names the line of code that reads it.

## Sizing and branch

130 files copied, about 6 written. Branch `feature/stage-6-configs`.

## Outcome

- [exportit/sandbox-configs/](../../../exportit/sandbox-configs/): all 130
  files, unchanged, under their own directory names, with a README,
  `Justfile` and tests.
- The schema (item 1) is written from cloudflow's code by
  [tools/configs_schema.py](../../../exportit/tools/configs_schema.py),
  not by hand: 17 `JOBTYPE`s and 2 platforms, every key with the line
  that reads it. A tools test fails when the code and the schema part.
- Every file classified (item 2) by written rules and recorded in a
  catalogue: 3 templates, 48 examples, 71 site files, 8 others. The
  unit's test fails when a file's kind, role or readability changes.
- Item 4's test, "every description parses and has the required
  keys", became "every description is as recorded": 99 of 122 are
  readable, 23 are not, each with its reason, since the copies are not
  edited.
- Item 5: the owners of each cluster value are in the README and
  [MAP.md](../../../exportit/MAP.md#where-the-cluster-values-come-from).
- Found: the cluster template a new site copies lacks `table_name`,
  which cloudflow now requires; the 40 AWS cluster descriptions span
  19 images and 13 placement groups, and only 4 match the latest
  deployment. Details in [MAP.md](../../../exportit/MAP.md#sandbox-configs).

---

\* A link marked with an asterisk opens the file or directory as it was at
commit [`ca0604a`](https://github.com/infrastructurebuilder/Cloud-Sandbox/commit/ca0604a4a27355b330353c7ded8a1ae00a7e24a6)
of this repository: the original project, from which every unit was made,
and every unit's baseline. These files are no longer on `develop`, because
[stage 22](STAGE-22.md) deleted the originals on 2026-11-19 once
each unit owned its copies.
