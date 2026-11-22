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

## 2. On AWS (operator's word at every step; hours of a head node)

1. `build-cache/`: plan (four additions), apply.
2. A head node, as spec 001's stages A and B, with `build_cache_bucket` set.
3. The signing key copied over SSM and trusted; `push-build-cache.yml` in
   check mode (lists), then for real (pushes), then again (`changed=0`).
4. `spack buildcache list` against the mirror shows the environment's packages
   for `linux-rhel10`.
5. A second environment directory installed with `spack_cache_only: 0`: the
   install log shows packages fetched from the cache (SC-003).
6. The defaults switched (merged first); a third install with the defaults
   alone fetches from the cache (SC-004).
7. The key removed from the node; the node removed as spec 001's stage E; the
   bucket stays.
