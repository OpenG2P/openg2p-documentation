---
description: >-
  How Inji Certify gets the citizen's claims — two paths. Phase 1 PUSHES claims
  from the Agent Portal API (Certify stays decoupled); the wallet flow PULLS via
  a custom DataProvider plugin with configura
---

# Registry Data Connector

Inji Certify needs the citizen's claim data at issuance. There are **two paths**, and OpenG2P uses each in a different phase:

| Path                       | Who reads the Registry                                                   | Used by                    | Plugin                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------ | -------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Push** (Phase 1, paper)  | the **Agent Portal API** reads the view and **pushes** claims to Certify | agent-driven issuance      | Certify's **built-in** `PreAuthDataProviderPlugin` (no custom code — returns the pushed claims as the subject) |
| **Pull** (Phase 2, wallet) | **Certify itself** queries the Registry                                  | wallet OpenID4VCI download | custom `RegistryDataProviderPlugin` (this page)                                                                |

> **Phase 1 uses push.** The agent backend owns the Registry connection and Certify never touches the Registry — see [Phase 1 — Paper Credential](phase-1-paper-credential.md). The **pull connector below** is for the **wallet flow** ([Phase 2](phase-2-device-wallet.md)), where the citizen (not an agent) authenticates and the wallet downloads the credential, so Certify must fetch the claims itself. Phase 1 needs **no custom plugin** (the push plugin is built into Certify); only the pull connector below is custom. Exactly one data-provider plugin is active per deployment.

## VC definitions are owned by the module, not by Certify

Certify is a generic signing service — a `credential_config` only has meaning once a module defines what it issues. So **the VC definitions live with the consuming module (Registry/NSR), not the Certify chart**, and a registry can issue **multiple VC types** (e.g. an ID card vs ID + socio-economic):

| Part of a VC definition                                       | Owner                                                | How it's supplied                                                                                                                                                                                                                                       |
| ------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Source view** (which registry fields, joins, active-only)   | the **registry extension**                           | a `meta_data/vc-views/*.sql` view in `nsr-extension` — **auto-deploys with the models** (the db-seed job applies it after migration)                                                                                                                    |
| **`credential_config`** (template, type, scope, DID, key, QR) | the **module's Helm**                                | a `vcDefinitions[].certifyConfig` list in the registry/NSR chart → registered into Certify on install via a Job (`POST /credential-configurations`)                                                                                                     |
| **Claim mapping** (type → view + columns)                     | the **module's Helm**                                | `vcDefinitions[]` → `REGISTRY_AGENT_PORTAL_API_VC_DEFINITIONS` (the Agent Portal API is config-driven and multi-VC)                                                                                                                                     |
| **Issuer** (DID + signing key)                                | **env-level** (one issuer/authority per environment) | set at **Certify install** — `global.vcIssuerDid` (+ the keymanager key alias); the module's register Job **references** this env issuer, it does not define it                                                                                         |
| **Photo** (face on the card + in the QR)                      | the **module's Helm** + **registry/MINIO**           | the view exposes the photo's **MINIO object key** (`vcDefinitions[].photo_key_column`); the Agent Portal API fetches it, thumbnails it, pushes it as the **`face`** claim → Certify embeds it in the signed **claim-169 QR**, and places it on the card |
| **Card design** (logo, layout, branding)                      | the **module/designer**                              | an **SVG template** in `vcDefinitions[].svg_template` (shipped via the `svgTemplates` ConfigMap, mounted at `/app/pdf-templates`); the API fills `{{field}}`/`{{photo}}`/`{{qr}}` and renders SVG→PDF. Same SVG can later drive the Phase-2 wallet card |

The Inji Certify chart stays **generic** (issuer + schema + keys); it seeds a module `credential_config` only behind a `dbSchemaInit.seedDemoCredential` flag (off by default — for standalone demos). Adding a VC type or changing fields is **config + a view**, not Certify changes.

## The pull connector (`registry-dataprovider-plugin`)

For the wallet/pull path, OpenG2P supplies a **custom DataProvider plugin** that reads an **external Registry database** with **configurable, scope-based SQL** and a **configurable claim→parameter** binding.

> Source code lives in the working repo at `vc-issuance/registry-dataprovider-plugin/`.

