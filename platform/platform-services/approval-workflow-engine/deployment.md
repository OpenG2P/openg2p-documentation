---
description: >-
  Deployment guide for the Approval Workflow Engine — local development with
  Docker Compose, Helm chart installation, configuration reference, Keycloak
  prerequisites, operational runbook, and security considerations.
---

# Deployment

## Local development

### With Docker Compose (one command)

```bash
docker compose up --build
```

Starts Postgres and the AWE service. After a few seconds:

* API: http://localhost:8000/v1/awe/
* Swagger: http://localhost:8000/v1/awe/docs
* Health: http://localhost:8000/v1/awe/health

Dev-mode auth is enabled — the Keycloak `issuer` is empty in
[`config/default.yaml`](https://github.com/OpenG2P/awe/blob/develop/config/default.yaml),
so the service accepts any unsigned JWT. **Never run this
configuration in production** — the Helm chart sets a non-empty issuer
which forces JWKS signature verification.

### Smoke test (create policy → request → approve)

```bash
# Dev token with the awe-admin role — accepted by dev-mode auth.
TOKEN='eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkZXYtYWRtaW4iLCJlbWFpbCI6ImRldkBsb2NhbCIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJhd2UtYWRtaW4iXX19.'

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

Open http://localhost:5173/v1/awe/admin/ — Vite proxies API calls to
the uvicorn instance on :8000.

## Kubernetes install via Helm

### Prerequisites

* Kubernetes 1.23+
* **PostgreSQL** reachable from the cluster (shared Postgres is fine).
  The chart's `postgres-init` subchart creates the database and user;
  it does **not** provision the Postgres server itself.
* **Keycloak**, deployed separately (via the commons-keycloak chart,
  shared with Registry / PBMS). AWE's clients and roles are
  provisioned on install by the `keycloak-init` subchart — see below.
* (If used) Istio for the VirtualService / Gateway templates.

### What the Keycloak integration provisions

On install, the `keycloak-init` subchart creates two clients under the
shared **`staff`** realm (this realm is created by the commons-keycloak
install; AWE just adds to it — it does not own it):

| Client               | Purpose                                                                                       | Type                             |
| -------------------- | --------------------------------------------------------------------------------------------- | -------------------------------- |
| `awe-admin-portal`   | OIDC login for the bundled admin SPA. Carries the `awe-admin` client role.                    | Public (browser redirect flow)   |
| `awe-admin-resolver` | Service account used by AWE to call Keycloak admin API for `role:` / `group:` approver rules. | Confidential (client credentials) |

Client roles provisioned on `awe-admin-portal`:

* `awe-admin` — gates policy CRUD and request cancellation

The commons `admin` user is mapped to `awe-admin` so you can
authenticate into the admin SPA out of the box. Grant the role to any
other users via the Keycloak admin UI.

**One manual step after install** (skip if your policies only use
`user:` / `expression:` / `http:` approver rules — this is only needed
for `role:` and `group:` rule resolution):

1. Open the Keycloak admin UI → realm `staff` → client
   `awe-admin-resolver` → **Service accounts** tab
2. Assign these realm-management roles to the service account:
   `view-users`, `query-groups`
3. (Alternatively, run `kcadm.sh add-roles --uusername
   service-account-awe-admin-resolver -r staff
   --cclientid realm-management --rolename view-users --rolename
   query-groups`)

keycloak-init v1.1.0 provisions clients + client roles + user
role-mappings but does not attach service-account roles, so this has
to be done out-of-band.

### Install

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

# Per-module install (one AWE deployment per caller — see Architecture).
helm install registry-awe openg2p/openg2p-awe \
  --namespace openg2p --create-namespace \
  --values values-registry-awe.yaml
```

Example `values-registry-awe.yaml`:

```yaml
global:
  aweHostname: awe.registry.trial.openg2p.org
  postgresqlHost: commons-postgresql
  keycloakBaseUrl: https://keycloak.trial.openg2p.org
  keycloakRealm: openg2p

awe:
  appConfig:
    module: registry
```

Most settings (issuer URL, JWKS URL, audience, resolver client ID) are
derived from the `global.*` values by the chart — no per-environment
overrides needed unless you diverge from the staff-realm convention.
See [`helm/openg2p-awe/values.yaml`](https://github.com/OpenG2P/awe/blob/develop/helm/openg2p-awe/values.yaml)
for the full set.

## Configuration reference

All keys under `awe:` in [`config/default.yaml`](https://github.com/OpenG2P/awe/blob/develop/config/default.yaml).
Env-var overrides use `AWE__` prefix with `__` as nested separator, e.g.
`AWE__WEBHOOK__MAX_ATTEMPTS=10`.

### Service metadata

| Key              | Default             | Purpose                                                                  |
| ---------------- | ------------------- | ------------------------------------------------------------------------ |
| `service_id`     | `openg2p.awe`       | Envelope `id` in API responses.                                          |
| `api_version`    | `1.0`               | Envelope `version`.                                                      |
| `module`         | `default`           | Logical caller module this deployment serves (embedded in audit events). |

### Webhook dispatch

| Key                          | Default                              | Purpose                                              |
| ---------------------------- | ------------------------------------ | ---------------------------------------------------- |
| `webhook.timeout_seconds`    | `10`                                 | Per-attempt HTTP timeout.                            |
| `webhook.max_attempts`       | `6`                                  | Total attempts before marking `exhausted`.           |
| `webhook.backoff_seconds`    | `[60, 300, 900, 3600, 21600]`        | Wait before each retry (length = max\_attempts − 1). |
| `webhook.poll_interval_seconds` | `2`                               | How often the dispatcher claims due deliveries.      |
| `webhook.batch_size`         | `20`                                 | Max deliveries claimed per tick.                     |

### Resolver

| Key                             | Default | Purpose                                     |
| ------------------------------- | ------- | ------------------------------------------- |
| `resolver.http_timeout_seconds` | `5`     | Timeout for HTTP-rule approver resolution.  |

### SLA

| Key                         | Default | Purpose                                          |
| --------------------------- | ------- | ------------------------------------------------ |
| `sla.check_interval_seconds` | `300`   | SLA monitor tick — scans for expired open tasks. |

### Keycloak

| Key                                 | Default                | Purpose                                                               |
| ----------------------------------- | ---------------------- | --------------------------------------------------------------------- |
| `keycloak.base_url`                 | `""` (disabled)        | Keycloak base URL for admin API calls.                                |
| `keycloak.realm`                    | `staff`                | Realm shared with Registry / PBMS. AWE provisions its clients here.  |
| `keycloak.admin_client_id`          | `awe-admin-resolver`   | Confidential client used for admin API.                               |
| `keycloak.admin_client_secret`      | `""`                   | Secret for that client — **never commit; inject via envVarsFrom**.    |
| `keycloak.issuer`                   | `""` (dev mode)        | Expected `iss` claim on inbound bearers. Empty disables verification. |
| `keycloak.jwks_url`                 | `""`                   | JWKS endpoint for signature verification.                             |
| `keycloak.audience`                 | `""`                   | Required `aud` claim. Empty disables audience check.                  |

### Notifier

| Key                          | Default              | Purpose                                    |
| ---------------------------- | -------------------- | ------------------------------------------ |
| `notifier.enabled`           | `false`              | Enable SMTP emails on task assignment.     |
| `notifier.smtp_host`         | `""`                 | SMTP server hostname.                      |
| `notifier.smtp_port`         | `587`                | SMTP port.                                 |
| `notifier.from_address`      | `no-reply@openg2p.org` | Envelope `From:` on sent mail.           |
| `notifier.use_tls`           | `true`               | STARTTLS.                                  |

### Admin UI

| Key                    | Default          | Purpose                                                     |
| ---------------------- | ---------------- | ----------------------------------------------------------- |
| `admin_ui.enabled`     | `true`           | Mount the bundled SPA if built into the image.              |
| `admin_ui.mount_path`  | `/v1/awe/admin`  | Path at which the SPA is served (matches Istio VirtualService). |

## Operational runbook

### A webhook delivery is stuck in `pending` beyond schedule

Check `last_error` / `last_status_code` in `webhook_delivery`. Common
causes:

* **Caller's endpoint returns 4xx on a valid signature** — means the
  caller's dedup logic or schema validation rejects the payload.
  Investigate on the caller side.
* **Network timeout** — `last_error` is `ReadTimeout`. Increase
  `awe.webhook.timeout_seconds` if the caller genuinely needs longer,
  or make the caller's handler faster (return 202 after queuing).

To force a retry: flip `next_attempt_at` to `now()` in Postgres. The
dispatcher picks it up on the next tick.

### A delivery is marked `exhausted`

The caller missed ~24 hours of retries. After fixing the root cause:

```sql
UPDATE webhook_delivery
SET status = 'pending',
    attempt = 0,
    next_attempt_at = now()
WHERE id = '<delivery_id>';
```

### A stage is stuck — no tasks appeared

Symptoms: `approval_request.status = pending` with no matching
`approval_task` rows.

Cause: stage resolution failed (Keycloak unreachable, HTTP resolver
down, or `on_empty=block` fired). Inspect `approval_event`:

```sql
SELECT event_type, payload, created_at
FROM approval_event
WHERE request_id = '<id>'
ORDER BY created_at;
```

Likely outcomes:

* `request_rejected` with `reason=no_approvers_resolved` — policy issue;
  add rules or change `on_empty`.
* No event at all after `request_created` — stage resolution threw;
  check service logs. Cancel the request and recreate once upstream is
  healthy.

### A request is stuck in `in_review` after all approvers decided

Shouldn't happen — the engine transitions synchronously on decision.
If observed, check:

```sql
SELECT action, count(*) FROM approval_decision
WHERE request_id = '<id>' AND stage_order = <current_stage>
GROUP BY action;
```

Compare against `stage.mode` and `stage.mode_value`. If the counts
should have triggered a transition, file a bug with the full event
timeline.

### Rotating the webhook signing secret

Each caller has one row in `callback_secret`. Rotate by inserting a new
row with `status=active` for the same `caller_service` and flipping the
old row to `status=rotated`. AWE picks up the new secret on the next
webhook delivery (the raw secret is loaded per-delivery — no in-process
cache to bust).

Don't forget to deliver the new raw secret to the caller out-of-band
(vault, password manager) before cutting over.

## Security considerations

* **Dev mode auth is never reachable in production.** The Helm chart
  values set a non-empty `awe.keycloak.issuer`. If you override to
  empty, your deployment accepts unsigned JWTs — don't.
* **`awe-admin-resolver` client secret** must be injected via
  `envVarsFrom` from a Kubernetes Secret; never commit it to values
  files.
* **Webhook signatures** are the caller's only line of defence against a
  spoofed AWE URL. Callers must reject deliveries without a valid
  `X-Approval-Signature` and reject replays (dedup on `event_id`,
  reject deliveries with a stale `X-Approval-Timestamp`).
* **Authorization scope** — the `awe-admin` realm role gates policy
  CRUD and request cancellation. Any valid token can read requests /
  events / tasks; task decisions require the token's `sub` to match the
  task's `assignee` (or `awe-admin` as an escape hatch for ops).
* **Audit of policy changes** — `approval_policy.created_by` records
  who created each version; activation events are reflected in the
  audit log. Pair with [Audit Manager](../audit-manager/) for
  long-term retention of these admin actions.
* **TLS** is terminated by the ingress (Istio gateway in the shipped
  chart); in-cluster traffic uses plain HTTP between gateway and pod.
  Runtime requests from callers must use the public HTTPS endpoint.
