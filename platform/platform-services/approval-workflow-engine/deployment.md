---
description: >-
  Deployment guide for the Approval Workflow Engine — local development with
  Docker Compose, Helm chart installation, configuration reference, Keycloak
  prerequisites, operational runbook, and security c
---

# Deployment

## Local development

### With Docker Compose (one command)

```bash
docker compose up --build
```

Starts **three** services — Postgres, the backend (`awe`), and the admin SPA (`awe-ui`, nginx-served static build). After a few seconds:

* Admin UI: http://localhost:8080/ (nginx proxies `/v1/awe/*` to the backend)
* API: http://localhost:8000/v1/awe/
* Swagger: http://localhost:8000/v1/awe/docs
* Health: http://localhost:8000/v1/awe/health

Dev-mode auth is enabled — the Keycloak `issuer` is empty in [`config/default.yaml`](https://gitlab.com/openg2p/awe/-/blob/develop/config/default.yaml), so the service accepts any unsigned JWT. **Never run this configuration in production** — the Helm chart sets a non-empty issuer which forces JWKS signature verification.

### Smoke test (create policy → request → approve)

```bash
# Dev token with the AWE_ADMIN role — accepted by dev-mode auth.
TOKEN='eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkZXYtYWRtaW4iLCJlbWFpbCI6ImRldkBsb2NhbCIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJBV0VfQURNSU4iXX19.'

# 1. Create a policy
curl -sX POST http://localhost:8000/v1/awe/policies \
  -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{
    "policy_key": "demo.v1",
    "name": "Demo approval",
    "artifact_type": "demo.artifact",
    "stages": [{
      "name": "Demo stage",
      "stage_order": 1,
      "mode": "any-n",
      "mode_value": 1,
      "rules": [{"rule_type": "user", "rule_value": {"user_id": "u-alice"}}]
    }]
  }'

# 2. Activate it
curl -sX POST http://localhost:8000/v1/awe/policies/demo.v1/versions/1/activate \
  -H "authorization: Bearer $TOKEN"

# 3. Caller creates a request
curl -sX POST http://localhost:8000/v1/awe/requests \
  -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{
    "policy_key": "demo.v1",
    "artifact_type": "demo.artifact",
    "artifact_id": "demo-1",
    "context": {}
  }'
# → { "request_id": "...", "status": "in_review", "tasks": [...] }

# 4. Alice approves
TASK_ID=<from previous response>
curl -sX POST "http://localhost:8000/v1/awe/tasks/$TASK_ID/decision" \
  -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{"action": "approve"}'

# 5. Verify terminal state
curl -s "http://localhost:8000/v1/awe/requests/<request_id>" \
  -H "authorization: Bearer $TOKEN" | jq .status
# → "approved"
```

### With hot reload (UI + API)

Useful when iterating on the admin UI.

```bash
# Terminal 1 — Postgres
docker compose up postgres -d

# Terminal 2 — API with reload
python3 -m venv .venv && .venv/bin/pip install -e '.[test]'
DB_HOST=localhost DB_PASSWORD=postgres \
  .venv/bin/uvicorn awe.main:app --reload

# Terminal 3 — UI dev server
cd ui && npm install && npm run dev
```

Open http://localhost:5173/ — Vite proxies API calls on `/v1/awe/*` to the uvicorn instance on :8000.

## Kubernetes install via Helm

### Chart deploys **two Deployments + one Istio VirtualService**

The single `openg2p-awe` chart ships:

* **`awe`** — the backend (FastAPI + Postgres). Image `registry.gitlab.com/openg2p/awe/openg2p-awe:<branch>`.
* **`awe-ui`** — the admin SPA, nginx-served static bundle. Image `registry.gitlab.com/openg2p/awe/openg2p-awe-ui:<branch>`. Low-traffic, single replica, \~10 mCPU / 32 Mi requests.
* **One Istio `VirtualService`** on the shared host (`global.aweHostname`) with two routes:
  * `/v1/awe/` → backend Service (most-specific prefix, evaluated first)
  * `/` → UI Service (catch-all)

Same host, different paths; the browser treats API and UI as same-origin so no CORS is needed.

### Prerequisites

* Kubernetes 1.23+
* **PostgreSQL** reachable from the cluster (shared Postgres is fine). The chart's `postgres-init` subchart creates the database and user; it does **not** provision the Postgres server itself.
* **Keycloak**, deployed separately (via the commons-keycloak chart, shared with Registry / PBMS). AWE's clients and roles are provisioned on install by the `keycloak-init` subchart — see below.
* (If used) Istio for the VirtualService / Gateway templates.

### What the Keycloak integration provisions

On install, the `keycloak-init` subchart creates two clients under the shared **`staff`** realm (this realm is created by the commons-keycloak install; AWE just adds to it — it does not own it):

| Client               | Purpose                                                                                       | Type                              |
| -------------------- | --------------------------------------------------------------------------------------------- | --------------------------------- |
| `awe-admin-portal`   | OIDC login for the bundled admin SPA. Carries the `AWE_ADMIN` and `AWE_VIEWER` client roles.  | Public (browser redirect flow)    |
| `awe-admin-resolver` | Service account used by AWE to call Keycloak admin API for `role:` / `group:` approver rules. | Confidential (client credentials) |

Client roles provisioned on `awe-admin-portal`:

* `AWE_ADMIN` — full read + write (policy CRUD, request cancel, delivery retry).
* `AWE_VIEWER` — read-only (policies, requests, events, deliveries, audit log).

The commons `admin` user is mapped to `AWE_ADMIN` so you can authenticate into the admin SPA out of the box. Grant `AWE_VIEWER` (or `AWE_ADMIN`) to other users via the Keycloak admin UI.

### Client-secret sync and service-account roles

keycloak-init handles both automatically:

* **Client secrets** — the chart's `client-secrets.yaml` template creates a Kubernetes Secret named after each `clientId` (`awe-admin-portal`, `awe-admin-resolver`) with key `client_secret`, generating a random value on first install and reusing the existing Secret on upgrades. The init Job mounts these Secrets and uses them when creating / updating the Keycloak clients, so Keycloak and K8s stay in sync. AWE's Deployment references `awe-admin-resolver` via `envVarsFrom` to pick up the client secret.
*   **Service-account roles** — Keycloak auto-creates the pseudo-user `service-account-awe-admin-resolver` when the resolver client is created with `serviceAccountsEnabled: true`. The chart's `users:` block targets this user and grants it the `realm-management` client roles below:

    | Role           | Why AWE needs it                                                                                                                                                            |
    | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `view-users`   | List role / group members; read user ids. Required for both realm-role and client-role rules.                                                                               |
    | `view-clients` | Translate `clientId` (e.g. `registry-staff-portal`) → internal UUID. Required before calling the client-role members endpoint, i.e. whenever a `role:` rule sets `client:`. |
    | `query-groups` | List group members for `group:` rules.                                                                                                                                      |

    These are **realm-wide reads** — the service account can enumerate users and client definitions across every client in the realm, including Callers' clients (Registry, Social Registry, etc.). This is Keycloak's default admin model. If your realm has **Fine-Grained Admin Permissions (FGAP)** enabled, you'll additionally need to grant the resolver service account `view` permission on each target client individually — consult whoever owns the realm.

#### Role rules: realm vs client

Approver rules of type `role:` can point at either a **realm role** or a **client role**:

```yaml
# Realm role — role exists at the realm level.
- rule_type: role
  rule_value: { role: "PROGRAM_MANAGER" }

# Client role — role is defined on a specific client (e.g. Registry's
# portal client). AWE does a clientId → UUID lookup, then queries the
# client's role members. Lets AWE integrate with Callers that already
# manage staff roles on their own client.
- rule_type: role
  rule_value:
    role: "PROGRAM_MANAGER"
    client: "registry-staff-portal"
```

At request creation time, AWE calls Keycloak to list the current members of the role and stores the resulting user ids as that stage's candidate approvers. Tasks are created for each — any one can act (or a quorum, if `min_approvals` > 1).

Both are declared in AWE's [helm values](https://gitlab.com/openg2p/awe/-/blob/develop/helm/openg2p-awe/values.yaml) — no post-install manual steps here.

### Why `awe-admin-portal` is a **public** client (and should stay that way)

The `keycloak-init` subchart (≥ `1.1.0-develop`) now honours the `publicClient: true` flag in AWE's helm values, so the admin SPA's client is created as public on first install — no Keycloak UI toggle needed. Worth understanding _why_ we do this before an operator is tempted to "harden" it by flipping Client authentication back on:

> **Why "Client authentication" must be Off for the SPA.** Client authentication means the client sends a stored `client_secret` on every `/token` call. A browser-based single-page app can't keep a secret secret — any JS shipped to the browser is visible in DevTools, so a client\_secret baked in effectively becomes public. OAuth 2.0 best current practice for browser apps is therefore "public client + PKCE": the SPA generates a one-time `code_verifier`/`code_challenge` pair per login, which Keycloak binds to the authorization code and verifies on exchange. Cryptographically equivalent, with no long-lived secret. The K8s `client_secret` that `keycloak-init` generates for this client is unused by the SPA — only our `awe-admin-resolver` service-account client (used by the backend pod, not the browser) needs that confidential flow. References: [RFC 8252 "OAuth 2.0 for Native Apps"](https://datatracker.ietf.org/doc/html/rfc8252), [RFC 7636 "PKCE"](https://datatracker.ietf.org/doc/html/rfc7636), and [OAuth 2.0 Security BCP §2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics).

If you ever do need to fix this by hand (e.g. you're on an older keycloak-init that still hardcoded `publicClient: false`):

```sh
kcadm.sh update clients/$(kcadm.sh get clients -r staff -q clientId=awe-admin-portal --fields id --format csv --noquotes) \
  -r staff \
  -s 'publicClient=true' \
  -s 'webOrigins=["+"]'
```

### Install

AWE is deployed as **one shared instance per environment** — a single
AWE serves all caller modules (Registry, PBMS, …). This is the commons
deployment model; see
[Architecture → deployment topology](technical-architecture.md#deployment-topology-shared-per-environment-default)
for the trade-offs and when a dedicated per-module instance is warranted
instead.

The AWE chart is published to the shared **GitLab** catalogue (`openg2p/charts`),
not the GitHub Helm repo. Use the **numeric project id** — the encoded-path form
breaks Rancher's link resolution. It is public, so no credentials are needed:

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

# One shared AWE per environment, serving all modules.
helm install awe openg2p/openg2p-awe \
  --namespace openg2p --create-namespace \
  --values values-awe.yaml
```

Example `values-awe.yaml`:

```yaml
global:
  aweHostname: awe.trial.openg2p.org
  postgresqlHost: commons-postgresql
  keycloakBaseUrl: https://keycloak.trial.openg2p.org
```

That's the whole override. The Keycloak client's `redirectUris` template references `global.aweHostname`, so changing that one value propagates through to the `awe-admin-portal` client's valid redirects and CORS Web Origins automatically.

Most other settings (issuer URL, JWKS URL, audience, resolver client ID) are also derived from the `global.*` values — no further per-environment overrides needed unless you diverge from the staff-realm convention. See [`helm/openg2p-awe/values.yaml`](https://gitlab.com/openg2p/awe/-/blob/develop/helm/openg2p-awe/values.yaml) for the full set.

> **Note:** the AWE Helm chart is expected to become part of the OpenG2P
> commons bundle (deployed once alongside `commons-postgresql`,
> `commons-keycloak`, etc.). That packaging work is pending — until then,
> install AWE as the standalone release shown above.

#### Operating a shared instance — what to agree up front

Because one AWE serves every module, a few conventions matter:

* **Namespace `policy_key` by module.** `policy_key` is globally unique
  across the shared instance, so each module must prefix its keys
  (`registry.*`, `pbms.*`, …) to avoid collisions. This is a naming
  convention — AWE does not enforce it.
* **AWE admin is global.** `AWE_ADMIN` / `AWE_VIEWER` grant access to
  *every* module's policies and a combined audit log. Hold the admin role
  with a single central (commons) team; don't hand it to individual
  module teams. (If modules need isolated admin, use a dedicated
  per-module instance instead — see the architecture note.)
* **Use UUID idempotency keys.** `Idempotency-Key` is global to the
  instance; callers should use UUIDs so keys from different modules never
  collide.

> **Why explicit redirect URIs (not `*`)?** A wildcard `*` works for Keycloak's _login redirect_ check, but it breaks CORS: Keycloak's `webOrigins: ["+"]` shorthand expands to the non-wildcard entries in the redirect URI list — so with `["*"]` the allowed-origins set ends up empty and the browser silently blocks the SPA's token-exchange POST. The chart ships with a host-templated URL to avoid this footgun.

### Uninstall / teardown

`helm uninstall` removes AWE's workloads but leaves several resources behind by design — things owned by shared commons services (the Postgres database + role in `commons-postgresql`), Helm hook Jobs pinned with `hook-delete-policy: before-hook-creation`, and the keycloak-init client Secrets annotated `helm.sh/resource-policy: keep`. A dedicated tear-down script handles the full cleanup:

```bash
# From the awe repo:
./scripts/uninstall-awe.sh --namespace <ns> --dry-run   # see what would happen
./scripts/uninstall-awe.sh --namespace <ns>             # do it, with confirmation
```

The script runs eight steps in order:

1. `helm uninstall <release>`
2. Delete leftover Jobs + orphan Pods (keycloak-init, postgres-init)
3. Delete the `awe-admin-portal` and `awe-admin-resolver` K8s Secrets (created by keycloak-init with `resource-policy: keep`)
4. Sweep any other Secrets / ConfigMaps carrying the release label
5. Drop the Postgres database + role via `kubectl exec` into `commons-postgresql`
6. Delete PVCs labeled with the release
7. Delete `Released` / orphaned PVs claimed by the namespace
8. _(Optional, behind `--delete-kc-clients`)_ delete the two Keycloak clients themselves via `kcadm.sh` inside the `commons-keycloak` pod

Useful flags:

| Flag                        | What it does                                                                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `--dry-run`                 | Prints every action; changes nothing. Always safe to run first.                                                                 |
| `--yes` / `-y`              | Skips the interactive "type the release name" confirmation — use in CI.                                                         |
| `--release <name>`          | Override the Helm release name (default `awe`).                                                                                 |
| `--postgres-release <name>` | Override the commons-postgresql release (default `commons-postgresql`).                                                         |
| `--keycloak-release <name>` | Override the commons-keycloak release. Only used with `--delete-kc-clients`.                                                    |
| `--delete-kc-clients`       | Also deletes the `awe-admin-portal` + `awe-admin-resolver` clients from the `staff` realm. Skip if another service reuses them. |
| `--keep-kc-secrets`         | Leave the keycloak-init Secrets in place — useful when re-installing immediately and you want the same client secret values.    |
| `--keep-pvs`                | Delete PVCs but not PVs (retain storage for forensic inspection).                                                               |

Prerequisites: `kubectl` (cluster-admin for the namespace), `helm`, `jq`, `bash` 4+.

## Configuration reference

All keys under `awe:` in [`config/default.yaml`](https://gitlab.com/openg2p/awe/-/blob/develop/config/default.yaml). Env-var overrides use `AWE__` prefix with `__` as nested separator, e.g. `AWE__WEBHOOK__MAX_ATTEMPTS=10`.

### Service metadata

| Key           | Default       | Purpose                                                                  |
| ------------- | ------------- | ------------------------------------------------------------------------ |
| `service_id`  | `openg2p.awe` | Envelope `id` in API responses.                                          |
| `api_version` | `1.0`         | Envelope `version`.                                                      |
| `module`      | `default`     | Logical caller module this deployment serves (embedded in audit events). |

### Webhook dispatch

| Key                             | Default                       | Purpose                                              |
| ------------------------------- | ----------------------------- | ---------------------------------------------------- |
| `webhook.timeout_seconds`       | `10`                          | Per-attempt HTTP timeout.                            |
| `webhook.max_attempts`          | `6`                           | Total attempts before marking `exhausted`.           |
| `webhook.backoff_seconds`       | `[60, 300, 900, 3600, 21600]` | Wait before each retry (length = max\_attempts − 1). |
| `webhook.poll_interval_seconds` | `2`                           | How often the dispatcher claims due deliveries.      |
| `webhook.batch_size`            | `20`                          | Max deliveries claimed per tick.                     |

### Resolver

| Key                             | Default | Purpose                                    |
| ------------------------------- | ------- | ------------------------------------------ |
| `resolver.http_timeout_seconds` | `5`     | Timeout for HTTP-rule approver resolution. |

### SLA

| Key                          | Default | Purpose                                          |
| ---------------------------- | ------- | ------------------------------------------------ |
| `sla.check_interval_seconds` | `300`   | SLA monitor tick — scans for expired open tasks. |

### Keycloak

| Key                            | Default              | Purpose                                                               |
| ------------------------------ | -------------------- | --------------------------------------------------------------------- |
| `keycloak.base_url`            | `""` (disabled)      | Keycloak base URL for admin API calls.                                |
| `keycloak.realm`               | `staff`              | Realm shared with Registry / PBMS. AWE provisions its clients here.   |
| `keycloak.admin_client_id`     | `awe-admin-resolver` | Confidential client used for admin API.                               |
| `keycloak.admin_client_secret` | `""`                 | Secret for that client — **never commit; inject via envVarsFrom**.    |
| `keycloak.issuer`              | `""` (dev mode)      | Expected `iss` claim on inbound bearers. Empty disables verification. |
| `keycloak.jwks_url`            | `""`                 | JWKS endpoint for signature verification.                             |
| `keycloak.audience`            | `""`                 | Required `aud` claim. Empty disables audience check.                  |

### Notifier

| Key                     | Default                | Purpose                                |
| ----------------------- | ---------------------- | -------------------------------------- |
| `notifier.enabled`      | `false`                | Enable SMTP emails on task assignment. |
| `notifier.smtp_host`    | `""`                   | SMTP server hostname.                  |
| `notifier.smtp_port`    | `587`                  | SMTP port.                             |
| `notifier.from_address` | `no-reply@openg2p.org` | Envelope `From:` on sent mail.         |
| `notifier.use_tls`      | `true`                 | STARTTLS.                              |

## Operational runbook

### A webhook delivery is stuck in `pending` beyond schedule

Check `last_error` / `last_status_code` in `webhook_delivery`. Common causes:

* **Caller's endpoint returns 4xx on a valid signature** — means the caller's dedup logic or schema validation rejects the payload. Investigate on the caller side.
* **Network timeout** — `last_error` is `ReadTimeout`. Increase `awe.webhook.timeout_seconds` if the caller genuinely needs longer, or make the caller's handler faster (return 202 after queuing).

To force a retry: flip `next_attempt_at` to `now()` in Postgres. The dispatcher picks it up on the next tick.

### A delivery is marked `exhausted`

The caller missed \~24 hours of retries. After fixing the root cause:

```sql
UPDATE webhook_delivery
SET status = 'pending',
    attempt = 0,
    next_attempt_at = now()
WHERE id = '<delivery_id>';
```

### A stage is stuck — no tasks appeared

Symptoms: `approval_request.status = pending` with no matching `approval_task` rows.

Cause: stage resolution failed (Keycloak unreachable, HTTP resolver down, or `on_empty=block` fired). Inspect `approval_event`:

```sql
SELECT event_type, payload, created_at
FROM approval_event
WHERE request_id = '<id>'
ORDER BY created_at;
```

Likely outcomes:

* `request_rejected` with `reason=no_approvers_resolved` — policy issue; add rules or change `on_empty`.
* No event at all after `request_created` — stage resolution threw; check service logs. Cancel the request and recreate once upstream is healthy.

### A request is stuck in `in_review` after all approvers decided

Shouldn't happen — the engine transitions synchronously on decision. If observed, check:

```sql
SELECT action, count(*) FROM approval_decision
WHERE request_id = '<id>' AND stage_order = <current_stage>
GROUP BY action;
```

Compare against `stage.mode` and `stage.mode_value`. If the counts should have triggered a transition, file a bug with the full event timeline.

### Rotating the webhook signing secret

Each caller has one row in `callback_secret`. Rotate by inserting a new row with `status=active` for the same `caller_service` and flipping the old row to `status=rotated`. AWE picks up the new secret on the next webhook delivery (the raw secret is loaded per-delivery — no in-process cache to bust).

Don't forget to deliver the new raw secret to the caller out-of-band (vault, password manager) before cutting over.

## Security considerations

* **Dev mode auth is never reachable in production.** The Helm chart values set a non-empty `awe.keycloak.issuer`. If you override to empty, your deployment accepts unsigned JWTs — don't.
* **`awe-admin-resolver` client secret** must be injected via `envVarsFrom` from a Kubernetes Secret; never commit it to values files.
* **Webhook signatures** are the caller's only line of defence against a spoofed AWE URL. Callers must reject deliveries without a valid `X-Approval-Signature` and reject replays (dedup on `event_id`, reject deliveries with a stale `X-Approval-Timestamp`).
* **Authorization scope** — the `awe-admin` realm role gates policy CRUD and request cancellation. Any valid token can read requests / events / tasks; task decisions require the token's `sub` to match the task's `assignee` (or `awe-admin` as an escape hatch for ops).
* **Audit of policy changes** — `approval_policy.created_by` records who created each version; activation events are reflected in the audit log. Pair with [Audit Manager](../audit-manager/) for long-term retention of these admin actions.
* **TLS** is terminated by the ingress (Istio gateway in the shipped chart); in-cluster traffic uses plain HTTP between gateway and pod. Runtime requests from callers must use the public HTTPS endpoint.
