---
description: >-
  The Composite's use-case file format and how it behaves at run time: which
  registry APIs it calls, query templates, response mapping,
  failure handling, the consent mode and the output format.
---

# Use-Case Configuration

The use-case file format of the [Composite](README.md) as built, and how a use case runs. The code, Helm chart and scripts are in [agri-stack/composite](https://github.com/openg2p/agri-stack/tree/develop/composite); installing it, every chart option and what is not built yet are in [Deployment: Composite](../deployment/composite.md). Partners calling it should read the [partner guide](../partner-guide.md).

The endpoints partners call, with request and response formats and error codes, are on [Composite API](api.md); how a partner signs and reads them, step by step, in the [partner guide](../partner-guide.md).

## Which registry APIs the Composite calls

**Every source is one DCI synchronous search** on a registry's **partner API**: `POST /dci/registry/sync/search`. The Composite calls nothing else on a registry, and nothing about a registry is hard-coded: the endpoints come from the service's settings, and what is asked from each comes from the use-case file.

**For `loan-profile`, per request:**

1. **One call to the Farmer Registry** (`farmer`, `reg_type: Farmer`), by `foundational_id` (FAN) or `functional_record_id` (farmer ID).
2. Then **two parallel calls to the Crop Sown Registry**: `season_summaries` (`reg_record_type: spdci-extensions-agri:ActivityAggregate`) and `crop_seasons` (`spdci-extensions-agri:CropSeason`), both by the farmer ID read from the farmer record.

The Composite first makes one call to the Exchange Consent Manager (see [consent mode](#consent-mode)). `loan-profile` sets `retries: 0`, so there are no extra calls; a use case that sets retries retries on network errors and 5xx only.

**What each call looks like.** The Composite renders the source's query template, adds the rest, signs the envelope with its own key and posts it:

```json
{"signature": "<composite's detached JWS>",
 "header": {"version": "1.0.0", "message_id": "…", "message_ts": "…", "action": "search",
            "sender_id": "agri-composite", "receiver_id": "farmer-registry",
            "total_count": 1, "is_msg_encrypted": false,
            "meta": {"on_behalf_of": "bank-a", "request_id": "<request_id>", "use_case": "loan-profile@1"}},
 "message": {"transaction_id": "<request_id>",
             "search_request": [{"reference_id": "<request_id>-farmer", "timestamp": "…", "locale": "eng",
                                 "search_criteria": {"version": "1.0.0",
                                                     "reg_type": "Farmer",
                                                     "reg_record_type": "spdci-extensions-dci:Farmer",
                                                     "query_type": "expression",
                                                     "query": {"type": "expression", "value": {"…": "…"}},
                                                     "pagination": {"page_size": 1, "page_number": 1},
                                                     "authorize": {"consent_jws": "<this registry's consent token>"}}}]}}
```

* `sender_id` is the Composite's PM ID; the registry verifies the Composite's signature against `PARTNER_AGRI_COMPOSITE`.
* `receiver_id` is the source's controller ID unless the registry's `receiver_id` is set.
* `header.meta.on_behalf_of` names the partner. The registry logs it; it never grants access.
* The registry's consent token travels at `search_criteria.authorize.consent_jws`, as for a partner calling the registry directly ([Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md)).

**Where it is configured:**

| What | Where | Example |
| --- | --- | --- |
| The registry's URL, per controller | Helm `composite.registries.<controller>.url` → env `AGRI_COMPOSITE_REGISTRIES` | `farmer-registry: https://partner-fr.<dept-domain>/dci/registry/sync/search` |
| Verify the registry's response signature (optional) | `composite.registries.<controller>.partnerId`: the registry's PM partner ID; its responses are verified against `PARTNER_<ID>` | empty (off) by default |
| The `receiver_id` sent (optional) | `composite.registries.<controller>.receiverId` | defaults to the controller ID |
| Which registry a source calls | use case `sources[].controller` | `farmer-registry` |
| What it asks for | use case `sources[].dci.reg_type`, `dci.reg_record_type`, `dci.query_template` | `Farmer`, `spdci-extensions-dci:Farmer` |

`AGRI_COMPOSITE_REGISTRIES` is JSON: `{"<controller>": {"url": "…", "partner_id": "…", "receiver_id": "…"}}`. The chart builds it from `composite.registries`. A use-case file whose sources name a controller with no configured endpoint **fails to load** (it is logged and skipped). Partner Management has no registry endpoints yet, so they are set here ([open items](../open-items/README.md#composite)). To add a registry, see [adding a data source](adding-a-data-source.md).

## Use-case file format

One YAML file per use case, validated strictly when loaded (**unknown keys are errors**). Who may call a use case is not in the file: a partner needs a policy for it (`name@major`) in the Exchange's Partner Management ([data-sharing policies](../architecture/data-sharing-policies.md)); the former `allowed_partners` key is an unknown key. Pods check the directory every 30 s and reload changed files without a restart. A file that fails validation is logged and skipped; if an earlier version of it loaded, that version keeps serving. Only `status: published` is served; if two files publish the same name and major, the higher version is served.

| Key | |
| --- | --- |
| `use_case` | Lower-case slug (letters, digits, `-`) |
| `version` | Semver `MAJOR.MINOR.PATCH`. Partners call `use_case@<major>`; without a major, they get the highest published major |
| `status` | `draft`, `validated`, `published`, `deprecated` or `retired`; only `published` is served |
| `title`, `description` | Shown by the describe endpoints |
| `policy` | Informational |
| `purpose` | Sent to the Exchange CM with the use case (`name@major`); the consent's purpose must match it, and the partner's policy for the use case must allow it |
| `consent.required` | Default `true`: a consent is needed — `message.consent_jws` (checked: signature, subject, validity, grants for mandatory sources), `message.consent_id`, or neither, when the Exchange CM looks it up (both checked by the Exchange CM; exchange mode only) |
| `input.subject.id_types` | Allowed `message.subject.type` values, e.g. `[FAYDA_FAN, FARMER_ID]` (see [subject ID types](#subject-id-types)) |
| `input.parameters.<name>` | `{type: integer\|number\|string\|boolean, description, required, default, min, max, enum}`. For strings, `min`/`max` bound the length. Unknown parameters are rejected. |
| `input.batch.max_subjects` | Must be 1 |
| `sources[]` | `{id, controller, requirement: mandatory\|optional, depends_on: [], scopes: [], optional_scopes: [], dci: {reg_type, reg_record_type, query_template}, timeout_ms, retries}`. `id` matches `^[a-z][a-z0-9_]*$`; `timeout_ms` 50–120000; `retries` 0–5 (default 0); `requirement` defaults to `mandatory`. `depends_on` may not form a cycle. |
| `sources[].scopes`, `sources[].optional_scopes` | The registry's [data scopes](#data-scopes) the source uses (IDs `<controller>.<name>`). See below. |
| `response.mapping` | `out.path: <JSONPath>` over `{subject, parameters, sources: {id: {status, records: [...]}}}`. Wildcards and filters give lists; other paths give one value. |
| `response.derived` | `out.path: <expr>` using `sum`, `count`, `min`, `max`, `first`, `round` over JSONPaths and numbers (no `eval`). The mapped output is at `$.data`. |
| `response.source_status` | Include `sources` in the response (default `true`) |
| `execution.overall_timeout_ms` | 100–300000; default from `DEFAULT_OVERALL_TIMEOUT_MS` (10000) |
| `execution.partial_response` | `allowed` (default): only a failing mandatory source fails the request. `denied`: any failing source does. |
| `limits.rate_per_partner` | e.g. `60/min` (units `s`, `min`, `hour`), as a token bucket per pod and worker. Limits across pods are to do (shared counters). |
| `audit.events` | Which audit events to send: `request`, `source_call`, `response` (default: all three) |

### Subject ID types

A subject ID type names the kind of identifier a request's subject is given in. It is a label, not a registry field: the use case's query templates map it to the field each registry searches, and the same label must be allowed in two places.

| Subject ID type | What it is | Farmer Registry field | Crop Sown Registry field |
| --- | --- | --- | --- |
| `FAYDA_FAN` | Fayda (national ID) FAN | `foundational_id` | `fayda_fan` |
| `FARMER_ID` | Farmer Registry ID, e.g. `FR-0007` | `functional_record_id` | `farmer_id` |

* **Use case:** `input.subject.id_types` lists the types a partner may send as `message.subject.type`.
* **Policies in Partner Management:** the partner's policy for the use case and the Composite's scope policy in each department must allow the type (`allowed_subject_id_types`, empty = any), or the CM refuses the consent.


### Data scopes

Each source names the data scopes it uses, from its registry's catalogue (signed `POST /partner/data_scopes` on the registry's partner API, or the console's **Registries** page). The use case, set by the admin, fixes what is asked for; a partner does not pick scopes.

* **`scopes` (required):** the partner's consent must grant every one. Missing for a **mandatory** source: the request fails (`403 consent_scope_missing`). Missing for an **optional** source: it is not called and reported `denied`.
* **`optional_scopes`:** may be left out of the consent; the fields they cover then come back `null`.
* **Nothing else is asked for.** The Composite asks the Exchange Consent Manager for consent tokens with only these scopes (`request_context.requested_scopes`), so each registry returns no other field.
* A scope ID must belong to the source's registry (`<controller>.`), may not be listed twice, nor in both lists. `request_scopes` is accepted as the earlier name of `scopes`.
* A source with neither list has no scope check (its registry's grant is used as it is); its registry's consent token then carries every scope the consent grants for that registry.
* A grant with no `data_scopes` (including a legacy consent with `data_controller` only) grants no scopes, so it fails a source with required scopes.
* The describe endpoint lists each source's scopes and, per registry, `consent_scopes: {required, optional}`: what to grant in the consent, and what each department's ceiling for the Composite must allow.

Also accepted from the design but **not acted on yet** (logged once at load): `owner`, `consent.collection`, `consent.mode`, `response.schema`, `response.correlate_on`, `response.mode: merged`, `execution.fan_out: parallel`, and `limits.daily_quota_per_partner`.

Output paths (`mapping` and `derived` keys) are dot-separated identifiers; each may be defined once, and a path can't be both a value and the parent of another.

A field built from a source that failed (`denied`, `unavailable`, `error`) is `null`; `[]` and `0` mean the registry answered and has nothing. So the Composite can tell which sources a field uses, name them in dotted form: `$.sources.<id>...` and `$.data.<path>`. A `[...]`, `*` or `..` right after `$`, `$.sources` or `$.data` is refused at load.

A rendered query whose expression has an empty `subject_id` (e.g. the farmer record carries no farmer ID) is not sent; the source is reported `error`. A list query that returns a full page (`page_size` above 1) is reported with the detail "the first N records only".

## Query templates

A template is sandboxed Jinja, given inline or as the name of a `.j2` (`.jinja`, `.jinja2`) file next to the use case (a plain file name: a ConfigMap has no subdirectories). It renders the query part of the DCI `search_criteria`, as `{"query_type", "query": {"type", "value"}, "pagination"?, "sort"?}`. The Composite adds `version`, `reg_type`, `reg_record_type` and the consent.

* **Context:** `subject` (`type`, `value`), `parameters` (every declared parameter; unset ones are `none`), `sources` (the results of `depends_on`: `{id: {status, records}}`), `request_id`, `today` (ISO date) and `use_case`.
* Use `| tojson` for values.
* Keep a space between consecutive braces (`} }`) so literal JSON doesn't read as `{{ … }}`.
* Templates are rendered with sample input when they're loaded (each subject type, with default and with all parameters), and must produce valid queries; otherwise the file doesn't load.

## Response mapping and derived values

* **Mapping:** each output path gets the value of a JSONPath (jsonpath-ng, extended syntax with filters) over `{subject, parameters, sources: {<id>: {status, records}}}`. A path with a wildcard, slice, filter or recursive descent gives the list of all matches; any other path gives its single value, or `null`.
* **Derived:** function calls over JSONPaths and numbers, parsed without `eval`: `sum`, `count`, `min`, `max`, `first`, `round`. Derived expressions also see the mapped output at `$.data`.
* A mapping or derived value that fails is logged and set to `null`; it never fails the request.

## Failure handling

| Setting / situation | Behaviour |
| --- | --- |
| `requirement: mandatory` | The source must succeed (`ok` or `no_record`), and the consent must have a grant for its controller, or the request fails |
| `requirement: optional` | Failure is reported in `sources` and the request still succeeds (with `partial_response: allowed`). No grant for it in the consent → `denied`, not called |
| `timeout_ms` | Per attempt; default `DEFAULT_SOURCE_TIMEOUT_MS` (5000) |
| `retries` | Extra attempts **on network errors (connect, read, timeout) and HTTP 5xx only**, with a short backoff (0.1 s × attempt, at most 0.5 s). A 4xx or a DCI rejection is not retried. |
| `overall_timeout_ms` | When reached, every source not yet finished is `unavailable` with `detail: "overall timeout reached"` |
| `depends_on` | A source whose dependency is not `ok` is **not called**; it takes the dependency's status, with `detail: "not called: dependency '<id>' is <status>"` |
| `partial_response: allowed` | Only a failing mandatory source fails the request |
| `partial_response: denied` | Any source that is `denied`, `unavailable` or `error` fails the request |

**Source statuses** come from the registry's answer:

| Status | When |
| --- | --- |
| `ok` | The search succeeded with records |
| `no_record` | The search succeeded with none |
| `denied` | HTTP 401/403; or a rejected search whose reason reads like an authorisation decision (consent, not permitted, subject mismatch, `controller_not_granted`…); or no grant in the consent |
| `unavailable` | Unreachable, timed out, HTTP 408/429/5xx (after retries), or the overall timeout |
| `error` | Any other non-200, a rejected search for another reason, a non-JSON or malformed answer, a response signature that does not verify (when `partnerId` is set), a template that fails to render, no endpoint configured |

**When the request fails** because of a source, the HTTP status is: any `denied` → **403** `source_denied`; else any `unavailable` → **504** if a timeout was involved, otherwise **503** (`source_unavailable`); else **502** `source_error`. `sources` is still included.

**`loan-profile`'s settings:** `farmer` mandatory; `season_summaries` and `crop_seasons` optional and `depends_on: [farmer]`; each `timeout_ms: 10000`, `retries: 0` (a slow registry search is not retried: a retry only doubles the wait); `overall_timeout_ms: 25000` (farmer, then the crop sources); `partial_response: allowed`. So the request fails only when the Farmer Registry fails (or denies), and the crop data is best effort.

## Consent mode

The consent mode is `exchange` (the chart default), as on the Agri Stack Exchange (`agrix`, see the [deployment topology](../deployment/README.md#topology)). Each registry receives its **own consent token** from the Exchange CM, not the partner's consent. The partner onboards and is granted use cases only at the Exchange (its PM); each department CM trusts the Exchange CM's consent tokens and applies the department's ceiling for the Composite, its scope policy in the department's PM.

After the partner's request signature and, for a `consent_jws`, consent checks (signature, subject, validity, grants), the Composite calls the Exchange CM's `POST /consent/v1/validate` with:

```json
{"consent_jws": "<the partner's consent>", "partner_id": "agri-composite",
 "issue_receipts": true,
 "request_context": {"subject_id": {"type": "FAYDA_FAN", "value": "…"},
                     "use_case": "loan-profile@1", "purpose": "credit-assessment",
                     "requested_scopes": ["<the use case's scopes>"]}}
```

With a `consent_id`, the Composite sends `"consent_id"` and `"consent_partner_id": "<the calling partner>"` instead of `consent_jws`; with neither, only `consent_partner_id`, and the Exchange CM looks up the partner's active consent for this subject and use case (none → `consent_not_found`, [consent by lookup](../../consent-management/api/verification-api.md#consent-by-lookup)). A `consent_jws` is accepted only if the partner's policy for the use case allows partner-signed consents (else `partner_consent_not_accepted`). With `use_case` (and the use case's `purpose`), the Exchange CM applies the calling partner's policy for that use case from PM: it must exist (else `use_case_not_granted`) and the consent's purpose must match. The Exchange CM checks a stored or looked-up consent (active, in its validity, obtained by that partner, about this subject) and returns its grants per registry with the consent tokens; the Composite applies the use case's scope rules to those grants (`consent_grant_missing`, `consent_scope_missing`).

`partner_id` is the Composite's partner ID, which must be one of the Exchange CM's **token presenters** (`receiptPresenters`). On `permit`, the answer carries `receipts: {<data_controller>: <consent token JWS>}` (consent tokens are called *receipts* in the API), and each source's DCI search carries its controller's consent token in `search_criteria.authorize.consent_jws`. The registry passes it to its own CM as usual.

| Situation | Result |
| --- | --- |
| Exchange CM answers `deny` | **403** `consent_denied` (with CM's reason code); no registry is called |
| No consent token for a **mandatory** source's controller | **403** `consent_receipt_missing`; no registry is called |
| No consent token for an **optional** source's controller | The source is `unavailable`, not called, with `detail: "not called: the exchange Consent Manager issued no consent receipt for <controller>"` |
| Exchange CM unreachable, timed out, HTTP 408/429/5xx, or no URL configured | **503** `consent_exchange_unavailable` (fails closed) |
| Exchange CM answers another non-200 or a non-JSON body | **502** `consent_exchange_error` |
| Use case with `consent.required: false` | The Exchange CM is not called and registries get no consent |

## Output format

* **The envelope** is DCI-style: `{signature, header, message}`, signed by the Composite (detached JWS over `{header, message}`), `header.action: on-query`, `header.status: succ | rjct`.
* **`message.data` is defined per use case** by its `mapping` and `derived` keys: each output path becomes a nested object (`farmer.name` → `{"farmer": {"name": …}}`).
* **Records keep the registries' shapes.** Where a mapping copies records (e.g. `land.parcels`, `crops.seasons`), they are the registries' DCI / SPDCI records (e.g. the Farmer Registry's `farm_details`, the Crop Sown Registry's `…:CropSeason` records with `crop_season`, `measures`, `location`, `farmer_reference`), already clamped by each registry to the consented scopes.
* **This is not an open standard.** The envelope follows DCI conventions; the `data` shape is Agri Stack's, per use case.
* **No machine-readable schema is published yet.** The describe endpoint lists the **output field names only** (`output_fields`). A JSON Schema per use case (an endpoint serving `response.schema`) is a [TODO](../open-items/README.md#composite).

## The `loan-profile` use case

The sample use case, [`composite/use-cases/loan-profile.yaml`](https://github.com/openg2p/agri-stack/blob/develop/composite/use-cases/loan-profile.yaml) (the Helm chart's default `composite.useCases.loan-profile` is kept identical; a test checks it):

```yaml
use_case: loan-profile
version: 1.0.0
status: published
title: Farmer loan profile
description: >-
  Identity, location, land and declared crops from the Farmer Registry, and crop
  seasons and season summaries from the Crop Sown Registry, for a loan decision.
  Pass crop_year and season to get one season (the total area sown is then that
  season's); without them, all of the farmer's seasons come back, newest first.

policy: credit-assessment
purpose: credit-assessment
consent:
  required: true

input:
  subject:
    id_types: [FAYDA_FAN, FARMER_ID]
  parameters:
    crop_year:
      type: integer
      description: Crop year, e.g. 2019 (Ethiopian calendar year the season belongs to)
      min: 1990
      max: 2100
    season:
      type: string
      description: Season code
      enum: [SEASON_MEHER, SEASON_BELG, SEASON_IRRIGATION]
  batch: { max_subjects: 1 }

sources:
  - id: farmer
    controller: farmer-registry
    requirement: mandatory
    scopes: [farmer-registry.farmer_identifiers, farmer-registry.personal_details,
             farmer-registry.land, farmer-registry.main_crops]
    optional_scopes: [farmer-registry.household_location, farmer-registry.land_location]
    dci:
      reg_type: Farmer
      reg_record_type: spdci-extensions-dci:Farmer
      query_template: |
        {%- set field = 'foundational_id' if subject.type == 'FAYDA_FAN' else 'functional_record_id' -%}
        {"query_type": "expression",
         "query": {"type": "expression",
                   "value": {"expression": {"query": {"{{ field }}": {"$eq": {{ subject.value | tojson }} } } } } },
         "pagination": {"page_size": 1, "page_number": 1} }
    timeout_ms: 10000
    retries: 0

  - id: season_summaries
    controller: crop-sown-registry
    requirement: optional
    depends_on: [farmer]
    scopes: [crop-sown-registry.farmer_reference, crop-sown-registry.crop_season,
             crop-sown-registry.measures]
    optional_scopes: [crop-sown-registry.location]
    dci:
      reg_type: CropSown
      reg_record_type: spdci-extensions-agri:ActivityAggregate
      query_template: |
        {%- set ns = namespace(fid=none) -%}
        {%- if subject.type == 'FARMER_ID' -%}{%- set ns.fid = subject.value -%}{%- endif -%}
        {%- for rec in sources.farmer.records -%}
          {%- for ident in rec.farmer_personal_details.member_identifier or [] -%}
            {%- if ns.fid is none and ident.identifier_type == 'FARMER_ID' and ident.identifier_value -%}
              {%- set ns.fid = ident.identifier_value -%}
            {%- endif -%}
          {%- endfor -%}
        {%- endfor -%}
        {"query_type": "expression",
         "query": {"type": "expression",
                   "value": {"expression": {"query": {
                     "subject_id": {{ ns.fid | tojson }},
                     "aggregate_type": "FARMER_SEASON_SUMMARY"
                     {%- if parameters.crop_year is not none %}, "crop_year": {{ parameters.crop_year | tojson }}{% endif %}
                     {%- if parameters.season %}, "season": {{ parameters.season | tojson }}{% endif %} } } } },
         "pagination": {"page_size": 20, "page_number": 1} }
    timeout_ms: 10000
    retries: 0

  - id: crop_seasons
    controller: crop-sown-registry
    requirement: optional
    depends_on: [farmer]
    scopes: [crop-sown-registry.farmer_reference, crop-sown-registry.crop_season,
             crop-sown-registry.measures]
    optional_scopes: [crop-sown-registry.location]
    dci:
      reg_type: CropSown
      reg_record_type: spdci-extensions-agri:CropSeason
      query_template: |
        {%- set ns = namespace(fid=none) -%}
        {%- if subject.type == 'FARMER_ID' -%}{%- set ns.fid = subject.value -%}{%- endif -%}
        {%- for rec in sources.farmer.records -%}
          {%- for ident in rec.farmer_personal_details.member_identifier or [] -%}
            {%- if ns.fid is none and ident.identifier_type == 'FARMER_ID' and ident.identifier_value -%}
              {%- set ns.fid = ident.identifier_value -%}
            {%- endif -%}
          {%- endfor -%}
        {%- endfor -%}
        {"query_type": "expression",
         "query": {"type": "expression",
                   "value": {"expression": {"query": {
                     "subject_id": {{ ns.fid | tojson }}
                     {%- if parameters.crop_year is not none %}, "crop_year": {{ parameters.crop_year | tojson }}{% endif %}
                     {%- if parameters.season %}, "season": {{ parameters.season | tojson }}{% endif %} } } } },
         "pagination": {"page_size": 100, "page_number": 1} }
    timeout_ms: 10000
    retries: 0

response:
  # JSONPath over {subject, parameters, sources: {<id>: {status, records: [...]}}}.
  mapping:
    farmer.name:        "$.sources.farmer.records[0].farmer_personal_details.demographic_info.name"
    farmer.sex:         "$.sources.farmer.records[0].farmer_personal_details.demographic_info.sex"
    farmer.birth_date:  "$.sources.farmer.records[0].farmer_personal_details.demographic_info.birth_date"
    farmer.identifiers: "$.sources.farmer.records[0].farmer_personal_details.member_identifier"
    farmer.location:    "$.sources.farmer.records[0].family_details.place"
    farmer.main_crops:  "$.sources.farmer.records[0].main_crops"
    land.parcels:       "$.sources.farmer.records[0].farm_details"
    crops.seasons:      "$.sources.crop_seasons.records"
    crops.season_summaries: "$.sources.season_summaries.records"
  # Functions: sum, count, min, max, first, round. The output so far is at $.data.
  derived:
    land.parcel_count: "count($.sources.farmer.records[0].farm_details)"
    # Sum of each parcel's land_size, in the parcels' unit (farm_details[].measurement).
    land.total_size:   "round(sum($.sources.farmer.records[0].farm_details[*].land_size), 4)"
    crops.total_area_sown_ha: "round(sum($.sources.crop_seasons.records[*].measures.area_sown_ha), 4)"
  source_status: true

execution:
  overall_timeout_ms: 25000
  partial_response: allowed   # a failing mandatory source (farmer) fails the request

limits:
  rate_per_partner: 60/min
```

* The Crop Sown Registry knows the farmer by farmer ID, so both crop sources depend on the farmer source and read `FARMER_ID` from its record (or use the subject itself when the partner sends a `FARMER_ID`).
* **Consent** (one consent, a grant per registry) names each registry's [data scopes](../../products/registry/registry/design/data-scopes.md). The use case lists them per source (`scopes`, `optional_scopes`); the describe endpoint gives them per registry as `consent_scopes`, and partners grant those. `farmer-registry.farmer_identifiers` is required, since the farmer ID the crop sources query by is read from it. The partner test kit grants every listed scope:
  * `farmer-registry`: `farmer_identifiers`, `personal_details`, `land`, `main_crops` (required); `household_location`, `land_location` (optional);
  * `crop-sown-registry`: `farmer_reference`, `crop_season`, `measures` (required); `location` (optional). Each as `<registry>.<name>`, e.g. `crop-sown-registry.crop_season`.

## Service settings, Helm values and scaling

The chart's options, the service's environment settings and scaling are in [Deployment: Composite](../deployment/composite.md#all-options).
