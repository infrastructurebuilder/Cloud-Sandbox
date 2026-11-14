# Stage 15: the live proof on AWS

*Status:* planned 2026-11-14 (first written as stage 12, renumbered the
same day so that the stage numbers follow the order of the work in
[PLAN.md](../PLAN.md)); nothing executed and nothing created on AWS. It
is executed on "do 15", after stages 12 to 14 and each **YOUR DECISION**
below has been asked, one at a time. **The first thing done at "do 15" is
to check the AWS session** and, if it is not fresh, to ask for it to be
refreshed before anything else.

## Why

Everything built in stages 3 to 11 is proved on the local machine and in
an AlmaLinux 10 container. What only a real head node can show is still
marked **not proved** in [MAP.md](../exportit/MAP.md#how-it-was-tested-and-what-was-not):

| Not proved | Why only a head node shows it |
| --- | --- |
| `efa_driver`, `fsx_lustre_client` | kernel modules, built for the running kernel |
| `hpc_tuning` | kernel settings and a `tuned` profile |
| `node-image.yml` | an EBS snapshot and a machine image, through `amazon.aws` |
| Building `spack_environment` | the container only concretizes: fake installs cannot stand in for the ESMF and PETSc build; a real build takes hours |
| Module files with `refresh_modules: when_needed` (stage 11) | only a real build writes real module files |
| The site mirror's list (stage 11, off by default) | needs the site's bucket and key |
| Anything on RHEL, or on AWS | the container is AlmaLinux |
| The first-boot script | needs a real EFS volume, and cloud-init |
| Whether the playbooks leave the same node the script does | needs a second node, built the old way |

[sandbox-provisioning/docs/LIVE-PROOF.md](../exportit/sandbox-provisioning/docs/LIVE-PROOF.md)
is the procedure, written in stage 3 and never run. It is out of date in
ways that would stop it partway (below), so this stage first brings it up
to date and then runs it.

## What exists, and what is out of date

- **LIVE-PROOF.md** (2026-11-12, stages A to E, boxes in the repository's
  form) assumes:
  - the repository's original `terraform/` and Terraform 1.5.7. Since
    stage 4 and the OpenTofu change, the unit is
    `exportit/sandbox-terraform` with OpenTofu 1.13.9, whose
    `versions.tofu` refuses any other version;
  - the playbooks copied to the node by `tar` and run with
    `ansible-playbook site.yml`. Since stage 10, `site.yml` needs the
    collection `infrastructurebuilder.csis_spack` installed first, which
    the page never does: **its box B2 would fail at the `spack` role.**
    The first-boot template now fetches the playbooks, installs
    `requirements.yml`, then runs `ansible-pull`;
  - nothing about the site mirror's list, check mode, the comparison of
    Spack's configuration, or `refresh_modules`.
- **The first boot:** `sandbox-terraform/main.tf` (a copy, unchanged)
  still renders `init_template.tpl`, which clones `ioos/Cloud-Sandbox`
  (reading only) and runs the old `setup-instance.sh`. The new template,
  `init_template.ansible.tpl`, needs two values `main.tf` does not pass
  yet: `provisioning_repo` (a git URL whose root is the playbooks) and
  `provisioning_version`. `sandbox-provisioning` has no repository of
  its own.
- **The defaults would make the build very slow.** `instance_type`
  defaults to `t3.medium`, two processors; `spack_jobs` is then 1. The
  script's `spack_cache_only: -1` (`--no-cache`) compiles everything.
- **The site's build cache is not usable by this Spack** (looked at
  2026-11-14): the index at
  `https://ioos-cloud-sandbox.s3.amazonaws.com/public/spack/mirror/`
  holds 103 specs, all `rhel8`/`x86_64`, built with oneAPI 2023.1.0,
  Intel 2021.9.0 and gcc 11.2.1, in the layout of Spack before 1.0. Its
  key, at `spack_key_url`, is the one `spack_key_fingerprint` names. So
  the site mirror's list can be proved (the key trusted by fingerprint,
  the mirror added), but the mirror will not supply anything to a RHEL 10
  build.
- **Tools on the local machine:** the AWS CLI and OpenTofu 1.13.9 are
  installed; `sandbox-terraform`'s `just init` puts OpenTofu in `.tofu/`.

## Items

1. **The session first.** At "do 15", before anything else:
   `aws sts get-caller-identity`. If it fails, stop and ask for the
   session to be refreshed. The build runs for hours; the session must
   last, or be refreshed between stages.

2. **Bring LIVE-PROOF.md up to date, as its version 2**, before running
   it. Every box keeps the repository's rules (numbered and versioned, a
   check as the last line of its box, a time estimate on any box over
   thirty seconds, every choice a bold **YOUR DECISION** with its
   default, "your local machine" and "the head node" named in every
   step). What changes:
   - **Stage A** uses a working copy of `exportit/sandbox-terraform` and
     `tofu` (its `.tofu/1.13.9/tofu`), in a workspace of its own, with a
     settings file of its own (`nameprefix`, `name_tag`, and decision 4's
     instance type). The gate stays: the plan must say `0 to change, 0 to
     destroy`, or stop.
   - **Stage B** depends on decision 2. Either way it ends with exactly
     what the first-boot template does: the checkout, `ansible-galaxy
     collection install -r requirements.yml`, then the plays.
   - **Stage B gains** a check-mode pass after the second apply (as the
     container test does), and the comparison of Spack's configuration
     with `tests/container/expected-spack-config.json`
     (`compare-spack-config.py`), which on RHEL may show differences the
     container did not; each is a finding, not a failure.
   - **Stage B gains** the module-file check of stage 11: after the
     second apply, every module file under the environment's root has
     the modification time it had after the first.
   - **Stage C** installs `requirements.yml`, which now holds both
     collections.
   - **"What to bring back"** names every log and dump the stage needs
     to settle the rows above.

