# sandbox-ops

The tools an operator of a Cloud Sandbox runs by hand: keeping the Spack
binary mirror, clearing old model output, changing the head node's
instance, the weekly job report. They are what was still in use of
everything left in `scripts/`, `misc/` and `jupyterhub/` once
provisioning had taken its part. The rest, files that something newer
has replaced and files that no longer apply, does not travel: it stays
with the original repository, in the umbrella's `attic/`.

## This is a copy

This directory is a copy of the files of `scripts/`, `misc/` and
`jupyterhub/` in the Cloud-Sandbox repository that `sandbox-provisioning`
does not take, made there. Every file is byte-identical to its original.
[../MAP.md](../MAP.md#sandbox-ops) describes how this project would be
moved to a repository of its own. Do not edit the copied files here:
change the original and run `just export sandbox-ops` at the repository
root.

What is new: this README, `LICENSE`, `Justfile`, `CATALOGUE.tsv` and
`tests/`.

## The catalogue

Each of the 92 files left over was read and marked, with the evidence:
its original path, where it went, its status, its group, what superseded
it, one sentence of evidence citing the lines it rests on, and a note
when it holds personal data.

| Status | Means | Where | Files |
| --- | --- | --- | ---: |
| in use | still makes sense on today's sandbox (RHEL 10, Spack, oneAPI, EFS, Prefect), even if nothing calls it | here, in `bin/` and `keys/` | 16 |
| superseded | what it did is done by something else, named in the catalogue: mostly a role of `sandbox-provisioning` | the umbrella's `attic/superseded/<original path>` | 26 |
| dead | refers to what no longer exists (Slurm and munge, RHEL 7 and 8, old Spack trees), or is a one-off note | the umbrella's `attic/dead/<original path>` | 50 |

[CATALOGUE.tsv](CATALOGUE.tsv) here holds the 16 rows of the tools in
use; `cloud-sandbox/attic/CATALOGUE.tsv` holds the other 76.

At first the attic was copied here, so that every file was accounted
for. On 2026-11-13 the operator decided that the attic does not travel
with the code: it stays with the original repository, which the
umbrella `cloud-sandbox` is. The files are still accounted for, by that
unit's map.

## The tools in use

| Tool | What it is for |
| --- | --- |
| `bin/spack-update-mirror.sh` | Push the built Spack packages to the S3 binary mirror. Its list of specs (gcc 11.2.1, Intel 2021.9.0, oneAPI 2023.1.0) is RHEL 8's and needs updating |
| `bin/spack-pubkey.sh` | Trust the mirror's key and add the S3 mirror, by hand; the setup leaves these steps commented out |
| `bin/scp-secret.sh` | Copy the mirror's private signing key from the local machine to the head node. The file holds only the key's path |
| `bin/spack-stack-mirror-create.sh`, `bin/spack-stack-update-mirror.sh` | The same for the spack-stack v2.0 tree that UFS Coastal uses |
| `keys/22DC0120263F329AE5C9DA08F525C05B06DCA266.pub` | The public half of the mirror's signing key; its user id carries a person's work address |
| `bin/scrub_nosofs.sh`, `bin/scrub_liveocean.sh` | Delete old plots, forecasts and forcing under `/com`. `scrub_liveocean.sh` does not parse: an `if` at L88 is never closed |
| `bin/change-instance-type.sh`, `bin/disableHT.sh`, `bin/newamised.sh` | Change the head node's instance type; take hyperthreads offline; swap an old image id for a new one in cluster descriptions. Each has values to edit before use |
| `bin/weekly_summary.nu` | A Nushell report of the past week's jobs from the DynamoDB table cloudflow writes; needs `nu`, which provisioning does not install |
| `bin/add-ufs-setup.sh`, `bin/ufs-envars.sh` | Add spack-stack for UFS Coastal to a built head node. `add-ufs-setup.sh` calls a function that `funcs-setup-instance.sh` no longer has (L27), so it fails as written |
| `bin/batch_spack_uninstall.sh`, `bin/spack.find` | Two Spack one-liners |

## Where it reaches outside its directory

The tools came from one directory and some still expect its neighbours:

- `bin/spack-update-mirror.sh` and `bin/spack-pubkey.sh` source
  `environment-vars.sh`, and `bin/add-ufs-setup.sh` sources
  `funcs-setup-instance.sh` and runs `./create_image.sh`. Those are now
  `sandbox-provisioning`'s, in its `legacy/`; its `group_vars/all.yml`
  holds the same values.

## Working on it

You need `just`, bash 4 or later and `shellcheck`. Nothing is run.

```sh
just init        # says which bash and shellcheck will be used
just test        # the catalogue matches the files; scripts parse as recorded; shellcheck counts as recorded
just full-test   # the same: there is nothing slower to check
just record      # write tests/shellcheck.counts again, after reviewing a change
```

The scripts are copies, so their shellcheck findings are counted, not
fixed, under the same rule as the model recipes. `tests/templates.txt`
names the one script that does not parse, so that the test notices if it
is ever fixed.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
