---
description: >-
  A prescriptive build guide (and AI prompt) for creating a new OpenG2P platform
  service the same way as Consent Manager, Partner Management, AWE and G2P Bridge.
---

# Creating a New Platform Service

This page is a **build guide and prompt**: hand it (or paste it) to a developer or
an AI agent tasked with creating a new OpenG2P platform/backend service, so the
result follows the same conventions, integrations and deployment shape as the
existing services. It captures not just the "what" but the **nuances** that are
easy to get wrong.

**Reference services (exemplars — read their code + docs before starting):**

| Service | Repo | Docs |
| --- | --- | --- |
| Consent Manager (CM) | `consent-manager` | [Consent Management](../../consent-management/README.md) |
| Partner Management (PM) | `partner-management` | [Partner Management](partner-management/README.md) |
| Approval Workflow Engine (AWE) | `awe` | [AWE](approval-workflow-engine/README.md) |
| G2P Bridge | `g2p-bridge` | — |
| Audit Manager | `audit-manager` | [Audit Manager](audit-manager/README.md) |

> **How to use this guide:** treat every numbered section as a requirement.
> Where a section says "see X", follow that page rather than re-deriving the
> pattern. When a requirement doesn't apply (e.g. no partner-facing API), say so
> explicitly rather than skipping silently.

---

## 1. Naming conventions

Pick a short, hyphenated **service slug** (e.g. `consent-manager`, `partner-management`)
and derive everything from it consistently:

| Thing | Convention | Example |
| --- | --- | --- |
| Git repo | `<slug>` | `consent-manager` |
| Python package | `openg2p_<slug_underscored>` (src layout, Hatchling) | `openg2p_consent_manager` |
| Config env prefix | `<SLUG_UPPER>_` (pydantic-settings `env_prefix`) | `CONSENT_MANAGER_` |
| Docker images | `openg2p/openg2p-<slug>[-<component>]` | `openg2p/openg2p-consent-manager`, `-sanity`, `-ui` |
| Helm chart | `openg2p-<slug>` | `openg2p-consent-manager` |
| K8s Deployments/Services | `<release>-<component>` (`nameOverride`) | `<release>-api`, `<release>-partner-api`, `<release>-ui` |
| Postgres DB | `<slug_underscored>_db` (or per-release, see PM/CM) | `consent_manager_db` |
| Keycloak clients | `<slug>` (confidential/service), `<slug>-ui` (public/browser) | `consent-manager`, `consent-manager-ui` |
| Keycloak roles | `<SLUG_UPPER>_ADMIN`, `<SLUG_UPPER>_APPROVER`, … | `CONSENT_MANAGER_ADMIN` |
| REST route prefix | `/<domain>/v1/...` (versioned, on `BaseController`) | `/consent/v1/validate` |

Hostnames and API-service names are covered in **§18**.

---

## 2. Backend on `openg2p-fastapi-common`

Build the API on **openg2p-fastapi-common** (see the
[FastAPI Common architecture](../architecture/openg2p-fastapi-common/README.md)):

- `Settings(BaseSettings)` with your `env_prefix`; `Initializer(BaseInitializer)`
  constructs services then controllers; `main.py` = `Initializer().return_app()`.
- Controllers subclass `BaseController` (they self-mount their router; set
  `self.router.prefix += "/<domain>/v1/..."`). Services subclass `BaseService`
  (singletons via `get_component()`), models subclass the common ORM base.
- **Postgres** via the framework's async engine (`dbengine`); one session per unit
  of work; the app is **stateless** (§14).
- **Migrations**: use `model.create_migrate()` (create-if-not-exists) in
  `migrate_database`. It does NOT alter existing tables — for schema changes on an
  existing DB add **idempotent** `ALTER TABLE … ADD COLUMN IF NOT EXISTS` /
  `CREATE INDEX IF NOT EXISTS` statements. Make migrate safe to run concurrently
  from multiple replicas (Dockerfile `CMD migrate && gunicorn …`).
- Expose `/ping` (via `PingInitializer`) for probes.
- **Do not** invent a bespoke auth or crypto layer — use the commons + the
  patterns below.
