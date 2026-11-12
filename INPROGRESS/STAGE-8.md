# Stage 8: documentation and the umbrella

*Status:* planned 2026-11-12. Waits for validation and "do 8". Last,
because it describes what the other stages made.

## Why

When the units have left, two things remain: the documentation, which
today describes the monorepo as one thing, and the question of what
Cloud-Sandbox itself is afterwards.

## What exists

- [docs/](../docs/): 175 tracked files. `docs/source/` is 35 Sphinx
  source files that document cloudflow's modules through `sys.path` entries
  into `cloudflow/` (C9 in [ANALYSIS.md](ANALYSIS.md)). The rest is
  the HTML built from them, committed (F11), and an older copy under
  `docs/save/`.
- Root documents: [README.md](../README.md),
  [DEPLOYMENT.md](../DEPLOYMENT.md) (304 lines, covering Terraform and
  provisioning together) and
  [CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md](../CLOUD_SANDBOX_MODEL_INTEGRATION_TEMPLATE.md).
- [images/](../images/), the root `TODO`, `.github/ISSUE_TEMPLATE.md`,
  `LICENSE` and `.gitignore`.

## Items

1. Copy `docs/source/` into the cloudflow export and make it build
   there against the installed package.

   **YOUR DECISION (built HTML):** do not copy the generated HTML;
   the map records it as rebuilt, not relocated (default), or copy
   it.
2. Split `DEPLOYMENT.md` in the map: which sections go to
   `sandbox-terraform`, which to `sandbox-provisioning`.

   **YOUR DECISION (splitting):** write the split documents into the
   exports (default), or only mark the sections in the map.
3. Write the umbrella: `exportit/cloud-sandbox/` with a README that
   says what a sandbox is made of, which units and which versions,
   and the order to apply them.

   **YOUR DECISION (what remains):** Cloud-Sandbox becomes a small
   repository that pins the units' versions (default), or it is
   retired and one unit takes over the name.
4. Assign every remaining tracked path, so that the root copy check
   reports no unmapped file in the repository.
5. Close [MAP.md](../exportit/MAP.md): the order in which the real
   relocations would be done, and what the original repository looks
   like after each.

## Out of scope

Publishing documentation. Changing the original documents.

## Acceptance

`just test` and `just full-test` pass at the root; the copy check
reports every tracked file as mapped or as explicitly not relocated;
the cloudflow documentation builds from the export.

## Sizing and branch

About 45 files copied, about 8 written. Branch
`feature/stage-8-docs-umbrella`.
