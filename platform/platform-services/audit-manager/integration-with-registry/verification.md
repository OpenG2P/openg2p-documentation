---
description: >-
  End-to-end smoke test confirming the Staff Portal API → Audit Manager
  integration works: a Keycloak-authenticated API call lands as a row in the
  cluster's audit_events table within seconds, with the f
---

# Verification — End to End

## What this page proves

Once the AuditMiddleware is wired in (see [Audit Middleware](audit-middleware.md)) and you've completed [Local Install — Staff Portal API](local-install.md), this page walks through the smoke test that confirms every link in the chain is alive:

```
curl  →  Staff Portal API (laptop)
            │
            ▼
       AuditMiddleware (records actor + outcome)
            │
            ▼  fire-and-forget asyncio.create_task
       HTTP POST  →  Audit Manager  (port-forwarded from cluster)
            │
            ▼
       Kafka  →  Audit consumer  →  PostgreSQL  →  audit_events row
```

If the row appears as expected, you have full validation of: authentication propagation, middleware ordering, fire-and-forget emission, CloudEvents schema correctness, audit-manager ingest, Kafka buffering, consumer write, and PostgreSQL column promotion.

## Pre-flight

Three things must already be running:

```bash
# 1. Local Postgres for staff portal (Phase 2 of local-install)
docker ps | grep pg-staff

# 2. Cluster Keycloak port-forwarded
kubectl get svc -A | grep keycloak     # confirm reachability
# In a separate terminal:
kubectl -n <ns> port-forward svc/<keycloak-svc> 8080:80

# 3. Cluster IAM port-forwarded
# In a separate terminal:
kubectl -n <ns> port-forward svc/<iam-svc> 9090:80
```

And one new thing for this verification:

```bash
# 4. Cluster Audit Manager port-forwarded
kubectl -n trial port-forward svc/audit-manager 8002:80

# Sanity check — should return 200 with {"status":"UP"}
curl -i http://localhost:8002/v1/auditmanager/health
```

## Configure staff portal to emit

Add to `~/sp-local/.env` (or wherever your `.env` lives):

```bash
REGISTRY_STAFF_PORTAL_API_AUDIT_ENABLED=true
REGISTRY_STAFF_PORTAL_API_AUDIT_MANAGER_URL=http://localhost:8002
# Optional: set to false to suppress audits of rejected anonymous calls.
# REGISTRY_STAFF_PORTAL_API_AUDIT_ANONYMOUS_FAILURES=false
```

Restart uvicorn:

```bash
cd ~/sp-local && source .venv/bin/activate
uvicorn openg2p_registry_staff_portal_api.main:app \
  --host 0.0.0.0 --port 8001 --reload
```

The startup log should include exactly this line — that's how you know the middleware is active:

```
AuditMiddleware enabled — emitting to http://localhost:8002/v1/auditmanager/events (audit_anonymous_failures=True)
```

If you see `AuditMiddleware disabled (...)` instead, the env vars didn't take. Confirm `.env` is in the directory you ran uvicorn from.

## Test 1 — authenticated call

Get a fresh Keycloak token (5-minute lifespan):

```bash
KEYCLOAK=http://localhost:8080
REALM=staff
CLIENT_ID=registry-staff-portal
CLIENT_SECRET=<from-keycloak-client-credentials-tab>
USERNAME=admin
PASSWORD=<admin-password>

TOKEN=$(curl -sX POST \
  "$KEYCLOAK/realms/$REALM/protocol/openid-connect/token" \
  -H 'content-type: application/x-www-form-urlencoded' \
  -d "grant_type=password" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "username=$USERNAME" \
  -d "password=$PASSWORD" \
  | jq -r '.access_token')
```

Hit any authenticated endpoint:

```bash
curl -i -X POST http://localhost:8001/registry-config/get_registry_configuration \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{}'
```

A `400 Bad Request` with field-required errors is **success for this test** — it means auth passed, the handler ran, and (more importantly) the audit middleware fired with `outcome=failure`.

Wait \~3 seconds, then query the cluster's audit Postgres:

```bash
kubectl -n trial exec -it commons-postgresql-0 -- \
  psql -U postgres -d audit_manager -c \
  "SELECT
     actor_id,
     actor_type,
     action,
     outcome,
     details->'actor'->>'name'     AS name,
     details->'actor'->>'username' AS username,
     details->'actor'->'roles'     AS roles,
     details->'actor'->>'ip'       AS ip,
     details->'context'->>'api'    AS api
   FROM audit_events
   WHERE source = '/openg2p/registry-staff-portal-api'
   ORDER BY ingested_at DESC LIMIT 1;"
```

