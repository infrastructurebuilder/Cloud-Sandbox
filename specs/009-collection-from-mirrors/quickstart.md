# Quickstart: checking that the playbooks take the collection's 0.0.3 and its `from_mirrors`

All on your local machine; nothing touches AWS.

## 1. The collection moves to 0.0.3

```sh
cd exportit/sandbox-provisioning
grep -A1 csis_spack requirements.yml          # version: ">=0.0.3,<0.1.0"
just init
grep -m1 '"version"' .collections/ansible_collections/infrastructurebuilder/csis_spack/MANIFEST.json
```

Expected: `"version": "0.0.3"`, where it was 0.0.2 before.

## 2. The steps and their tests

```sh
grep -n "from_mirrors\|yes-to-all" roles/spack/tasks/main.yml roles/intel_oneapi/tasks/main.yml
just test
```

Expected: three `from_mirrors: true` steps and no `--yes-to-all`; `just test`
passes (parity carries the scripts' command as `from_mirrors`, the floor
held at 0.0.3).

## 3. The container: a mirror that publishes a key

```sh
just full-test
```

Expected, among its lines: the signed push to a second mirror in a directory,
the key taken off, then `site.yml --tags spack,intel_oneapi` with that mirror:
the key trusted with no prompt, and a second apply changing nothing.

## 4. The root

```sh
cd ../.. && just test && just full-test
```

Expected: both pass; `units.toml` names sandbox-provisioning 0.0.5 once it is
tagged.

## 5. On a real node (spec 004)

Spec 004's head node, the next built, records that its first boot ended
`failed=0`, installed from the RHEL 10 cache, and ran the three `from_mirrors`
steps with no prompt (this spec's FR-007).