- **Run the container as non-root.** In the Dockerfile, create a dedicated user
  and switch to it before `CMD` — use uid/gid **1001** to match the chart's
  `runAsUser`/`fsGroup`, and `chown` the app dir so runtime writes succeed:

  ```dockerfile
  RUN addgroup -g 1001 openg2p \
   && adduser -D -u 1001 -G openg2p -h /home/openg2p openg2p \
   && chown -R 1001:1001 /app
  USER 1001
  ENV HOME=/home/openg2p
  ```

  Bind on a port `>1024` (e.g. `8000`) so no `NET_BIND_SERVICE` capability is
  needed. Baking non-root into the image (rather than only forcing it from the
  chart) means the pod `securityContext` can be enabled cleanly — the image
  already runs as `1001`, so `runAsNonRoot`/`runAsUser` are consistent and writes
  don't break. Root containers fail Pod Security Standards "restricted" / CIS and
  enlarge the container-escape blast radius. Pair this with a **restricted pod
  `securityContext`** in the chart (`runAsNonRoot: true`, `runAsUser: 1001`,
  `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`,
  `seccompProfile: RuntimeDefault`); add `readOnlyRootFilesystem: true` last, with
  an `emptyDir` mounted at each temp/cache path.

---

## 3. Separation into staff / partner / beneficiary / agent APIs (IAM)

Every service exposes up to **four API audiences**, and the first three connect to
**IAM (Keycloak)** each with its own **realm**; the fourth authenticates with
**partner keys**, not Keycloak. See [Identity & Access Management](../../identity-and-access-management/README.md)
and, for a worked implementation, [CM's API-audience split](../../consent-management/design/architecture.md).

| Audience | Who | Auth | Realm |
| --- | --- | --- | --- |
| **staff** | operators/admins/approvers | Keycloak bearer | `staff` |
| **beneficiary** | end users (self-service) | Keycloak bearer | `beneficiary` |
| **agent** | field agents | Keycloak bearer | `agent` |
| **partner** | machine-to-machine consumers | **partner keys / signature** (no Keycloak) | — |

**Implementation pattern (one image, a Deployment per audience):**

- Keep ONE codebase/image. Add a config field `<PREFIX>_API_AUDIENCE`
  (`staff|partner|beneficiary|agent|all`, default `all` for dev). The Initializer
  mounts ONLY that audience's controllers.
- The **partner API carries NO Keycloak** — its trust is the partner-signed
  payload verified against PM keys (see §5), replay-guarded (e.g. a `jti`). Secure
  the caller→service hop at transport level (Istio mTLS / NetworkPolicy), not a
  Keycloak realm.
- Only build the audiences you need now; **scaffold** the rest disabled (e.g.
  beneficiary `enabled: false`) so they're a config flip away.
- Each audience is its own Deployment + Service + VirtualService **inside the one
  chart** (§10) with its own hostname (§18) and per-deployment auth env.

> **Nuance:** don't split into multiple charts — it's one chart with multiple
> Deployments (like G2P Bridge's partner-api + bene-portal-api). Give each
> Deployment a **distinct** `app.kubernetes.io/component` label so the Services
> don't cross-select each other's pods.

---

## 4. Keycloak clients, roles & role assignment

Provision via the chart's **`keycloak-init`** dependency (it creates clients,
roles, users and role-mappings in the shared commons Keycloak). See
[Staff Portal Application Registration](../../identity-and-access-management/staff-portal-application-registration.md).

- **Confidential service client** `<slug>` (serviceAccountsEnabled) — defines your
  admin/approver **client roles**; its service account drives automation and gets a
  client-credentials secret (auto-created Secret named after the client). The
  service itself validates inbound tokens via JWKS (no secret needed to validate).
- **Public browser client** `<slug>-ui` (publicClient, standardFlow) for the UI's
  login — redirect URIs + webOrigins to the UI host. No secret.
- **Assign the first-install admin user** (and the service account, where it drives
  automation) to your roles via `clientRoleMappings`.

> **Nuances (learned the hard way):**
> - To call **another** service's admin API you need **that service's** role, which
>   is usually a **client role on that service's client** (e.g. PM's `partner_manager`
>   lives on the `partner-management-staff-portal` client, and PM checks
>   `resource_access[<that client>].roles`). Grant it via
>   `clientRoleMappings: { <other-service-client>: [<role>] }` — using the wrong
>   client name silently 403s.
> - keycloak-init **fails** if it references a client/role that doesn't exist yet, so
>   a cross-service grant creates an **install-ordering** dependency (the other
>   service must be installed first). Only enable it when that dependency is real
>   (e.g. you already depend on that service), and document the escape hatch.
> - **401 vs 403** when integrating: 401 = no/invalid token (missing secret / wrong
>   issuer); 403 = valid token but missing role.
> - **Token issuer alignment**: a service-to-service call fails with `Invalid issuer`
>   when the token's `iss` ≠ the callee's configured issuer. Ensure both sides
>   resolve the **same** `global.keycloakIssuerUrl` (watch internal-vs-external
>   Keycloak URLs / frontend-URL).