Expected row:

| Column       | Expected value                                                       |
| ------------ | -------------------------------------------------------------------- |
| `actor_id`   | Keycloak `sub` UUID, e.g. `de7cf744-206a-4b0f-9d82-eec3a1dbb808`     |
| `actor_type` | `user`                                                               |
| `action`     | `get` (first word of the function name `get_registry_configuration`) |
| `outcome`    | `failure` (because the empty body returned 400)                      |
| `name`       | `Admin User` (from JWT `name` claim)                                 |
| `username`   | `admin` (from JWT `preferred_username` claim)                        |
| `roles`      | `["Operations Administrator", "Technical Administrator"]`            |
| `ip`         | `127.0.0.1`                                                          |
| `api`        | `POST /registry-config/get_registry_configuration`                   |

## Test 2 — rejected anonymous call

Hit the same endpoint **without** a token:

```bash
curl -i -X POST http://localhost:8001/registry-config/get_registry_configuration \
  -H "Content-Type: application/json" -d '{}'
```

Expected: `401 Unauthorized` (the endpoint is permission-protected; an anonymous call gets rejected by `AuthMiddleware`).

Wait \~3 seconds, then query again — last row:

```sql
SELECT actor_id, actor_type, outcome, details->'actor'->>'ip' AS ip,
       details->'context'->>'http_status' AS http_status
FROM audit_events
WHERE source = '/openg2p/registry-staff-portal-api'
ORDER BY ingested_at DESC LIMIT 1;
```

Expected row:

| Column        | Expected value |
| ------------- | -------------- |
| `actor_id`    | `anonymous`    |
| `actor_type`  | `anonymous`    |
| `outcome`     | `denied`       |
| `ip`          | `127.0.0.1`    |
| `http_status` | `401`          |

This proves the rejected-anonymous-attempt path is captured. To suppress this path, set `AUDIT_ANONYMOUS_FAILURES=false` in `.env` and restart uvicorn — repeat the `curl`, and you should see no new audit row for it.

## Test 3 — successful anonymous call (should NOT be audited)

Hit `/ping`:

```bash
curl -i http://localhost:8001/ping
```

Expected: `200 pong` — and **no** new audit row, because `/ping` is in the middleware's hard-coded skip-list.

```sql
-- Confirm: the LAST audit row is still the one from Test 1 or 2,
-- not a new one for /ping.
SELECT id, type, occurred_at
FROM audit_events
WHERE source = '/openg2p/registry-staff-portal-api'
ORDER BY ingested_at DESC LIMIT 3;
```

## Troubleshooting matrix

| Symptom                                                           | Likely cause                                               | Fix                                                                                                        |
| ----------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Uvicorn log says `AuditMiddleware disabled (...). No-op.`         | `.env` not loaded, or `AUDIT_ENABLED!=true`, or URL empty  | Confirm cwd and the env vars; restart uvicorn                                                              |
| HTTP `curl` returns expected status, but no audit row appears     | Audit-manager unreachable / port-forward died              | Check `curl http://localhost:8002/v1/auditmanager/health` returns 200                                      |
| Uvicorn logs show `Audit emission failed for event ...`           | Audit-manager URL wrong, or it returned 503 (backpressure) | Inspect the log line; fix URL or wait for audit-manager to recover                                         |
| Row appears but `details.actor.name` is missing                   | Old audit-manager image without the `_compute_details` fix | Confirm deployed image tag includes the fix; `kubectl rollout restart deploy/audit-manager`                |
| Anonymous call audited even with `AUDIT_ANONYMOUS_FAILURES=false` | Setting didn't reload                                      | Restart uvicorn after changing the env var                                                                 |
| `actor_id=anonymous` for a 403 with a valid token                 | Audit-manager image lacks the JWT-decode-on-403 path       | Confirm staff-portal-api has the latest `audit_middleware.py` (the JWT-decode helper). Rebuild + redeploy. |

## Cleaning up old test rows

If repeated experiments have left noise in `audit_events`, prune selectively:

```sql
DELETE FROM audit_events
WHERE source = '/openg2p/registry-staff-portal-api'
  AND occurred_at < now() - interval '1 hour';
```
