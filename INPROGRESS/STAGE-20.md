# Stage 20: sandbox-configs split by owner

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. Only if stage 19 relocates `sandbox-configs`. It is executed on
"do 20", after each **YOUR DECISION** below has been asked, one at a
time. Eleventh in the order of the remaining work ([PLAN.md](../PLAN.md)):
before stage 22, whose step 4 relocates `sandbox-configs` and needs it
split first.

## Why

`sandbox-configs` is two kinds of file with two owners (stage 6's
catalogue): 3 templates and 48 examples that show how cloudflow is used,
and 71 descriptions of one site's deployments, which are that site's.
And 23 of the 122 cannot be read by today's cloudflow, the template a new
site copies among them (no `table_name`). MAP.md's sandbox-configs
section has the details.

## Items

1. **The split.** The templates and examples go with cloudflow, under
   its `examples/configs/` (cloudflow's map gains them, `sandbox-configs`'
   loses them); the schema writer moves into cloudflow, so that the
   schema is published with the code that reads it. `sandbox-configs`
   keeps the site's files and the schema check, against cloudflow's
   published schema.

   **YOUR DECISION (the site's files):** keep them as one unit,
   `sandbox-configs`, for the IOOS deployment (default); or not relocate
   them at all, leaving them in Cloud-Sandbox for the site to keep.

2. **The 23 that cannot be read.** **YOUR DECISION:** repair what can be
   repaired, as patches (the trailing commas, the missing `table_name`
   in the template, the missing keys), and retire the rest to the attic
   with the reason (default); or leave them, recorded, for the site.

3. **`current.system` and `current.image_id`,** read by nothing, kept by
   hand: **YOUR DECISION:** replace them with what `sandbox-terraform`
   writes (stage 4 asked for an output carrying a complete cluster-
   description fragment, `table_name` included; this stage adds it)
   (default); or leave them.

4. **Tests:** the catalogue and the schema check follow the files;
   cloudflow's tests check the examples it now carries against its
   schema.

## Acceptance

The root `just test` and `just full-test` pass; every description in
either place can be read by cloudflow, or is in the attic with its
reason.
