# The attic

These are the files of Cloud-Sandbox's `scripts/` and `misc/` that were
read, one by one, and found to be no longer in use. Each sits under its
status and its original path:

| Status | What it means | Where | Files |
| --- | --- | --- | --- |
| superseded | what it did is now done by something else, named in the catalogue: mostly a role of `sandbox-provisioning` | `superseded/<original path>` | 26 |
| dead | refers to what no longer exists (Slurm and munge, RHEL 7 and 8, old Spack trees), or is a one-off note | `dead/<original path>` | 50 |

[CATALOGUE.tsv](CATALOGUE.tsv) has one row per file: where it came from,
its status, what superseded it, the evidence for the judgement, and
whether it holds anything sensitive.

## Why it is here

The attic does not travel with the code. The tools still in use went to
`sandbox-ops`; these stay with the original repository, which this
umbrella is (the operator's decision, 2026-11-13). They are kept so that
nothing is lost, not because anything needs them: nothing in any unit
refers to them.

Two files hold personal data and are marked so in the catalogue:
`dead/scripts/system/patrick.gitconfig` (a named person's name and
email) and `superseded/scripts/system/.tcshrc` (one user's home paths).
They were in the original repository already; keeping them here adds
nothing to it, but they should not be copied anywhere else.

## Checking it

`just test` at the umbrella runs `tests/check_attic.py`: every file has
exactly one row, every row names a file that is here, and each file sits
where its status says.
