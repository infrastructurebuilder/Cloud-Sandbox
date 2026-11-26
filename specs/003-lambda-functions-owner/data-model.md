# Data model: The Lambda functions, owned and deployable

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-20

## A moved file (in Cloud-Sandbox's maps)

| Field | Meaning | Rule |
| --- | --- | --- |
| source | the original's path | a file a `copy` rule of the leaving unit takes; moved once |
| leaving unit | the map the line is in | keeps its `copy` rule |
| arriving unit | the unit named | another unit; does not copy the source |
| destination | the path in the arriving unit | not a path the arriving unit copies; unique in that unit |

State: written once, when the file moves. It stays as long as the leaving
unit's `copy` rule does: it is what keeps a later sync from bringing the file
back. The full rules are [contracts/moved-directive.md](contracts/moved-directive.md).

## An overdue node (DynamoDB, written by cloudflow, unchanged)

| Attribute | Meaning |
| --- | --- |
| `instance-id` | the key |
| `start-time` | seconds since the epoch, when cloudflow started it |
| `minutes-max` | its own limit, read and not used: the functions hold every node to `ORG_MAX_MINUTES` |

The terminating function terminates a node started more than `ORG_MAX_MINUTES` ago, if the node
carries the launch tag (else the call is refused and reported, spec edge
case), and deletes the item of every node it terminated or found gone.

## The launch tag

| Key | Value | Put on by | Required by |
| --- | --- | --- | --- |
| `csis:launched-by` | `cloudflow` | cloudflow, on every instance it launches | the terminating role's `ec2:TerminateInstances` condition |

## The report

`<report_bucket>/monitoring/IOOS_Coastal_Sandbox_Suspect_Report_<YYYY-MM-DD-HH>.html`,
written once per run of the identifying function; the bucket is now the
setting `REPORT_BUCKET`.
