# Contract: `LIVE-PROOF.md`, version 2

**Where**: `csis-sandbox-provisioning/docs/LIVE-PROOF.md`, rewritten (FR-002),
using the files of `csis-sandbox-terraform/proof/` (research R1).

## Form (every box)

- Starts `# <step> -- box N of M -- v2`; a rewrite of a box bumps its version.
- Says where it runs: **your local machine** or **the head node** (over SSM).
- A command whose output must be checked is the box's last line, and the text
  after it says what it must show.
- A box over thirty seconds states its time.
- Every choice is a bold **YOUR DECISION** line with its default.
- Every box that creates, changes or removes something on AWS says so first,
  and the agent stops for the operator's word before it.

## Stages and their gates

| Stage | Boxes (outline) | Gate before going on |
| --- | --- | --- |
| A. The node | A1 session and `session-manager-plugin`; A2 working copy of `csis-sandbox-terraform` at its tag, `proof/` copied in, key pair; A3 the VPC and subnet (**decision**), `proof.tfvars`, the VPC's description saved; A4 `tofu init`, workspace `live-proof`, plan | the plan shows only additions, `0 to change, 0 to destroy`; then the operator's word to apply |
| A5 | apply; the node's ID; an SSM session opens | the SSM session answers |
| B. The build | B1 follow the first boot (repeatable); B2 the boot's recap, `failed=0`; B3 the second apply; B4 check mode; B5 Spack's configuration compared; B6 module-file times; B7 `jupyterhub.yml` applied, the hub answering on its port | each result read; changes are findings, not stops |
| C. The image | C1 `node-image.yml` on the head node; C2 `describe-images` from your local machine | the operator's word before C1; the image `available` |
| D. The comparison | skipped unless `compare_with_script` is `true`; then the second node's boot, and the comparison of the two | — |
| E. Removal | E1 workspace check; E2 `tofu destroy`; E3–E4 image and snapshot by ID; E5 nothing with the prefix; E6 the VPC's description compared with A3's | the operator's word before E2, E3 and E4; E5 empty; E6 equal |
| What to bring back | the logs stay on your local machine; their summary goes into spec 001's outcome and `exportit/MAP.md` | — |
