---
description: >-
  What is built, and the decisions, checks and TODOs still pending in Agri Stack: identity,
  consent and policies, the Composite, the registries, catalogues, and the
  platform and build.
---

# TODOs & Open Items

## What is built

Besides the existing OpenG2P registries, PM and CM, the following are built (October 2026). The rest is design.

| Part | Status | Where |
| --- | --- | --- |
| Activity registers in the registry platform | Built | [Activity register](../../products/registry/registry/features/activity-register.md) |
| Typed participants, entities first, partner corrections, Cluster register, crop-change link, verification status in DCI, shared sample data | Built | [Activity register](../../products/registry/registry/features/activity-register.md); [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) |
| Common verification and correction model, disputes, beneficiary API for occurrences, subscribe/notify | Design | [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md) |
| Livestock Registry | Design | [Livestock Registry](../design/livestock-registry.md) |
| Crop Sown Registry | Built | [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md); [deployment](../deployment/crop-sown-registry.md) |
| Farmer Registry: declared main crops, `FARMER_ID` in DCI, sample lands | Built | [Farmer Registry](../../products/registry/farmer-registry/README.md); [deployment](../deployment/farmer-registry.md) |
| One consent with a grant per registry, in CM | Built | [Consent](../architecture/consent.md); [Consent Manager](../../consent-management/README.md) |
| Composite, first version | Built | [Composite](../deployment/composite.md) |
| Exchange mode: the Exchange CM issues a consent token per registry, each registry checks it at its own CM; a consent collected in CM used through the Composite (`consent_id`) | Built | [Request flow](../architecture/request-flow.md); [Exchange](../deployment/exchange.md); [Exchange setup](../deployment/after-install.md#exchange-setup) |
| Consent collection, scenario 1 (in person): partner portal, national-ID login (eSignet), signed form as evidence, CM staff verification, Farmer ID check in the Farmer Registry, consent record for the partner | Built | [Consent](../architecture/consent.md) |
| Composite staff console | Built | [Composite console](../composite/console.md) |
| Consent in person digitally (no form, no staff step) and self-service; a consent collected in CM presented directly at a registry; policies held in PM; registry-to-registry sync; rate limits across pods and quotas; publish checks; data-blind mode | Design / TODO | [TODOs and open items](../open-items/README.md) |

## Identity, consent and policies

* **Common farmer identifier.** Confirm that every department's registry stores the same national identifier (Fayda-based in the reference setup). If each registry is a separate MOSIP relying party with its own token, records can't be joined.
* **Consent collected in CM, remaining paths.** Built in Exchange mode: a consent recorded in CM's partner portal (national-ID login, evidence, staff verification) is presented to the Composite as `message.consent_id`, and the Exchange CM turns it into a consent token per registry ([partner guide](../partner-guide.md#step-6-collect-the-farmers-consent)). Still to do: presenting a CM-held consent directly at a registry without the Composite (path A in the [architecture](../architecture/README.md#components-and-who-talks-to-whom); see [consent](../architecture/consent.md)). Decide whether consent spanning registries should always be collected in CM (recommended). See [consent](../architecture/consent.md).
* **More ways to give consent** at the Exchange CM: in person digitally (no form, no staff step) and self-service (scenarios 2 and 3), with notifications to farmers (e.g. of consent requests). See [consent](../architecture/consent.md).
* **Partner policy within the department's policy.** The Exchange CM should refuse a partner policy that grants more than a department's standing policy for the Composite allows, when the policy is created or widened. Today the department CM only cuts the scopes at request time. Needs each department to publish its policy for the Composite and its scope catalogue.
* **Which CM to trust, per partner.** A department CM trusts the Exchange CM's consent tokens for every partner the Composite presents. A per-partner choice of trusted CM is to design.
* **Moving policies to PM.** Move `PartnerPolicy` from CM to Partner Management, with a section per department, AWE approval per section, and partner associations; `/validate` then reads from PM. Until then the Composite's `allowed_partners` stands in for the partner association ([data-sharing policies](../architecture/data-sharing-policies.md)).
* **Who may search across subjects.** Activity-register aggregates can be searched without a subject (e.g. for a benefit run). Today the registry operator allow-lists those partners and their scopes in the partner API's configuration (`dci_bulk_aggregate_partners`), because there is no per-person consent for such a search. This belongs in a Partner Management policy (a programme's legal basis for bulk access, approved by the department), checked like any other policy.
* **Partner self-service in PM.** Onboarding and key rotation are done by a PM administrator today; partners can't submit their own requests.

