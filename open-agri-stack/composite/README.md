---
description: >-
  The Composite, Agri Stack's partner entry point: one generic service that
  serves approved use cases, each a configuration file. Design overview, with
  the pages on creating a use case, its API, use-case configuration, adding a
  data source, console and local running.
---

# Composite

The **Composite** is the partners' entry point to Agri Stack and the Agri Stack–specific part of the [Exchange](../architecture/exchange.md). It serves one approved use case at a time, such as `loan-profile`: a partner sends one signed request about one farmer, with the farmer's consent, and the Composite queries several departmental registries and returns one signed response. There is **one generic Composite service**; each use case is a **configuration file** that it loads, not new code. This page is the design; the pages below cover the built service.

| Page | Covers |
| --- | --- |
| [Creating a Use Case](creating-a-use-case.md) | The steps to add a use case: the file, the configuration, partners, the department policies, testing |
| [Composite API](api.md) | The partner and console endpoints, request and response formats, error codes (OpenAPI) |
| [Use-Case Configuration](use-case-configuration.md) | The use-case file format and how a use case runs: which registry APIs it calls, failure handling, consent mode, output format |
| [Adding a Data Source](adding-a-data-source.md) | Adding a registry (e.g. a Livestock Registry) as a source of a use case, step by step |
| [Composite Console](console.md) | The read-only staff console: use cases, registries and their data scopes, partners, the call log |
| [Running the Composite Locally](running-locally.md) | Running the service and its tests on a laptop |

Installing the Composite and every chart option (registries, consent mode, use cases, signing key, console, scaling) is in [Deployment: Composite](../deployment/composite.md).

