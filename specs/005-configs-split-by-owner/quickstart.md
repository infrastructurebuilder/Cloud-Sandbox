# Quickstart: checking the split

All on your local machine; no AWS.

```sh
cd exportit/sandbox-configs && just test     # every file as catalogued; retired only under attic/
cd ../cloudflow && just test                 # the schema equals the code; every example read by it
cd ../sandbox-terraform && just test         # tofu test: cluster_description's keys; the fixture
cd ../.. && just test                        # configs-schema-check; the tools tests across units
just full-test                               # lineage of both units; the sync rehearsal with a moved file
```

Expected: SC-001 (every description readable, in either place, or retired
with its reason); SC-002 (both acceptance tests, lineage among them).
