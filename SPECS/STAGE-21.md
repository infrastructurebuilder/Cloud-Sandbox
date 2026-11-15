# Stage 21: the first boot runs the playbooks

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. Only if stage 19 relocates both `sandbox-terraform` and
`sandbox-provisioning`. Twelfth in the order of the remaining work
([PLAN.md](../PLAN.md)): written and tested before stage 22, and put
into use at stage 22's step 6, the first moment `sandbox-provisioning`
has a repository whose URL can be named.

## Why

`sandbox-terraform/main.tf` is a byte-identical copy and still renders
`init_template.tpl`, which clones `ioos/Cloud-Sandbox` and runs the old
`setup-instance.sh`. The new template, `init_template.ansible.tpl`
(stage 4, extended in stage 10), runs the playbooks with `ansible-pull`,
and needs two values `main.tf` does not pass: `provisioning_repo` and
`provisioning_version`. MAP.md calls this "the two-variable change".

## Items

1. **The change, as a patch** (`sandbox-terraform.patches/`), so that the
   copy stays its original plus written-down corrections: `main.tf`
   renders `init_template.ansible.tpl` and passes the two values;
   `variables.tf` gains them, with no default for `provisioning_repo`,
   so that a plan without it fails; `sandbox_version` stays, because the
   template still clones Cloud-Sandbox for cloudflow (its first lines).

   **YOUR DECISION (cloudflow at first boot):** keep cloning
   Cloud-Sandbox for cloudflow, as now, until cloudflow's own relocation
   gives it an installable package (default); or install cloudflow from
   its relocated repository at a tag, which needs stage 22's step 1 done
   first and a line in the template.

2. **Tests:** `test_template.py` renders the main module with the two
   values and holds the rendered user data to the template; `tofu
   validate`; a plan in an empty workspace shows the user data naming the
   repository.

3. **At stage 22, step 6:** `provisioning_repo` is the relocated
   `sandbox-provisioning`'s URL and `provisioning_version` its first tag;
   `DEPLOYMENT.md` says how to set them.

## Acceptance

The root `just test` and `just full-test` pass with the patch; a plan
without `provisioning_repo` fails with a message naming it.