---

## 5. Partner keys & caching (partner-facing services)

Partner **identity and signing keys live in Partner Management (PM)** — do NOT
store partner keys locally or poll a partner `jwks_url`. Fetch them from PM and
verify locally. Full contract + caching discipline:
[Partner Management Integration](../../consent-management/design/partner-management-integration.md).

- Fetch: `GET {partner_mgmt_api_url}/keys/{partner_id}` (also `/keys/{id}/{kid}`,
  `/keys/{id}/jwks.json`) → PEM + kid + algorithm. **404 = fail-closed reject.**
- Cache per pod with the full discipline: **soft TTL** (respect the response
  `Cache-Control: max-age`), **hard TTL** (serve last-known-good during a PM outage,
  then fail closed), **negative cache** (brief 404 memo), **unknown-kid refresh**
  (rate-limited, to pick up rotation), **single-flight**.
- Your service stores only a **binding/reference** to the PM partner
  (`partner_mgmt_id`, falling back to an audience), plus its own domain data.
- Add an **algorithm-confusion guard** (declared alg must equal the PM key's alg).

---

## 6. Integration with AWE (if an approval process is involved)

If any action needs human approval, integrate the shared **Approval Workflow
Engine** rather than building your own. Full mechanics:
[Approval Workflow (AWE) Integration](../../consent-management/design/approval-workflow-integration.md)
and [AWE](approval-workflow-engine/README.md).

- Make it **opt-in** (`<PREFIX>_AWE_ENABLED`, default **false**). The service must be
  fully usable with AWE off (the gated action just proceeds immediately).
- **Caller side**: on the gated action, create the artifact in a `pending` state and
  `POST {awe}/v1/awe/requests` with a **service token**, `policy_key`,
  `artifact_type`, `artifact_id`, a context snapshot, `callback_url` and
  `callback_secret_id`. Apply the terminal decision only on AWE's **HMAC-signed**
  webhook (`X-Approval-Signature: sha256=` HMAC(secret, `"<ts>.<rawbody>"`), verify
  over RAW bytes; dedupe on the event id).
- **Approver side**: approvers act in **your** UI, not AWE's — **proxy** AWE's
  task-list + decision endpoints forwarding the **approver's own JWT** (AWE has no
  approver UI). Two token types: a service token for `create_request`; the approver
  JWT for the proxy.
- **Callback secret**: register your per-caller secret into AWE's DB (a seed Job) and
  hold the same raw HMAC secret to verify webhooks.

> **Nuances:** the **AWE approval policy** for your `policy_key` (stages/approvers)
> is **NOT** auto-provisioned — an operator creates it (`POST /v1/awe/policies` draft
> → `.../activate`, needs `AWE_ADMIN`). Distinguish the two "policies": your domain
> policy (the artifact) vs the AWE **approval** policy (the workflow). Your sanity
> e2e must be **AWE-aware** (a gated action stays `pending` awaiting a human — assert
> that and skip the happy-path round-trip).

