# Contract: `push-build-cache.yml`

**Where**: `csis-sandbox-provisioning`, beside `site.yml`; run by hand on a
built head node: `ansible-playbook -i inventories/local/hosts.yml
push-build-cache.yml`.

## Behaviour

| Run | Result |
| --- | --- |
| check mode (`--check`) | lists the environment's packages the mirror lacks; pushes nothing; `changed` if any are missing |
| first run | pushes the missing packages, signed with `spack_key_fingerprint`, rebuilds the index; `changed` |
| second run | `ok`, `changed=0` |
| after an interruption | pushes only what is still missing |
| the key is not in Spack's keyring | fails before pushing, naming the fingerprint |

## Never

- handles a private key (the module does not; the key is put in place by hand);
- runs from `site.yml`;
- writes to `ioos-cloud-sandbox`.

# Contract: `build-cache/` (csis-sandbox-terraform)

A root module of its own: `tofu init`, `tofu plan`, `tofu apply` in
`build-cache/`, on the operator's word. Plan in an empty workspace adds four
resources and changes nothing. Its removal is a step asked for by name, never
part of a head node's removal.
