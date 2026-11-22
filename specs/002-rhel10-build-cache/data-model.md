# Data model: A build cache for RHEL 10

## The bucket (`csis-sandbox-terraform/build-cache/`)

| Variable | Type | Default |
| --- | --- | --- |
| `bucket_name` | string | `csis-sandbox-rhel10-build-cache` |
| `region` | string | `us-east-2` |
| `project_tag` | string | `CSIS-Sandbox` |

| Resource | Settings |
| --- | --- |
| `aws_s3_bucket` | the name; tags `Name`, `Project` |
| `aws_s3_bucket_public_access_block` | all four `true` |
| `aws_s3_bucket_ownership_controls` | `BucketOwnerEnforced` |
| `aws_s3_bucket_server_side_encryption_configuration` | `AES256` |

Output: `mirror_url` = `s3://<bucket_name>/`.

## The head node's permission (main module)

| Variable | Type | Default | Effect |
| --- | --- | --- | --- |
| `build_cache_bucket` | string | `null` | when set, `aws_iam_role_policy.build_cache`: `s3:ListBucket` on the bucket; `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on `bucket/*` |

## The playbook's inputs (`push-build-cache.yml`)

| Variable | Default | The script's |
| --- | --- | --- |
| `spack_environment_dir` | the role's | the environment it pushed |
| `spack_mirror` | `group_vars/all.yml` (FR-004 changes it) | `SPACK_MIRROR` |
| `spack_key_fingerprint` | `22DC0120…F525C05B06DCA266` | `KEY=F525C05B06DCA266` |

## The defaults, before and after

| Variable | Until SC-003 holds | After (this spec's last step) |
| --- | --- | --- |
| `spack_cache_only` | `-1` (`--no-cache`) | `0` (cache if present) |
| `spack_site_mirror` | `false` | `true` |
| `spack_mirror` | `s3://ioos-cloud-sandbox/public/spack/mirror` | `s3://<bucket_name>/` |

## The cache's states

```text
empty ─▶ first push (packages for RHEL 10, signed) ─▶ second push: nothing new
      ─▶ a build with the cache on installs from it (SC-003) ─▶ defaults switched ─▶ a build with the defaults installs from it (SC-004)
interrupted push ─▶ run again ─▶ only what is missing pushed
```