---

## 7. Integration with Audit Manager

Keep an **in-house, append-only audit trail** (decision/action log; signed receipts
where applicable) as the authoritative record — it's needed for the hot path and
low-latency queries. For **centralized, long-term, tamper-evident** compliance,
add a forwarder that emits **CloudEvents over HTTP** to the
[Audit Manager](audit-manager/README.md) (Kafka-buffered). Treat the forwarder as an
add-on, not a replacement; start in-house and add it when centralized retention is a
requirement.

---

## 8. Signing & receipts (if the service issues signed artifacts)

If your service signs artifacts (e.g. receipts): sign with an asymmetric **PKCS#12
(.p12)** key, publish the public key at `/.well-known/jwks.json` so anyone can
verify, and mount the key **only** on the component that signs. Ship a **demo key**
for turnkey testing but **loudly flag** it (distinctive `kid`, boot warning) — it's
public and must be replaced for production. Prefer local `.p12` over a remote
Keymanager unless the platform requires the latter.

---

## 9. UI & branding

If the service has an admin/self-service UI, build it like the reference consoles
(AWE UI / CM UI): **React 18 + Vite + TypeScript + @tanstack/react-query +
react-router + keycloak-js**, plain CSS on OpenG2P design tokens.

- **Branding**: OpenG2P palette (yellow `#F5BB1A` accent, black `#061327`, orange
  `#F07B1A`, magenta/grey/blue used sparingly), **Roboto** + **Roboto Slab** fonts,
  the OpenG2P logo. Match the AWE UI look. (Brand assets/guidelines live in the
  `branding` repo.)
- **Runtime config**: read `/config.json` at boot (Keycloak url/realm/clientId,
  API base, roles) so one image works everywhere; inject it via a **ConfigMap
  overlay** (subPath) — no per-env rebuild. Dev falls back to an unsigned token when
  `keycloak.url` is empty.
- Serve as static files behind **nginx-unprivileged**; deploy on the **staff host**
  via a **single combined VirtualService** (`/<domain>/` → the staff API, `/` → the
  UI) so it's same-origin (no CORS). Suppress the API's standalone VirtualService
  while the UI owns the host (two VSes racing one host is non-deterministic).

---

## 10. Single Helm chart

**One chart** (`openg2p-<slug>`) for the whole service. See
[CM Deployment](../../consent-management/deployment/README.md) for a full example.

- **Dependencies**: `common` (template helpers), `postgres-init` (DB + user +
  password Secret), `keycloak-init` (clients/roles). Add others (e.g. an AWE
  callback secret) as templates.
- **A Deployment + Service + VirtualService per API audience** (§3) plus the UI
  (§9) — the cleanest DRY approach is a base `…Api` values block and an `extraApis`
  list whose entries are **merged over** the base, so each states only its
  differences (audience, auth, hostname, whether it mounts the signing key).
- Config via a shared `envVars` map (+ `envVarsFrom` for `secretKeyRef`s); per-audience
  overrides (`API_AUDIENCE`, `AUTH_ENABLED`) set on each Deployment.
- HPA (§14), an expiry/maintenance **CronJob** if needed (§14), the sanity Job (§15).

---

## 11. Versioning & CI — the central pipeline

**Do not** hand-write `docker-build.yml` / `helm-publish.yml`. Images and the chart
are versioned and published by the **central reusable workflow**; the new repo
only needs a ~40-line caller stub. This gives every artifact **one immutable
version per commit** (`0.0.0-develop.N`, `1.0.0-rc.N`, frozen `1.0.0`), with the
chart and images always in lockstep.

