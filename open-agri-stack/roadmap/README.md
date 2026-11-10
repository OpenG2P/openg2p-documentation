---
description: What comes next, by phase.
---

# Roadmap

What is still to be built in Agri Stack, in phases. Each item says what is to be done and where its design stands: a design page, the approach already decided, or "not designed yet". Country data and registry settings are set by the system integrator for each rollout and are not listed here.

The longer designs are on their own pages: [Generic Exchange](generic-exchange.md), [Interoperability with OAN (Beckn)](oan-interoperability.md), [Livestock Registry](livestock-registry.md) and [Registry Data Sync](registry-data-sync.md).

## Phase 1 — First production release

### Functional, in order

1. **Consent without a form** — the farmer gives consent in person digitally (national-ID login, then approval on the Consent Manager's own screen: no form, no staff step), and is notified (e.g. of consent requests). The national-ID login is built; today it is part of the form-and-staff flow. *Design:* [consent](../architecture/consent.md#how-a-farmer-gives-consent).
2. **Sharing on a mandate** — sharing for a purpose on a legal basis other than each farmer's consent (a public function or legitimate use): programmes such as a subsidy run; registry-to-registry checks, e.g. the Crop Sown Registry checking a farmer is registered; a yes/no Farmer ID check before consent; staff of another department or the Exchange reading a farmer's data for their work, e.g. a grievance desk. The basis (`consent` or a named mandate) in each Partner Management policy: the use-case policy at the Exchange (the Composite then asks for no consent tokens), and the scope policy at each department, which decides whether it accepts the mandate; the registry then skips the Consent Manager but still applies its scope ceiling. One internal caller, named use cases, narrow scopes; every use audited with the basis and the purpose (e.g. the grievance ticket) and shown to the farmer among the accesses to their data. Today the partner API checks consent on every query or, with `consent_enforcement_enabled` off, never; staff working on their own registry need no consent (IAM roles). *Design:* recommended as stated, not detailed yet. *Depends on:* the departments agreeing the legal basis.
3. **Dashboards and cross-registry figures** — dashboards (Superset or Insights) on the Crop Sown Registry's reporting views, open only to roles allowed to see every location, since the views bypass data policies; and figures that combine registries (e.g. area sown by farmer gender): a consented copy of farmer attributes on activities, or an analytics layer joining the registries. *Design:* dashboards decided as stated; the combined figures not designed yet.
4. **Land ownership as events** — transfers, inheritance and tenure changes recorded as dated events with history and evidence (an activity register on land parcels, or events on the Farmer Registry's land records). *Design:* not designed yet; the [activity register](../../products/registry/registry/features/activity-register.md) is the likely mechanism.
5. **Contributions from value-chain actors** — cooperatives, input suppliers, buyers and certification bodies onboarded as partners that add or update records directly: activities already can ([partner activity submission](../../products/registry/registry/features/activity-register.md#partner-activity-submission)); entity records through partner ingestion with change requests; registries for inputs used or produce sold when needed. *Design:* not designed yet.
6. **Attestation on records** — who verified a record, when and with what evidence, visible to partners: one verification model for entity and activity registers, corrections marked as such, disputes, verification reset on change. Programme approval stays in PBMS. *Design:* [Verification and Correction](../../products/registry/registry/design/verification-and-correction.md#phase-2).
7. **Registry-to-registry sync** — crop activity kept in the Farmer Registry, and basic farmer data mirrored in other registries, by publish/subscribe set up by configuration; the registries' outgestion pointed at the commons WebSub hub (`websub.<baseDomain>`), consumers polling meanwhile. *Design:* [Registry Data Sync](registry-data-sync.md). *Depends on:* sharing on a mandate.
8. **Use cases written in the Composite console**:
   1. a query shorthand instead of Jinja for common sources, e.g. `query: {by: subject}` (raw `query_template` stays for unusual cases);
   2. "New use case": use cases stored in the Composite's database instead of the Helm ConfigMap, edited with live validation and a "try it" run for a sample farmer, published or retired from the UI, with who changed what and when (in the database and the Audit Manager);

   *Design:* decided as listed.
9. **Livestock Registry** — an Animal register and a livestock events register. *Design:* [Livestock Registry](livestock-registry.md).

### Needed before production

* **Restrict the registries' partner APIs** — an Istio `AuthorizationPolicy` so only the Composite (and partners deliberately allowed direct access) can call them. *Design:* decided ([Networking and Gateway](../architecture/networking-and-gateway.md)).
* **Authorised access to the catalogue API** — non-public reads already need a staff or service token; partners still need requests signed with their Partner Management key and per-partner grants, as on the registries' partner APIs, so data that is not fully public can be shared with them. `/public` stays anonymous. *Design:* decided as stated.
* **Publish checks** — a use case is published only if its purpose, each source's scopes and its subject ID types are within the Composite's scope policy in each department it reads, every mapping path reads only fields its scopes cover, and its response schema validates the output. Today only the templates are checked, when the file loads. *Design:* decided as stated.
* **Request ID end to end** — the Composite sends it in the DCI header, but the registries' audit reads only the `x-request-id` header and the Consent Manager records none; one ID recorded at every hop. *Design:* decided as stated.
* **Composite key rotation without a gap** — the Composite's JWKS serving the next key before it signs with it (and the old one for a while after); today registries may refuse its calls for up to 5 minutes after a rotation ([Keys](../administration/keys.md#rotate-the-generated-key)). *Design:* not designed yet.
* **Partner end dates** — an end date for a partner or its use-case policies, and a renewal step; today a partner stays active until disabled. *Design:* not designed yet.
* **Migrations run once** — as a Helm hook Job instead of in every API on start (extension migrations can collide). *Design:* decided as stated.
* **Composite on a fastapi-common release** — its image builds openg2p-fastapi-common and iam-core from `develop`; pin released versions instead (fastapi-common's 1.2.x releases now have the same `crypto` layout as `develop`). *Design:* decided as stated.
* **Pinned catalogue release in the staff UI** — the registry APIs honour `global.catalogueRelease`; the staff UI still reads the latest. *Design:* decided as stated.
* **Finding consents** — a **Consents** search in the CM console: by the farmer's ID (national ID or Farmer ID), consent ID or partner, with filters (status, how it was given, use case), paged, each opening the consent's page (revoke there); for Consent Approvers and admins. Today a consent is reached only from an approval, from the **Access Log** once used, or by its ID, so revoking at a farmer's request needs the consent ID. And the partner portal's **Consents** listing the partner's own signed consents too, marked as signed by the partner (today only consents collected through the CM). No database change. *Design:* decided as stated.

## Phase 2 — Farmers, partners and the Open Agri Network

* **Interoperability with OAN (Beckn)** — the Composite as a provider node on the Open Agri Network. *Design:* [Interoperability with OAN](oan-interoperability.md).
* **Farmer access to their own records** — a farmer portal or app and beneficiary APIs for the Farmer Registry and Crop Sown Registry, to see their records and consents and ask for corrections (the Consent Manager's farmer routes are a start). *Design:* not designed yet.
* **Farmer-readable consent form** — generated from the request: the purpose, the period and, per registry, each data scope in plain language and the farmer's language, instead of a form the partner prepares. *Design:* not designed yet.
* **Partial consent and revocation** — the farmer declines individual data items, or revokes one registry's grant only, instead of the whole consent. *Design:* not designed yet.
* **Partner-level limits and daily quotas** — `limits.daily_quota_per_partner` in use cases, and the policy's `max_fetch_frequency` and `data_life` enforced (today recorded only), counted in the Redis that holds the rate-limit buckets. *Design:* [rate limiting](../composite/rate-limiting.md#later).
* **A published schema per use case** — an endpoint serving each use case's JSON Schema (`response.schema`), and responses checked against it. *Design:* decided as stated.
* **Exchange consent used directly at a registry** — a consent held by the Exchange Consent Manager used at a registry without the Composite (path A in the [architecture](../architecture/README.md#data-sharing-paths)); today a registry's own Consent Manager finds only the consents it holds. *Design:* recommended: always collect consent spanning registries at the Exchange.
* **Which Consent Manager to trust, per partner** — today a department trusts the Exchange Consent Manager's tokens for every partner the Composite presents. *Design:* not designed yet.
* **Who may search across farmers** — searches of season summaries without a farmer (e.g. for a benefit run) allowed by a Partner Management policy with the programme's legal basis, approved by the department, instead of the registry's allow-list (`dci_bulk_aggregate_partners`). *Design:* not designed yet.
* **Sources that are not registries** — e.g. the G2P Bridge (a beneficiary's payments) or PBMS, read by the Composite: a source type for a REST API (request template, response mapping), its data scopes defined at the Exchange, and consent (or another legal basis) checked by the Exchange Consent Manager; the source trusts the Composite as a service. *Depends on:* each source's API to search by a beneficiary's ID for a signed, allowed partner (the G2P Bridge has none today). *Design:* not designed yet.
* **Credentials after a change** — decide whether changing or correcting a record suspends or revokes credentials already issued from it (Inji Certify's status list) and prompts reissue. *Design:* not designed yet.
* **Catalogue: registries on its API only** —
  * entity registers record the catalogue versions they used (activities already do), and accept an unchanged retired value when a record is edited;
  * the staff UI stops using the legacy `/attributes` and `/geo` reads (geo levels already come from `/catalogue`);
  * the National Social Registry moves its seeded lists to catalogue datasets;
  * the Farmer Registry's maps stop assuming three levels with Ethiopian names (its reporting views already work for any levels);
  * the Disability Registry chart drops `syncGeoWidgets` and `loadGeoData`.

  *Design:* registries read the catalogue only through its API ([consumers](../../platform/platform-services/master-data-service/consumers.md)).
* **Catalogue: edit rights per publisher** — only the dataset's publisher (department) edits and approves it, instead of anyone with the catalogue permissions. *Design:* not designed yet.
* **Public catalogue on the internet** — a public gateway, DNS and TLS, and the choice of which datasets go public; decide whether a published version not yet in effect stays hidden from `/public`. *Design:* [public catalogue](../../platform/platform-services/master-data-service/public-catalogue.md).

## Phase 3 — Many departments, other stacks, conveniences

* **Data from partners through the Composite** — partners (e.g. on OAN) send data back into Agri Stack through the Composite only, which routes it to the registries; partners make no arrangement with each registry. *Design:* open; everything is still to be designed.
* **Generic Exchange** — generic names in place of Agri ones (one coordinated release), stacks as packs (`agri-stack` holding content only), connectors per registry for other standards, use cases from criteria and a field picker. *Design:* [Generic Exchange](generic-exchange.md).
* **Across departments** —
  * shared services by URL in the registry charts (catalogue, Exchange Consent Manager), and setup jobs that call service APIs instead of writing into another service's database;
  * a gateway between departments with mutual TLS (a client certificate per department) on top of signed requests; site-to-site WireGuard documented as the alternative for a few departments;
  * versioning and a compatibility promise for the shared APIs (Composite, consent tokens, catalogue, registry partner API);
  * usage metering per partner at the Exchange (later: billing);
  * onboarding a department as one documented step list (the [test](../deployment/testing.md) already does the keys and scope policies for test installs).

  *Design:* not designed yet.
* **Central catalogue** — the Exchange's catalogue as the authoritative copy, read by departments through its API (cached, pinned to a release) or mirrored; department-only datasets in it under their own publisher. Today each department has its own catalogue, loaded from the same country pack version. *Depends on:* authorised access and edit rights per publisher.
* **Registry endpoints in Partner Management** — instead of the Composite's `composite.registries`. *Design:* not designed yet.
* **Data-blind responses** — each registry encrypts its part to the partner's key; the Composite only bundles the parts. *Design:* not designed yet.
* **Activity registers from configuration** — projection and aggregate specs and per-register tables created from metadata, so simple registers need no extension. *Design:* [configuration file](../../products/registry/registry/design/activity-register.md#configuration-file); decided: a table per register. *Depends on:* a second real activity register.
* **Scripted installs for many departments** — Rancher Fleet (`fleet.yaml` per release, ordering, pinned chart versions), one git repo for the Exchange and each department. *Design:* decided as stated.
* **Consent from the farmer's own app** — self-service: the farmer logs in with the national ID in their own portal or app, approves or declines requests, and revokes any consent. *Design:* [consent](../architecture/consent.md#how-a-farmer-gives-consent) (scenario 3).
* **Conveniences** —
  * in the Composite console: picking fields from the registries' data scopes to fill a use case's scopes and mappings (the console API already lists them); copying an existing use case; "give partner X use case Y" (check the partner's key and raise the policy request in Partner Management);
  * partner self-service in Partner Management: partners file their own onboarding, key and policy requests (today a Partner Management administrator does);
  * a developer sandbox: each use case's schema, sample request and response, and a test harness;
  * data scopes shown in the registry's staff UI (the registry staff API already lists them).

  *Design:* decided for the console items; the rest not designed yet.

## To decide or explore

* **Activity registers, compared with the Observations design** ([relation](../../products/registry/registry/design/activity-register.md#relation-to-the-observations-design)): activity types defined through an API (today seed SQL only); per-type processing switches and per-stage status for enrichment (weather or satellite data first); a shared calendar-period helper; GPS as standard fields; recomputing aggregates after boundary changes; an agent field app, only if field agents don't use ODK.
* **Activity registers, other gaps** — bulk export API, file import, archiving old partitions, entry in the agent portal, checking Farmer Registry farmer and plot IDs exist (today only their format is checked) ([not built](../../products/registry/registry/design/activity-register.md#not-built)).
* **Plot geography in two places** — whether the Crop Sown Registry checks a crop season's district against the Farmer Registry's land location.
* **Crop sources in parallel with the farmer** — when the partner already sends a Farmer ID, search the Crop Sown Registry alongside the Farmer Registry ([request flow, step 7](../architecture/request-flow.md)).
* **Agricultural data standards per dataset** — AGROVOC, ICC, CPC/FAOSTAT, EPPO, BBCH and others: map our codes (SKOS matches) or adopt the standard's ([standards](../architecture/standards.md#todo-agricultural-data-standards-for-the-catalogues)).
* **Agri input datasets** — fertilisers, pesticides and equipment as country-pack datasets when a deployment needs them; no code change ([typed fields](../../platform/platform-services/master-data-service/concepts.md#typed-fields)).
* **Catalogue APIs for other tools** — OGC API – Features for geography; OData for BI tools, when their users ask.
* **API gateway product** — only if a common portal, keys, analytics or billing across many partner-facing APIs are needed, or a national API gateway is mandated ([Networking and Gateway](../architecture/networking-and-gateway.md)).

## Build and tooling

* **SQLAlchemy at the root** — declare `sqlalchemy[asyncio]` in [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) (and test with 2.1) instead of each service pinning it. *Depends on:* openg2p-fastapi-common changes, frozen for now.
* **Changelog for one path (CI)** — an option in the shared [openg2p-packaging](https://github.com/openg2p/openg2p-packaging) workflow to build a changelog from one path's commits (here `composite/`). *Design:* not designed yet.
