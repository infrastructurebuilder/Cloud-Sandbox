# Research: sandbox-configs split by owner

Each item records a decision, why, and what else was weighed. Written on
2026-11-21, from `csis-sandbox-configs`' `tests/catalogue.json`, which gives
every file a `kind`, a `role` and a `status`.

## R1. Which files move

**Decision**: the catalogue's `role` decides. The 3 `template` and 48
`example` files move to cloudflow; the 71 `site` files stay; the 4 `helper`
scripts, 2 `note` files and 2 `pointer` files stay with the site's files
(they serve them: `list_amis.sh`, `get_aws_ec2meta.sh`, and notes naming site
files).

| Role | Count | Readable today | Goes to |
| --- | ---: | ---: | --- |
| template | 3 | 1 | cloudflow `examples/configs/` |
| example | 48 | 41 | cloudflow `examples/configs/` |
| site | 71 | 57 | stays |
| helper, note, pointer | 8 | n/a | stays |

**Rationale**: the catalogue already records each file's role, checked by the
unit's tests, so the split needs no new judgement.

## R2. The 23 unreadable, before the move (FR-003)

**Decision**: the rule for each, applied in `csis-sandbox-configs` before any
`moved` line is written:

| Status in the catalogue | Count | Repair |
| --- | ---: | --- |
| `not JSON: …` | 3 (site) | fixed when the intended JSON is evident (a trailing comma, two objects run together); else retired |
| `missing table_name` | 5 site, 1 template | `"table_name": "IOOS-Sandbox-Compute-Nodes"`, the table cloudflow and the reaper use |
| `missing SAVEDIR`, `GRID`, `CASE_FILE, MODEL_DIR`, `NML_IN, NML_TMPL, RNDAY`, `BCKTFLDR, BUCKET, FSPEC` | 13 | the key added when a sibling description of the same model gives its value; else retired |
| `unknown JOBTYPE 'XXX_MODEL_EXPERIMENT'` | 1 template | the placeholder replaced by the JOBTYPE of the model the template is for, so the schema reads it |

Retired files go to a new `attic/` in `csis-sandbox-configs`, keeping their
path below it, with the catalogue's `status` set to `retired: <reason>`; the
unit's test accepts that status only under `attic/`. Each repair is its own
commit naming the file and the key.

**Rationale**: FR-003 and SC-001: every description readable or retired with
its reason, before cloudflow receives any. A sibling's value is the
evidence for a repair; without one the file is not guessed at.

## R3. The move

**Decision**: one `moved` line per file in `exportit/sandbox-configs.map`, in
spec 003's form, `moved <source> cloudflow examples/configs/<path below
job.configs/ or cluster.configs/, with that directory kept>`, for example
`moved cluster.configs/template.ioos cloudflow
examples/configs/cluster.configs/template.ioos`. The lines are generated
from the catalogue (role `template` or `example`) by a small script in the
workshop and reviewed. The files are added to cloudflow, as they are after
R2, in one commit; they leave `csis-sandbox-configs` in one commit.

**Rationale**: FR-005; spec 003's contract (single files, written in the
leaving unit's map, the leaving map keeps its `copy` rule). Keeping the two
directory names below `examples/configs/` keeps a reader's way around.

**Dependency**: spec 003's `moved` directive, implemented and merged.

## R4. Moving into a public repository

**Decision**: before the files are added to cloudflow, which is public since
2026-11-21, they are searched for secrets and personal data as the
repositories' histories were. They came from the public original, so they are
expected to hold only resource IDs (security groups, subnets, images) and
paths; anything else stops the move for the operator.

## R5. The schema's one place

**Decision**: `configs_schema.py` moves to cloudflow as
`tools/configs_schema.py`, reading cloudflow's own `src/`, and writes
`schema/jobs.json` and `schema/clusters.json` in cloudflow, which its tests
check against its code (as the workshop's tools tests do today). Cloudflow's
tests check every file under `examples/configs/` against them (FR-006).
`csis-sandbox-configs` keeps a copy of the two files in `schema/`, written by
the workshop (`just configs-schema`, now copying from cloudflow's checkout)
and checked by the root's `just test` (as `just constitution-check` checks the
shared constitution); its own tests read the copy.

**Rationale**: principle I: the schema lives in one place, the code that
reads the descriptions; a unit that needs it gets a copy written and checked
from there. The writer stops reading another unit's code.

**Alternatives considered**: cloudflow as a dependency of
`csis-sandbox-configs`' test environment (`git+https` at a tag; possible now
that it is public, but every schema change would need a cloudflow tag before
the configs' tests saw it).

## R6. The fragment that replaces `current.system` (FR-004)

**Decision**: `csis-sandbox-terraform`'s main module gains an output,
`cluster_description`, an object with `platform` (`"AWS"`), `region`,
`subnet_id`, `sg_ids` (the base and EFS groups), `placement_group`,
`table_name` (a new variable, `node_table_name`, default
`IOOS-Sandbox-Compute-Nodes`) and `image_id`. The image is made by
`node-image.yml`, after Terraform; `image_id` is read with a
`data "aws_ami_ids"` lookup for the deployment's image name prefix, owner
`self`, and is `null` until the image exists; `tofu apply -refresh-only`
after the image fills it. A test in cloudflow checks the output's keys
against the cluster schema (a sample of the output, rendered by `tofu test`
in the terraform unit and kept as a fixture there, read by a test in the
workshop that has both).

**Rationale**: the hand-kept file held exactly these keys; Terraform knows
all but the image, and the lookup gets that without the playbook writing
anywhere.

## R7. Where the check between the two units runs

**Decision**: the workshop's tools tests (`exportit/tools/tests/`), which
already see every unit: the terraform unit's fixture checked against
cloudflow's cluster schema; the `moved` lines checked against the catalogue's
roles.
