# Research: The Lambda functions, owned and deployable

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-20

Everything here was found by reading the code and by trying it on the local
machine, in scratch directories, with nothing created in any AWS account.

## R1. The AWS provider the unit pins cannot make a supported Lambda

**Decision:** The functions' OpenTofu goes in a **root module of its own**,
`reaper/` in `csis-sandbox-terraform`, with its own `versions.tofu` and
providers: `hashicorp/aws ~> 6.0` and `hashicorp/archive ~> 2.0`, runtime
`python3.13`. It is applied on its own, after the unit's main module, as
`remote-state/` already is.

**Rationale:** the unit's `main.tf` pins `hashicorp/aws ~> 3.47` (3.76.1 is
installed). Tried on 2026-11-20: that provider refuses `runtime =
"python3.12"`; its newest Python is `python3.9`, which AWS has deprecated. In a
scratch module, `hashicorp/aws` 6.73.0 with `hashicorp/archive` 2.8.1 accepts
`python3.13`, and `tofu validate` passes under the pinned OpenTofu 1.13.9. A
child module called from `main.tf` would have to share its provider, and
`~> 3.47` and `~> 6.0` cannot both hold; a separate root module leaves the
main module's provider, and every node it already describes, untouched.

**Alternatives considered:**
- Raise the main module to `aws ~> 6.0`: three major versions, across a module
  the live proof (spec 001) has not yet applied once; a change of its own, not
  this spec's.
- `python3.9` on the old provider: a runtime AWS no longer supports.

## R2. Testing the module without an account

**Decision:** `tofu test`, with `mock_provider "aws"` and
`mock_provider "archive"`, in `reaper/tests/*.tftest.hcl`, run by the unit's
`just test` through its pytest wrapper; `tofu validate` as for the other
modules. Two runs: `enable_reaper = false` (nothing planned) and `true` (the
functions, their schedule, the role, its policy).

**Rationale:** a plain `tofu plan` needs credentials and calls AWS, even in an
empty workspace. OpenTofu 1.8 and later mock a provider in `tofu test`, so the
plan is made and asserted on with no credentials and no network beyond the
providers' download, which `just init` does once into `.terraform-plugins/`.
The spec's "a plan against a workspace with no resources" is met by the mocked
plan, which is how a plan with no account can be made at all.

**Alternatives considered:** `tofu plan` with fake credentials and every
`skip_*` provider setting; brittle, and it still reaches AWS's endpoints for
some calls.

## R3. What the functions call, and so what the role needs

Read from the code (2026-11-20):

| Function | Calls |
| --- | --- |
| `lambda_identify_zombies.py` | DynamoDB `Scan`; `batch_writer().delete_item` (DynamoDB `BatchWriteItem`); S3 `PutObject` of `monitoring/IOOS_Coastal_Sandbox_Suspect_Report_<time>.html` into `ioos-transfers` |
| `lambda_terminate_zombies.py` | DynamoDB `Scan`; EC2 `TerminateInstances`; `batch_writer().delete_item` (DynamoDB `BatchWriteItem`) |

**Decision:** each function gets its own role, allowed exactly what it calls:
the table (`dynamodb:Scan`, `dynamodb:BatchWriteItem`), for the identifying
function `s3:PutObject` on `<report_bucket>/monitoring/*`, for the terminating
function `ec2:TerminateInstances` under the tag condition of R5, and both the
CloudWatch Logs actions on their own log group.

**Rationale:** least privilege, and two roles keep the one that can stop nodes
from writing anywhere else.

**A difference from the spec:** FR-005 named `ec2:DescribeInstances`. Neither
function calls it, so the role does not have it; FR-005 is corrected to match.

## R4. `AWS_REGION` is the runtime's, not the module's

**Decision:** the module sets `TABLE_NAME`, `ORG_MAX_MINUTES` and
`REPORT_BUCKET` (FR-009), and not `AWS_REGION`.

**Rationale:** Lambda reserves `AWS_REGION` and sets it itself, in the
function's own region; a function configuration that sets it is refused. The
functions read it from the environment, as they already do.

## R5. The tag cloudflow adds, and one it already adds

**Decision (as clarified):** cloudflow adds `csis:launched-by = cloudflow` to
the tags of every node it launches, beside the cluster description's own; the
constant lives in `cloudflow.cluster.AWSCluster`. The terminating role's
`ec2:TerminateInstances` carries the condition `StringEquals
ec2:ResourceTag/csis:launched-by = cloudflow`. The key and value are the
module's variables `launch_tag_key` and `launch_tag_value`, defaulting to
cloudflow's constant. Tag keys may contain `:`; only the `aws:` prefix is
reserved.

**Found while planning, for the operator:** cloudflow already adds one tag of
its own to every node it launches, whatever the cluster description says:
`ApprovedSubnet = <the cluster's subnet>` (`AWSCluster.py`, line 407, with the
comment "used with EC2 policy to restrict ec2 visibility to current subnet").
A condition on it would need no cloudflow change, would also cover nodes
started before this spec, and could be held to the sandbox's own subnet. The
clarified answer stands; this is raised, not acted on.

## R6. Carrying a moved file: the `moved` directive

**Decision:** a new mapping directive, written in the map of the unit the file
leaves:

```text
moved <source> <unit> <destination>
```

The leaving unit's `copy` rules are not changed, so its filtered history, and
its lineage, stay what they were; the arriving unit's map does not name the
file, so its lineage stays too. The directive changes three things: the
leaving unit no longer expects the file; the arriving unit accepts it as its
own; and a sync of the leaving unit carries the original's changes to the file
into the arriving unit as a patch, and does not bring the file back into the
unit it left. The full behaviour is in
[contracts/moved-directive.md](contracts/moved-directive.md).

**Rationale:** it is the one way of the three the operator was offered that
keeps both units' lineage, keeps one copy of each file (constitution 1.1.0,
principle I) and rewrites no history.

**How a sync handles it, found by reading `command_sync`:** the leaving unit's
filtered original still holds the moved file, so the merge onto the unit's
`develop`, which no longer has it, either leaves it deleted (the original did
not change it) or stops on a modify/delete conflict (it did). The sync resolves
exactly those conflicts, and only those, by keeping the file deleted, and stops
on any other as today. The patch for the arriving unit is the original's diff
of the source between the baseline and the original's head, with its path
rewritten, checked with `git apply --check` before either unit is touched.

## R7. Where the moved files land, and their tests

**Decision:** `reaper/functions/lambda_identify_zombies.py`,
`reaper/functions/lambda_terminate_zombies.py` and `reaper/functions/lambda.env`
in `csis-sandbox-terraform`; their tests in `tests/test_reaper_functions.py`,
with the AWS calls replaced by `botocore`'s Stubber (FR-004), and the module's
in `reaper/tests/`. `reaper/` is declared `new` in `sandbox-terraform.map`;
`tests/support.py`'s `MODULES` gains `reaper`.

**Rationale:** the functions sit beside the module that packages them, as the
spec's owner decision asks; Stubber is part of `botocore`, which the functions
already import, so no new test dependency is needed for them.

## R8. cloudflow's side

- `tests/test_modules.py` lists the two functions as modules it cannot import;
  the list loses them (FR-006), and `outward_references.json` is recorded
  again if they were in it.
- cloudflow has no test of a launch request today. FR-008's test calls the
  launch with a stand-in EC2 resource and holds the `TagSpecifications` it was
  given to contain the tag.
