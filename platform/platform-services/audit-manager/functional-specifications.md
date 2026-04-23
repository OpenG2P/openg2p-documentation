---
description: >-
  Event schema (CloudEvents envelope + OpenG2P data conventions), mapping to
  Postgres columns, how to emit audit events from API calls, naming
  conventions, and PII handling.
---

# Functional Specifications

## Event schema

All events follow the **CloudEvents v1.0** specification
(https://cloudevents.io/ — CNCF graduated standard). The envelope is
canonical across all OpenG2P services; the `data` block is event-type
specific.

### Envelope (required attributes)

| Field             | Type    | Purpose                                                 |
| ----------------- | ------- | ------------------------------------------------------- |
| `specversion`     | string  | Always `"1.0"`                                          |
| `id`              | string  | Unique event id (ULID or UUIDv7 recommended); dedup key |
| `source`          | string  | Emitting service, e.g. `/openg2p/beneficiary-service`   |
| `type`            | string  | Reverse-DNS event type, e.g. `org.openg2p.auth.login`   |
| `time`            | RFC3339 | When the event occurred, as seen by the emitter         |
| `datacontenttype` | string  | Always `application/json`                               |
| `data`            | object  | OpenG2P-specific payload (see below)                    |

Optional top-level fields:

| Field         | Purpose                                                   |
| ------------- | --------------------------------------------------------- |
| `subject`     | Primary object acted on, e.g. `beneficiary/b_1029384756`  |
| `traceparent` | W3C trace-context header for correlating with logs/traces |

### `data` block — OpenG2P conventions

Three sub-fields are **always required**, giving every event a consistent
"who did what, and did it work" triple:

| Field     | Type   | Values                                          |
| --------- | ------ | ----------------------------------------------- |
| `actor`   | object | Who triggered the event (user/system/service)   |
| `action`  | string | Verb: `login`, `read`, `update`, `approve`, ... |
| `outcome` | enum   | `success` \| `failure` \| `denied`              |

One sub-field is **strongly recommended when applicable**:

| Field      | Type   | Purpose                                        |
| ---------- | ------ | ---------------------------------------------- |
| `resource` | object | The object acted on, e.g. beneficiary, payment |

Anything else (`changes`, `reason`, `context`, domain-specific fields)
lives in `data` as event-type-specific attributes.

### Actor shape

```json
{
  "type": "user",              // "user" | "system" | "service" | "anonymous"
  "id": "u_4421",              // stable identifier
  "name": "fatima.k",          // optional display name
  "roles": ["program.operator"],
  "ip": "10.2.14.88",
  "session_id": "sess_93ka..."
}
```

## Mapping from CloudEvents to Postgres columns

The service validates the full CloudEvents input and then persists a flat
row. Some envelope fields are validated but **not stored** (they don't add
signal to a forensic query). The `audit_events` table has exactly 15
columns — every input field either maps to one of them or is dropped.

| CloudEvents input field                                       | Stored as (DB column) | Notes                                                                                             |
| ------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------- |
| `specversion`                                                 | — (dropped)           | Validated (`"1.0"`), not stored — same for every row.                                             |
| `datacontenttype`                                             | — (dropped)           | Always `application/json` — no information to preserve.                                           |
| `id`                                                          | `id`                  | Primary key (together with `occurred_at`) — dedup on replay.                                      |
| `source`                                                      | `source`              | Which service emitted the event.                                                                  |
| `type`                                                        | `type`                | Reverse-DNS event type.                                                                           |
| `time`                                                        | `occurred_at`         | Renamed on store — consistent with `ingested_at` naming.                                          |
| `subject`                                                     | `subject`             | Primary object acted on; nullable.                                                                |
| `traceparent`                                                 | `trace_id`            | Only the 16-byte trace id is extracted from the W3C header.                                       |
| `data.actor.type`                                             | `actor_type`          | `user` \| `system` \| `service` \| `anonymous`.                                                   |
| `data.actor.id`                                               | `actor_id`            | Stable actor identifier.                                                                          |
| `data.actor.*` (other fields)                                 | `details.actor.*`     | Remaining actor fields (name, roles, ip, session\_id) preserved under `details`.                  |
| `data.action`                                                 | `action`              | Verb.                                                                                             |
| `data.outcome`                                                | `outcome`             | `success` \| `failure` \| `denied`.                                                               |
| `data.reason`                                                 | `reason`              | Promoted — common filter for failure / denied outcomes.                                           |
| `data.resource.type`                                          | `resource_type`       | Nullable (login events have no resource).                                                         |
| `data.resource.id`                                            | `resource_id`         | Nullable.                                                                                         |
| `data.resource.*` (extras)                                    | `details.resource.*`  | Remaining resource attributes (amount, currency, program\_id, etc.).                              |
| `data.changes` / `data.context` / other event-specific fields | `details.*`           | Event-type-specific extras carried in `details` JSONB.                                            |
| — (server-assigned)                                           | `ingested_at`         | `DEFAULT now()` at insert time; useful for "recent arrivals" queries distinct from `occurred_at`. |

**Columns in the DB that aren't input fields:** only `ingested_at`, set by
Postgres `DEFAULT now()` at insert time.

**Input fields that don't produce a column:** `specversion`,
`datacontenttype` (both are always the same value and carry no forensic
signal).

## Emitting events from API calls

The common case for OpenG2P is: a service's REST API handler emits one
audit event per incoming call — capturing *who* called, *which* API, *on
which entity*, and *the outcome*. This is distinct from recording data
changes (field diffs, version history) — those are tracked separately. The
audit event answers *"did this call happen?"* not *"what did the data look
like before and after?"*.

Given what a handler has at the moment of the call:

| You have                                  | Goes into                                                   |
| ----------------------------------------- | ----------------------------------------------------------- |
| User from auth token (id, name, roles)    | `data.actor.{type, id, name, roles}`                        |
| Module name                               | `source` (as `/openg2p/<module>`) and `data.context.module` |
| API name (HTTP method + path)             | `data.context.api`                                          |
| Path param `{id}` for the primary entity  | `data.resource.{type, id}` and top-level `subject`          |
| HTTP response status code                 | `data.context.http_status` (drives `outcome`)               |
| Response error reason (on failure/denied) | `data.reason`                                               |

**Outcome rule:** `2xx` → `success`, `401/403` → `denied` (+ `reason`),
other `4xx/5xx` → `failure` (+ `reason`).

**`subject` vs `data.resource` — both refer to the primary entity but in
different shapes.** `subject` is a single string, part of the CloudEvents
envelope — used by generic event-bus tooling for filtering and routing.
`data.resource` is a structured `{ type, id, ...extras }` object — its
`type` and `id` land in the flat, indexed DB columns `resource_type` and
`resource_id`, so it's what forensic SQL queries actually use. Keep them
consistent (same type, same id). If the entity has extra attributes worth
capturing (e.g. a payment's `amount`, `currency`, `beneficiary_id`), put
them on `data.resource` only — those extras flow into the `details` JSONB
column.

### Example A — user logs in (`POST /v1/auth/login`, outcome = success)

```json
{
  "specversion": "1.0",
  "id": "01HXQ9R2V...",
  "source": "/openg2p/auth",
  "type": "org.openg2p.auth.login",
  "time": "2026-04-23T09:00:12Z",
  "data": {
    "actor":   { "type": "user", "id": "u_4421", "name": "fatima.k", "ip": "10.2.14.88" },
    "action":  "login",
    "outcome": "success",
    "context": {
      "api":    "POST /v1/auth/login",
      "module": "auth"
    }
  }
}
```

DB row ends up as: `actor_id = u_4421`, `type = org.openg2p.auth.login`,
`outcome = success`, no `resource_*`, and `details.context` preserved
intact (`{"api": "POST /v1/auth/login", "module": "auth"}`).

### Example B — creating a beneficiary (`POST /v1/beneficiary/register`, 201)

```json
{
  "specversion": "1.0",
  "id": "01HXQ9R2X...",
  "source": "/openg2p/beneficiary-service",
  "type": "org.openg2p.beneficiary.created",
  "subject": "beneficiary/b_1029384756",
  "time": "2026-04-23T09:02:30Z",
  "data": {
    "actor":    { "type": "user", "id": "u_4421", "roles": ["registrar"] },
    "action":   "create",
    "outcome":  "success",
    "resource": { "type": "beneficiary", "id": "b_1029384756" },
    "context": {
      "api":         "POST /v1/beneficiary/register",
      "module":      "beneficiary-service",
      "http_status": 201,
      "request_id":  "req_8f2b..."
    }
  }
}
```

No `changes[]` field — because data-version tracking lives elsewhere. The
audit records that `u_4421` called this API successfully against
`b_1029384756`; the actual diff of before/after values is not duplicated
here.

### Example C — call denied (`PUT /v1/beneficiary/{id}`, 403)

Same API as an update, but the caller lacks the required role. The update
never happens — still, we emit the event so investigators can find
attempted unauthorised actions with a single indexed query on `outcome`.

```json
{
  "specversion": "1.0",
  "id": "01HXQ9R31...",
  "source": "/openg2p/beneficiary-service",
  "type": "org.openg2p.beneficiary.updated",
  "subject": "beneficiary/b_1029384756",
  "time": "2026-04-23T09:12:00Z",
  "data": {
    "actor":    { "type": "user", "id": "u_7777", "roles": ["viewer.basic"] },
    "action":   "update",
    "outcome":  "denied",
    "reason":   "insufficient_role",
    "resource": { "type": "beneficiary", "id": "b_1029384756" },
    "context": {
      "api":         "PUT /v1/beneficiary/b_1029384756",
      "module":      "beneficiary-service",
      "http_status": 403
    }
  }
}
```

DB row: `outcome = denied`, `reason = insufficient_role` — both are flat
indexed columns, so this finds the record in milliseconds:

```sql
SELECT occurred_at, actor_id, type, resource_id, reason
FROM audit_events
WHERE outcome = 'denied'
  AND occurred_at > now() - interval '24 hours';
```

### Practical emit — one line per handler

```python
# in a FastAPI middleware or dependency
audit.emit(CloudEvent(
    source=f"/openg2p/{MODULE}",
    type=f"org.openg2p.{MODULE}.{VERB}",
    subject=f"{resource_type}/{resource_id}" if resource_id else None,
    data=AuditData(
        actor=Actor(
            type="user", id=user.id, name=user.name,
            roles=user.roles, ip=request.client.host,
        ),
        action=VERB_TO_ACTION[VERB],
        outcome=outcome_from_status(response.status_code),
        reason=error_reason if outcome != "success" else None,
        resource=Resource(type=resource_type, id=resource_id) if resource_id else None,
        context={
            "api":         f"{request.method} {request.url.path}",
            "module":      MODULE,
            "http_status": response.status_code,
            "request_id":  request.headers.get("x-request-id"),
        },
    ),
))
```

This is idiomatic for FastAPI — a single middleware can emit for every API
call, and hand-written emits only happen for events that aren't 1:1 with
an HTTP call (e.g. a scheduled reconciliation job).

## Naming conventions for `type`

* Lowercase, reverse-DNS: `org.openg2p.<domain>.<past_participle_verb>`
* One type = one fixed `data` shape. To change the shape, bump the type
  (`org.openg2p.beneficiary.updated.v2`). Never repurpose a type.
* Canonical verbs: `created`, `updated`, `deleted`, `viewed`, `login`,
  `logout`, `login_failed`, `approved`, `rejected`, `reversed`, `enrolled`.

## PII handling

* **Never** put PII in `type`, `subject`, `actor.id` prefix, or any other
  field that is indexed or logged.
* PII belongs inside `data.resource` / `data.changes`, where it can be
  redacted or encrypted per field before emit.
* Event-type-specific extras (diffs, amounts, context) are stored in the
  `details` JSONB column. Access to `details` should be restricted in
  production since it may carry PII from `changes[]`.

## FAQ

**Can I emit events from Odoo?** Yes — Odoo makes an HTTP POST to
`/v1/auditmanager/events`. Use Odoo's `queue_job` (OCA) so the call is
async and retried on transient failure. The same CloudEvents payload works
unchanged.

**What if my service is not Python?** HTTP is the universal integration.
Any language that can POST JSON works. We may publish small SDKs later for
convenience, but they are not required.

**Can I query the audit store from a UI?** Not from this service. Audit
data is intentionally not exposed via a UI in this release; investigators
query Postgres directly. A separate, read-only `audit-query` service
(different auth boundary) can be added when a real need appears.

**What happens if I replay a Kafka message?** Nothing user-visible. Inserts
use `ON CONFLICT (id, occurred_at) DO NOTHING` so duplicates are silently
absorbed.

**Can I change the event schema for one type?** No — treat schemas as
immutable once in production. To evolve, create a new type
(`org.openg2p.beneficiary.updated.v2`). Old events stay queryable; new
consumers handle both. This keeps the forensic record honest.

**Does this service log the events it audits?** No. It logs operational
events (startup, shutdown, errors, DLQ). It does not log the audit payloads
themselves — those would duplicate the audit store into the regular log
pipeline, which is exactly what we're trying to avoid.
