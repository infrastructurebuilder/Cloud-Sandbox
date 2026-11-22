# Quickstart: running the live proof

The proof is a procedure, run by the agent box by box with the operator's
word at every gate: `csis-sandbox-provisioning/docs/LIVE-PROOF.md`, version
2 ([its contract](contracts/live-proof-procedure.md)). This page says how to
know it is ready and how to know it is done.

## Before it is run (your local machine, no AWS)

```sh
cd exportit/sandbox-terraform && just test && just full-test     # proof/ checked by tofu test, mocked
cd ../sandbox-provisioning && just test                         # LIVE-PROOF.md's boxes are well formed
cd ../.. && just test && just full-test
```

Expected: all pass; `tofu test` shows the proof's boot starting with the SSM
agent, containing `ansible-pull` with `spack_site_mirror=true` and the
cloudflow install, and not containing `node-image.yml`; with
`compare_with_script = true` a second instance is planned, with `false` none.

## Running it (your local machine and the head node; hours, billed)

1. `aws sts get-caller-identity` answers for the `noaa` account; if not, ask
   for the session to be refreshed.
2. Follow `LIVE-PROOF.md` from A1 to E6.

## Done when

- `site.yml` ended `failed=0`; the second apply and check mode changed
  nothing, or each change is a finding (SC-001).
- The image was `available` (SC-002).
- Every row of the "Not proved" table in `exportit/MAP.md` is marked (SC-003).
- E5 found nothing with the prefix and E6 found the VPC as it was (SC-004).
- With the flag `false`, stage D was skipped and recorded as deferred (SC-005).
