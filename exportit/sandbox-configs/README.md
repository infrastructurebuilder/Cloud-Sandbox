# sandbox-configs

The job and cluster descriptions that cloudflow runs with on a Cloud
Sandbox. A *job description* says what to run: the model, the kind of
job, the dates, where the install and the inputs are. A *cluster
description* says where to run it: AWS (instance type and count, the
image, the network) or the local machine. Both are JSON files, given to
cloudflow by path:

```sh
python workflows/workflow_main.py ../cluster.configs/IOOS/cbofs.cluster ../job.configs/OFS/cbofs.fcst
```

## This is a copy

This directory is a copy of `job.configs/` and `cluster.configs/` from
the Cloud-Sandbox repository, made there. Every file is here,
byte-identical, under the same directory names, so the paths in
cloudflow's documentation still hold. By the operator's decision the
copies keep the identifiers they carry (image ids, security groups,
subnets, key names): they are one site's live configuration, kept with
the templates and examples that any site can start from.
[../MAP.md](../MAP.md#sandbox-configs) describes how this project would
be moved to a repository of its own. Do not edit the copied files here:
change the original and run `just export sandbox-configs` at the
repository root.

What is new: this README, `LICENSE`, `Justfile`, `pyproject.toml`,
`uv.lock`, `.python-version`, `schema/` and `tests/`.

## The schema

[schema/jobs.json](schema/jobs.json) and
[schema/clusters.json](schema/clusters.json) list every key that
cloudflow reads, for each kind of job and each platform, with the line
of cloudflow's code that reads it (`cloudflow/job/ROMSForecast.py:135`
and so on, in Cloud-Sandbox). A key is:

- **required** when cloudflow reads it as `cfDict['KEY']` and would stop
  without it;
- **optional** when it is read with a default (`.get()`, a `try`, or
  `if 'KEY' in cfDict`);
- **conditional** when it is needed only for some values of other keys
  (`EXPNAME`, for a LiveOcean hindcast).

A job description picks its class with `MODEL` and `JOBTYPE`; 17
`JOBTYPE`s exist. A cluster description picks `AWS` or `Local` with
`platform`. The schema is written from cloudflow's code by
`just configs-schema` at the Cloud-Sandbox root, and a test there
fails when the code and the schema part.

## What the files are

`tests/catalogue.json` records, for each of the 130 files, its kind,
its role and whether cloudflow can read it. The role follows rules in
[tests/descriptions.py](tests/descriptions.py):

| Role | Rule | Files |
| --- | --- | ---: |
| template | the name says `template`, or the values are placeholders (`/pathway/to/...`) | 3 |
| site | names an AWS resource (`ami-`, `sg-`, `subnet-`) or a path in one person's directory (`/save/patrick/...`) | 71 |
| example | any other description: it runs as it is on a sandbox laid out the default way | 48 |
| helper, note, pointer | a script, a note, or a file that holds the name of another description | 8 |

Of the 122 descriptions (78 jobs, 44 clusters), cloudflow can read 99.
Of the other 23, 3 are not valid JSON, 19 lack a key that cloudflow
requires, and one, the experiment template, names a `JOBTYPE` that
does not exist, as a template should. The catalogue lists each with
the reason.

## Where the cluster values come from

| Key | Comes from |
| --- | --- |
| `region` | `sandbox-terraform`: `var.preferred_region` |
| `key_name` | `sandbox-terraform`: `var.key_name`, output `key_name` |
| `sg_ids` | `sandbox-terraform`: output `aws_security_groups` (three groups) |
| `subnet_id` | `sandbox-terraform`: output `aws_subnet` |
| `placement_group` | `sandbox-terraform`: output `aws_placement_group` |
| `image_id` | `sandbox-provisioning`: `node-image.yml`, run on the head node after it is provisioned |
| `table_name` | the operator: a DynamoDB table made by hand, named here |
| `platform`, `nodeType`, `nodeCount`, `tags`, `vm_retry_delay`, `vm_max_retries`, `PPN` | the person who writes the description |

Terraform writes its five values into `deployment_info.txt`;
`cluster.configs/IOOS/current.system` is a copy of such a fragment,
with the table name added, kept by hand. Nothing reads it.

## Working on it

You need `just` and `uv`. No AWS account is needed: nothing here is
checked against AWS.

```sh
just init        # test environment
just test        # every file is as catalogued; the schema names a line for every key
just full-test   # the same: nothing slower to check
just record      # write tests/catalogue.json again, after reviewing a change
```

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
