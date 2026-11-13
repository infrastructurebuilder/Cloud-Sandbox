# Stage 5: model recipes as an independent unit

*Status:* executed and merged into `develop` 2026-11-12. The decisions are
under [Decisions taken](#decisions-taken); the result under
[Outcome](#outcome).

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

## Decisions taken

1. **Granularity:** one unit per model, `model-<name>`, eight of them.
2. **Shared files** (a follow-up to 1): everything shared, the two
   module files and the four notes, in a ninth unit, `model-common`.
3. **The bar for copied scripts:** `bash -n` must pass; shellcheck's
   findings are counted per script and the test fails when a count
   changes. The copies are not edited.

## Out of scope

Building or running any model. Fetching any data.

## Acceptance

`just test` passes at the root and in the export; the copy check
covers every tracked file under `models/` and `patches/`; every
launcher path that refers to a model install has a row in the
contract.

## Sizing and branch

149 files copied, about 5 written. Branch `feature/stage-5-models`.

## Outcome

- Nine units under [exportit/](../exportit/): `model-adcirc-cora`,
  `model-eccofs`, `model-liveocean`, `model-necofs`, `model-nosofs`,
  `model-secofs`, `model-ucla-roms`, `model-ufscoastal` and
  `model-common`; 149 files, byte-identical, each model directory at
  its unit's root (`patches/adcirc-cora/` to `patches/` of
  `model-adcirc-cora`).
- The unit's own description is `UNIT.md`, not `README.md`: two
  models have a `README.md` of their own, which the first attempt
  overwrote in the copy (restored from the original at once, before
  any commit).
- One harness, `tests/check-scripts.sh`, the same in every unit (a
  check in `tools` holds them identical, and tests its behaviour):
  53 scripts parse, 4 templates do not and are listed, 943 shellcheck
  findings recorded with shellcheck 0.11.0.
- The install contract, 42 rows, in
  [MAP.md](../exportit/MAP.md#the-install-contract), with a check in
  `tools` that fails on a launcher path without a row or a row
  without a launcher path.
- Found: module names carry Spack build hashes that a rebuilt sandbox
  will not reproduce; five setup scripts exit 1 when they create
  their install directory; several recipes assume their place in a
  Cloud-Sandbox checkout; some installs have no recipe at all.
  Details in [MAP.md](../exportit/MAP.md#found).
- Correction to the question asked at "do 5": the common
  `intel_x86_64.impi_2021.12.1` is used only by `adcirc-cora`'s
  build. The cloudflow launchers load a module of the same name from
  `$SAVEDIR/modulefiles`, which for NECOFS is `model-necofs`'s own,
  different file. The decision stands.
- Before the stage: the DynamoDB table recorded as made by hand and
  supplied as configuration (operator), on stage 4's branch.
