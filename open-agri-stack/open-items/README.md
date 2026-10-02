---
description: >-
  Decisions, checks and TODOs still pending in Open Agri Stack: identifiers,
  consent and policies, the composite, the registries, Master Data and the
  platform.
---

# TODOs & Open Items

## Identity, consent and policies

* **Common farmer identifier.** Confirm that every department's registry stores the same Fayda-based identifier. If each registry is a separate MOSIP relying party with its own token, records can't be joined.
* **Consent across registries.** Decide the rest of the [consent model](../architecture/consent-model.md): whether consent that spans registries is always collected by CM (recommended) or may be collected by the partner, and whether the farmer may decline individual items. One consent with a grant per registry is built for partner-signed consents.
* **CM-originated consent at registries.** A consent collected inside the Consent Manager (the farmer approving with a Fayda OTP) cannot yet be presented at a registry, directly or through the composite. Until it can, partners sign consents they obtained from the farmer themselves ([partner guide](../guides/partner-guide.md#step-6-collect-the-farmers-consent)).
* **Replay guard.** CM's replay check is per (`jti`, controller). Under the single-consent model it should move to a per-request nonce (the DCI envelope already carries message IDs and timestamps), with usage counted per consent and controller.
* **Presentation via the composite (CM presenter check).** CM accepts a partner-signed consent presented by the composite on the partner's behalf (the composite forwards it unchanged). CM should also check that the presenter of a consent whose audience is a partner is a **registered composite**.
* **Moving policies to PM.** Move `PartnerPolicy` from CM to Partner Management, with a section per department, AWE approval per section, and partner associations; `/validate` then reads from PM. CM's design docs still describe policies held in CM. Until then the composite's `allowed_partners` stands in for the partner association ([policy and consent](../architecture/policy-and-consent.md)).
* **Who may search across subjects.** Activity-register aggregates can be searched without a subject (e.g. for a benefit run). Today the registry operator allow-lists those partners and their scopes in the partner API's configuration (`dci_bulk_aggregate_partners`), because there is no per-person consent for such a search. This belongs in a Partner Management policy (a programme's legal basis for bulk access, approved by the department), checked like any other policy.
* **Partner self-service in PM.** Onboarding and key rotation are done by a PM administrator today; partners can't submit their own requests.

## Composite

The [composite as built](../implementation/composite.md) leaves these for later:

* **Publish checks** when a use case is published, against PM policies (which PM doesn't hold yet): policy and purpose, requested scopes within approved sections, subject types, mapping paths within scopes, response schema ([design](../design/use-case-composite.md#checks-when-a-use-case-is-published)).
* **Data-blind mode:** each registry encrypts its part to the partner's PM key and the composite only bundles the parts.
* **API gateway:** global rate limits and daily quotas (`limits.daily_quota_per_partner`), partner authentication and the policy association check at the edge. The composite's rate limit is per pod and worker.
* **Registry endpoints and policies held in PM** rather than in the composite's configuration.
* **Calling the crop sources in parallel with the farmer** when the partner already sends a farmer ID.
* **A configuration UI.**
* **TODO: JSON Schema per use case.** No machine-readable response schema is published; the describe endpoint lists output field names only. Add an endpoint serving each use case's JSON Schema (`response.schema`, accepted but not acted on), and validate responses against it.
* **Developer sandbox** with each published use case's schema, sample request and response, and a test harness.

## Registries

* **Crop sown fork.** The earlier crop-sown implementation overwrites the platform core with a modified copy and patches the ingestion worker. The genuine gaps should be fixed upstream as part of the [activity register](../design/activity-register.md).
* **Activity register design.** Settle the verification, sequence, period-locking and calendar rules (see [activity register](../design/activity-register.md#new-features-not-in-the-registry-platform-before)).
* **Crop seasons in two registries.** Crop seasons can be kept by the Crop Sown Registry, or by a register in the Farmer Registry's own extension (not built). If a country runs both, decide which one is authoritative for crop seasons, or how the two are merged when data is shared, so that sown area isn't counted twice.
* **Generic, code-free activity storage.** The Observations design keeps every type in one platform table, and adds types through an API with no code. That would let "Activity" appear under Add Register. Deferred: crop sown needs an extension either way. Revisit for simple registers such as attendance.
* **Geography of a plot in two places.** The Crop Sown Registry records the plot's woreda on the crop season; the Farmer Registry has its own location for the Land record. If they disagree, the crop season's woreda is what CSR's figures use. Decide whether CSR should check it against the Farmer Registry when it looks plots up.
* **Dashboards on the reporting views.** The Crop Sown Registry has reporting views by region, zone and woreda; the Superset/Insights dashboards on them are not built. Views bypass data policies, so dashboard access must be limited to roles allowed to see all locations.
* **Register model design, phase 2.** Phase 1 of the [register model design](../design/register-model-design.md#platform-changes-in-phases) is built:
  * typed participants;
  * entities first, with temporary plot IDs withdrawn;
  * partner corrections;
  * the Cluster register;
  * the crop-change link;
  * verification status in DCI;
  * shared sample data.

  Phase 2 remains, from the [concept notes review](../design/concept-notes-review.md):
  1. a common verification model for both kinds: what to verify configurable per field, section, record or activity type; verification records with evidence; automatic verification from trusted sources; status in DCI;
  2. corrections marked as such on entity change requests, disputes, and verification reset on change;
  3. a beneficiary API for occurrences (it needs beneficiary authentication on the registry first);
  4. DCI subscribe/notify for occurrence events;
  5. a season-window date check.

  Programme approval and certificates are not registry work: PBMS decides whether a programme acts on verified records.
* **TODO: geo dropdowns on register forms.** A register's geo dropdowns (how many, which levels) are fixed in each extension's seed metadata; the values come from Master Data, but a country whose levels differ gets empty dropdowns. "Match geo dropdowns to country" (`syncGeoWidgets`) rewrites them at install, and is off by default in the registry platform (on in FR, off in CSR, whose Cluster register has a woreda dropdown).
  * **Next:** default it on in the registry platform and remove it from the Rancher form, keeping it only as a values setting for deployments that have hand-edited their geo dropdowns.
  * **Later:** have register forms read Master Data's levels when they load, as activity-register forms already do, so the sync and the switch go away.
* **Credentials after a change.** Certificates are verifiable credentials issued from a record (agent portal, Inji Certify). When that record is changed or corrected, credentials already issued from it stay valid. Decide whether a change suspends or revokes them (through Certify's status list) and prompts reissue.
* **Sample data at the registries' edges.** The CSR sample farmer and plot IDs match the Farmer Registry's only by convention (`FR-<n>`, `LAND-<n>-<k>` from Master Data's sample people). If either registry changes its sample ID rule, the other must follow.
* **Aligning with the Observations design.** Built: the profile tab, `schema_version`, `submission_id`, the asynchronous enrichment and aggregate layer, geography as named levels with indicators and reporting views by level, season windows, and aggregates over DCI. Still to do: per-type switches for enrichment and aggregation with per-stage status, a beneficiary API, and agent-app capture (offline drafts, sync badge). The Crop Sown Registry uses the aggregate layer for a farmer's season summary and has no enrichment yet; weather or satellite data would be the first. See [activity register](../design/activity-register.md#relation-to-the-observations-design).
* **Activity register gaps.** Not yet designed:
  * bulk export API;
  * file import into activity registers;
  * archiving old partitions;
  * agent-portal entry;
  * looking up Farmer Registry farmer and plot IDs (today only their format is checked).

## Catalogues

* **TODO: design and build proper catalogues.** Layer 2 (code lists, reference entities such as seed varieties, input products and breeds, geography) is served today by the Master Data Service (MDS), as a stand-in. The catalogues themselves are not designed yet. Decide between:
  * **enhancing MDS** with typed attributes per list, AWE approvals, history and audit, a public read API and a change feed;
  * **using the registry platform:** catalogues as registers, which already have approvals, history, audit and APIs;
  * **adopting an existing open-source DPG** built for catalogues.

  Whichever is chosen, registries must stop reading a database directly (below), and the country pack must load into it. See [Layer 2: catalogues](../architecture/registry-model.md#layer-2-catalogues).

The items below are about MDS as it serves the catalogues today.

* **Registries read Master Data's database directly.** Registries no longer copy code lists at install; they query Master Data's code-list tables live over a database connection. That couples every registry to Master Data's schema. A public read API for the catalogues (see [Layer 2](../architecture/registry-model.md#layer-2-catalogues)) would replace the direct connection.
* **Ethiopia country pack.**
  * Master Data's pack loader upserts but never deletes. An existing Master Data therefore keeps retired codes, such as the old `CROP_SEASON` values `SEASON_SUMMER`, `SEASON_MONSOON` and `SEASON_WINTER`, after a reload. Retiring a code needs an `is_active` flag or a delete step.
  * `CROP_COMMODITY` still lacks enset, pulses beyond faba bean, haricot bean and chickpea, and horticulture beyond a handful of crops. The list needs review with MoA.
  * `SEED_VARIETY` is flat. Tying a variety to its crop needs typed attributes per list (below).
* **MDS partner endpoints.** They currently have no authentication decorator.

## Platform and build

* **Registry platform build pins.** Fresh builds resolve SQLAlchemy 2.1, which no longer installs `greenlet`, and async database access then fails. Registry-platform core now pins `sqlalchemy[asyncio] >=2.0,<2.1`, and the Consent Manager pins `sqlalchemy[asyncio] <2.1` (its image died at import).
* **TODO: fix the SQLAlchemy dependency at the root.** [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common) declares `sqlalchemy >=2.0.20`, without the `asyncio` extra and without an upper bound, so every service built on it must pin on its own. Declaring `sqlalchemy[asyncio]` there (and testing against 2.1) would fix it once for all services.
* **Concurrent migrations.** Every API migrates on start; concurrent `CREATE TABLE`s collided and left tables missing. Core migration now takes a Postgres advisory lock. The extension's own migration (e.g. Farmer tables) still runs unlocked and can still collide; one API then logs the error while another completes the tables, as before. A lasting fix is to run migrations once, as a Helm hook Job, instead of in every API on start.
* **TODO: changelog path option (CI).** agri-stack builds and publishes only when `composite/` changes, but the shared [openg2p-packaging](https://github.com/openg2p/openg2p-packaging) workflow builds a repository's changelog from all of its commits, including design-only ones. An option to limit the changelog to a path (here `composite/`) is needed.
* **`PartnerMgmtKeyStore` unreleased.** The partner-key store the composite uses exists only on openg2p-fastapi-common `develop`, so the composite pins `develop` ([service guide notes](service-guide-notes.md), item 15).
* **Service guide.** Where the "Creating a new service" guide disagrees with current practice: see [service guide notes](service-guide-notes.md).
