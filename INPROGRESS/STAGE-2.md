# Stage 2: cloudflow as an independent project

*Status:* planned 2026-11-12. The operator asked for it to be executed
straight after [stage 1](STAGE-1.md); its decisions are asked first.

## Why

cloudflow is the only software product in the repository, and it is
the unit the operator named. Today it cannot be installed: it runs
from a checkout by changing `sys.path`, it has two `setup.py` files
that describe two different things, and it has no test that runs
without a live sandbox (couplings C1 to C4 and defects F1 to F5 in
[ANALYSIS.md](ANALYSIS.md)).

## What exists

- [cloudflow/](../cloudflow/): 195 tracked files. About 12,000 lines
  of Python in six sub-packages (`cluster`, `job`, `services`,
  `utils`, `workflows`, `plotting`), 3,000 lines of shell launchers
  and helper scripts, 44 model input templates (the largest files),
  22 notebook files, notes, two cron scripts, and seven script-style
  "tests" that need a running sandbox.
- At the repository root: [setup.py](../setup.py),
  [setup-plotting.sh](../setup-plotting.sh),
  [CLOUDFLOW.md](../CLOUDFLOW.md), [PREFECTv3.md](../PREFECTv3.md)
  and
  [LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md](../LOCAL_PYTHON_MINIFORGE3_INSTALLATION_CLOUD_SANDBOX_INSTRUCTIONS.md).
- What the code imports from outside the standard library: `boto3`,
  `botocore`, `prefect`, `dask`, `distributed` everywhere; `numpy`,
  `matplotlib`, `netCDF4`, `pyproj`, `PIL` and others in `plotting`,
  which [job_tasks.py](../cloudflow/workflows/job_tasks.py#L21)
  imports when it is loaded; `xarray`, `pandas`, `s3fs` in the Dask
  examples; the Jupyter libraries in `utils/notebook.py`.

## Items

1. **A mapping file and a copy tool.** `exportit/cloudflow.map` lists
   source path and destination path, one pair per line, by prefix.
   `exportit/tools/export.py` copies by that file, keeping file modes,
   and has a check mode that fails when a copied file differs from its
   source or when a tracked file under the unit's source paths is not
   mapped. The same file is what a history-preserving extraction would
   be driven by, so the map and the copy cannot drift apart.
2. **The project skeleton** under `exportit/cloudflow/`: `README.md`,
   `LICENSE` (a copy), `pyproject.toml` (replacing both `setup.py`
   files), a `Justfile` with the five contract targets wrapping `uv`.

   **YOUR DECISION (layout):** `src/cloudflow/` (default) or
   `cloudflow/` at the project root.
3. **The copy.** Library code goes into the package; everything else
   in `cloudflow/` goes beside it, so nothing is left behind:
   `notebooks/`, `notes/`, `docs/`, `examples/cron/`, `requirements/`,
   `legacy-tests/`, and `legacy/` for the files that
   `pyproject.toml` supersedes.

   **YOUR DECISION (fidelity):** every copied file byte-identical to
   its source, with only new files added (default), or also edit the
   copies so the code no longer depends on the monorepo.

   **YOUR DECISION (plotting):** `cloudflow.plotting` stays a
   sub-package of the one distribution (default), or becomes a second
   project.

   **YOUR DECISION (Lambda functions):** the two zombie-node functions
   and their notes travel with cloudflow, outside the package, under
   `aws-lambda/` (default), or are assigned to `sandbox-ops`
   ([stage 7](STAGE-7.md)).
4. **Tests that run anywhere.** New `tests/` for `pytest`: every
   Python file compiles; every library module imports; every file the
   code looks up beside itself (launchers, templates, helper scripts)
   is present and executable where it must be; and a ratchet that
   lists today's references to paths outside the package
   (`../job.configs`, `Cloud-Sandbox/...`, home directories) and fails
   when a new one appears.

   **YOUR DECISION (the bar for copied code):** new files pass `ruff`
   and `pyright` in full, while copied code is held to "compiles,
   imports, no undefined names" with the remaining debt counted and
   written down (default); or the copied code is brought to zero
   findings now, which means editing it.
5. **A root `Justfile`.** The repository has none, and the acceptance
   rule needs one. `test` runs the copy check and each exported
   unit's own `just test`; `init`, `build`, `full-test` and `release`
   delegate the same way.
6. **`full-test`.** Builds the wheel, installs it into an empty
   environment away from the source tree, and checks there that the
   package data arrived and that the `cloudflow` command starts.
7. **The cloudflow section of [MAP.md](../exportit/MAP.md):** the
   path table, the new and the superseded files, what the code would
   have to change at a real relocation (taken from the ratchet), what
   cloudflow expects from the other units, and the commands that
   would extract it with its history.

## Out of scope

- The Sphinx sources under `docs/source/`. They belong to cloudflow
  and are assigned to it in the map, and they are copied in
  [stage 8](STAGE-8.md) with the rest of the documentation.
- Changing anything under the original `cloudflow/`.
- Publishing: no repository is created and nothing is uploaded to a
  package index.

## Acceptance

- `just test` at the repository root passes: the copy check, lint,
  type-check with zero errors, and the tests.
- `just full-test` passes.
- `git status` shows no change outside `exportit/`, `INPROGRESS/`,
  `PLAN.md` and the new root `Justfile`.

## Sizing and branch

About 200 files copied, about 10 written. Branch
`feature/stage-2-cloudflow`, cut from `feature/stage-1-analysis`
because stage 1 is not merged yet; commits local.