Full details — the versioning table, the frozen-tag convention (bare `1.0.0`, no
`v`, tag-don't-branch), the CI diagram, and how the chart injects versions — are on
**[Helm & Docker Versioning Strategy and CI](../../releases/helm-docker-versioning-and-ci/README.md)**.

**To set it up in the new repo,** follow
[Onboarding a repo](../../releases/helm-docker-versioning-and-ci/onboarding-a-new-repo.md)
— it includes a **copy-paste prompt** you can hand to an AI agent to generate the
stub. Use `consent-manager`'s `build-publish.yml` as the exemplar.

Key points to get right for a new service:

- `Chart.yaml` keeps the placeholder `version: 0.0.0-develop`; CI overrides it at
  package time. `values.yaml` image tags are placeholders too — CI injects the real
  version.
- Declare **one `images` entry per Docker image** (api, sanity, ui, …) with its
  `dockerfile`/`context`, and add a **per-image `pin`** for any build-arg that is a
  git ref (e.g. `FASTAPI_COMMON_REF`).
- List the chart's OpenG2P image-tag `yq` paths in `chart-image-paths` (exclude
  third-party images).
- The changelog is generated from **commit messages** automatically — write clear
  `G2P-#### <subject>` commit messages. See
  [Changelogs](../../releases/helm-docker-versioning-and-ci/changelogs.md).

---

## 12. `questions.yaml` — surface the right parameters in Rancher

Provide `questions.yaml` in the chart so operators configure the service from the
**Rancher form** without editing YAML. Surface the **applicable** parameters
(hostnames, image tags, auth toggles, signing-key source, scaling, integration
URLs) grouped logically. Keep **break-glass / advanced** switches OUT of the form
(values-only) so they're not fiddled with casually (e.g. "disable sanity" or
"report-only" toggles).

---

## 13. Adding the service to the Rancher catalog

- Add the `openg2p.org/add-to-rancher: ""` **annotation** + `catalog.cattle.io/*`
  annotations to `Chart.yaml`, plus an **`app-readme.md`** (the catalog card
  description) and `questions.yaml` (§12).
- The central workflow's chart job merges annotated charts into
  `rancher/index.yaml` in the central helm repo. See
  [Helm charts](../../releases/helm-charts.md).

---

## 14. Scalability (high-traffic services)

- **Stateless pods** — no per-pod state, no session affinity; any replica serves any
  request. Scale by adding pods.
- **HPA is CPU-only.** Do NOT autoscale on memory — a Python process's memory
  baseline stays high and would scale up and never come back down. Default
  `replicaCount: 1`, autoscaling off; turn HPA on (CPU target ~80%, e.g. 1–10) for
  hot paths.
- **No in-process scheduler.** Scheduled work (expiry, cleanup) runs as a **CronJob**
  (`python -m <pkg>.<task>`) so it fires once per tick regardless of replica count;
  optionally lazily on read too.
- **Pod-local caches** (partner keys/policies) with a short TTL — independent per
  pod, safe across replicas, bounded staleness.
- Idempotent operations on the hot path (e.g. dedupe by a request id) so retries/
  concurrency are safe; idempotent migrations (§2) so concurrent replicas start
  cleanly.

---

## 15. Sanity test job (smoke + brief e2e), with `TEST` tags

Ship an **in-cluster sanity suite** (a separate small pytest image) run as a Helm
`post-install,post-upgrade` **hook Job**:

- **Smoke + contract** (always): `/ping`, JWKS/OpenAPI served, and the auth model
  holds (protected endpoints reject; a keys-authenticated endpoint is open). Creates
  no data.
- **Brief e2e** (opt-in, `runE2e`): a real round-trip through the primary flow. When
  the service is split by audience, the suite targets **each audience's URL**. When
  it depends on PM/AWE, it **seeds** what it needs (idempotently) or **skips** with a
  clear reason.
- **Tag TEST data everywhere**: prefix every created entity / identifier with
  `TEST_` (e.g. `TEST_SANITY_*`) so test data is unmistakable and easy to purge; the
  suite cleans up (or leaves clearly-tagged, inert data).
- **Gating**: `failOnError: true` by default → a failing hook Job fails the
  install/upgrade. Provide a values-only escape hatch, and turn the data-creating e2e
  **off for production**.

---

## 16. Full clean uninstall script

