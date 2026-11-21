# Contract: the `reaper` module, and the functions' settings

**Where**: `csis-sandbox-terraform`, directory `reaper/`, a root module of its
own (research R1), applied after the unit's main module.

## Variables

| Variable | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enable_reaper` | bool | `false` | Nothing is created unless it is true |
| `region` | string | none | The region of the table and the nodes |
| `name_prefix` | string | none | Prefix of every resource's name, as the main module's `nameprefix` |
| `table_name` | string | none | The DynamoDB table cloudflow writes (a cluster description's `table_name`) |
| `lambda_max_minutes` | number | none | `ORG_MAX_MINUTES`: a node started longer ago than this is overdue. The functions use only this; each node's own `minutes-max` is read and not used (the line that would use it is commented out) |
| `report_bucket` | string | `"ioos-transfers"` | `REPORT_BUCKET`: where the identifying function writes its report |
| `schedule` | string | `"rate(1 hour)"` | When both functions run (EventBridge schedule expression) |
| `launch_tag_key` | string | `"csis:launched-by"` | The tag the terminating role requires |
| `launch_tag_value` | string | `"cloudflow"` | Its value |

No variable has a site's account number, a key or a secret.

## Resources, when `enable_reaper` is true

- Two `aws_lambda_function`s, runtime `python3.13`, each packaged by an
  `archive_file` from `reaper/functions/`, handler `<file>.lambda_handler`.
- Their environment: `TABLE_NAME`, `ORG_MAX_MINUTES`, and, for the
  identifying function, `REPORT_BUCKET`. Not `AWS_REGION`, which Lambda sets
  (research R4).
- A schedule rule and its two targets, with the permission for EventBridge to
  invoke each function.
- Two roles, each with a policy allowing exactly (research R3):
  - both: `dynamodb:Scan` and `dynamodb:BatchWriteItem` on the table; the
    CloudWatch Logs actions on the function's own log group;
  - the identifying function: `s3:PutObject` on
    `arn:aws:s3:::<report_bucket>/monitoring/*`;
  - the terminating function: `ec2:TerminateInstances` on `*`, with the
    condition `StringEquals { "ec2:ResourceTag/<launch_tag_key>":
    "<launch_tag_value>" }`, and no other EC2 action.

When it is false, the plan holds no resource.

## The functions' settings

| Setting | Read by | Set by |
| --- | --- | --- |
| `TABLE_NAME` | both | the module |
| `ORG_MAX_MINUTES` | both | the module |
| `REPORT_BUCKET` | the identifying function (new, FR-009) | the module; `lambda.env` for a local run |
| `AWS_REGION` | both | Lambda itself; `lambda.env` for a local run |

## The launch tag (cloudflow)

`cloudflow.cluster.AWSCluster` adds `{"Key": "csis:launched-by", "Value":
"cloudflow"}` to the tags of every instance it launches, after the cluster
description's own tags and `ApprovedSubnet`. The key and value are one
constant there; the module's defaults equal it, and a test in Cloud-Sandbox's
`exportit/tools/` holds the two equal (a check between units belongs where all
of them are checked out; no unit reads another).
