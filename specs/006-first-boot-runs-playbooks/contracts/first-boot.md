# Contract: the first boot's inputs and order

**Where**: `csis-sandbox-terraform`'s `init_template.ansible.tpl`, rendered by
`main.tf` through `templatefile()` into `local.user_data`.

## Inputs

Exactly these template variables, and no other (a test compares the
template's placeholders with what `main.tf` passes):

| Name | From |
| --- | --- |
| `efs_name` | `aws_efs_file_system.main_efs.dns_name` |
| `ami_name` | `"${var.name_tag}-${random_pet.ami_id.id}"` |
| `aws_region` | `var.preferred_region` |
| `project` | `var.project_tag` |
| `provisioning_repo`, `provisioning_version` | the variables of the same names |
| `cloudflow_repo`, `cloudflow_version` | the variables of the same names |

## Order, as the rendered script runs it

1. `git` and `ansible-core` installed; the EFS volume mounted (as today).
2. cloudflow cloned: `git clone --quiet --branch "<cloudflow_version>"
   "<cloudflow_repo>" /save/$RUNUSER/cloudflow`, as `$RUNUSER`; on failure,
   `Fetching cloudflow FAILED` in `~/setup.log` and exit 1. Then the link
   `/save/$RUNUSER/Cloud-Sandbox/cloudflow` → `…/cloudflow/src/cloudflow`.
3. The playbooks cloned, their `requirements.yml` installed (as today).
4. `ansible-pull … site.yml` (as today).
5. cloudflow installed: `python3 -m pip install --user --no-deps --editable
   /save/$RUNUSER/cloudflow`, as `$RUNUSER`; on failure, `Installing cloudflow
   FAILED` and exit 1.
6. `node-image.yml` (as today).

## Guarantees

- No URL in the rendered script names `ioos/Cloud-Sandbox` (FR-002).
- No credential, key or token is in the rendered script or put on the node
  (FR-003): both clones are anonymous HTTPS.
- A clone or install that fails stops the boot before any image is made.
