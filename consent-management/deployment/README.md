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
where the key material lives. Setting `signingKey.enabled: false` falls back to an ephemeral
per-pod key (receipts won't verify across pods — only for throwaway local runs).

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

1. **Use .p12 Signing Key** = on.
2. **Signing Key Source** = `existing`.
3. **Existing Signing Secret** = the name from A.3 (`consent-manager-signing`).
4. **Upgrade / Install**.

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
