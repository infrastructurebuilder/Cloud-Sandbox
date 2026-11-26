# Quickstart: checking the RHEL 10 build cache

## 1. Without AWS (your local machine)

```sh
cd exportit/sandbox-terraform && just test && just full-test        # build-cache/ validated and tofu-tested, mocked
cd ../sandbox-provisioning && just test && just full-test         # parity, lint, the container push to a directory
cd ../sandbox-ops && just test                                    # the catalogue's superseded_by
cd ../.. && just test && just full-test
```

Expected: the container's push reports `changed` the first time and
`changed=0` the second; `tofu test` plans four resources for `build-cache/`
and, with `build_cache_bucket` set, one scoped policy on the head node's role.

## 2. On AWS (operator's word at every step; about an hour of a head node)

As run on 2026-11-24 and 25 (the spec's outcome):

1. `build-cache/`: plan (four additions), apply.
2. A head node, as spec 001's stages A and B, with `build_cache_bucket` set.
3. The signing key's private half, from the team's Keybase folder, copied to
   the node as a file through a Session Manager tunnel and trusted with
   `spack gpg trust --yes-to-all`, then the file removed;
   `push-build-cache.yml` in check mode (lists), then for real (pushes), then
   again (`changed=0`).
4. `spack buildcache list --allarch` with the cache added shows the
   environment's packages for `linux-rhel10`; their manifests verify with the
   key.
5. A build from the cache: an environment from the same `spack.yaml` with an
   install tree of its own (`config:install_tree:root`), installed with the
   cache on, fetches the packages and builds none (SC-003). A second
   environment in the node's own install tree proves nothing: its packages are
   found installed.
6. The defaults switched (merged and tagged first); the signing key taken off
   the node (`spack gpg untrust --signing`); the node replaced with its EFS
   volume, so that Spack's store is empty; its first boot with the defaults
   alone fetches the packages and builds none (SC-004).
7. The node removed as spec 001's stage E; the bucket stays.
