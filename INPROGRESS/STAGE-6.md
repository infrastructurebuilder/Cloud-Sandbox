# Stage 6: job and cluster descriptions as an independent unit

*Status:* planned 2026-11-12. Waits for validation and "do 6".
Better after [stage 2](STAGE-2.md), which states the schema.

## Why

[job.configs/](../job.configs/) and
[cluster.configs/](../cluster.configs/) are data, not code. cloudflow
reads them by a path given on the command line. Many of them carry
one site's AWS identifiers (image id, security groups, subnet, key
name), so they are that site's configuration and have a different
owner and a different rate of change from the software (C2 and C7 in
[ANALYSIS.md](ANALYSIS.md)).

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
6. The configs section of [MAP.md](../exportit/MAP.md).

## Out of scope

Changing any description. Validating identifiers against AWS.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under both directories; every key in the
schema names the line of code that reads it.

## Sizing and branch

130 files copied, about 6 written. Branch `feature/stage-6-configs`.
