# Contract: the `moved` mapping directive

**Where**: `exportit/<unit>.map` in Cloud-Sandbox, read by
`exportit/tools/export.py`.

## Form

```text
moved <source> <unit> <destination>
```

- `<source>`: a path of the original repository, a single file (not a
  directory).
- `<unit>`: the name of another unit (another map's name).
- `<destination>`: the file's path in that unit's repository.

It is written in the map of the unit the file **leaves**, which keeps the
`copy` rule that took it.

## Rules the check enforces

A problem, reported by `check`, `check --baselines`, `lineage` and `sync`:

1. `<source>` is not taken by a `copy` rule of the map it is written in.
2. `<unit>` is not a unit, or is the map's own unit.
3. `<destination>` is a file the arriving unit's map copies, or two `moved`
   lines give the same destination in one unit.
4. A `copy` rule of any other unit also takes `<source>`.
5. The same `<source>` is moved twice.

## What it changes

| Where | Without `moved` | With `moved` |
| --- | --- | --- |
| The leaving unit's expected files (`check`, `copy`) | include the file | do not include it |
| The arriving unit's files | the file is "neither copied nor declared new" | the file is accepted as the unit's own (as if declared `new`) |
| `lineage` of either unit | unchanged | unchanged: each unit is filtered with its `copy` rules, as it was made |
| `sync <leaving unit>` | carries the file's changes into the leaving unit | see below |
| `sync <arriving unit>` | does not concern the file | does not concern the file |

## `sync` of the leaving unit

Before anything is changed:

1. For each moved source that the original changed between the leaving unit's
   baseline and the original's head, the patch is the original's diff of that
   source, with its path rewritten to the destination.
2. The arriving unit must be checked out under `exportit/`, clean, and on its
   `develop`; each patch must pass `git apply --check` on it. If any of this
   fails, the sync stops and neither unit changes.

Then:

3. The leaving unit is merged as today, onto `feature/<branch>`. A
   modify/delete conflict on a moved file's copied path is resolved by keeping
   the file deleted; any other conflict stops the sync and leaves the unit as it
   was.
4. In the arriving unit, `feature/<branch>` is made from its `develop`, the
   patches are applied, and one commit records them, its message naming the
   upstream commits that changed each file (subject and author) and the range.
5. The leaving unit's baseline moves to the original's head; the arriving
   unit's does not.
6. The report names each moved file carried, and the arriving unit's branch.

Nothing is pushed.

## Cloudflow's lines (this spec)

```text
moved cloudflow/cluster/lambda_identify_zombies.py  sandbox-terraform  reaper/functions/lambda_identify_zombies.py
moved cloudflow/cluster/lambda_terminate_zombies.py sandbox-terraform  reaper/functions/lambda_terminate_zombies.py
moved cloudflow/cluster/lambda.env                  sandbox-terraform  reaper/functions/lambda.env
```