* **Standing permission for a purpose (registry to registry, Farmer ID check).** Today every data share needs the subject's consent. Operational sharing between registries (e.g. the Crop Sown Registry checking that a farmer is registered) and a yes/no check of a Farmer ID against a national ID before consent is collected usually rest on a mandate instead. The Consent Manager needs a rule for that: a standing permission for one caller, one purpose and narrow scopes, with its legal basis recorded, and every use logged. Needs the departments' agreement on the legal basis.

## Composite

The [Composite](../deployment/composite.md) as built leaves these for later:

* **Publish checks** when a use case is published, against PM policies (which PM doesn't hold yet): policy and purpose, requested scopes within approved sections, subject types, mapping paths within scopes, response schema ([design](../composite/README.md#checks-when-a-use-case-is-published)).
* **Data-blind mode:** each registry encrypts its part to the partner's PM key and the Composite only bundles the parts.
* **No separate API gateway.** Partners come in through the OpenG2P deployment's ingress (Nginx, Istio); see [entry point](../architecture/README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway). What remains to do:
  * **Restrict the registries' partner APIs** with an Istio `AuthorizationPolicy`, so only the Composite (and partners deliberately allowed direct access) can call them, and partners cannot bypass the Composite.
  * **Rate limits across pods and daily quotas** in the Composite (`limits.daily_quota_per_partner`), with shared counters in Redis. Today the rate limit is per pod and worker.
  * **Reconsider a gateway product** only if a partner portal, API keys, analytics or billing across many partner-facing APIs are needed, or a national API gateway is mandated.
* **Registry endpoints held in PM** rather than in the Composite's configuration (`composite.registries`).
* **Calling the crop sources in parallel with the farmer** when the partner already sends a farmer ID.
* **Console, next steps** (the read-only [console](../composite/console.md) is built):
  * **TODO: make adding a use case easy.** Today a use case is YAML in the Helm values (`composite.useCases`), with a Jinja query template and JSONPath mappings per source. In order:
    1. **Query shorthand** instead of Jinja for common sources, e.g. `query: {by: subject}` (FAN or farmer ID → the registry's field) or `query: {by: farmer.identifiers.FARMER_ID, filters: [crop_year, season]}`; raw `query_template` stays for unusual cases.
    2. **"New use case" in the console** (with editing, below): live validation, and a "try it" run for a sample farmer showing the registries' records beside the mapped output; publish / retire / partners from the UI.
    3. **Pick fields from the registry's data scopes** (Registries page): the console fills `scopes`, `optional_scopes` and the output mappings.
    4. **Copy an existing use case** as a starting point.
  * **Editing use cases in the console:** use cases stored in the Composite's database instead of the Helm ConfigMap (registries and settings stay in Helm), YAML editing with validation and a "try it" run against the registries, and a record of who changed what and when (in the database, and sent to the Audit Manager). Earlier versions need not be kept.
  * **"Give partner X use case Y":** one flow that checks the partner's key in PM, creates its Consent Manager policy from the use case's data scopes and adds it to the use case's partners.
  * **Data scopes for registries a partner calls directly:** a registry's own staff UI (and CM's policy form) do not list its data scopes yet; the registry staff API has them (`/data_scopes/get_data_scopes`).
* **TODO: JSON Schema per use case.** No machine-readable response schema is published; the describe endpoint lists output field names only. Add an endpoint serving each use case's JSON Schema (`response.schema`, accepted but not acted on), and validate responses against it.
* **Developer sandbox** with each published use case's schema, sample request and response, and a test harness.

## Registries

* **Scripted installs for multi-department setups (later).** The Exchange is installed by hand in Rancher today. For production across departments and clusters, add Rancher Fleet (`fleet.yaml` per release with `dependsOn` ordering and `releaseName` `commons` / `commons-services`) with the Exchange choices as override files and pinned chart versions, so one git repo describes the Exchange and each department. Trade-offs: changes only through git, secrets kept outside git, drift correction undoes manual patches.

* **TODO: across departments.** Built: department installs and one shared Exchange install (by hand in Rancher), department CMs trusting the Exchange CM's consent tokens, the Composite's Exchange mode and `scripts/setup_exchange.py` ([architecture](../architecture/README.md#across-departments)). Still to do:
  * **Remote shared services in registry charts:** a "shared services" question group with external URLs (catalogue, Exchange CM) in the Rancher form; setup jobs that call service APIs instead of writing into another service's database (e.g. Certify credential configs).
  * **Gateway between departments** with mutual TLS (a client certificate per department) on top of signed requests, exposing only the service APIs others need; document site-to-site WireGuard as the alternative for a few departments.
  * **Request ID** passed through the Composite, registries and CMs, and recorded in every audit log, to trace one request across departments.
  * **API versioning** and a compatibility promise for the shared APIs (Composite, consent tokens, catalogue, registry partner API), since the Exchange and departments upgrade on their own schedules.
  * **Usage metering** per partner at the Exchange (later: billing, for a marketplace).
  * **Onboarding a department** to the Exchange as one documented step list: keys in both PMs, the standing policy, its published scope catalogue, its client certificate, the Exchange URLs in its charts.

* **TODO: sync farmer data into other registries.** Read-only mirror registers kept up to date by publish/subscribe from the Farmer Registry, set up by configuration. See [Registry Data Sync](../design/registry-data-sync.md).

* **TODO (design): activity registers from configuration, next steps.** Step 1 is built: declarations, output record templates per format and plausibility rules (JSON Logic) are configuration (see [configuration file](../../products/registry/registry/design/activity-register.md#configuration-file)). The later steps, a projection spec, an aggregate spec, and per-register tables generated from metadata, wait for a **second real activity register**, so the specs are designed from two domains, not from crop sown alone.
* **Code-free activity registers for simple cases.** Today every activity register needs a small extension (models and a domain service). We keep a table per register rather than the Observations design's single generic table, for typed columns (indexes, data policies, indicators, DCI filters), yearly partitions and isolation per register (see [relation to the Observations design](../../products/registry/registry/design/activity-register.md#relation-to-the-observations-design)). The middle path: the platform creates the per-register table itself from metadata (the activity types and which fields to promote to columns), with a default domain service. Simple registers such as attendance would then need no code, and Add Register could offer "Activity"; an extension would be needed only for custom logic, as in crop sown.
* **Geography of a plot in two places.** The Crop Sown Registry records the plot's district on the crop season; the Farmer Registry has its own location for the Land record. If they disagree, the crop season's district is what CSR's figures use. Decide whether CSR should check it against the Farmer Registry when it looks plots up.
* **Dashboards on the reporting views.** The Crop Sown Registry has reporting views by administrative level; the Superset/Insights dashboards on them are not built. Views bypass data policies, so dashboard access must be limited to roles allowed to see all locations.
* **Verification and correction, phase 2.** Phase 1 is built:
  * typed participants;
  * entities first, with temporary plot IDs withdrawn;
  * partner corrections;
  * the Cluster register;
  * the crop-change link;
  * verification status in DCI;
  * shared sample data.

  Phase 2 remains (design: [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md)):
  1. a common verification model for both kinds: what to verify configurable per field, section, record or activity type; verification records with evidence; automatic verification from trusted sources; status in DCI;
  2. corrections marked as such on entity change requests, disputes, and verification reset on change;
  3. a beneficiary API for occurrences (it needs beneficiary authentication on the registry first);
  4. DCI subscribe/notify for occurrence events;
  5. a season-window date check.

  Programme approval and certificates are not registry work: PBMS decides whether a programme acts on verified records.
* **Registries reading the catalogue only through its API.** Register forms now read geo levels from the catalogue at runtime, and seed scripts use its API; `syncGeoWidgets` and `loadGeoData` are gone from the registry platform. Left to do:
  * bump the registry-platform version pinned by the Farmer Registry, Crop Sown Registry and NSR charts, which get the change only then;
  * NSR still seeds its lists (reference data) into its own database (`g2p_attribute_values*.sql`, `loadAttributes`); move them to catalogue lists;
  * the Farmer Registry's analytics maps and reporting views assume Ethiopian level names and at most five levels;
  * the staff UI's geo levels do not yet follow `catalogueRelease`;
  * the Disability Registry chart still carries the removed `syncGeoWidgets` and `loadGeoData`; drop them when it moves to the current platform.
* **Credentials after a change.** Certificates are verifiable credentials issued from a record (agent portal, Inji Certify). When that record is changed or corrected, credentials already issued from it stay valid. Decide whether a change suspends or revokes them (through Certify's status list) and prompts reissue.
* **Sample data at the registries' edges.** The CSR sample farmer and plot IDs match the Farmer Registry's only by convention (`FR-<n>`, `LAND-<n>-<k>` from the catalogue's sample people). If either registry changes its sample ID rule, the other must follow.
* **Gaps compared with the Observations design** (table in [activity register design](../../products/registry/registry/design/activity-register.md#relation-to-the-observations-design)):
  1. **Activity-type definitions through an API** (create and update types and schemas), instead of seed SQL only.
  2. **Per-type processing switches and per-stage status** for enrichment and aggregation. The Crop Sown Registry has no enrichment yet; weather or satellite data would be the first.
  3. **A shared calendar-period helper** (month, quarter, year) for aggregates, beside domain-defined periods such as seasons.
  4. **Decide how area totals get farmer attributes** (e.g. farmers by gender), which live in the Farmer Registry: a consented copy of selected attributes on activities, or an analytics layer joining the registries.
  5. **GPS as standard fields on every activity**, filled from the device.
  6. **Recomputing aggregates after boundary changes**, from the catalogues' current boundaries.
  7. **Agent field app** (offline drafts, sync badge, device GPS), only if field agents don't use ODK; see agent-portal entry below.
* **Activity register gaps.** Not yet designed:
  * bulk export API;
  * file import into activity registers;
  * archiving old partitions;
  * agent-portal entry;
  * looking up Farmer Registry farmer and plot IDs (today only their format is checked).

## Catalogues

* **In progress: extending the catalogues.** Decided: extend the existing catalogue rather than use the registry platform or adopt another DPG. See the [Master Data Service](../../platform/platform-services/master-data-service/README.md): versioned lists and geography, drafts with AWE or maker-checker approval, typed attributes per list, a crosswalk for boundary changes, a change feed and an opt-in public read API. The GeoPrism Registry was evaluated: strong temporal geography, but versioning and approvals only for geographic lists, a Java and OrientDB stack, and no Helm chart or Keycloak integration; the catalogue borrows its working/published versions and split/merge lineage. An import adapter from GeoPrism or the Common Geo Registry is a possible later add-on. Still to do once it is built: registries move from reading the catalogue's database to the catalogue APIs (below). See [catalogues](../README.md#catalogues-platform-services-and-the-exchange).

The items below are about the catalogue as it runs today.

* **Registries read the catalogue API** (done for the registry platform: versioned and cached, with direct database reads kept as a rollback setting). Still to do: entity registers recording the catalogue versions used (activities already do), accepting an unchanged retired value when an entity record is edited, and the registry staff UI moving from the legacy `/attributes` and `/geo` APIs to `/catalogue` (geo levels already come from `/catalogue`). Install-time seed scripts read the catalogue through its API.
* **Ethiopia country pack.**
  * The catalogue's pack loader upserts but never deletes. An existing catalogue therefore keeps retired codes, such as the old `CROP_SEASON` values `SEASON_SUMMER`, `SEASON_MONSOON` and `SEASON_WINTER`, after a reload. MDS fixes this: a later pack load creates a draft in which dropped codes are retired, not deleted ([country packs and migration](../../platform/platform-services/master-data-service/country-packs-and-migration.md)).
  * `CROP_COMMODITY` still lacks enset, pulses beyond faba bean, haricot bean and chickpea, and horticulture beyond a handful of crops. The list needs review with MoA.
  * `SEED_VARIETY` is flat. Tying a variety to its crop needs typed attributes per list, which MDS provides through a per-list attribute schema (see the catalogues item above).
* **Authorised access to the catalogue API (priority).** The catalogue's partner endpoints have no authentication decorator today, and there is no partner-controlled access to the catalogue at all. Every non-public catalogue API call should be authorised: staff and services by token (as `/catalogue` already is), partners by requests signed with their Partner Management key and per-partner grants (as the registries' partner APIs do). The anonymous `/public` API stays as is, for data marked public.
* **Public catalogue: future-effective versions.** A public dataset serves a published version whose effective date is still ahead when asked for by number ("latest", the list and DCAT show only the version in effect). Decide whether future-effective versions stay hidden from `/public` until they take effect.
* **Pinned catalogue release in registries.** A registry can read the catalogue as of a named catalogue release (`global.catalogueRelease`, Rancher "Pinned Catalogue Release"; empty = latest published), so a department adopts new codes or geography when it chooses (e.g. at season end) and departments can pin the same release. Support is incomplete: the staff UI's geo dropdowns do not follow the pinned release yet, so forms can show newer geography than the registry validates against. To do: make the staff UI (and every catalogue read) honour the pinned release; until then, hide the Rancher question or mark it advanced with this limitation.
* **Per-publisher edit rights.** Anyone with `MASTER_DATA_ADMIN` can edit every dataset. Restrict editing (and approving) to the dataset's publisher (department), needed before a central catalogue serves several departments.
* **Deploy and check on trial.** Publish the latest Master Data build (public catalogue, Datasets wording, grouped geography, home page), upgrade trial, click through the admin UI, and re-run the seed job so the stored theme (`domain`) is filled (the UI falls back meanwhile).
* **Public catalogue (done; opt-in).** The catalogue stays an admin UI; datasets and the geography marked public are readable anonymously at their published versions under `/public` (downloads, DCAT, SKOS); see [Public catalogue](../../platform/platform-services/master-data-service/public-catalogue.md). Off by default, private by default. Still to do:
  * **Internet exposure:** the chart's public host uses the internal gateway by default; publishing to the internet needs a public gateway, DNS and TLS, and a decision on which datasets go public.
  * **WebSub:** commons-services now installs a WebSub hub (`websub.<baseDomain>`). Still to do: point the catalogue (`catalogue.websubHubUrl`) and the registry platform's outgestion at it if push notifications are wanted; until then consumers poll the change feed.
  * **OGC API – Features for geography:** today boundaries are a GeoJSON file per level; a features API (paging, bbox, per-unit features) is to explore.
  * **Partner-controlled catalogue API:** a catalogue read API for partners under Partner Management (signed requests, per-partner grants), for data that should not be fully public.
* **TODO: evaluate agricultural data standards for every catalogue dataset** (AGROVOC, ICC, CPC/FAOSTAT, EPPO, BBCH, DAD-IS, WIEWS, WRB, GAEZ, WCA 2020, ADAPT, ISIC, UCUM, …) and pick the best fit per dataset: map our codes (SKOS matches in the public catalogue) or adopt the standard's. Preferred direction (later): standard-agnostic, so a country chooses each dataset's standard and registries and other modules read whichever it chose. Candidates and method: [standards](../architecture/standards.md#todo-agricultural-data-standards-for-the-catalogues).
* **OData for BI tools (to explore).** An OData query endpoint on the public catalogue would let Excel, Power BI and Tableau query datasets live. Revisit when BI-tool users ask; CSV/JSON downloads cover today's need.

* **Central catalogue and mirroring.** Decided for now: each department runs its own catalogue, loaded from the same `openg2p-data` country pack version, so codes and geography match. Later: the Exchange's catalogue becomes the authoritative copy, and departments read it through its API (cached, pinned to a release, a remote catalogue URL in the registry charts) or mirror its published versions; department-only datasets can live in it under their own publisher. Needs authorised access and per-publisher edit rights (above). See [across departments](../architecture/README.md#across-departments).

## Platform and build

* **TODO: fix the SQLAlchemy dependency at the root.** Fresh builds resolve SQLAlchemy 2.1, which no longer installs `greenlet`, and a service then dies at import. [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) declares `sqlalchemy >=2.0.20` without the `asyncio` extra, so each service pins on its own (the registry platform, Master Data, CM and Partner Management pin `sqlalchemy[asyncio] >=2.0,<2.1`). Declaring `sqlalchemy[asyncio]` in the framework (and testing against 2.1) fixes it once for all services.
* **Concurrent migrations.** Every API migrates on start; concurrent `CREATE TABLE`s collided and left tables missing. Core migration now takes a Postgres advisory lock. The extension's own migration (e.g. Farmer tables) still runs unlocked and can still collide; one API then logs the error while another completes the tables, as before. A lasting fix is to run migrations once, as a Helm hook Job, instead of in every API on start.
* **TODO: changelog path option (CI).** agri-stack builds and publishes only when `composite/` changes, but the shared [openg2p-packaging](https://github.com/openg2p/openg2p-packaging) workflow builds a repository's changelog from all of its commits, including design-only ones. An option to limit the changelog to a path (here `composite/`) is needed.
* **`PartnerMgmtKeyStore` unreleased.** The partner-key store the Composite uses exists only on openg2p-fastapi-common `develop`, so the Composite pins `develop` ([service guide notes](service-guide-notes.md), item 15).
* **Service guide.** Where the "Creating a new service" guide disagrees with current practice: see [service guide notes](service-guide-notes.md).
