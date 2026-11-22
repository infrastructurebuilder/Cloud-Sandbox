# Data model: sandbox-configs split by owner

## A description's catalogue entry (`csis-sandbox-configs/tests/catalogue.json`)

| Field | Values | Change |
| --- | --- | --- |
| `kind` | `job`, `cluster`, `other` | none |
| `role` | `template`, `example`, `site`, `helper`, `note`, `pointer` | `template` and `example` entries leave with their files |
| `status` | `ok`, `missing …`, `not JSON: …`, `unknown JOBTYPE …`, `a script`, `text`, `names …` | + `retired: <reason>`, only for a path under `attic/` |

Cloudflow gains its own catalogue of what it carries,
`examples/configs/catalogue.json`, with the same fields, every `status`
`ok`.

## A `moved` line (spec 003's contract)

```text
moved <job.configs/… or cluster.configs/…> cloudflow examples/configs/<the same path>
```

51 lines in `exportit/sandbox-configs.map`, one per `template` or `example`
file; none for a retired file.

## The output `cluster_description` (csis-sandbox-terraform)

| Key | From |
| --- | --- |
| `platform` | `"AWS"` |
| `region` | `var.preferred_region` |
| `subnet_id` | the subnet the module reads or makes |
| `sg_ids` | the base and EFS security groups |
| `placement_group` | the module's placement group |
| `table_name` | `var.node_table_name` (default `IOOS-Sandbox-Compute-Nodes`) |
| `image_id` | the deployment's image, by name prefix; `null` until `node-image.yml` has made it |

## A file's way through this spec

```text
unreadable ─▶ repaired (sibling evidence) ─▶ readable
          └▶ no evidence ─▶ attic/, retired: <reason>
readable template or example ─▶ searched (public repository) ─▶ moved to cloudflow ─▶ checked by cloudflow's schema
readable site file ─▶ stays ─▶ checked by the copy of cloudflow's schema
current.system, current.image_id ─▶ attic/, retired: replaced by the output cluster_description
```