Provide `deployment/scripts/uninstall-<slug>.sh` that fully removes the service:
`helm uninstall`, **drop the Postgres DB + role** (via `kubectl exec` into the
commons Postgres), and sweep leftover **Jobs / Secrets / PVCs / ConfigMaps** the
release created (including auto-generated client/DB/signing secrets). Support
`--dry-run` and `--yes`, and flags for optional destructive extras (drop signing
secret, keep PVs). Mirror the reference services' uninstall scripts.

---

## 17. Documentation in GitBook only (no local READMEs)

- **No content in local `README.md`s** — everything goes in GitBook. A repo README,
  if present, is a thin pointer to the docs site.
- Add the service under **Platform Services** in `SUMMARY.md`, with (at least) design,
  API reference, deployment, testing, and a **`versions.md`** page.
- **Keep the versions page current** — it's the compatibility record operators rely
  on. Update it (and the release notes) on every meaningful change.
- **Point to existing pages** (IAM, AWE, PM, Audit Manager, versioning, branding)
  rather than duplicating them; only inline content when it's genuinely
  service-specific.

---

## 18. API service & UI hostnames

Per-audience Services and hostnames follow the platform convention (see the
reference services for exact strings):

| Component | Service name | Hostname |
| --- | --- | --- |
| Staff API + console UI | `<release>-api` (+ `<release>-ui`) | `<slug>.<ns>.openg2p.org` |
| Partner API | `<release>-partner-api` | `<slug>-partner.<ns>.openg2p.org` |
| Beneficiary API | `<release>-bene-api` | `<slug>-bene.<ns>.openg2p.org` |
| Admin/staff-portal API (where identity is managed) | `<release>-staff-portal-api` | `<slug>-staff-portal.<ns>.openg2p.org` |

The UI is served on the **staff** hostname (same origin as the staff API via one
combined VirtualService, §9). External partners/PEPs call the **partner** hostname;
internal service↔service traffic uses the in-cluster Service DNS names, not the
external hostnames.

---

## Nuance checklist (don't ship without checking)

- [ ] Partner API has **no Keycloak**; its trust is the signed payload + PM keys +
      replay guard; caller hop is mTLS.
- [ ] Cross-service role grants target the **correct client** and respect **install
      ordering**; document the escape hatch.
- [ ] Service-to-service tokens: **issuer alignment** (no internal/external mismatch).
- [ ] PM key fetch is **fail-closed on 404**, cached with soft/hard/negative TTL +
      unknown-kid refresh + single-flight.
- [ ] AWE is **opt-in**; the AWE approval policy is registered **out of band**; the
      e2e is **AWE-aware**.
- [ ] Migrations are **idempotent** (`IF NOT EXISTS`) and safe under concurrent
      replicas.
- [ ] Container image runs as **non-root** (`USER 1001` + `chown`, port `>1024`);
      the chart enables a **restricted `securityContext`** (`runAsNonRoot`, drop
      caps, no priv-esc).
- [ ] HPA is **CPU-only**; scheduled work is a **CronJob**, not an in-process timer.
- [ ] Signing uses a **.p12** + JWKS; the **demo key** is loudly flagged and
      replaceable.
- [ ] One chart, a **Deployment per audience** with **distinct component labels**;
      one combined VirtualService per host.
- [ ] CI **path filters** cover every build input; chart version is
      `0.0.0-develop.<N>`.
- [ ] Test data is **`TEST_`-tagged**; sanity gates the deploy; e2e is prod-safe-off.
- [ ] A **full clean uninstall** script exists.
- [ ] All docs in **GitBook**; the **versions page** is updated.

---

## Related pages

* [Identity & Access Management](../../identity-and-access-management/README.md)
* [Partner Management](partner-management/README.md) ·
  [PM integration (keys + caching)](../../consent-management/design/partner-management-integration.md)
* [Approval Workflow Engine](approval-workflow-engine/README.md) ·
  [AWE integration](../../consent-management/design/approval-workflow-integration.md)
* [Audit Manager](audit-manager/README.md)
* [Consent Manager](../../consent-management/README.md) — the most complete worked
  example of every pattern here.
* [Versioning conventions](../../releases/versioning.md) ·
  [Helm charts](../../releases/helm-charts.md)
