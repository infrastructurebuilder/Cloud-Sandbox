# Stage 19: relocate, or not

*Status:* **decided 2026-11-17, ahead of its turn: relocate all.** The
operator asked for every unit to be given a private repository on
`infrastructurebuilder` and kept as a submodule
([moving day](../../../exportit/MOVINGDAY.md)), which was done the same day.
What "What has to be true before it is asked" required was not all true
then: the live proof (stage 15) had not run, for want of an AWS account,
and stages 16 to 18 and the collection's stage 5 were not done. That is
the operator's choice, recorded here. Planned 2026-11-14 on
`feature/remaining-plans`, as a decision: at "do 19" it was to be asked,
and the answer recorded. Tenth in the order of the remaining work
([PLAN.md](../../PLAN.md)), after everything that makes the commit tree
good, as the operator said on 2026-11-13: "We might never relocate this.
We're figuring that out after we've got a good commit tree." Stages 20
to 22 follow only if the answer is to relocate.

## What has to be true before it is asked

- Stages 12 to 18 done or deliberately dropped, and collection stages 4
  and 5.
- The live proof (stage 15) run, so that what would be relocated is
  known to work.
- The parity watch on `main` (PLAN.md) current: no change on
  `origin/main` past the baseline uncarried.
- The operator's timeline: "approximately 4-5 weeks, and then actual
  migration" (2026-11-13), which this decision confirms or changes.

## The decision

**YOUR DECISION:**

- **Relocate all the units** (the order and method are in
  [MAP.md](../../../exportit/MAP.md#the-order-of-the-real-relocations)): stages
  20 to 22. Each unit gets a repository of its own on
  `infrastructurebuilder`, extracted with its history, never under
  `ioos`.
- **Relocate some:** the operator names which. MAP.md's order still
  holds for those: a unit goes after every unit it needs. The rest stay
  in Cloud-Sandbox, in their original paths, and `exportit/` keeps their
  copies or loses them (asked).
- **Do not relocate:** Cloud-Sandbox stays one repository. Then the
  question is what becomes of `exportit/`: **YOUR DECISION (then):**
  move the translations into place, replacing the originals, so that the
  repository runs on what was built here (the Ansible, the OpenTofu, the
  collection), one stage per unit; or keep `exportit/` as it is, a
  record and a test bed.

## What the answer changes

| Answer | What follows |
| --- | --- |
| All | stages 20, 21, 22 as planned |
| Some | stage 22 for the named units; 20 only if `sandbox-configs` is among them; 21 only if `sandbox-terraform` and `sandbox-provisioning` both are |
| None, move into place | a new set of stages, planned then |
| None, keep | the parity watch ends; PLAN.md and REMINDERS.md say so |

## The answer

**Relocate all**, given on 2026-11-17 by asking for moving day rather
than at "do 19". Of "what the answer changes": stages 20 and 21 stay
planned, 20 now after `sandbox-configs` moved whole; stage 22's
repositories exist, and what is left of it is the deletion of the
original paths.

## Acceptance

The answer is in this file, in PLAN.md, and in REMINDERS.md, whose item
closes.
