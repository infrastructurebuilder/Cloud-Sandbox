# sandbox-provisioning

Ansible playbooks that turn a bare RHEL 10 instance, with the sandbox's
EFS volume mounted, into a Cloud Sandbox head node, and then turn that
head node into the machine image its compute nodes boot from.

They do what `scripts/setup-instance.sh` does in the Cloud-Sandbox
repository, step for step. The difference is in how: the playbooks can
be applied again to a node that is already built, one step can be
applied on its own, and the first step that fails stops the run.

| Playbook | What it does |
| --- | --- |
| [site.yml](site.yml) | Builds the software stack: twelve roles, one per function of the script, in the script's order |
| [node-image.yml](node-image.yml) | Snapshots the head node's root volume and registers the compute-node image |

## This is a translation, kept beside its original

This directory was made inside the Cloud-Sandbox repository. The
scripts it replaces are in [legacy/](legacy/), unchanged, and every
task carries a comment that names the lines it replaces:

```yaml
# Replaces funcs-setup-instance.sh L229
- name: Create the prefect group
```

The tests hold the two together. They fail if a task names no lines,
if a line of the scripts that does something is neither replaced nor
listed with a reason in [tests/not_carried.yml](tests/not_carried.yml),
or if a version, a package list or a file's text differs from what the
script computes. [../MAP.md](../MAP.md) has the function-to-role
table, the places where the script's behaviour is an accident and what
was done about each, and what has not been proved.

## How it is applied

**At first boot, by the node to itself.**
[first-boot/init_template.tpl](first-boot/init_template.tpl) is the
head node's first-boot script. After it has mounted the EFS volume it
runs:

```sh
ansible-pull --url <this repository> --checkout <version> \
    --directory /opt/sandbox-provisioning \
    --inventory inventories/local/hosts.yml site.yml
```

`ansible-pull` clones the playbooks and applies them to the machine it
runs on. `site.yml` needs nothing but the `ansible-core` package that
RHEL 10 ships.

**Later, on the head node.** Logged in to the head node:

```sh
cd /opt/sandbox-provisioning
sudo ansible-playbook site.yml --tags efa_driver
```

**Later, from your local machine.** The second inventory finds the
running head node by its tags:

```sh
ansible-playbook -i inventories/aws/aws_ec2.yml site.yml --tags efa_driver
```

Every role has a tag of its own name. The scripts that were copies of
`setup-instance.sh` with steps removed become one command each:

| Script | Now |
| --- | --- |
| `update-efa.sh` | `--tags efa_driver` |
| `setup-python-deps.sh` | `--tags python_user_env` |
| `rhel10-setup.sh` | `--skip-tags prefect_server,hpc_tuning`, then `node-image.yml` |

`rhel10-setup.sh` also differs in its last lines (it does not stop the
Prefect server for the image and runs `spack clean` without `--all`);
those differences are not carried.

## The roles

| Order | Role | Function in the script | In the container test |
| ---: | --- | --- | --- |
| 1 | `sandbox_paths` | `setup_paths` | yes |
| 2 | `user_shell` | `setup_aliases` | yes |
| 3 | `base_system` | `setup_environment` | yes |
| 4 | `prefect_server` | `setup_prefect-server` | yes |
| 5 | `mpi_ssh` | `setup_ssh_mpi` | yes |
| 6 | `efa_driver` | `install_efa_driver` | no: builds a kernel module |
| 7 | `fsx_lustre_client` | `install_fsx_driver` | no: installs a kernel module |
| 8 | `python_user_env` | `install_python_modules_user` | yes |
| 9 | `spack` | `install_spack` | yes |
| 10 | `intel_oneapi` | `install_intel_oneapi_dnf` | yes |
| 11 | `spack_environment` | `create_spack-environment`, `build_spack-environment` | no: hours of compiling |
| 12 | `hpc_tuning` | `configure_optimizations` | no: changes kernel settings |

The versions are in [group_vars/all.yml](group_vars/all.yml), which is
`environment-vars.sh` as data. Settings that belong to one role are in
that role's `defaults/main.yml`.

## Working on it

You need `just`, `uv` and `shellcheck`; `full-test` also needs Docker.

```sh
just init        # tool environment, and the amazon.aws collection
just test        # syntax, ansible-lint, shellcheck, and the comparisons with the scripts
just full-test   # also applies eight roles to an AlmaLinux 10 container, twice
```

`full-test` builds a container that stands in for a freshly booted
node, runs the same `ansible-pull` command as the first-boot script,
runs it again, and fails unless the second run changes nothing and the
result is what the roles should leave
([tests/container/](tests/container/)).

## What has not been proved

No playbook here has been applied to a real head node, on RHEL, or
on AWS. The four roles marked "no" above and `node-image.yml` have
only been checked for syntax, lint and agreement with the scripts'
text.
[docs/LIVE-PROOF.md](docs/LIVE-PROOF.md) is the procedure for proving
them on AWS; it costs money and has itself not been run.

## One deliberate correction: the Prefect server

On 2026-11-12, the Prefect server that the script's command installs
does not start: pip picks FastAPI 0.162, and Prefect 3.7.8's server
fails at import with any FastAPI from 0.155 on, then restarts every
five seconds. The `prefect_server` role therefore installs Prefect
with `fastapi<0.155` (`prefect_server_extra_requirements` in
[roles/prefect_server/defaults/main.yml](roles/prefect_server/defaults/main.yml)).
It is the one place where the playbook does not do what the script
does; set the variable to `[]` to install exactly what the script
installs.

## Licence

BSD 3-Clause; see [LICENSE](LICENSE).