{% hint style="info" %}
**Status: first version built (October 2026)**, in the agri-stack repository under [`composite/`](https://github.com/openg2p/agri-stack/tree/develop/composite) (service, Helm chart, partner test kit). See [what the first version does](#what-the-first-version-does) and what it does not yet, and [Use-Case Configuration](use-case-configuration.md) for the file format the service accepts.
{% endhint %}

The configuration describes **how** a request is served. It **never grants access**. What a partner may receive is decided only by the policies in Partner Management (the partner's use-case grant, each department's ceiling for the Composite) and the farmer's consent, and each registry enforces that itself (see [data-sharing policies](../architecture/data-sharing-policies.md)).

## Example configuration (full design)

This example is a hypothetical next version of the shipped use case, `loan-profile@2`: it shows the full design, including a livestock source that does not exist yet. The built service accepts all of these keys, acts on most of them, and lists the rest as not yet enforced ([Use-Case Configuration](use-case-configuration.md#use-case-file-format)). The sample use case that ships is [`loan-profile`](use-case-configuration.md#the-loan-profile-use-case).

```yaml
# ── Identity ──────────────────────────────────────────────────────────────
use_case: loan-profile
version: 2.0.0                        # semver; breaking response changes → new major
status: published                     # draft | validated | published | deprecated | retired
title: Farmer credit profile
description: Identity, landholding, recent crops and herd, for credit assessment.
owner: agri-stack-platform

# ── Governance (links, does not grant) ────────────────────────────────────
policy: credit-assessment             # a label; callers are the partners with a PM policy for loan-profile@2
purpose: credit-assessment            # must be allowed by the partners' and departments' PM policies
consent:
  required: true
  collection: cm-originated           # accepted, not enforced
  mode: single                        # accepted, not enforced; the consent mode is a service setting

# ── Input: what the SP sends ──────────────────────────────────────────────
input:
  subject:
    id_types: [FAYDA_FAN, FARMER_ID]     # must be within the PM policies' allowed_subject_id_types
  parameters:
    seasons: { type: integer, min: 1, max: 4, default: 2 }
  batch: { max_subjects: 1 }             # 1 = one farmer per request

# ── Sources: one entry per registry ───────────────────────────────────────
sources:
  - id: farmer
    controller: farmer-registry          # PM participant; endpoint and keys resolved from PM
    requirement: mandatory               # mandatory | optional
    scopes: [farmer-registry.farmer_identifiers, farmer-registry.personal_details,
             farmer-registry.land]            # the consent must grant all of these
    optional_scopes: [farmer-registry.land_location]   # if not granted: fields come back null
    dci:
      reg_type: Farmer
      reg_record_type: spdci-extensions-dci:Farmer
      query_template: templates/farmer-by-id.json.j2
    timeout_ms: 2000
    retries: 1

  - id: crops
    controller: crop-sown-registry
    requirement: optional
    scopes: [crop-sown-registry.farmer_reference, crop-sown-registry.crop_season]
    dci:
      reg_type: CropSown
      reg_record_type: spdci-extensions-agri:ActivityAggregate   # the farmer's season summaries
      query_template: templates/crop-seasons.json.j2   # uses parameters.seasons
    timeout_ms: 2500
    retries: 1

  - id: herd
    controller: livestock-registry
    requirement: optional
    scopes: [livestock-registry.herd]
    dci:
      reg_type: Livestock
      query_template: templates/herd-by-owner.json.j2
    timeout_ms: 2000
    retries: 0

# ── Assembly: what the SP gets back ───────────────────────────────────────
response:
  mode: merged                           # merged | data-blind
  schema: schemas/loan-profile-2.json  # published JSON Schema / JSON-LD context for SPs
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
  source_status: true                    # per-source ok | no_record | denied | unavailable | error

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
| **Governance** | The purpose and the consent settings | Who may call is not in the file: partners with a policy for `name@major` in the Exchange's PM; the Composite rejects any other caller. The consent settings follow the [consent](../architecture/consent.md). As built, `consent.collection` and `consent.mode` are accepted but not enforced: how consent is checked is one setting for the whole service, in its Helm chart (`exchange`, the default). |
| **Input** | What the partner sends: subject identifier types, parameters, batch size | Checked before any registry is called |
| **Sources** | One entry per registry: controller, whether it's mandatory, the data scopes it needs (`scopes`) and may use (`optional_scopes`), DCI query template, timeout, retries | Endpoints and signing keys come from **PM**, never from this file. The query templates use the Jinja style the registries already use for DCI mapping. |
| **Response** | Merged or data-blind, published schema, field mapping, derived fields, per-source status | In data-blind mode `mapping` and `derived` aren't allowed. Each registry encrypts its part to the partner's PM key and the Composite only bundles the parts. |
| **Execution / limits / audit** | Timeouts, partial-response rule, rate limits, audit events | Limits are enforced by the Composite (there is no separate API gateway; see [entry point](../architecture/README.md#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)) |

{% hint style="warning" %}
**First version:** registry endpoints are configured in the Composite's own settings (`registries`), because PM holds no registry endpoints yet, and the Composite enforces a per-pod rate limit itself. See [what the first version does](#what-the-first-version-does).
{% endhint %}

## Checks when a use case is published

A use case moves from `draft` → `validated` → `published` only if all of these pass:

1. `purpose` is allowed by the Composite's scope policy (the department's ceiling) in the PM of each department the use case reads.
2. Each source's `scopes` and `optional_scopes` (earlier `request_scopes`) ⊆ that controller's **approved** ceiling. A source whose scopes aren't yet approved can stay in the configuration, but it returns `denied` until the department approves them.
3. `input.subject.id_types` ⊆ the ceilings' allowed subject identifier types.
4. Every `mapping` path refers only to fields covered by the requested scopes, using each registry's published scope-to-field mapping. A use case can't map a field it didn't ask for.
5. The query templates render valid DCI requests against sample data. The sandbox runs each use case end to end with test fixtures.
6. The response schema validates against the mapped output.

Publishing is done by the Agri Stack platform team. Because the configuration can't widen access, it doesn't need department approval: each department approves its ceiling in its own PM, and each partner's grant of the use case is approved in the Exchange's PM ([who approves what](../architecture/data-sharing-policies.md#who-approves-what)).

{% hint style="info" %}
**First version:** only check 5 is done, partly: every template is rendered with sample input when the file is loaded, and must produce a valid query. The other checks are not built yet ([open items](../open-items/README.md)).
{% endhint %}

## At runtime and worked example

How the Composite serves a request, hop by hop (partner checks, consent tokens, each registry's own check, the signed response), is in the [request flow](../architecture/request-flow.md); what the first version does per request is [below](#what-it-does-per-request). A worked example with the shipped `loan-profile` use case, the same one the test scripts run, with its request and response, is in the [partner guide](../partner-guide.md#worked-example-loan-profile).

## Where configurations live

* **Storage:** configuration files, query templates and schemas are kept in a Git repository, reviewed like code, and loaded by the Composite service. An admin UI is optional.
* **Sandbox:** each published use case appears in the developer sandbox with its schema, sample request and response, and a test harness.
* **Adding a use case** (e.g. `input-subsidy-eligibility`) means a new configuration file, plus a policy for it per partner in the Exchange's PM (**Add policy**). No code changes are needed unless the use case requires a new kind of derived field.

{% hint style="info" %}
**First version:** use cases are YAML entries in the Composite's Helm values, rendered into a ConfigMap and edited in Rancher's **Edit YAML** view (or your own ConfigMap); the sample is also kept in the repository at [`composite/use-cases/loan-profile.yaml`](https://github.com/openg2p/agri-stack/blob/develop/composite/use-cases/loan-profile.yaml). There is no sandbox yet.
{% endhint %}

## What the first version does

* **One generic service**, `openg2p-agri-composite`. The partner API is stateless; a database is used only by the [console](console.md), for its call log.
* **Use cases are configuration**, not code: YAML files in a ConfigMap.
* **No partner data is stored.** Logs carry the request ID, use case, partner, statuses and timings only; the response, audit events and call log also name the consent used (its ID, as the Exchange CM gives it).

### What it does per request

1. Verifies the partner's signature against PM (key `PARTNER_<SENDER_ID>`). Checks the message is fresh (`header.message_ts` within 300 seconds) and addressed to the Composite.
2. Checks that the partner has a policy for the use case (`name@major`) in the Exchange's PM: cached; no grant fails with `partner_not_allowed`, and PM unreadable with nothing cached with `partner_policy_unavailable`.
3. Validates the input (subject type, parameters) and applies the per-partner rate limit.
4. Checks the consent. For a `consent_jws`: the partner's signature, the subject, the validity window, and a grant with the use case's required [data scopes](use-case-configuration.md#data-scopes) for every mandatory source; the Exchange CM then accepts it only if the partner's policy for the use case allows partner-signed consents (`partner_consent_not_accepted`). A `consent_id` is checked by the Exchange CM (active, in its validity, obtained by this partner, about this subject). With no consent, the Exchange CM looks up the partner's active consent for this subject and use case (Exchange mode only; passthrough mode refuses with `consent_required`).
5. Gets a consent token per registry from the Exchange CM, sending the partner, the subject, the use case and its purpose so that the CM applies the partner's policy for that use case. A deny fails the request (`consent_denied`, with the CM's reason, e.g. `consent_not_found`); a mandatory source without a consent token fails it too; an optional one is reported `unavailable`.
6. Calls the sources in dependency order (`depends_on`), in parallel within a level, each a DCI sync search signed with the Composite's key, naming the partner in `header.meta.on_behalf_of` and carrying that registry's consent token. Per-source timeout and retries; overall timeout.
7. Maps the results, computes derived fields, and returns a response signed by the Composite, with a status per source (`ok`, `no_record`, `denied`, `unavailable`, `error`).
8. Sends audit events to the Audit Manager, without ever blocking the request.

Each registry still decides what it releases ([how departments trust the Exchange](../architecture/exchange.md#how-departments-trust-it)).

### Not built yet

* Checks when a use case is published (against the departments' ceilings in PM).
* Data-blind mode.
* Daily quotas and rate limits across pods (shared counters).
* Registry endpoints held in PM rather than in configuration.
* Calling the crop sources in parallel with the farmer when the partner already sends a Farmer ID.
* A configuration UI.
* A machine-readable response schema per use case. The describe endpoint lists output field names only.

These are tracked in [TODOs and open items](../open-items/README.md#composite).
