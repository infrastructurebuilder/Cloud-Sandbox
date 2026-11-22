# Contract: the schema's place, and the move

## The schema

| Where | What | Checked by |
| --- | --- | --- |
| cloudflow `tools/configs_schema.py` | writes `schema/jobs.json`, `schema/clusters.json` from cloudflow's `src/` | cloudflow's tests: the files equal what the code gives |
| cloudflow `examples/configs/` | the 51 templates and examples | cloudflow's tests: each read by the schema, `table_name` in the cluster template |
| `csis-sandbox-configs/schema/` | a copy of cloudflow's two files | the root's `just test`: equal to cloudflow's (`just configs-schema-check`) |
| `csis-sandbox-configs` | the site's files | its own tests, against its copy |

`just configs-schema` (root) copies cloudflow's files into
`csis-sandbox-configs/schema/`; `just configs-schema-check` fails on any
difference.

## The move

- Before: no `template` or `example` file is unreadable (R2).
- `exportit/sandbox-configs.map`: 51 `moved` lines; `exportit/cloudflow.map`
  unchanged (the arriving files are accepted by `moved`).
- `just export-check`, `just export-lineage` and the sync rehearsal pass for
  both units (FR-005).
- A change to a moved file in a later original lands in cloudflow on
  `just export-sync`.
