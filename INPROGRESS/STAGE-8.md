# Stage 8: documentation and the umbrella

*Status:* executed and merged into `develop` 2026-11-12. The decisions are
under [Decisions taken](#decisions-taken); the result under
[Outcome](#outcome).

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

## Decisions taken

1. **Built HTML:** not copied; the sources are, and the HTML and
   `docs/save/` are dropped as rebuilt.
2. **Splitting DEPLOYMENT.md:** written, as a `DEPLOYMENT.md` in
   `sandbox-terraform` and one in `sandbox-provisioning`.
3. **What remains:** an umbrella repository that pins the units'
   versions.

## Out of scope

Publishing documentation. Changing the original documents.

## Acceptance

`just test` and `just full-test` pass at the root; the copy check
reports every tracked file as mapped or as explicitly not relocated;
the cloudflow documentation builds from the export.

## Sizing and branch

About 45 files copied, about 8 written. Branch
`feature/stage-8-docs-umbrella`.

## Outcome

- Item 1: `docs/source/` and its build files in
  [exportit/cloudflow/docs/sphinx/](../exportit/cloudflow/docs/sphinx/);
  one patch makes `conf.py` document the installed packages; `just docs`
  builds, and a slow test holds the build to the three pages whose
  modules are gone. 129 built files and `docs/save/` dropped.
- Item 2: [sandbox-terraform/DEPLOYMENT.md](../exportit/sandbox-terraform/DEPLOYMENT.md)
  and [sandbox-provisioning/DEPLOYMENT.md](../exportit/sandbox-provisioning/DEPLOYMENT.md),
  each naming the original's lines and its departures.
- Item 3: [exportit/cloud-sandbox/](../exportit/cloud-sandbox/README.md),
  with `units.toml` (15 units, versions, apply steps, relocation order;
  14 since plotting was folded back into cloudflow on 2026-11-13),
  its own check, and a tools test that holds it to the repository.
- Item 4: the umbrella's map says `covers ./`, a form the export tool
  learned for it; every one of the 814 tracked files outside `exportit/`
  is now taken or dropped with a reason.
- Item 5: [MAP.md](../exportit/MAP.md#the-order-of-the-real-relocations)
  closes with the relocation steps (nine, eight since 2026-11-13) and what the original holds
  after each.
- Found: six broken links in the root README; DEPLOYMENT.md stale
  against the Terraform module; the Terraform version (1.5.7 in the
  documents, 1.9.8 in the tests) left as a choice to make.
