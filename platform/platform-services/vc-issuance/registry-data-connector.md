---
description: >-
  How Inji Certify gets the citizen's claims — a custom OpenG2P DataProvider
  plugin that reads an external Registry database via configurable scope-based
  SQL and a configurable token-claim → query-parameter binding.
---

# Registry Data Connector

In the hosted-wallet (pull) model, Certify receives a **token** and must source the citizen's
claims. OpenG2P uses a **custom DataProvider plugin** — `registry-dataprovider-plugin` — that
reads an **external Registry database** with **configurable, scope-based SQL** and a
**configurable claim→parameter** binding.

> Source code lives in the working repo at `vc-issuance/registry-dataprovider-plugin/`.

## Why a custom plugin (and not the stock Postgres plugin)

Certify ships a `PostgresDataProviderPlugin`, but it has two limitations for our case:

1. it queries **Certify's own database** (shared `EntityManager`), so reaching a separate
   `registrydb` would need FDW / replication / cross-schema tricks; and
2. it binds the query's `:id` to the token **`sub`** only — forcing `sub` = phone in the IdP.

The custom plugin removes both:

| Concern | Stock Postgres plugin | Custom Registry plugin |
|---|---|---|
| Datasource | Certify's own DB | **Dedicated external** Registry datasource |
| Lookup key | hardcoded `:id = sub` | **Configurable** `param → claim` mapping |
| Query | config (SQL per scope) | config (SQL per scope) — same flexibility |
| Code | none | a small Java plugin (built once, in Docker) |

It keeps the good part — **queries defined in config** — so adding a credential type stays config,
and the plugin never needs recompiling to change what's read.

## How it works

At issuance Certify calls `fetchData(identityDetails)` with the validated token claims. The plugin:

1. reads the **`scope`** claim and picks the matching SQL from `scope-query-mapping`;
2. binds each SQL named parameter from the token claim named in `param-claim-mapping`
   (for phone login: `:id` ← `phone_number`);
3. runs the query on the **dedicated Registry datasource**;
4. returns the single matching row's columns as the VC claims.

```properties
# selection & discovery
mosip.certify.integration.scan-base-package=org.openg2p.certify.registry
mosip.certify.integration.data-provider-plugin=RegistryDataProviderPlugin

# dedicated external Registry datasource (read-only)
mosip.certify.data-provider-plugin.registrydb.url=jdbc:postgresql://registry-db:5432/registrydb
mosip.certify.data-provider-plugin.registrydb.username=certify_ro
mosip.certify.data-provider-plugin.registrydb.password=${REGISTRY_DB_PASSWORD}

# scope -> SQL (the view/table lives entirely in the SQL; alias columns to template vars)
mosip.certify.data-provider-plugin.scope-query-mapping={\
  'registry_vc_ldp': 'select "fullName","dateOfBirth","gender","functionalId" \
                       from beneficiary_vc_view where phone = :id'\
}

# SQL param -> token claim (no hardcoded sub)
mosip.certify.data-provider-plugin.param-claim-mapping={ 'id': 'phone_number' }
```

## The view and the identifier

* The plugin is **schema-agnostic** — the table/view name, joins and filters are all inside the
  configured SQL. So the Registry exposes a **read-only view** (e.g. `beneficiary_vc_view`),
  **phone-keyed** and **active-only**, surfacing only the VC columns. The plugin doesn't need to
  know its name; it's just part of the query string.
* **Identifier is configurable:** binding `:id` ← `phone_number` matches "citizen logs in by
  phone". The Registry is assumed **one-to-one** phone → functional ID. No IdP `sub` constraint.
* **Column → claim names:** alias view columns to match the credential template `${...}`
  variables (quote camelCase in Postgres); format dates as text for clean string claims.

## Lookup behaviour

| Case | Query result | Outcome |
|---|---|---|
| Phone maps 1:1 to an **active** record | 1 row | claims returned → VC issued |
| **No** record for the phone | 0 rows | `DataProviderExchangeException` → Certify error → portal "no eligible record" |
| Record exists but **inactive** | 0 rows (filtered in the view) | same — treated as not eligible |
| Multiple rows | >1 | first row used + warning logged (enforce 1:1 / `LIMIT 1`) |

Presence and active/inactive are handled entirely in the **SQL/view** — no code change.

## Build & deploy

* **Build without a local Java toolchain** — `vc-issuance/registry-dataprovider-plugin/build.sh`
  runs the Maven Docker image and produces `target/registry-dataprovider-plugin.jar` (a
  `Dockerfile` build is also provided). All dependencies are `provided`, so the JAR contains only
  the plugin's classes (no version clashes).
* **Deploy** — mount the JAR into Certify's plugin **loader_path**, add the properties above to
  the active profile, create the read-only **view** + `certify_ro` user in the Registry DB, and
  define the `credential_config` (template, issuer DID, signing key, scope).

## Security

* Read-only DB user limited to the **view**; TLS to the DB; network access restricted to Certify.
* The Registry owns what the view exposes — Certify never touches raw tables.

## Future option — REST instead of DB

The same `DataProviderPlugin` interface allows a REST variant that calls the Registry's **API**
(honouring its API-layer authorization, no DB coupling) instead of the DB. It is interchangeable
behind the same interface, so moving to it later is low-risk. The DB connector is the chosen
Phase-1 approach for its simplicity (SQL + config, no API to build).
