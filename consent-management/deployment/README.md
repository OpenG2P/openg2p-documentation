---
description: >-
  Deploying the Consent Manager — Docker image, Helm chart, Keycloak
  provisioning, and how the service scales horizontally.
---

# Deployment

The Consent Manager ships as a Docker image and a Helm chart, following the same conventions as
the other OpenG2P services (e.g. g2p-bridge).

## Docker

The image is built from `docker/consent-manager-api/Dockerfile` with the **repository root** as
the build context. It installs `openg2p-fastapi-common` from git, installs the local `backend/`
source, then on start runs migrations and serves with gunicorn + uvicorn workers:

```
python3 -m openg2p_consent_manager.main migrate
gunicorn openg2p_consent_manager.main:app --worker-class uvicorn.workers.UvicornWorker ...
```

`migrate` is idempotent (`CREATE TABLE IF NOT EXISTS`), so concurrent replicas starting together
are safe. Published as `openg2p/openg2p-consent-manager` by `.github/workflows/docker-build.yml`,
tagged from the branch/tag name.

## Helm chart

Chart: `deployment/charts/openg2p-consent-manager/`. Dependencies (from the OpenG2P helm repo):

| Dependency | Purpose |
| --- | --- |
| `common` | Shared template helpers (names, labels, image, capabilities). |
| `postgres-init` | Creates the database, user, and password Secret on the commons Postgres. |
| `keycloak-init` | Provisions the Consent Manager Keycloak client and admin role (see below). |

Rendered resources for the API component (`templates/api/`):

* **Deployment** — a `postgres-checker` init container waits for the DB; the app container mounts
  the `.p12` signing key from a Secret and exposes `/ping` for startup/liveness/readiness probes.
* **Service** (`ClusterIP`) and an Istio **VirtualService** routing
  `/<openapiRootPath>/` to the service.
* **HorizontalPodAutoscaler** — opt-in (off by default; a single replica suffices). Enable it for
  high consent-verification load (1–10 replicas, **CPU-only** target at 80% — memory-based
  autoscaling is deliberately off, as a Python process's memory baseline would make it scale up
  and never come back down).
* **CronJob** — runs `python -m openg2p_consent_manager.expire` on a schedule (default every 15
  min) so expiry runs once per tick regardless of replica count.

