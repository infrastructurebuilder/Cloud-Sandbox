# Quickstart: checking that the first boot puts the site's descriptions on the node

## 1. Without AWS (your local machine)

```sh
cd exportit/sandbox-terraform && just test && just full-test
cd ../.. && just test && just full-test
```

Expected: `tests/configs.tftest.hcl` plans no `configs_secret` policy unset
and one on the ARN when set, and fails as the contract says for a missing
version or secret, or an HTTPS URL; the template renders the configs block in
order with no key in it, and spec 007's user data unchanged when unset;
`tests/test_links.py` reaches the site's file through `../job.configs/` from
the cloudflow link and through `Cloud-Sandbox/job.configs/`.

## 2. The documents (your local machine)

```sh
grep -rln -E "\.\./(job|cluster)\.configs/" exportit --include='*.md' --include='README*'
grep -rln -E "configs_secret_arn|deploy key" <the places FR-008 lists>
```

Expected: every guide found carries the note of FR-006 (research R5); every
place FR-008 lists names the key (SC-005).

## 3. On AWS (the operator's word at every step)

1. A new tag of `csis-sandbox-configs` (research R7).
2. The deploy key: made by the operator (`ssh-keygen -t ed25519`), its public
   half added to `csis-sandbox-configs` as read-only, its private half in a new
   Secrets Manager secret (`DEPLOYMENT.md`, the boxes).
3. A head node, as spec 001's stages A and B, with `configs_repo`,
   `configs_version` and `configs_secret_arn` set.
4. On the node: `/save/$RUNUSER/sandbox-configs` at the tag; from
   `/save/$RUNUSER/Cloud-Sandbox/cloudflow`, `ls ../job.configs/` and a Python
   `open('../cluster.configs/<a file>')` reach the site's files; cloudflow's
   `git status` is clean (SC-001, SC-004).
5. A search of the node for the key's text finds nothing (SC-003).
6. The node removed as spec 001's stage E; the secret and the deploy key stay
   unless the operator says otherwise.
