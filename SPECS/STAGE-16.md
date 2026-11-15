# Stage 16: a build cache for RHEL 10, and pushing to it without scripts

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. It is executed on "do 16", after each **YOUR DECISION** below
has been asked, one at a time. Sixth in the order of the remaining work
([PLAN.md](../PLAN.md)): **it needs the live proof (stage 15) first**,
because it needs a real build to push, and the access the proof shows
the node has.

## Why

- **The site's build cache is of no use to today's sandbox** (found
  while planning stage 15): its index holds 103 packages, all `rhel8`,
  built with oneAPI 2023.1.0, Intel 2021.9.0 and gcc 11.2.1, in the
  layout of Spack before 1.0. A RHEL 10 head node with Spack v1.2.0
  builds everything from source, for hours, every time.
- **Pushing to it is three scripts in `sandbox-ops`,** run by hand:
  `spack-update-mirror.sh` (a list of RHEL 8 specs, pushed one by one),
  `spack-stack-update-mirror.sh` and `spack-stack-mirror-create.sh` (the
  same for UFS's spack-stack), with `scp-secret.sh` to copy the private
  signing key from the operator's machine. The collection's
  `spack_buildcache_push` does the pushing, and reports only what the
  mirror gained.
- **The head node may not be allowed to write there:** its IAM role
  (`sandbox-terraform/main.tf` L52-L59) allows objects in
  `ioos-coastalsb-*puts`, not in `ioos-cloud-sandbox`, the bucket the
  mirror is in. The live proof will show what it can read.

## Items

1. **A playbook, `push-build-cache.yml`,** in `sandbox-provisioning`:
   `spack_buildcache_push` for the environment, signed with the key
   `spack_key_fingerprint` names, to `spack_mirror`, with
   `update_index: true`. It is run by hand after a build, not by
   `site.yml`. The private key is still put in place by hand
   (`scp-secret.sh` stays in `sandbox-ops`): it is never in the
   repository or a variable.

   **YOUR DECISION (where the new cache goes):** a new prefix beside the
   old one, for example `public/spack/mirror-rhel10/`, so that the old
   cache stays for any RHEL 8 node still running (default); or the same
   prefix, replacing it.

   **YOUR DECISION (who may write):** the head node, with a policy for
   that prefix added to the IAM role in `sandbox-terraform` (default: the
   build and the push are on the same machine), or the operator's own
   credentials, passed for the one run.

2. **The first push,** from the live proof's node if it is kept, or from
   the next head node built: what `spack_env` installed, with check mode
   first to list what will go.

3. **Using it:** with a cache that holds this sandbox's packages, a build
   can install from it. **YOUR DECISION (the default for new builds):**
   leave `spack_cache_only: -1` and `spack_site_mirror: false` (default:
   a build keeps compiling everything until the cache has been shown to
   work); or `spack_cache_only: 0` and `spack_site_mirror: true`, so a
   build takes what the cache has and compiles the rest.

4. **The three scripts go:** `spack-update-mirror.sh`,
   `spack-stack-update-mirror.sh`, `spack-stack-mirror-create.sh` move to
   `sandbox-provisioning/legacy/`, replaced, or, for the two spack-stack
   ones, are left until stage 18 decides spack-stack; `sandbox-ops`'
   records follow.

5. **Tests:** parity (the playbook's mirror, key and environment are the
   variables the scripts read); the playbook's syntax and lint; its push
   proved against a mirror in a directory, in the container, unsigned.
   The push to S3 itself is proved by doing it, in item 2.

## Out of scope

The UFS spack-stack's cache (stage 18).

## Acceptance

The cache at the chosen prefix lists this sandbox's packages for RHEL
10; a second push reports nothing new; a build with the cache turned on
installs from it.
