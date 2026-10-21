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

### API audiences (one chart, one image, a Deployment per audience)

Following the platform's 4-API pattern, the **one** chart runs a separate Deployment + Service +
VirtualService per API audience (same image, selected by `CONSENT_MANAGER_API_AUDIENCE`):

| Deployment | Audience | Auth | Hosts |
| --- | --- | --- | --- |
| `<release>-api` (`templates/api/`) | **staff** | Keycloak (staff realm; `CONSENT_MANAGER_ADMIN` + `CONSENT_MANAGER_APPROVER`) | Access Log, consent approvals, partner portal API |
| `<release>-partner-api` (`templates/extra-api/`) | **partner** | **none** — callers (registries, the Composite) reach it in-cluster over Istio mTLS; partner-signed consent objects are verified against Partner Management keys (`jti` replay-guarded) | the PDP `/validate`, consent status, receipts, `/.well-known/jwks.json` (mints receipts → mounts the `.p12` signing key). In cluster only, except the JWKS ([below](#what-is-reachable-from-outside)) |
| `<release>-bene-api` | **beneficiary** | Keycloak (beneficiary realm) | `/my/*` + origination — **scaffolded, `enabled: false`** |

`extraApis[]` entries are merged over `consentManagerApi`, so each only states its differences
(audience, auth, signing, hostname). Only the **partner-api** mounts the signing key.

Rendered resources per audience:

* **Deployment** — a `postgres-checker` init container waits for the DB; the app container exposes
  `/ping` for startup/liveness/readiness probes. The partner-api additionally mounts the `.p12`
  signing key from a Secret.
* **Service** (`ClusterIP`) and an Istio **VirtualService** routing
  `/<openapiRootPath>/` on that audience's hostname to the service — for the partner-api only the
  paths below.
* **HorizontalPodAutoscaler** — opt-in (off by default; a single replica suffices). Enable it for
  high consent-verification load (1–10 replicas, **CPU-only** target at 80% — memory-based
  autoscaling is deliberately off, as a Python process's memory baseline would make it scale up
  and never come back down).
* **CronJob** — runs `python -m openg2p_consent_manager.expire` on a schedule (default every 15
  min) so expiry runs once per tick regardless of replica count.

Configuration is supplied through `values.yaml` as `CONSENT_MANAGER_*` env vars (database from
`postgres-init`'s Secret, Keycloak issuer/JWKS, admin role, `.p12` path) — see
`backend/.env.example` for the full variable list. There is no data controller chart value: each
partner policy in Partner Management names its controller, and the registry names its controller on
each `/validate` call (registry chart value `global.consentDataController`).

### What is reachable from outside

Every VirtualService uses the `internal` gateway, which is reachable from outside the cluster like
the Composite. The partner-api has no login (`/validate` trusts its in-cluster callers), so its
VirtualService routes **only an allow-list of paths** on `consent-manager-partner.<baseDomain>`
(prefix `/api/consent-manager-partner`); any other path gets a `404` at the gateway. Registries
and the Composite call the partner-api at its in-cluster Service (`http://<release>-partner-api`),
as does the sanity suite.

| Value | Default | Routed |
| --- | --- | --- |
| `partnerApi.publicPaths` | `[/.well-known/jwks.json]` | The CM's public keys: departments on other clusters check consent tokens with them, partners check their consent record |
| `partnerApi.exposeReceiptStatus` | `false` | `GET /consent/v1/receipts/{jti}/status` only (not the receipts themselves). Turn on at the Exchange only when a department sets **Token Status Check** to `always`. Rancher: **Expose Token Status Endpoint** (Exchange group, exchange role) |

### Partner Management

Partners, their keys and their access policies are read from Partner Management
([how](../design/partner-management-integration.md)).

| Value (`global.*`) | Default | |
| --- | --- | --- |
| `partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | PM partner API (keys and policies) → `CONSENT_MANAGER_PARTNER_MGMT_API_URL`. Empty = nothing can be fetched; every check fails closed |
| `partnerPolicyCache.ttlSeconds` | `60` | `CONSENT_MANAGER_PARTNER_POLICY_CACHE_TTL_SECONDS` — how long a fetched policy is reused (also capped by PM's `max-age`); an approved policy change applies within this time |
| `partnerPolicyCache.hardTtlSeconds` | `21600` | `CONSENT_MANAGER_PARTNER_POLICY_HARD_TTL_SECONDS` — while PM is down, the last fetched policy is used this long; then requests are denied `policy_unavailable` |
| `partnerPolicyCache.negativeTtlSeconds` | `30` | `CONSENT_MANAGER_PARTNER_POLICY_NEGATIVE_TTL_SECONDS` — how long "no policy" (PM `404`) is remembered |
| `partnerPolicyCache.fetchTimeoutSeconds` | `3` | `CONSENT_MANAGER_PARTNER_POLICY_FETCH_TIMEOUT_SECONDS` — timeout of one call to PM |
| `partnerManagementUiUrl` | `https://partner-management.<baseDomain>` | **Partner Management UI URL** in Rancher: PM's staff UI, linked from the CM console as **Partners & policies**. Empty = no link |
| `partnerManagementAdminApiUrl`, `pmSeedClientId` | `http://commons-services-pm-staff-portal-api`, `commons-services-staff-portal` | Used only by the sanity e2e to seed its test partner in PM (below) |

What these times mean for policy changes and PM outages: [caching](../design/partner-management-integration.md#caching).

**Changing them:** `ttlSeconds` and `hardTtlSeconds` are in the Rancher form (**Partner Management** group: **Partner Policy Cache TTL**, **Partner Policy Hard TTL**). The hard TTL is a trade-off during a PM outage: a revoked partner can still get through for up to that long; shorter stops it sooner but refuses everyone sooner. The others: **Edit YAML** on the release, `global.partnerPolicyCache.*`. Installed through Commons Services, set them under `global.partnerPolicyCache` in its values; the CM picks them up on upgrade.

Partner keys are cached the same way, with settings that have no chart value of their own; to change one, add it under `consentManagerApi.envVars` in **Edit YAML**:

| Environment variable | Default | |
| --- | --- | --- |
| `CONSENT_MANAGER_PARTNER_KEY_CACHE_TTL_SECONDS` | `300` | Reuse a fetched key this long |
| `CONSENT_MANAGER_PARTNER_KEY_HARD_TTL_SECONDS` | `21600` | While PM is down, use the last key this long |
| `CONSENT_MANAGER_PARTNER_KEY_NEGATIVE_TTL_SECONDS` | `30` | Remember "no key" this long |
| `CONSENT_MANAGER_PARTNER_KEY_REFRESH_COOLDOWN_SECONDS` | `10` | Minimum interval between refreshes for an unknown `kid` |
| `CONSENT_MANAGER_PARTNER_KEY_FETCH_TIMEOUT_SECONDS` | `3` | Timeout of one key fetch |

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
* the **`CONSENT_MANAGER_ADMIN`** client role required by the admin endpoints (the Access Log);
* the **`CONSENT_MANAGER_APPROVER`** client role, which lets a user verify assisted consents
  (approve or reject their evidence);
* role mappings granting `CONSENT_MANAGER_ADMIN` and `CONSENT_MANAGER_APPROVER` to the `admin` user,
  and `CONSENT_MANAGER_ADMIN` to the client's own service account.

Partners and their policies are managed in Partner Management, with PM's own role
(`partner_manager`).

The service **validates tokens via JWKS only**. The generated `client_secret` is used for
client-credentials tokens: by the staff API to read [Master Data code lists](#master-data-code-lists),
and by automation (e.g. the sanity suite) for the admin role. `/validate` needs no token.

## Partner portal and consent evidence — optional

{% hint style="info" %}
**In Rancher (commons-services):** the signing key, consent tokens (exchange and department roles), partner portal, national-ID login and required subject identifiers are all fields in the **Consent Manager** group of the commons-services form; no Edit YAML is needed. The values below are what those fields set.
{% endhint %}

The partner portal lets partner users (a partner's own employees) collect consent in person: create a request, upload the subject's signed form, submit it; CM staff then check it in the CM console (**Consent Approvals**) and the consent becomes active. See [consent collection](../design/consent-collection.md).

| Value | Default | |
| --- | --- | --- |
| `partnerPortal.enabled` | `false` | The portal SPA (`consent-partner-portal.<namespace>.openg2p.org`), the partner realm in Keycloak, and evidence storage |
| `partnerPortal.requiredSubjectIdentifiers` | `[]` | Other identifiers every request must carry besides the subject ID, e.g. `[FARMER_ID]` in Agri Stack; staff confirm them in the registry before approving ([identifiers and demographics](../design/consent-collection.md#identifiers-and-demographics)) |
| `partnerPortal.consentRecordJwksUrl` | the partner API's `/.well-known/jwks.json` on `consent-manager-partner.<namespace>.openg2p.org` | Named in the [consent record](../design/consent-collection.md#the-partners-copy-of-a-consent) partners download, to check the CM's signature (`CONSENT_MANAGER_CONSENT_RECORD_JWKS_URL`) |
| `partnerPortal.compositeUrl` | empty | Optional: a Composite URL; the portal then shows its use cases and pre-fills requests from them (the Composite must allow the portal's origin: `composite.corsAllowOrigins`) |
| `evidence.*` | Garage at `http://commons-garage:3900`, bucket `consent-evidence`, keys from Secret `commons-minio` | Uploaded files; the commons Garage init job creates the bucket |

The staff API gets `CONSENT_MANAGER_PARTNER_AUTH_ISSUER` / `_JWKS_URL` (partner realm) and `CONSENT_MANAGER_EVIDENCE_*`.

**One-time Keycloak setup.** The chart's keycloak-init creates the `partner` realm, the `consent-partner-portal` client and its **client roles** `PARTNER_OPERATOR` and `PARTNER_ADMIN` (a partner user needs one; the CM treats them alike). It cannot declare user-profile attributes, add token mappers or create users with attributes. After installing, run [`deployment/scripts/setup-partner-realm.sh`](https://github.com/OpenG2P/consent-manager/blob/develop/deployment/scripts/setup-partner-realm.sh) (idempotent): it declares the `partner_id` user attribute, adds its token mapper, and optionally creates partner users, each with the client role and a generated password kept in a Secret `partner-user-<username>` (on an older install it also creates the client roles):

```bash
deployment/scripts/setup-partner-realm.sh --namespace <ns> --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

A partner user's `partner_id` must be the partner's audience (e.g. `bank-a`, PM partner `PARTNER_BANK_A`).

### Master Data code lists

The portal's purposes and subject ID types come from Master Data code lists, as in Partner Management ([how](../design/consent-collection.md#purposes-and-subject-id-types)). Rancher: **Partner portal** group of this chart's form; through Commons Services, **Edit YAML** under `openg2p-consent-manager.masterData`.

| Value (`masterData.*`) | Default | Env (`CONSENT_MANAGER_*`) |
| --- | --- | --- |
| `url` | `http://commons-services-master-data-api` | `MDS_URL` — **Master Data URL**; empty = free text |
| `purposeListCode` | `CONSENT_PURPOSE` | `MDS_PURPOSE_LIST_CODE` — **Purposes List Code** |
| `subjectIdTypeListCode` | `SUBJECT_ID_TYPE` | `MDS_SUBJECT_ID_TYPE_LIST_CODE` — **Subject ID Types List Code** |
| `cacheTtl` | `300` | `MDS_CACHE_TTL` — seconds a list is reused (a failed read is retried after 30 s) |
| `timeout` | `5` | `MDS_TIMEOUT` — seconds per call |

The token comes from `global.keycloakIssuerUrl` (`MDS_TOKEN_URL`) for the `consent-manager` client (`MDS_CLIENT_ID`), its secret from the keycloak-init Secret `consent-manager` (`MDS_CLIENT_SECRET`). Set on the staff API only.

## National ID authentication of the subject (eSignet)

Off by default. With `partnerPortal.subjectAuth.enabled: true` (and the partner portal on), the subject of every assisted request must log in with their national ID through eSignet before the request can be submitted ([how it works](../design/consent-collection.md#national-id-authentication-in-the-partner-portal)). Needs **eSignet** in the namespace and, to test with sample identities, the **mock identity system** (and Artifactory, which they use); in commons-services: Install eSignet and Install Mock Identity System on (Artifactory is always installed).

| Value (`partnerPortal.subjectAuth.*`) | Default | |
| --- | --- | --- |
| `enabled` | `false` | Turns it on (mandatory once on) |
| `esignetHostname` | `esignet.<namespace>.openg2p.org` | eSignet's public host; `discoveryUrl` is derived from it |
| `clientId` | `<release>-consent-partner-portal` | The CM's OIDC client in eSignet |
| `redirectUri` | `https://<partner portal host>/consent/v1/partner-portal/subject-auth/callback` | eSignet sends the browser back here (the portal host routes it to the CM API) |
| `acrValues` | `mosip:idp:acr:generated-code` | How the person logs in (one-time code); e.g. `mosip:idp:acr:biometrics` |
| `idTypes` | `[FAYDA_FAN, NATIONAL_ID, national_id]` | Subject ID types that are the national ID; only these can log in |
| `keySecretName` | `<release>-subject-auth-client-key` | The client's RSA key (`client.pem`), mounted into the staff API |
| `bootstrap.enabled` | `true` | The Job below |

**The client in eSignet.** A Job (re-run on each upgrade) generates the client's RSA key once and keeps it in the Secret (never rotating it), then registers the client in eSignet's database (`esignet.client_detail`: redirect URI, claims `name` and `individual_id`, the ACR, `private_key_jwt` with the public key, `kid` = the client ID). eSignet's client API needs a scope an install cannot obtain, so the row is written directly, as the registry does for its credential flow. The Job waits up to 20 minutes for eSignet's tables. The staff API reads the key when it is first needed, so it works as soon as the Job has run.

The staff API gets `CONSENT_MANAGER_SUBJECT_AUTH_*` (enabled, provider name, discovery URL, client ID, redirect URI, ACR, ID types, key path). Further backend settings, defaulted: `subject_auth_scope` (`openid profile`), `subject_auth_claims`, `subject_auth_subject_claim` (`individual_id`), `subject_auth_stored_claims` (`[name]`), `subject_auth_session_ttl_seconds` (300).

**Testing with the mock identity system:** its identities are the national IDs of the sample people loaded in Master Data (Load Sample People), so a request for sample person `ETH-IND-0007` uses FAN `946053125409`. For the one-time code it accepts, see the mock identity system's configuration.

## Exchange — optional

Off by default: with these values empty nothing is rendered and CM behaves exactly as a standalone
install. In Rancher, pick **Exchange Role** (`global.agriStackExchange.role`):
**exchange** or **department**. The role alone gives working defaults, the reference values the Agri Stack test
scripts use; the other fields only override them. The Exchange CM
issues short-lived **consent tokens** (called *receipts* in the API and settings), one per registry
and query; a department CM accepts them. How the two roles work:
[Exchange consent tokens](../design/exchange-receipts.md).

| Value (`global.agriStackExchange.*`) | Env (`CONSENT_MANAGER_*`) | Role | Meaning |
| --- | --- | --- | --- |
| `role` | — | both | `exchange`, `department`, or empty (none: the fields below act as set) |
| `defaultIssuer`, `defaultPresenter` | — | both | Used for an empty issuer or presenter in a role: `agri-stack-exchange-cm`, `agri-composite` |
| `exchangeDomain` | — | department | **Exchange Domain**; empty = `agrix.<parent of this install's domain>`. The JWKS URL defaults to `https://consent-manager-partner.<exchange domain>/api/consent-manager-partner/.well-known/jwks.json` |
| `defaultSubjectIdentifiers` | — | exchange | Required subject identifiers when the partner portal leaves them empty: `[FARMER_ID]` |
| `issuer` | `RECEIPT_ISSUER` | exchange | **Token Issuer ID** — stamped as `iss` on consent tokens (e.g. `agri-stack-exchange-cm`). Empty = no tokens |
| `receiptPresenters` | `RECEIPT_PRESENTERS` (JSON list) | exchange | Callers (`partner_id` / DCI `sender_id`) **Token Presenters** — allowed to request consent tokens, e.g. `agri-composite`. List or comma-separated string |
| `receiptTtlSeconds` | `RECEIPT_TTL_SECONDS` | exchange | **Token Lifetime (seconds)** — consent-token lifetime, capped by the consent's expiry (default 300) |
| `compositeApiUrl` | `COMPOSITE_API_URL` | exchange | **Composite API URL** — where the CM reads a use case's purpose and scopes for consents made by use case (partner portal, lifecycle API). Empty = `defaultCompositeApiUrl`, `http://agri-composite-api` (the Composite in this namespace). Unreachable: such consents cannot be made (`503`) |
| `trustedReceiptIssuers` | `TRUSTED_RECEIPT_ISSUERS` (JSON list) | department | `[{issuer, jwks_url, presenter, status_url?}]`. `jwks_url` is the Exchange CM partner API's `/.well-known/jwks.json`; status (if checked) is read from `<same base>/consent/v1/receipts/{jti}/status` unless `status_url` (with `{jti}`) is given |
| `trustedIssuer.{issuer, jwksUrl, presenter}` | (added to the list above) | department | One trusted issuer as plain fields — what Rancher sets (**Trusted Token Issuer ID**, **Trusted Issuer JWKS URL**, **Trusted Token Presenter**); empty fields take the defaults above |
| `receiptStatusCheck` | `RECEIPT_STATUS_CHECK` | department | **Token Status Check** — `never` (default) or `always`: also check each token's status at the Exchange CM, one runtime call per token ([why it is off](../design/exchange-receipts.md#department-role-accepting)); `always` needs the Exchange to route its status endpoint (`partnerApi.exposeReceiptStatus`) |

Consent-token issuing uses the **signing key** above (same `kid`, same JWKS): the demo key works for a
demo, but give a production Exchange CM its own `.p12`. With the exchange role and the partner
portal on, the national-ID login is always on, required subject identifiers default to `FARMER_ID`, and
the Composite URL to `https://agri-composite.<this domain>`. Further backend settings, defaulted: `receipt_status_cache_ttl_seconds`
(10), `receipt_jwks_cache_ttl_seconds` (300), `receipt_jwks_refresh_cooldown_seconds` (10),
`receipt_fetch_timeout_seconds` (3).

**Exchange (`agrix`)** — role `exchange`. Each partner (e.g. `bank-a`) needs one policy per use case
it calls in the Exchange's Partner Management. Everything is in the commons-services
form (see the Agri Stack
[deployment guide](../../open-agri-stack/deployment/exchange.md)).

**Department (`trial`, `dept1`)** — role `department` (set **Exchange Domain** or the JWKS URL if the
Exchange is not at `agrix.<parent domain>`; it must be reachable from this CM's partner API).
The Composite (`agri-composite`, PM partner `PARTNER_AGRI_COMPOSITE`) needs a scope policy for each of
the department's registries in the department's Partner Management: that is the department's
ceiling ([Exchange consent tokens](../design/exchange-receipts.md#setting-up-a-department-for-the-exchange)). The migration adds two nullable columns to `decision_logs` and an `issued_receipts` table;
both stay empty on a standalone install.

## Horizontal scalability

The service is designed to scale out under a high rate of consent verification:

* **Stateless** — no per-pod state; any replica serves any request, no session affinity. Scale by
  adding pods/workers behind the load balancer (HPA does this automatically).
* **Shared Postgres** with framework connection pooling. Size `max_connections ≳ pods × workers ×
  pool_size + headroom`.
* **No in-process scheduler** — expiry is the external CronJob above, so it fires exactly once per
  tick regardless of replica count; the hot path also lazily expires on read.
* **Hot-path cache** — partner keys and policies (from Partner Management) are cached per pod with a short TTL, keeping
  `/validate` cheap under load (each pod's cache is independent — safe across replicas).
* **Idempotent `/validate`** — re-validating the same consent object (`jti`) for the same
  `data_controller` returns the same decision instead of minting duplicates.

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

* **Smoke + contract** (always, when sanity is on) — `/ping` (both apis), the partner-api's
  `/.well-known/jwks.json` + OpenAPI, and that the auth model holds: the partner-api's `/validate`
  is open (no Keycloak), while the staff-api's admin endpoints reject an unauthenticated call.
  Needs no token and **creates no data**. Catches a broken/booting-wrong image immediately.
* **Full e2e** (`Run Full E2E` / `sanity.runE2e`, **default on**) — ensures a persistent test
  partner (`PARTNER_CM_SANITY`) exists in **Partner Management** with its key and a scope policy for
  the sanity data controller that accepts its own signed consents (`allow_partner_consents`; a `pm-seed` Job raises and approves the onboarding, key-update or
  policy request when something is missing, using the `pmSeedClientId` client), signs a consent
  object with the matching private key, and exercises a real `POST /validate` on the
  **partner-api** (permit + the `signature_invalid` and `scope_exceeds_policy` denials), then
  verifies the CM's receipt signature against the partner-api's JWKS.
  **Turn this off for production** to avoid creating test data; smoke + contract still run and gate.
  Because it runs by default and gates, **Keycloak and Partner Management must be reachable at deploy
  time** — if they aren't, the e2e fails/skips (turn the e2e off, or fix the dependency).

The suite is **independent of which `.p12` the deployment uses**: it signs consent objects with a
bundled TEST key (whose public half is seeded into Partner Management), and verifies the CM's receipt
against the **live** partner-api `/.well-known/jwks.json` — handling EdDSA/ES256/RS256 — so it works
the same whether the CM runs the demo key or your production key. It never needs the CM's private key.

Form options (**Sanity** group): `Run Sanity Tests (gates the deploy)` (`sanity.enabled`) and
`Run Full E2E` (`sanity.runE2e`). The suite ships as a separate image
(`openg2p/openg2p-consent-manager-sanity`) built by the same CI workflow.

> A **Postman collection** for hands-on/manual API exploration is maintained separately (for
> integrators trying the API by hand); it is complementary to — not a replacement for — this
> automated in-cluster gate.
