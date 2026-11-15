# Stage 17: the Lambda functions, owned

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. It is a decision first: at "do 17" the **YOUR DECISION** below
is asked, and only then is the work it leads to done. Eighth in the
order of the remaining work ([PLAN.md](../PLAN.md)): it depends on
nothing, is larger than the stages before it, and must come before any
relocation, because cloudflow is relocated first and the functions are
in it.

## Why

Put aside on 2026-11-13 ([REMINDERS.md](../exportit/REMINDERS.md)). Two
AWS Lambda functions, `lambda_identify_zombies.py` and
`lambda_terminate_zombies.py`, find compute nodes that cloudflow left
running past `ORG_MAX_MINUTES` (from the DynamoDB table cloudflow writes,
`TABLE_NAME`, in `AWS_REGION`) and terminate them, with an HTML report to
S3. They are the sandbox's guard against paying for nodes nobody stops.

- They sit in cloudflow's package (`src/cloudflow/cluster/`), by stage
  2's decision 5, but **cloudflow never imports them**: they read their
  settings from the environment when loaded, which is why cloudflow's
  import test lists them as skipped.
- **Nothing deploys them:** no Terraform or OpenTofu, no playbook, no
  packaging. They, their schedule and their IAM role are made by hand
  (found in stage 4), like the DynamoDB table.
- `cloudflow/docs/ZOMBIE_JOB_CHECKLIST.md` describes the zombie
  problem and its manual clean-up; `lambda.env` holds the three
  variables for running them locally.

## The decision

**YOUR DECISION (who owns them):**

- **`sandbox-terraform`** (default): they are infrastructure of the
  account, beside the table they read. The module gains them: the two
  functions packaged from their source, a schedule (EventBridge), an IAM
  role allowed exactly the table, `ec2:DescribeInstances` and
  `ec2:TerminateInstances` on instances the sandbox tagged, and the
  report's bucket. The table's name is the variable stage 4 asked for.
  The source moves out of cloudflow's package with the commands to
  test it.
- **A unit of their own, `sandbox-reaper`**, with its own tests and its
  own OpenTofu module, applied after `sandbox-terraform`. Cleanest to
  relocate; one more repository.
- **Stay in cloudflow**, outside the package (`aws-lambda/`, stage 2's
  original default), still deployed by hand; documented as such.

**YOUR DECISION (deploy them now?):** with either of the first two,
write the module and test it with `tofu validate` and `tofu plan`
against a workspace with no resources (default); or also apply it in the
account. Applying it means the functions start terminating nodes past
their limit; it is the operator's to switch on.

## Work, with the default

1. **The code** moves to `sandbox-terraform/lambda/` from cloudflow's
   copy, byte-identical, through the map (cloudflow's map drops the two
   files and `lambda.env`; `sandbox-terraform.map` takes them).
   cloudflow's import test loses the two skipped modules.
2. **Tests:** unit tests of both handlers with the AWS calls replaced
   (`botocore`'s Stubber): a node past its limit is terminated, one
   within it is not, one already gone is reported as invalid, a failure
   is reported and does not stop the rest; the report is written.
3. **The module:** `lambda.tf` with the two functions, their packaging
   (`archive_file`), the schedule, the role and its policy, and
   variables `lambda_max_minutes`, `table_name`, `report_bucket`; off
   unless `enable_reaper` is true. Its test renders and validates it.
4. **Records:** MAP.md (both units' sections, and the order of
   relocation: the functions now travel with `sandbox-terraform`),
   `DEPLOYMENT.md`, REMINDERS.md.

## Out of scope

Changing what the functions do, beyond what a test finds broken.

## Acceptance

The root `just test` and `just full-test` pass; `tofu validate` and
`tofu plan` of the module succeed with `enable_reaper` true and false;
REMINDERS.md loses the item.