3. **Run it.** The boxes of the new page, in order, stopping at any
   result the page does not predict.

   **YOUR DECISION (who runs the boxes):** I run them (default): the
   local machine's boxes in my shell, the head node's over `ssh`, reading
   each result before the next, and stopping to ask at every gate, every
   decision box, and every box that creates, changes or removes
   something on AWS (`tofu apply`, `tofu destroy`, `node-image.yml`, the
   image and snapshot removal). Or you run them from the page and bring
   back the logs.

4. **YOUR DECISION (the head node's instance type for the build):** a
   compute-optimised type with sixteen processors or more, chosen when
   the settings file is written (default: `spack_jobs` is then fifteen,
   and the build takes a few hours instead of a day; the instance can be
   made smaller afterwards, as `DEPLOYMENT.md` describes); or the settings
   file's own type, which for the module's default `t3.medium` means one
   build job.

5. **YOUR DECISION (how the playbooks reach the node):**
   - **By hand, as the first boot would** (default): the node boots with
     the old template, its last step removed, as stage 3's page did. The
     unit is then copied to the node as a git repository, and the three
     commands of `init_template.ansible.tpl` are run there by hand, with
     the repository's path as `provisioning_repo`. Proves the commands and
     the playbooks; does not prove cloud-init running the new template.
   - **By the real first boot:** the working copy's `main.tf` renders
     `init_template.ansible.tpl` with the two values, and
     `provisioning_repo` is a private repository made for the proof, on
     `infrastructurebuilder`, holding what `just export-filter
     sandbox-provisioning` extracts. Proves the first-boot script end to
     end. Creates a repository (yours to approve, and to delete
     afterwards) and needs the node to be able to clone it (a deploy key,
     or the repository public for the proof).

6. **YOUR DECISION (the Spack build):** as the script does,
   `spack_cache_only: -1`, compiling everything (default: it is what the
   sandbox does today, and the only way to prove the build); or
   `spack_cache_only: 0`, taking from Spack's public binary cache what it
   has, which is faster but proves less.

7. **YOUR DECISION (the site mirror's list):** apply it on the proof
   node, `spack_site_mirror: true` (default: it is the only place it can
   be proved, and with decision 6's default the build reads no binary
   cache, so the mirror cannot change what is built); or leave it off.

8. **YOUR DECISION (stage D, a second node built the old way):** skip it
   (default: the container's comparison already holds Spack's
   configuration to the shell's, and a second build doubles the cost); or
   run it, which is the only direct evidence for the last row of the
   table above.

9. **YOUR DECISION (a compute node from the image):** out of scope
   (default: it needs a cluster description, the DynamoDB table, and
   cloudflow, and is a proof of its own); or include one: start one
   compute node from the image with cloudflow and run the smallest model
   job a site has.

10. **Removing everything.** **YOUR DECISION:** remove the node, the EFS
    volume, the image and its snapshot at the end (default), each step
    asked first; or keep the node for a look, billed while it stands.

11. **What stages 12 to 14 add to the proof.** They come first so that
    the head node proves them too:
    - stage 12 (the old settings in the login user's scope): the node is
      built fresh and has none, so the stage's own container test is its
      proof; nothing is added here;
    - stage 13 (JupyterHub), if it makes JupyterHub part of the build:
      `jupyterhub.yml`, or `site.yml` with it, applied and checked as the
      container test checks it, the hub answering on its port;
    - stage 14 (the scrub timer): the timer enabled, its next run listed
      by `systemctl list-timers`, and one run started by hand against a
      `/com` that holds a dated directory old enough to go and one that
      is not.

12. **Records.** In `exportit/MAP.md`, each row of the table above
    marked proved, with the date and what was seen, or left "not
    proved" with the reason; every finding under "Found while testing";
    `LIVE-PROOF.md`'s header says when it was run. `REMINDERS.md` loses
    the live-proof item. The logs themselves are not committed: they
    hold the node's addresses and the account's identifiers. Their
    summary goes in this file's outcome.

## Out of scope

- Changing the repository's original `terraform/`, or `main.tf` in
  `sandbox-terraform`: the working copy is edited, never the unit.
- Running a model, unless decision 9 says so.
- Fixing what the proof finds. A finding becomes a stage of its own, or
  a change to the collection, released as a new version.

## Acceptance

- The session checked first; the plan's gate held (`0 to change, 0 to
  destroy`) before anything was created.
- `site.yml` applied to a RHEL 10 head node with `failed=0`; applied
  again; check mode after it; every task that changed on the second run
  or in check mode listed as a finding.
- `node-image.yml` made an image that AWS reports `available`.
- Everything the proof created is removed, or kept by decision, and the
  account shows nothing else left behind.
- MAP.md says, for each row above, what is now proved.
