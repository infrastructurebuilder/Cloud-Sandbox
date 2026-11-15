# Stage 13: JupyterHub, decided

*Status:* planned 2026-11-14 on `feature/remaining-plans`, and executed
the same day on "do 13", on `feature/stage-13-jupyterhub`, and merged
into `develop` on 2026-11-15. The decision is under
[Decisions taken](#decisions-taken), the result under
[Outcome](#outcome). Third in the order
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

## Decisions taken

Asked on 2026-11-14: **keep it an option**, the default. `jupyterhub.yml`
stays apart from `site.yml`; the live proof (stage 15) does not apply it.

## Acceptance

`sandbox-provisioning`'s `just test` and `just full-test` pass; REMINDERS.md
loses the item; MAP.md says what was decided.

## Outcome

- **No site's settings in the role's defaults.** The server name, the
  OAuth callback, the certificate and key paths, and the two Python
  literals (the administrators and the address-to-user map, which in the
  original file are placeholders, `user1` and `user1@gmail.com`) have no
  default. The defaults say, in comments, what the original files hold.
  `jupyterhub_spawn_users` keeps its default, `[jupyter]`, the hub's own
  user: it names no person.
  - Six variables are required, not the plan's four: the plan named the
    spawn users, which have a sound default, and left out the two
    placeholder literals, which do not.
- **The role checks first** (`tasks/check.yml`, included at the top of
  `main.yml`) and refuses, naming every missing or empty one, before
  anything is installed.
- **README.md** says what a site supplies, and that it must open 443 in
  the head node's security group itself.
- **Tests:** the parity tests render the templates with the originals'
  values, now given explicitly (`support.JUPYTERHUB_ORIGINALS`), and still
  hold them to the original files byte for byte; the check is applied
  alone and refuses with nothing given, names exactly what is missing or
  blank, and passes with everything; a test holds the defaults free of
  the one site's values. The container gives test values
  (`hub.example.invalid`) and checks the hub as before.
- `sandbox-provisioning`'s `just test`: 458 tests. The root `just test`
  and `just full-test` pass (2026-11-14): every unit, all 15 extraction
  proofs, and the container test with every play checked.

## Found

**The container test had not been checking `users.yml` and
`jupyterhub.yml` since stage 7, and passed anyway.** `converge.sh` gave
`verify.yml` the list of plays as `--extra-vars "verify_plays=site users
jupyterhub"`; in that key=value form Ansible cuts the value at the first
space, so the list was `site`, and the plays that check the test user and
the hub matched no host and were skipped. Stage 7's checks were real when
it ran them, it seems with one play at a time, where a single name is
passed whole. The list is now passed as JSON, and the test fails if any
play it asked to check is skipped. With that, the full container test
checks all three again, and they pass: the test user and its groups, and
the hub up on port 8000 with nginx enabled and not started (no
certificate).