## Why a custom plugin (and not the stock Postgres plugin)

Certify ships a `PostgresDataProviderPlugin`, but it has two limitations for our case:

1. it queries **Certify's own database** (shared `EntityManager`), so reaching a separate `registrydb` would need FDW / replication / cross-schema tricks; and
2. it binds the query's `:id` to the token **`sub`** only — forcing `sub` = phone in the IdP.

The custom plugin removes both:

| Concern    | Stock Postgres plugin  | Custom Registry plugin                      |
| ---------- | ---------------------- | ------------------------------------------- |
| Datasource | Certify's own DB       | **Dedicated external** Registry datasource  |
| Lookup key | hardcoded `:id = sub`  | **Configurable** `param → claim` mapping    |
| Query      | config (SQL per scope) | config (SQL per scope) — same flexibility   |
| Code       | none                   | a small Java plugin (built once, in Docker) |

It keeps the good part — **queries defined in config** — so adding a credential type stays config, and the plugin never needs recompiling to change what's read.

## How it works

At issuance Certify calls `fetchData(identityDetails)` with the validated token claims. The plugin:

1. reads the **`scope`** claim and picks the matching SQL from `scope-query-mapping`;
2. binds each SQL named parameter from the token claim named in `param-claim-mapping` (for phone login: `:id` ← `phone_number`);
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

* The plugin is **schema-agnostic** — the table/view name, joins and filters are all inside the configured SQL. So the Registry exposes a **read-only view** (e.g. `beneficiary_vc_view`), **phone-keyed** and **active-only**, surfacing only the VC columns. The plugin doesn't need to know its name; it's just part of the query string.
* **Identifier is configurable (flow-agnostic):** the plugin binds `:id` from whatever identity claim the issuance carries. In **Phase 1** (assisted, agent-driven) that's the citizen's **functional ID** resolved by the agent's lookup; in a future self-service/wallet flow it could be `phone_number`. The mapping is configuration, so the same plugin serves both. No IdP `sub` constraint.
* **Multiple phone numbers per person:** in the OpenG2P registry an individual may have **more than one** phone number (the `phone_numbers` field is a list). The view therefore exposes **one row per phone number** (e.g. by expanding the list), so a citizen who logs in with **any** of their registered numbers resolves to their record. Each number must map to exactly one person (phone → person is one-to-one, even though a person → phones is one-to-many), so a lookup by phone still returns a single record.
* **Column → claim names:** alias view columns to match the credential template `${...}` variables (quote camelCase in Postgres); format dates as text for clean string claims.

## Lookup behaviour

| Case                                   | Query result                  | Outcome                                                                       |
| -------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------- |
| Phone maps 1:1 to an **active** record | 1 row                         | claims returned → VC issued                                                   |
| **No** record for the phone            | 0 rows                        | `DataProviderExchangeException` → Certify error → portal "no eligible record" |
| Record exists but **inactive**         | 0 rows (filtered in the view) | same — treated as not eligible                                                |
| Multiple rows                          | >1                            | first row used + warning logged (enforce 1:1 / `LIMIT 1`)                     |

Presence and active/inactive are handled entirely in the **SQL/view** — no code change.

## Build & deploy

* **Build without a local Java toolchain** — `vc-issuance/registry-dataprovider-plugin/build.sh` runs the Maven Docker image and produces `target/registry-dataprovider-plugin.jar` (a `Dockerfile` build is also provided). All dependencies are `provided`, so the JAR contains only the plugin's classes (no version clashes).
* **Deploy** — mount the JAR into Certify's plugin **loader\_path**, add the properties above to the active profile, create the read-only **view** + `certify_ro` user in the Registry DB, and define the `credential_config` (template, issuer DID, signing key, scope).

## Security

* Read-only DB user limited to the **view**; TLS to the DB; network access restricted to Certify.
* The Registry owns what the view exposes — Certify never touches raw tables.

## Future option — REST instead of DB

The same `DataProviderPlugin` interface allows a REST variant that calls the Registry's **API** (honouring its API-layer authorization, no DB coupling) instead of the DB. It is interchangeable behind the same interface, so moving to it later is low-risk. The DB connector is the simpler default for the pull path (SQL + config, no API to build).
