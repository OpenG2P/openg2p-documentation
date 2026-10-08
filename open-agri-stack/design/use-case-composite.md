---
description: >-
  Design of the use-case composite: one generic service that serves approved
  use cases, each a configuration file — format, publishing checks, runtime,
  and a worked example.
---

# Use-Case Composite

{% hint style="info" %}
**Status: first version built (October 2026)**, in the agri-stack repository under [`composite/`](https://github.com/openg2p/agri-stack/tree/develop/composite) (service, Helm chart, partner test kit). See [composite as built](../implementation/composite.md) for what is in it and what is not yet, and the [composite configuration guide](../guides/composite-configuration.md) for the file format the service accepts.
{% endhint %}

A **composite** serves one approved use case, such as `credit-profile`, by querying several departmental registries and returning one response. There is **one generic composite service**; each use case is a **configuration file** that it loads, not new code.

The configuration describes **how** a request is served. It **never grants access**. What a partner may receive is decided only by the policy and the farmer's consent, and each registry enforces that itself (see [policy and consent](../architecture/policy-and-consent.md)).

## Example configuration: `credit-profile`

This is the full design. The built service accepts all of these keys, acts on most of them, and lists the rest as not yet enforced ([composite configuration guide](../guides/composite-configuration.md#use-case-file-format)). The sample use case that ships is [`loan-profile`](../guides/composite-configuration.md#the-loan-profile-use-case).

```yaml
# ── Identity ──────────────────────────────────────────────────────────────
use_case: credit-profile
version: 1.2.0                        # semver; breaking response changes → new major
status: published                     # draft | validated | published | deprecated | retired
title: Farmer credit profile
description: Identity, landholding, recent crops and herd, for credit assessment.
owner: agri-stack-platform

# ── Governance (links, does not grant) ────────────────────────────────────
policy: credit-assessment             # PM policy; caller must be associated with it
purpose: credit-assessment            # must be one of the policy's allowed purposes
consent:
  required: true
  collection: cm-originated           # cm-originated | partner-embedded
  mode: single                        # one consent, one grant per registry (see the consent model)

# ── Input: what the SP sends ──────────────────────────────────────────────
input:
  subject:
    id_types: [FAYDA_FAN, FARMER_ID]     # must be within the CM policy's allowed_subject_id_types
  parameters:
    seasons: { type: integer, min: 1, max: 4, default: 2 }
  batch: { max_subjects: 1 }             # 1 = one farmer per request

# ── Sources: one entry per registry ───────────────────────────────────────
sources:
  - id: farmer
    controller: farmer-registry          # PM participant; endpoint and keys resolved from PM
    requirement: mandatory               # mandatory | optional
    request_scopes: [farmer:profile, farmer:land]
    dci:
      reg_type: Farmer
      reg_record_type: spdci-extensions-dci:Farmer
      query_template: templates/farmer-by-id.json.j2
    timeout_ms: 2000
    retries: 1

  - id: crops
    controller: crop-sown-registry
    requirement: optional
    request_scopes: [crop:season]
    dci:
      reg_type: CropSown
      reg_record_type: spdci-extensions-agri:ActivityAggregate   # the farmer's season summaries
      query_template: templates/crop-seasons.json.j2   # uses parameters.seasons
    timeout_ms: 2500
    retries: 1

  - id: herd
    controller: livestock-registry
    requirement: optional
    request_scopes: [livestock:herd]
    dci:
      reg_type: Livestock
      query_template: templates/herd-by-owner.json.j2
    timeout_ms: 2000
    retries: 0

# ── Assembly: what the SP gets back ───────────────────────────────────────
response:
  mode: merged                           # merged | data-blind
  schema: schemas/credit-profile-1.json  # published JSON Schema / JSON-LD context for SPs
  correlate_on: subject                  # results joined on the resolved subject identifier
  mapping:                               # source fields → response fields
    farmer.name:          "$.farmer.name"
    farmer.sex:           "$.farmer.sex"
    farmer.kebele:        "$.farmer.address.kebele"
    land.parcels:         "$.farmer.land[*]"
    crops.seasons:        "$.crops.records[*]"
    herd.animals:         "$.herd.records[*]"
  derived:
    land.total_ha:        "sum($.farmer.land[*].area_ha)"
  source_status: true                    # per-source ok | no_record | denied | unavailable

# ── Behaviour ─────────────────────────────────────────────────────────────
execution:
  fan_out: parallel
  overall_timeout_ms: 3000
  partial_response: allowed              # a mandatory source failing → whole request fails
limits:
  rate_per_partner: 60/min
  daily_quota_per_partner: 20000
audit:
  events: [request, source_call, response]   # sent to audit-manager, linked by request ID
```

## What each section does

| Section | Purpose | Notes |
| --- | --- | --- |
| **Identity** | Name, version and lifecycle status | Partners call `use_case@major`. A breaking change to the response means a new major version, and the old one is deprecated with a sunset date. |
| **Governance** | Links the use case to a policy, a purpose and a consent mode | The composite rejects callers not associated with `policy`. The consent settings follow the [consent model](../architecture/consent-model.md). |
| **Input** | What the partner sends: subject identifier types, parameters, batch size | Checked before any registry is called |
| **Sources** | One entry per registry: controller, whether it's mandatory, requested scopes, DCI query template, timeout, retries | Endpoints and signing keys come from **PM**, never from this file. The query templates use the Jinja style the registries already use for DCI mapping. |
| **Response** | Merged or data-blind, published schema, field mapping, derived fields, per-source status | In data-blind mode `mapping` and `derived` aren't allowed. Each registry encrypts its part to the partner's PM key and the composite only bundles the parts. |
| **Execution / limits / audit** | Timeouts, partial-response rule, rate limits, audit events | Limits are enforced by the composite (there is no separate API gateway; see [entry point](../architecture/README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)) |

{% hint style="warning" %}
**First version:** registry endpoints are configured in the composite's own settings (`registries`), because PM holds no registry endpoints yet; the composite enforces a per-pod rate limit itself; and `allowed_partners` in each use case stands in for the policy association. See [composite as built](../implementation/composite.md).
{% endhint %}

## Checks when a use case is published

A use case moves from `draft` → `validated` → `published` only if all of these pass:

1. The `policy` exists in PM and is active, and `purpose` is one of its allowed purposes.
2. Each source's `request_scopes` ⊆ that controller's **approved** section of the policy. A source whose section isn't yet approved can stay in the configuration, but it will always return `denied` until the section is approved.
3. `input.subject.id_types` ⊆ the policy's allowed subject identifier types.
4. Every `mapping` path refers only to fields covered by the requested scopes, using each registry's published scope-to-field mapping. A use case can't map a field it didn't ask for.
5. The query templates render valid DCI requests against sample data. The sandbox runs each use case end to end with test fixtures.
6. The response schema validates against the mapped output.

Publishing is done by the Agri Stack platform team. Because the configuration can't widen access, it doesn't need department approval; the departments have already approved the policy.

{% hint style="info" %}
**First version:** only check 5 is done, partly: every template is rendered with sample input when the file is loaded, and must produce a valid query. The other checks need policies in PM ([open items](../open-items/README.md)).
{% endhint %}

## What happens at runtime

1. **Ingress:** the OpenG2P deployment's ingress (Nginx, Istio) routes the request to the composite. There is no separate API gateway; the composite does the partner checks below.
2. **Composite:**
   * verifies the partner's signature, checks its association with `policy` and applies rate limits;
   * validates the input and selects `use_case@version`;
   * renders one DCI request per source from its template;
   * signs each request with its own PM key, carrying the partner's consent and the request ID;
   * sends the requests in parallel.
3. **Each registry:** calls CM `/validate` and releases only the effective scopes.
4. **Composite:**
   * waits up to the timeout;
   * applies the partial-response rule;
   * maps the results, computes derived fields, adds the per-source status, and validates against the schema;
   * responds, then discards everything.
5. **Audit:** every step sends an audit event, linked by the request ID.

How the first version runs a request, step by step, is in [composite as built](../implementation/composite.md#what-it-does-per-request).

## Worked example: wheat sown by a farmer this season

The question is "total area of wheat sown by farmer X in this season". Both registries answer with one **synchronous** DCI call each, `POST /dci/registry/sync/search`. Neither registry has an asynchronous search, so the composite never waits for a callback.

**Farmer Registry:** who the farmer is. Search the Farmer register by Fayda FAN (`foundational_id`) or farmer ID (`functional_record_id`):

```json
"search_criteria": {
  "reg_type": "Farmer",
  "query_type": "expression",
  "query": {"type": "expression", "value": {"expression": {"query": {"foundational_id": {"$eq": "<FAN>"}}}}}
}
```

The farmer record carries both identifiers, `UIN` (the FAN) and `FARMER_ID` (e.g. `FR-0007`). It comes with the farmer's linked records (land, household, livestock) and declared main crops, whether the search is by exact field or by ID.

Any question about one farmer follows the same pattern: the farmer's record from the Farmer Registry, and from the Crop Sown Registry the farmer's activities, crop seasons or season summaries, each filtered on its own fields. Nothing in the registries is specific to a particular question.

**Crop Sown Registry:** what they sowed. Search the farmer's season summary for the crop year and season:

```json
"search_criteria": {
  "reg_type": "CropSown",
  "reg_record_type": "spdci-extensions-agri:ActivityAggregate",
  "query_type": "expression",
  "query": {"type": "expression", "value": {"expression": {"query": {
    "subject_id": "FR-0007", "aggregate_type": "FARMER_SEASON_SUMMARY",
    "crop_year": 2019, "season": "SEASON_MEHER"}}}}
}
```

One record comes back. The answer is at `measures.by_crop.CROP_WHEAT.area_sown_ha`, beside the season's totals and the other crops. Alternatively, `reg_record_type: spdci-extensions-agri:CropSeason` with `"crop": "CROP_WHEAT"` returns the wheat crop seasons, one per plot, each with its `area_sown_ha`, stage and whether sowing was verified. The mapping then sums them.

| | Season summary (`…:ActivityAggregate`) | Crop seasons (`…:CropSeason`) |
| --- | --- | --- |
| Records | One per farmer and season | One per plot and crop |
| Answer | Read one field | Sum over plots |
| Freshness | Updated by the outbox worker, seconds after each activity | Updated in the same transaction as each activity |
| Filters | `aggregate_type`, `period_key`, `crop_year`, `season` | Any plain projection column: `crop_year`, `season`, `crop`, `stage`, `plot_id`… |

**Sequencing.** The Crop Sown Registry knows the farmer by farmer ID, not by FAN.

* **The partner sends a farmer ID:** both sources can be called in parallel.
* **The partner sends a FAN:** the Farmer Registry is called first, and the Crop Sown query uses the `FARMER_ID` it returns. The source then declares `depends_on: farmer`, and its query template reads the farmer ID from the farmer result.

{% hint style="info" %}
In the built `loan-profile`, the crop sources always declare `depends_on: farmer` and use the subject itself when it is a `FARMER_ID`; calling them in parallel with the farmer when the partner sends a farmer ID is [not built yet](../implementation/composite.md#not-built-yet).
{% endhint %}

**"This season"** is resolved by the composite (the crop year and season from today's date, using the season windows in the [Crop Sown Registry](crop-sown-registry.md#farmers-season-summary)) and passed as parameters. Without them, the summaries come back newest first.

## Response to the partner (example)

```jsonc
{
  "use_case": "credit-profile@1",
  "request_id": "…",
  "subject": { "type": "fayda_token", "value": "…" },
  "sources": {
    "farmer": { "status": "ok" },
    "crops":  { "status": "ok" },
    "herd":   { "status": "unavailable" }
  },
  "data": {
    "farmer": { "name": "…", "sex": "F", "kebele": "…" },
    "land":   { "parcels": [ … ], "total_ha": 1.4 },
    "crops":  { "seasons": [ … ] }
  }
}
```

As built, this body is the `message` of a signed DCI-style envelope; see the [partner guide](../guides/partner-guide.md#step-10-read-the-response).

## Where configurations live

* **Storage:** configuration files, query templates and schemas are kept in a Git repository, reviewed like code, and loaded by the composite service. An admin UI is optional.
* **Sandbox:** each published use case appears in the developer sandbox with its schema, sample request and response, and a test harness.
* **Adding a use case** (e.g. `input-subsidy-eligibility`) means a new configuration file plus the matching PM policy. No code changes are needed unless the use case requires a new kind of derived field.

{% hint style="info" %}
**First version:** use cases are YAML entries in the composite's Helm values, rendered into a ConfigMap and edited in Rancher's **Edit YAML** view (or your own ConfigMap); the sample is also kept in the repository at [`composite/use-cases/loan-profile.yaml`](https://github.com/openg2p/agri-stack/blob/develop/composite/use-cases/loan-profile.yaml). There is no sandbox yet.
{% endhint %}
