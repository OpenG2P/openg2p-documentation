---
description: >-
  How Inji Certify gets the citizen's claims in Phase 1 — the stock Postgres
  DataProvider plugin reading a phone-keyed view inside Certify's database,
  with the authorization-code token subject as the lookup key.
---

# Registry Data Connector (Phase 1: DB-direct)

In the hosted-wallet (pull) model, Certify receives a **token** and must source the citizen's
claims. **Phase 1 uses the stock `PostgresDataProviderPlugin`** — no custom Certify code — reading
a **phone-keyed view** that exposes the Registry data inside Certify's database.

## How the stock Postgres plugin works

* Plugin selection: `mosip.certify.integration.data-provider-plugin=PostgresDataProviderPlugin`.
* You configure **one SQL query per credential scope**:
  ```properties
  mosip.certify.data-provider-plugin.postgres.scope-query-mapping={\
    'registry_vc_ldp': 'select full_name, date_of_birth, gender, functional_id \
                         from certify.beneficiary_vc_view where phone = :id'\
  }
  ```
* At issuance the plugin runs: `query.setParameter("id", identityDetails.get("sub"))` — i.e.
  **`:id` is bound to the access token's `sub` claim**, and the query is chosen by the token's
  `scope`. The returned columns become the VC fields.

This yields **two hard requirements** that shape the Phase-1 design.

## Requirement 1 — the token `sub` must be the phone number

The plugin binds `:id` to **`sub`** only (it does not read `phone_number` or any other claim). So
for a phone-based lookup, **Logto must issue the access token with `sub` = the citizen's phone
number** (the phone is the citizen's Logto username and login identifier).

* **Action:** configure Logto so the subject identifier presented to Certify is the **phone
  number**. (Verify Logto's behaviour — if `sub` is an opaque user id instead, the stock plugin
  cannot key on phone, and you would need the custom REST connector below or a Logto/identifier
  adaptation.)
* The citizen always logs in via **phone + OTP**; full name etc. are profile attributes, but the
  **identifier used here is the phone number**.

## Requirement 2 — the data must live inside Certify's database

The Postgres plugin uses Certify's **own** `EntityManager` (no separate datasource); its native
query runs on **Certify's database connection**. Since Certify's DB and the registry's `registrydb`
are **separate databases**, the registry data must be **made reachable inside Certify's DB**. Pick
one:

| Approach | What it is | Freshness | Setup |
|---|---|---|---|
| **A. PostgreSQL FDW (recommended)** | `postgres_fdw` foreign tables in Certify's DB pointing at the registry tables, wrapped in a read-only **view** | Live | DBA: create FDW server + user mapping + grants |
| **B. Replicated/synced table** | A job copies the needed fields into a `certify.*` table | Periodic/event | A sync pipeline |
| **C. Same database, different schema** | If Certify shares the *same database* as the registry, a cross-schema view + `SELECT` grants | Live | Grants only (only if same DB) |

In all cases, expose a **read-only view** — e.g. `certify.beneficiary_vc_view` — that surfaces
**only the VC-relevant columns**, keyed by **phone**, and **filters to active records**.

```sql
-- illustrative view (over FDW foreign tables or a synced copy)
CREATE VIEW certify.beneficiary_vc_view AS
SELECT phone, full_name, date_of_birth, gender, functional_id
FROM   <registry-foreign-or-synced-tables>
WHERE  status = 'active';
```

## Lookup behaviour (the cases you asked for)

With `... where phone = :id` against the active-only view:

| Case | Query result | Outcome |
|---|---|---|
| Phone maps 1:1 to an **active** record | 1 row | Claims returned → VC issued |
| **No** record for the phone | 0 rows | Plugin throws *No Data Found* → Certify error → portal shows "no eligible record" |
| Record exists but **inactive** | 0 rows (filtered) | Same as above — treated as not eligible |

* The **one-to-one phone → functional ID** assumption is enforced by the view; defensively add
  `LIMIT 1` or a uniqueness guarantee so multiple matches can never leak the wrong record.
* Active/inactive and presence are handled **entirely in the SQL/view** — no Certify code.

## Field mapping

The view's **column names** must line up with the credential's configured `credentialSubject`
keys and the Velocity template `${...}` placeholders (e.g. `functional_id` → `functionalId`).
Alias columns in the view as needed. The **functional ID** is carried as a VC claim; the holder
binding (`credentialSubject.id`) is the hosted wallet's custodial key, not any registry ID.

## Security

* Certify connects with a **read-only** DB user; expose **only the view**, never raw registry
  tables.
* For FDW, the foreign user mapping should also be least-privilege (read-only on the needed
  tables).

## Future / alternative — custom REST connector

A custom `DataProviderPlugin` that calls the **Registry REST API** (rather than the DB) is the
cleaner long-term option:

* reads the **`phone_number`** claim (so it does **not** require `sub` = phone),
* avoids DB federation and schema coupling,
* lets the Registry enforce its own authorization and compute derived claims.

It costs **custom Java**, so Phase 1 uses the **DB-direct** approach above; the REST connector is
the recommended Phase-2 evolution if DB coupling, the `sub = phone` constraint, or FDW operations
become undesirable.
