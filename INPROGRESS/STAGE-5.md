# Stage 5: model recipes as an independent unit

*Status:* planned 2026-11-12. Waits for validation and "do 5".

## Why

[models/](../models/) holds the recipes that fetch, patch and build
each ocean model on a sandbox. They are not used by any code in the
repository; they are run by hand, and they leave executables and
module files at paths that the cloudflow launchers then assume (C3 in
[ANALYSIS.md](ANALYSIS.md)). That assumption is the only tie, and it
is written down nowhere.

## What exists

147 tracked files: eight model directories (`adcirc-cora` with 55
files is the largest; then `necofs`, `ufscoastal`, `secofs`, `eccofs`,
`liveocean`, `nosofs` and `ucla-roms`), shared `modulefiles` and
`utils`, and three notes. Two scripts under [patches/](../patches/)
belong to `adcirc-cora`. The recipes were read only as a file list.

## Items

1. Read each model directory and record, per model: what it fetches
   and from where, which compilers and modules it needs from
   provisioning, and where it installs.
2. Copy `models/` and `patches/` to `exportit/sandbox-models/`
   through a mapping file.

   **YOUR DECISION (granularity):** one unit holding all models
   (default), or one unit per model.
3. Add `README.md`, `LICENSE` and a `Justfile` (`test` = `shellcheck`
   and `bash -n` on the recipes; no model is built).

   **YOUR DECISION (the bar for copied scripts):** report
   `shellcheck` findings as a count and fail only on syntax errors
   (default), or hold the copies to zero findings, which means
   editing them.
4. Write the install contract: for each model, the paths that
   cloudflow's launchers expect, taken from the launchers themselves.
5. The models section of [MAP.md](../exportit/MAP.md).

## Out of scope

Building or running any model. Fetching any data.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under `models/` and `patches/`; every
launcher path that refers to a model install has a row in the
contract.

## Sizing and branch

149 files copied, about 5 written. Branch `feature/stage-5-models`.