Configuration is supplied through `values.yaml` as `CONSENT_MANAGER_*` env vars (database from
`postgres-init`'s Secret, Keycloak issuer/JWKS, admin role, `.p12` path) — see
`backend/.env.example` for the full variable list. The data controller / module is a per-partner
attribute set at onboarding, not a chart value.

### Publishing &amp; Rancher catalog

The `.github/workflows/helm-publish.yml` workflow (mirroring the other OpenG2P services) packages
the chart and pushes it to the **central `openg2p/openg2p-helm`** repo's `gh-pages` branch, then
merges it into that repo's `rancher/index.yaml`. The chart carries the
`openg2p.org/add-to-rancher` annotation plus a `questions.yaml` form and `app-readme.md`, so it
surfaces in the **Rancher catalog**. Publishing runs only from the `OpenG2P` org and requires the
`OPENG2P_BOT_GITHUB_PAT` secret; chart versions are derived from the branch
(`develop` → `0.0.0-develop.<run>`, `N.N.N` → frozen release).

### Signing key (`.p12`)

The CM receipt-signing private key is a **PKCS#12** keystore. However it is supplied, the `.p12`
ends up in a Kubernetes Secret and is **mounted as a file** on the pod (Secret-as-volume) at
`consentManagerApi.signingKey.mountPath`; the keystore **password** is a key in a Secret, injected
as the `CONSENT_MANAGER_CM_SIGNING_P12_PASSWORD` env var. The app opens the file using the password
— file-as-mount, password-as-secret, the standard pattern. The signing algorithm is auto-detected
from the key type, and only the public half is published at `/.well-known/jwks.json`.

**The key id (`kid`) is a label you set, _not_ something read from the `.p12`.** It is configured
separately (chart **Signing Key ID** → `global.consentSigningKid` → `CONSENT_MANAGER_CM_SIGNING_KID`,
default `cm-2025-01`) and is stamped into the JWKS and every receipt so verifiers know which key
signed. When you bring your own `.p12`, give it your own `kid`, and **change the `kid` on every key
rotation** — that lets the old and new public keys coexist in the JWKS under different `kid`s so
in-flight receipts keep verifying. (Reusing one `kid` across different keys breaks verification.)

Signing is **on by default** using a **bundled demo key**, so a fresh install signs receipts with a
fixed, consistent key out of the box — no setup needed for testing. The `consentManagerApi.signingKey.mode`
chooses the source (all selectable in the Rancher form's **Signing** group, no command line):

* **`demo`** (default) — uses the demo `.p12` shipped in the chart (`files/cm_signing_demo.p12`).
  Fixed and consistent across pods/restarts. **Testing only — the key and its password are public;
  replace it for production.**
* **`existing`** (production) — reference a Secret you create via **Rancher → Storage → Secrets →
  Create → Opaque**: upload the `.p12` as key **`cm_signing.p12`** and add a **`password`** key (the
  Secret UI handles the binary upload — no base64, no CLI). Set **Existing Signing Secret** to its
  name. Key material stays out of the Helm release.
* **`inline`** — paste the **base64 of the `.p12`** and the **password** into the form; the chart
  creates the Secret. Fully in-form, but the material then lives in the Helm release values.

All three produce the same mounted-file + password-secret the pod consumes — the only difference is
where the key material lives. **Receipts are always signed; the form only asks for the source
(`mode`)** — there is no on/off toggle. (An advanced values-only flag, `signingKey.enabled: false`,
falls back to an ephemeral per-pod key for a throwaway local pod; it is not exposed in Rancher and
should be left on for any real deployment.)

#### Replacing the demo key for production (Rancher, step by step)

The demo key ships **only so a fresh install works out of the box for testing**. It is public —
anyone can forge "valid" receipts with it — so every real deployment **must** replace it. Entirely
through the Rancher UI, no command line:

**Step A — create the signing Secret** (Rancher → cluster → **Storage → Secrets → Create**):

1. **Namespace**: the one the Consent Manager is (or will be) installed in.
2. **Type**: `Opaque`.
3. **Name**: e.g. `consent-manager-signing`.
4. Under **Data**, add exactly these two entries — **the key names must match exactly**:
   * `cm_signing.p12` → click the upload/file control and **upload your `.p12`** (Rancher handles
     the binary; this is the step the app form cannot do).
   * `password` → type the `.p12` password.
5. **Create**.

**Step B — point the app at it** (Rancher → **Apps → consent-manager → ⋮ → Edit/Upgrade**, or
**Install** for a new deployment) → **Signing** group:

1. **Signing Key Source** = `existing`.
2. **Existing Signing Secret** = the name from A.3 (`consent-manager-signing`).
3. **Upgrade / Install**.

**Verify**: open a pod's logs — you should see `Loaded CM signing key from PKCS#12 keystore
/app/secrets/cm_signing.p12` (not the ephemeral-key warning), and `/.well-known/jwks.json` serves
your key's `kid`.

> **Gotchas** (each will make it silently fail): the Secret must exist **before** the upgrade; it
> must be in the **same namespace** as the app; and the data keys must be named **exactly**
> `cm_signing.p12` and `password`. To **rotate** later: update the Secret, advertise a new `kid`
> (Signing Key ID in the form), and redeploy so pods reload — keep the old key valid during the
> rolling restart.

> **Alternative (`inline`)**: if you'd rather not pre-create a Secret, set **Signing Key Source =
> `inline`** and paste the **base64 of the `.p12`** + the password into the form; the chart creates
> the Secret. The trade-off is that the key + password then live in the Helm release values.

## Uninstall / cleanup

`deployment/scripts/uninstall-consent-manager.sh` cleanly removes a release and everything it
touched — including the Postgres database and role inside the shared commons Postgres, which
survive `helm uninstall`. It mirrors the g2p-bridge uninstaller: stop in-flight hook Jobs, `helm
uninstall`, delete leftover Jobs/Secrets/ConfigMaps, drop the DB + role via `kubectl exec` into
commons-postgresql, then remove PVCs/PVs. Always `--dry-run` first.

```bash
deployment/scripts/uninstall-consent-manager.sh --namespace trial --dry-run
deployment/scripts/uninstall-consent-manager.sh --namespace trial          # with confirmation
```

It preserves other modules' databases and the Keycloak client by default; pass
`--drop-signing-secret` to also remove the `.p12` Secret and `--keep-pvs` to retain volumes.

## Keycloak provisioning

With `keycloak-init.enabled` (default `true`), the chart provisions, in the configured realm:

* a confidential client **`consent-manager`** (service account enabled) — keycloak-init
  auto-creates a Kubernetes Secret named `consent-manager` holding its `client_secret`;
* the **`CONSENT_MANAGER_ADMIN`** client role required by the partner/policy admin endpoints;
* role mappings granting `CONSENT_MANAGER_ADMIN` to the `admin` user and to the client's own
  service account (for onboarding automation).

The service itself **validates tokens via JWKS only** — it consumes no client secret. The
generated `client_secret` exists for *callers*: the registry/PEP obtaining a client-credentials
token to call `/validate`, and admin automation obtaining a token that carries the admin role.

## Horizontal scalability

The service is designed to scale out under a high rate of consent verification:

* **Stateless** — no per-pod state; any replica serves any request, no session affinity. Scale by
  adding pods/workers behind the load balancer (HPA does this automatically).
* **Shared Postgres** with framework connection pooling. Size `max_connections ≳ pods × workers ×
  pool_size + headroom`.
* **No in-process scheduler** — expiry is the external CronJob above, so it fires exactly once per
  tick regardless of replica count; the hot path also lazily expires on read.
* **Hot-path cache** — partner keys and policies are cached per pod with a short TTL, keeping
  `/validate` cheap under load (each pod's cache is independent — safe across replicas).
* **Idempotent `/validate`** — re-validating the same consent object (`jti`) returns the same
  decision instead of minting duplicates.

## Database

The chart targets the shared commons PostgreSQL. `postgres-init` creates a per-release database
and user and stores the password in a Secret that the Deployment references via
`secretKeyRef`. Tables are created at startup by the `migrate` step.

## Sanity tests (in-cluster)

The chart includes a **sanity suite** that runs **automatically on every install/upgrade** as a
Helm `post-install,post-upgrade` Job — so a broken image or misconfiguration is flagged the moment
you Install/Upgrade/Redeploy in Rancher, **no command line needed**.

### Where to see the results

Read the **`<release>-sanity` Job pod's logs** — in Rancher: **Workloads → Jobs →
`<release>-sanity` → the pod → Logs** (or `kubectl -n <ns> logs job/<release>-sanity`). The tail
summarises it, e.g. `7 passed` (all green) or `5 passed, 2 failed` with the failing assertions
above. The finished pod is kept until the next install/upgrade so the logs stay viewable.

### Pass/fail behaviour

**If sanity runs, it gates the deploy.** The Job is a Helm hook, so a failing run **fails the Job
and therefore the release** — Helm marks the release failed and Rancher shows the app in an error
state. So a deploy is only "successful" when sanity passes. There is no separate "fail the deploy"
switch — failing the job *is* failing the deploy.

**Leave sanity on everywhere — including production.** The default smoke+contract level **creates no
data** and is safe in every environment, so there's no data-related reason to disable it. The
disable (`Run Sanity Tests` / `sanity.enabled = false`) is a **break-glass** for one narrow case:
the sanity **image itself** can't run (it wasn't mirrored, or a bad build crashes on startup), which
blocks the gated deploy at the **pod level** — and the report-only flag can't rescue that, because
the container never reaches the tests. Then `sanity.enabled=false` (don't create the Job) lets you
ship the app and fix the test infra separately. (Data is created only by the e2e — its own opt-in.)

Two caveats:
* The gate **flags** a bad deploy rather than reverting it — a post-upgrade hook runs **after** the
  new pods are rolled out, so the failed pods keep running until you act. For automatic rollback,
  the upgrade must be **atomic** (`helm upgrade --atomic`), which Rancher does not do by default.
* An **advanced, values-only** escape hatch exists for report-only behaviour
  (`sanity.failOnError: false` → the Job exits 0 on failure, deploy succeeds, read the logs). It is
  **not** in the Rancher form, because running sanity is meant to gate.

Two levels — **both run by default** when sanity is enabled; turn the e2e off individually if you
don't want test data:

* **Smoke + contract** (always, when sanity is on) — `/ping`, `/.well-known/jwks.json`, OpenAPI
  served, and that auth is enforced (protected endpoints return 401 without a token). Needs no token
  and **creates no data**. Catches a broken/booting-wrong image immediately.
* **Full e2e** (`Run Full E2E` / `sanity.runE2e`, **default on**) — onboards a `TEST_SANITY_*`
  partner, signs a consent object, and exercises a real `POST /validate` (permit + the
  `signature_invalid` and `scope_exceeds_policy` denials), then verifies the CM's receipt signature
  against its JWKS. It obtains a client-credentials token from Keycloak (the `consent-manager`
  client) and **suspends** the test partner afterwards (there is no delete endpoint). **Turn this
  off for production** to avoid creating test data; smoke + contract still run and gate. Because it
  runs by default and gates, **Keycloak must be reachable at deploy time** for the token — if it
  isn't, the e2e fails the deploy (turn the e2e off, or fix Keycloak).

The suite is **independent of which `.p12` the deployment uses**: it signs consent objects with its
own throwaway key (onboarded on the test partner), and it verifies the CM's receipt against the
**live** `/.well-known/jwks.json` — handling EdDSA/ES256/RS256 — so it works the same whether the
CM runs the demo key or your production key. It never needs the CM's private key or password.

Form options (**Sanity** group): `Run Sanity Tests (gates the deploy)` (`sanity.enabled`) and
`Run Full E2E` (`sanity.runE2e`). The suite ships as a separate image
(`openg2p/openg2p-consent-manager-sanity`) built by the same CI workflow.

> A **Postman collection** for hands-on/manual API exploration is maintained separately (for
> integrators trying the API by hand); it is complementary to — not a replacement for — this
> automated in-cluster gate.
