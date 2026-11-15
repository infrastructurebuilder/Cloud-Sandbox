# Stage 14: clearing old model output on a timer

*Status:* **set aside, 2026-11-15, by the operator: "We are not going to
do this at this time."** Moved to `INPROGRESS/ATTIC/`, with nothing
executed. The two scrub scripts stay in `sandbox-ops/bin/`, run by hand,
as they were. The plan is kept as written, below, in case it is taken
up: it would need a stage number of its own again, and a place in
[PLAN.md](../../PLAN.md)'s order (it needs nothing first, and was to come
before the live proof so that the proof covers it). Planned 2026-11-14,
as the fourth item of the remaining work.

## Why

Two tools in `sandbox-ops`, run by hand, delete old model output from
`/com` so that the EFS volume does not fill:

- `bin/scrub_nosofs.sh` (67 lines): under `/com/nos/plots`, plot
  directories older than 1 day; under `/com/nos`, forecast directories
  (`<model>ofs.<YYYYMMDDHH>`) older than 7; under `/com/nos-noaa`,
  verification directories older than 0. Each `find` runs twice, once to
  list and once to delete.
- `bin/scrub_liveocean.sh` (120 lines): the same for `/com/liveocean`
  and `/com/liveocean-uw`, and old history files (`ocean_his_00NN.nc`)
  by age. **It does not parse**: an `if` at L88 is never closed (stage 7),
  so it has never run as it is.

Nothing schedules either. A role can declare the same rules as data, run
them on a timer, and say what it deleted.

## Items

1. **A role, `output_scrub`, in `sandbox-provisioning`,** with the rules
   as a variable: each rule a directory, a pattern (the scripts' own
   regular expressions, kept), a kind (`directory` or `file`), and an age
   in days, with the scripts' `-daystart` meaning (whole days, counted
   from midnight). The role installs one small program that applies the
   rules, a systemd service that runs it, and a timer.
   - The program **lists before it deletes**, as the scripts do, and logs
     every path it removes to the journal; a dry-run switch only lists.
   - A directory that does not exist is skipped, as `scrub_liveocean.sh`
     does with `if [ -d ... ]` and `scrub_nosofs.sh` does not (its `cd`
     fails and its `find` then runs in the wrong directory: the role does
     not carry that).
   - The rules of both scripts are the defaults, each with `# Replaces
     scrub_<model>.sh L<n>`. `scrub_liveocean.sh`'s rules are carried as
     its author evidently meant them, and its parse error is recorded:
     the traceability names the lines, `not_carried.yml` the unclosed
     `if`.
   - Both scripts move from `sandbox-ops/bin/` to
     `sandbox-provisioning/legacy/`, as `spack-pubkey.sh` did in stage
     11, and `sandbox-ops`' catalogue, map, README and shellcheck record
     follow.

   **YOUR DECISION (the program):** a short Python program the role
   installs (default: rules as JSON, ages computed in one place, testable
   with pytest against a temporary directory tree); or `find` commands
   rendered from the rules into a shell script, closer to the originals.

2. **YOUR DECISION (on by default?):** the timer installed but not
   enabled unless `output_scrub_enabled` is true (default: deleting
   output is not something a build should start doing on its own); or
   enabled on every head node, daily.

3. **YOUR DECISION (when, if enabled):** daily at a fixed time in UTC
   (default 06:00, after the overnight cycles), with `Persistent=true` so
   a run missed while the node was stopped happens at the next start; or
   another time the operator gives.

4. **Tests.**
   - Unit: each rule applied to a temporary tree with directories and
     files dated by `touch -d`: what is old enough goes, what is not
     stays, what does not match stays, a missing directory is skipped,
     the dry run deletes nothing.
   - Parity: each default rule is the script's directory, pattern and age.
   - Traceability: every line of both scripts that does something is
     replaced or listed.
   - Container: the role applied twice; the second run changes nothing;
     the timer and service are present and, as decided, enabled or not;
     one run started by hand against a prepared `/com` removes exactly
     what it should.

## Out of scope

Copying output to S3 before deleting it. The scripts assume the plots
"have been sent to S3"; nothing here checks.

## Acceptance

The root `just test` and `just full-test` pass, and the container's
hand-started run removes exactly the old directories and files.
