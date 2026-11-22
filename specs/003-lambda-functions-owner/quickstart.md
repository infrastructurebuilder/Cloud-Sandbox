# Quickstart: proving spec 003 works

Every step runs on your local machine, in the Cloud-Sandbox checkout with its
units checked out (`just init`). No step reaches an AWS account.

## 1. The functions and their tests, in their new unit

```sh
cd exportit/sandbox-terraform
just test
```

Expected: the reaper's function tests pass (a node past its limit
terminated; one within it left; one already gone reported invalid; a failure
reported and the rest still handled; the report written to the bucket
`REPORT_BUCKET` names), and the module's `tofu test` runs pass:

- `enable_reaper = false`: no resource planned;
- `enable_reaper = true`: two functions on `python3.13`, their schedule, and
  two roles; the terminating role's `ec2:TerminateInstances` limited to the
  launch tag, and no other EC2 action ([contracts/reaper-module.md](contracts/reaper-module.md)).

## 2. The tag, in cloudflow

```sh
cd exportit/cloudflow
just test
```

Expected: a launch request carries `csis:launched-by = cloudflow` beside the
cluster description's tags; the import test no longer lists the two functions.

## 3. The move, held by Cloud-Sandbox

```sh
just test
```

Expected: the export tool's tests pass, among them the `moved` directive's
on throw-away repositories ([contracts/moved-directive.md](contracts/moved-directive.md));
`cloudflow.map`'s three `moved` lines are read without a problem; the
functions are in `csis-sandbox-terraform` and nowhere in cloudflow.

## 4. Lineage, and a sync of a moved file

```sh
just full-test
```

Expected: `export-lineage` passes for all fifteen units, cloudflow and
`csis-sandbox-terraform` among them; the sync rehearsal passes its scenarios,
the new one among them: a change to `lambda_terminate_zombies.py` in a
made-up original lands in `csis-sandbox-terraform`'s `reaper/functions/`, on
its sync branch, and does not come back into cloudflow.
