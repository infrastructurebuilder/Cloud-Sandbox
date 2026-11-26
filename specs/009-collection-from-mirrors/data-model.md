# Data model: The playbooks take the collection's 0.0.3 and its `from_mirrors` again

## The requirement (`csis-sandbox-provisioning`'s `requirements.yml`)

| Collection | Before | After |
| --- | --- | --- |
| `infrastructurebuilder.csis_spack` | `>=0.0.1,<0.1.0` | `>=0.0.3,<0.1.0` |
| `amazon.aws` | `>=9.0.0,<10.0.0` | unchanged |

## The three steps

Each replaces the scripts' `spack buildcache keys --install --trust`.

| Role, list | Script line | Since spec 002 | After |
| --- | --- | --- | --- |
| `spack`, its first list | `funcs-setup-instance.sh` L700 | `kind: command`, `args: [buildcache, keys, --install, --trust, --yes-to-all]`, `changes: never` | `kind: gpg_key`, `from_mirrors: true` |
| `spack`, the site mirror's list | `spack-pubkey.sh` L19 | the same | the same as above |
| `intel_oneapi`, its list | `funcs-setup-instance.sh` L959 | the same | the same as above |

What a run reports, by step:

| | `command` (since spec 002) | `from_mirrors` (0.0.3) |
| --- | --- | --- |
| A key newly trusted | no change reported | `changed`, the fingerprint in `trusted` |
| Nothing new | no change | no change |
| Check mode | not run, no change | not run, `previewed: false` |
| Spack does not trust a key afterwards | not noticed | fails, naming it |

## The release

| Unit | Version | Recorded in |
| --- | --- | --- |
| `csis-sandbox-provisioning` | 0.0.5 (`pyproject.toml`, `uv.lock`, the tag) | `csis-cloud-sandbox`'s `units.toml` |
