---
description: >-
  Work still to do in Agri Stack, each item with the design worked out so far:
  identity, consent and policies; the Composite; the registries; catalogues;
  the platform and build.
---

# TODOs & Open Items

Each item says what is to be done and where its design stands: a link to the design, the approach already decided, or "not designed yet".

## Priorities

Functional work, in order, for the first production release. Country data and registry settings are set by the system integrator for each rollout; livestock and the DA Registry come later.

| # | Item | Details |
| --- | --- | --- |
| 1 | **Consent without a form:** in person digitally (national-ID login, approval on the CM's screen), self-service, and notifications to farmers | [More ways to give consent](#identity-consent-and-policies) |
| 2 | **Sharing on a mandate:** a standing permission for a purpose (programmes such as a subsidy run, registry-to-registry checks) instead of each farmer's consent | [Standing permission for a purpose](#identity-consent-and-policies) |
| 3 | **Dashboards and cross-registry figures:** dashboards on the reporting views, and figures that combine registries (e.g. area sown by farmer gender) | [Dashboards](#registries); [Observations gaps, item 4](#registries) |
| 4 | **Land ownership as events:** transfers, inheritance and tenure changes recorded as dated events with history and evidence | [Land ownership events](#registries) |
| 5 | **Contributions from value-chain actors:** cooperatives, input suppliers, buyers and certification bodies registering and updating records directly | [Value-chain contributions](#registries) |
| 6 | **Attestation on entity records:** who verified a record, when and with what evidence, visible to partners | [Verification and correction, phase 2](#registries) |
| 7 | **Registry-to-registry sync:** crop activity in the Farmer Registry; basic farmer data in other registries | [Sync farmer data into other registries](#registries) |
| 8 | **Use case authoring in the Composite console:** "New use case", "try it", publish from the UI | [Make adding a use case easy](#composite) |

**Phase 2:** farmer-facing access to their own records (see [Farmer access](#identity-consent-and-policies)).

## Identity, consent and policies

* **Common farmer identifier** — confirm that every department's registry stores the same national identifier (Fayda-based in the reference setup); with a separate MOSIP relying party and token per registry, records can't be joined. *Design:* a check, not a build.
* **Consent held in CM, presented directly at a registry** — without the Composite (path A in the [architecture](../architecture/README.md#components-and-who-talks-to-whom)). Also decide whether consent spanning registries is always collected in CM. *Design:* [consent](../architecture/consent.md); recommended: always collect it in CM.
* **More ways to give consent** at the Exchange CM — in person digitally (no form, no staff step) and self-service (scenarios 2 and 3), with notifications to farmers (e.g. of consent requests). *Design:* [consent](../architecture/consent.md).
* **Which CM to trust, per partner** — let a department CM choose, per partner, which CM's consent tokens it trusts (today it trusts the Exchange CM for every partner the Composite presents). *Design:* not designed yet.
* **Who may search across subjects** — searches of activity-register aggregates without a subject (e.g. for a benefit run) checked against a PM policy (a programme's legal basis for bulk access, approved by the department), instead of the partner API's `dci_bulk_aggregate_partners` allow-list. *Design:* not designed yet ([data-sharing policies](../architecture/data-sharing-policies.md)).
* **Farmer access to their own records (phase 2)** — a farmer-facing portal or app and beneficiary APIs for the Farmer Registry and Crop Sown Registry, to see their records and request corrections (the CM's beneficiary API is scaffolded). *Design:* not designed yet.
* **Partner self-service in PM** — partners submit their own onboarding, key-rotation and policy requests (today a PM administrator files them). *Design:* not designed yet.
* **Standing permission for a purpose** — a Consent Manager rule for sharing on a mandate instead of consent (registry to registry, e.g. CSR checking a farmer is registered; a yes/no Farmer ID check before consent): one caller, one purpose, narrow scopes, legal basis recorded, every use logged. *Depends on:* the departments agreeing the legal basis.

## Composite

* **Publish checks** — when a use case is published, check it against the departments' ceilings for the Composite in PM (purpose, scopes, subject types), and its mapping paths and response schema against its scopes. *Design:* [checks when a use case is published](../composite/README.md#checks-when-a-use-case-is-published).
* **JSON Schema per use case** — an endpoint serving each use case's JSON Schema (`response.schema`, accepted but not used today), and responses validated against it. *Design:* decided as stated; see [use-case configuration](../composite/use-case-configuration.md).
* **Developer sandbox** — each published use case's schema, sample request and response, and a test harness. *Design:* not designed yet.
* **Data-blind mode** — each registry encrypts its part to the partner's PM key; the Composite only bundles the parts. *Design:* not designed yet.
* **Restrict the registries' partner APIs** — an Istio `AuthorizationPolicy` so only the Composite (and partners deliberately allowed direct access) can call them. *Design:* [entry point](../architecture/README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway); decided: Istio policy, no separate API gateway.
* **Rate limits across pods and daily quotas** — shared counters in Redis, and `limits.daily_quota_per_partner` enforced (today the rate limit is per pod and worker). *Design:* decided as stated.
* **API gateway product** — reconsider only if a partner portal, API keys, analytics or billing across many partner-facing APIs are needed, or a national API gateway is mandated. *Design:* decided: none for now ([entry point](../architecture/README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)).
* **Registry endpoints in PM** — instead of the Composite's `composite.registries`. *Design:* not designed yet.
* **Crop sources in parallel with the farmer** — when the partner already sends a Farmer ID, search the Crop Sown Registry alongside the Farmer Registry. *Design:* see step 7 of the [request flow](../architecture/request-flow.md).
* **Make adding a use case easy** — in order:
  1. a query shorthand instead of Jinja for common sources, e.g. `query: {by: subject}` or `query: {by: farmer.identifiers.FARMER_ID, filters: [crop_year, season]}` (raw `query_template` stays for unusual cases);
  2. "New use case" in the [console](../composite/console.md): live validation, a "try it" run for a sample farmer showing the registries' records beside the mapped output, publish / retire / partners from the UI;
  3. picking fields from the registry's data scopes (Registries page) to fill `scopes`, `optional_scopes` and the output mappings;
  4. copying an existing use case as a starting point.

  *Design:* decided as listed.
* **Editing use cases in the console** — use cases stored in the Composite's database instead of the Helm ConfigMap (registries and settings stay in Helm), YAML editing with validation and a "try it" run, and who changed what and when (in the database and the Audit Manager). Earlier versions need not be kept. *Design:* decided as stated.
* **"Give partner X use case Y"** — one console flow: check the partner's key in PM and raise the PM policy request that adds `name@major` to its use-case policy (approved in PM as usual). *Design:* decided as stated.
* **Data scopes for registries a partner calls directly** — list a registry's data scopes in its staff UI and in PM's policy form (the registry staff API has them: `/data_scopes/get_data_scopes`). *Design:* not designed yet.

## Registries

* **Sync farmer data into other registries** — read-only mirror registers kept up to date by publish/subscribe from the Farmer Registry, set up by configuration. *Design:* [Registry Data Sync](../design/registry-data-sync.md). *Depends on:* standing permission for a purpose.
* **WebSub for registry outgestion** — point the registry platform's outgestion at the commons WebSub hub (`websub.<baseDomain>`) where push is wanted; consumers poll meanwhile. *Design:* decided as stated ([standards](../architecture/standards.md)).
* **Land ownership events** — transfers, inheritance and tenure changes recorded as dated events (an activity register on land parcels, or events on the Farmer Registry's land records), with history and evidence. *Design:* not designed yet; the [activity register](../../products/registry/registry/features/activity-register.md) is the likely mechanism.
* **Value-chain contributions** — cooperatives, input suppliers, buyers and certification bodies onboarded as partners that add or update records directly: activities already ([partner activity submission](../../products/registry/registry/features/activity-register.md#partner-activity-submission)); entity records through partner ingestion with change requests; registries for inputs used or produce transactions when needed. *Design:* not designed yet.
* **Activity registers from configuration** — a projection spec, an aggregate spec, and per-register tables created by the platform from metadata (activity types, fields promoted to columns) with a default domain service, so simple registers (e.g. attendance) need no extension and Add Register can offer "Activity". *Design:* [configuration file](../../products/registry/registry/design/activity-register.md#configuration-file) and [relation to the Observations design](../../products/registry/registry/design/activity-register.md#relation-to-the-observations-design); decided: keep a table per register. *Depends on:* a second real activity register, so the specs come from two domains.
* **Verification and correction, phase 2** — a common verification model for entity and activity registers; corrections marked as such, disputes and verification reset on change; a beneficiary API for occurrences (needs beneficiary authentication first); DCI subscribe/notify for occurrence events; a season-window date check. Programme approval stays in PBMS. *Design:* [Verification and Correction (Proposal), phase 2](../../products/registry/registry/design/verification-and-correction.md#phase-2).
* **Gaps compared with the Observations design** — *Design:* [relation to the Observations design](../../products/registry/registry/design/activity-register.md#relation-to-the-observations-design).
  1. activity-type definitions through an API (today seed SQL only);
  2. per-type processing switches and per-stage status for enrichment and aggregation (weather or satellite data would be the first enrichment);
  3. a shared calendar-period helper (month, quarter, year) for aggregates;
  4. decide how area totals get farmer attributes held in the Farmer Registry (e.g. farmers by gender): a consented copy on activities, or an analytics layer joining the registries;
  5. GPS as standard fields on every activity, filled from the device;
  6. recomputing aggregates after boundary changes;
  7. an agent field app (offline drafts, sync, device GPS), only if field agents don't use ODK.
* **Activity register gaps** — bulk export API, file import, archiving old partitions, agent-portal entry, looking up Farmer Registry farmer and plot IDs (today only their format is checked). *Design:* not designed yet ([not built](../../products/registry/registry/design/activity-register.md#not-built)).
* **Plot geography in two places** — decide whether CSR checks the crop season's district against the Farmer Registry's Land location when it looks plots up (CSR's figures use its own). *Design:* not designed yet.
* **Dashboards on the reporting views** — Superset/Insights dashboards on CSR's reporting views; access limited to roles allowed to see all locations, since views bypass data policies. *Design:* decided as stated ([Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)).
* **Credentials after a change** — decide whether changing or correcting a record suspends or revokes credentials already issued from it (Certify's status list) and prompts reissue. *Design:* not designed yet.
* **Sample IDs in step** — CSR's sample farmer and plot IDs match the Farmer Registry's only by convention (`FR-<n>`, `LAND-<n>-<k>`); a change to either rule must be made in both.

## Catalogues

* **Agri input datasets** — inputs (fertilisers, pesticides, equipment) are not in the shipped country pack. Add them as pack datasets with typed fields when a deployment needs them; no code change. *Design:* [typed fields](../../platform/platform-services/master-data-service/concepts.md#typed-fields). Livestock datasets come with the Livestock Registry.
* **Registries on the catalogue API, remaining** — *Design:* registries read the catalogue only through its API ([Master Data Service consumers](../../platform/platform-services/master-data-service/consumers.md)).
  * bump the registry-platform version pinned by the Farmer Registry, Crop Sown Registry and NSR charts;
  * entity registers record the catalogue versions used (activities already do), and accept an unchanged retired value when an entity record is edited;
  * the staff UI moves from the legacy `/attributes` and `/geo` APIs to `/catalogue`;
  * NSR moves its seeded lists (`g2p_attribute_values*.sql`, `loadAttributes`) to catalogue datasets;
  * the Farmer Registry's analytics maps and reporting views stop assuming Ethiopian level names and at most five levels;
  * the Disability Registry chart drops `syncGeoWidgets` and `loadGeoData` when it moves to the current platform.
* **Pinned catalogue release in the staff UI** — the staff UI (and every catalogue read) honours `global.catalogueRelease`; until then hide the Rancher question or mark it advanced with this limitation. *Design:* decided as stated.
* **Authorised access to the catalogue API (priority)** — every non-public call authorised: staff and services by token, partners by requests signed with their PM key and per-partner grants (as the registries' partner APIs do), so data that should not be fully public can be shared with partners. `/public` stays anonymous. *Design:* decided as stated.
* **Per-publisher edit rights** — only the dataset's publisher (department) edits and approves it, instead of anyone with `MASTER_DATA_ADMIN`. Needed before a central catalogue serves several departments. *Design:* not designed yet.
* **Deploy and check on trial** — publish the latest Master Data build (public catalogue, Datasets wording, grouped geography, home page), upgrade trial, click through the admin UI, and re-run the seed job so the stored theme (`domain`) is filled.
* **Public catalogue, remaining** — *Design:* [Public catalogue](../../platform/platform-services/master-data-service/public-catalogue.md).
  * **Internet exposure:** a public gateway, DNS and TLS, and a decision on which datasets go public (the public host uses the internal gateway by default);
  * **future-effective versions:** decide whether a published version not yet in effect stays hidden from `/public` when asked for by number;
  * **OGC API – Features for geography** (paging, bbox, per-unit features): to explore;
  * **OData for BI tools:** to explore when BI-tool users ask.
* **Agricultural data standards per dataset** — evaluate AGROVOC, ICC, CPC/FAOSTAT, EPPO, BBCH and others, and per dataset map our codes (SKOS matches) or adopt the standard's. *Design:* [standards](../architecture/standards.md#todo-agricultural-data-standards-for-the-catalogues); preferred later: standard-agnostic, each country choosing a dataset's standard.
* **Central catalogue** — the Exchange's catalogue becomes the authoritative copy; departments read it through its API (cached, pinned to a release, a remote catalogue URL in the registry charts) or mirror its published versions; department-only datasets live in it under their own publisher. *Design:* [across departments](../architecture/README.md#across-departments); decided for now: a catalogue per department, loaded from the same country pack version. *Depends on:* authorised access and per-publisher edit rights.

## Platform and build

* **Across departments** — *Design:* [across departments](../architecture/README.md#across-departments).
  * **Remote shared services in registry charts:** a "shared services" question group with external URLs (catalogue, Exchange CM), and setup jobs that call service APIs instead of writing into another service's database (e.g. Certify credential configs);
  * **Gateway between departments** with mutual TLS (a client certificate per department) on top of signed requests, exposing only the service APIs others need; document site-to-site WireGuard as the alternative for a few departments;
  * **Request ID** passed through the Composite, registries and CMs, and recorded in every audit log;
  * **API versioning** and a compatibility promise for the shared APIs (Composite, consent tokens, catalogue, registry partner API);
  * **Usage metering** per partner at the Exchange (later: billing);
  * **Onboarding a department** as one documented step list: keys in both PMs, the Composite's scope policy (the department's ceiling), its published scope catalogue, its client certificate, the Exchange URLs in its charts.
* **Scripted installs for multi-department setups (later)** — Rancher Fleet (`fleet.yaml` per release, `dependsOn` ordering, `releaseName` `commons` / `commons-services`), Exchange choices as override files, pinned chart versions, one git repo for the Exchange and each department. Trade-offs: changes only through git, secrets outside git, drift correction undoes manual patches. *Design:* decided as stated.
* **SQLAlchemy dependency at the root** — declare `sqlalchemy[asyncio]` in [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) (and test against 2.1), instead of each service pinning `sqlalchemy[asyncio] >=2.0,<2.1` (SQLAlchemy 2.1 no longer installs `greenlet`). *Depends on:* openg2p-fastapi-common changes, frozen for now.
* **Migrations run once** — run migrations as a Helm hook Job instead of in every API on start (extension migrations still run unlocked and can collide). *Design:* decided as stated.
* **Changelog path option (CI)** — an option in the shared [openg2p-packaging](https://github.com/openg2p/openg2p-packaging) workflow to build a repository's changelog from one path's commits (here `composite/`). *Design:* not designed yet.
* **Composite on a fastapi-common release** — the Composite pins openg2p-fastapi-common `develop` (and iam-core `develop` with it), where `PartnerMgmtKeyStore` is in `utils.crypto` instead of the 1.2.x releases' `crypto`; release that layout, or move the Composite to 1.2.x. *Design:* decided as stated.
