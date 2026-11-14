# Stage 13: JupyterHub, decided

*Status:* planned 2026-11-14 on `feature/remaining-plans`; nothing
executed. It is a decision first: at "do 13" the **YOUR DECISION** below
is asked, and only then is the work it leads to done. Third in the order
of the remaining work ([PLAN.md](../PLAN.md)): it depends on nothing,
and it comes before the live proof (stage 15) so that the proof covers
what is decided.

## Why

Put aside on 2026-11-13 ([REMINDERS.md](../exportit/REMINDERS.md)).
Stage 7 found that nothing ever installed JupyterHub: both install
scripts were broken and neither was called. Its `jupyterhub` role is the
first install that works, in the container, and is applied by
`jupyterhub.yml`, not by `site.yml`. What it carries from the scripts is
one site's configuration:

- Google sign-in (`GoogleOAuthenticator`), with the callback
  `https://jupyterhub.rpsgroup.com/hub/oauth_callback`;
- nginx in front, with the certificate and key
  `/etc/ssl/star_ioos_us.crt` and `.key`, which nothing puts there; the
  role starts nginx only when they exist;
- a list of users the hub may spawn for (`jupyterhub_spawn_users`).

`sandbox-terraform`'s security groups open SSH and NFS only: nothing can
reach the hub's port or nginx's from outside.

## The decision

**YOUR DECISION:**

- **Keep it an option, as now** (default): `jupyterhub.yml` for a site
  that wants it. The work is to say so plainly, and to make the option
  complete enough to take up: the role's defaults lose the one site's
  callback URL and certificate paths (they become required variables,
  with the role refusing to run without them), and the README says what
  a site must supply (its OAuth application, its certificate, its
  users) and that the security group must be opened by the site.
- **Make it part of every build:** the same, and `site.yml` imports the
  role after the others, `sandbox-terraform` gains a variable that opens
  443 to a list of addresses, and the live proof applies it.
- **Remove it:** the role, `jupyterhub.yml`, their tests and the stage 7
  parity tests for them go; the scripts stay in `legacy/` and are listed
  as not carried, with the reason.

## Work, with either of the first two

1. Required variables, checked by the role first:
   `jupyterhub_oauth_callback_url`, `jupyterhub_ssl_certificate`,
   `jupyterhub_ssl_certificate_key`, `jupyterhub_spawn_users`. The parity
   test, which renders the configuration with the scripts' values, passes
   those values in.
2. The container test passes test values and checks the hub as it does
   now.
3. With "every build": the security group's variable, its test in
   `sandbox-terraform`, and the hub's port in the live proof's checks.

## Acceptance

`sandbox-provisioning`'s `just test` and `just full-test` pass; REMINDERS.md
loses the item; MAP.md says what was decided.
