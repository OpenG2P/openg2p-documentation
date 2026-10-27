---
description: >-
  The Composite's use-case file format, key by key: identity and versioning
  (name@major), purpose and consent, inputs and parameters, sources and their
  data scopes, query templates, response mapping, derived values and output,
  execution, limits and audit, with the shipped loan-profile file.
---

# Use-Case Configuration

The format of a use-case file, as the [Composite](README.md) accepts it. How a use case runs (the registry calls, failure handling, the consent mode) is in the [Composite overview](README.md#what-the-first-version-does); where the files go, the reload interval and the service settings are in [Deployment: Composite](../deployment/composite.md#use-cases); writing one step by step is in [Creating a Use Case](creating-a-use-case.md).

## File structure

One YAML file per use case, validated strictly when it loads: **unknown keys are errors**. A file that fails validation is logged and skipped (shown with its error on the [console](console.md)); if an earlier version of it loaded, that version keeps serving. A query template can sit in its own file next to the use case ([query templates](#query-templates)).

| Key | Required | Section |
| --- | --- | --- |
| `use_case`, `version`, `status`, `title`, `description` | All but `description` | [Identity and versioning](#identity-and-versioning) |
| `policy`, `purpose`, `consent` | No | [Purpose and consent](#purpose-and-consent) |
| `input` | Yes | [Inputs](#inputs) |
| `sources` | Yes, at least one | [Sources](#sources) |
| `response` | No | [Response mapping and derived values](#response-mapping-and-derived-values) |
| `execution`, `limits`, `audit` | No | [Execution, limits and audit](#execution-limits-and-audit) |

Who may call a use case is **not** in the file: a partner needs a policy for it (`name@major`) in the Exchange's Partner Management ([data-sharing policies](../architecture/data-sharing-policies.md)). The former `allowed_partners` key is an unknown key.

## Identity and versioning

| Key | |
| --- | --- |
| `use_case` | The name: a lower-case slug of letters, digits and `-`, starting with a letter and not ending with `-` |
| `version` | Semver `MAJOR.MINOR.PATCH` |
| `status` | `draft`, `validated`, `published`, `deprecated` or `retired`. Only `published` is served |
| `title` | Not empty. Shown by the describe endpoints and the console |
| `description` | Shown by the describe endpoints and the console |

Partners call a use case as **`name@major`** (e.g. `loan-profile@1`); without a major they get the highest published one. A breaking change to the response (a field renamed or removed) needs a new major; an added optional source or output field is a minor. Two files may publish different majors of one name side by side; if two publish the same name and major, the higher version is served and the other is reported as an error.

## Purpose and consent

| Key | |
| --- | --- |
| `policy` | Informational label |
| `purpose` | Sent to the Exchange CM with `name@major`: the consent's purpose must match it, and the partner's policy for the use case must allow it |
| `consent.required` | Default `true`. `false`: the Exchange CM is not called and registries get no consent token. How the consent is presented and checked: [consent mode](README.md#consent-mode) |

## Inputs

| Key | |
| --- | --- |
| `input.subject.id_types` | Required, not empty: the [subject ID types](#subject-id-types) a partner may send as `message.subject.type` |
| `input.parameters.<name>` | The [parameters](#parameters) a partner may send in `message.parameters` |
| `input.batch.max_subjects` | Must be `1` (one farmer per request) |

### Subject ID types

A subject ID type names the kind of identifier a request's subject is given in. It is a label, not a registry field: the use case's query templates map it to the field each registry searches, and the same label must be allowed in two places.

| Subject ID type | What it is | Farmer Registry field | Crop Sown Registry field |
| --- | --- | --- | --- |
| `FAYDA_FAN` | The national ID (as named in the Ethiopia example) | `foundational_id` | `fayda_fan` |
| `FARMER_ID` | Farmer Registry ID, e.g. `FR-0007` | `functional_record_id` | `farmer_id` |

* **Use case:** `input.subject.id_types` lists the types a partner may send.
* **Policies in Partner Management:** the partner's policy for the use case and the Composite's scope policy in each department must allow the type (`allowed_subject_id_types`, empty = any), or the CM refuses the consent.

### Parameters

Each parameter is a name (an identifier) mapped to:

| Key | |
| --- | --- |
| `type` | `integer` (or `int`), `number`, `string` (default) or `boolean` |
| `description` | Shown by the describe endpoints |
| `required` | Default `false` |
| `default` | Used when the partner leaves it out; must itself be valid |
| `min`, `max` | Bounds for numbers; for strings, the length |
| `enum` | The allowed values (not empty) |

A parameter the use case does not declare is rejected. Templates see every declared parameter; one that is not sent and has no default is `none`.

## Sources

One entry per registry search.

| Key | |
| --- | --- |
| `id` | Required, unique, matches `^[a-z][a-z0-9_]*$`. Named in `depends_on`, templates and mappings as `sources.<id>` |
| `controller` | Required: the registry's data controller ID (e.g. `farmer-registry`). It must have an endpoint in the Composite's settings ([Deployment: registries](../deployment/composite.md#registries)), or the file does not load |
| `requirement` | `mandatory` (default) or `optional`: whether the source failing fails the request ([failure handling](README.md#failure-handling)) |
| `depends_on` | A source ID or a list of them. This source runs after them and its template sees their results; it is not called if one of them is not `ok`. No unknown IDs, no self-reference, no cycles |
| `scopes`, `optional_scopes` | The registry's [data scopes](#data-scopes) the source uses. `request_scopes` is accepted as the earlier name of `scopes` |
| `dci.reg_type`, `dci.reg_record_type` | Required: sent in the DCI `search_criteria` (e.g. `Farmer`, `spdci-extensions-dci:Farmer`) |
| `dci.query_template` | Required: the [query template](#query-templates), inline or a file name |
| `timeout_ms` | Per attempt, 50–120000; default from the service setting `DEFAULT_SOURCE_TIMEOUT_MS` (5000) |
| `retries` | 0–5, default 0. Extra attempts on network errors and HTTP 5xx only |

### Data scopes

Each source names the data scopes it uses, from its registry's catalogue (signed `POST /partner/data_scopes` on the registry's partner API, or the console's **Registries** page). The use case, set by the admin, fixes what is asked for; a partner does not pick scopes.

* **`scopes` (required):** the partner's consent must grant every one. Missing for a **mandatory** source: the request fails (`403 consent_scope_missing`). Missing for an **optional** source: it is not called and reported `denied`.
* **`optional_scopes`:** may be left out of the consent; the fields they cover then come back `null`.
* **Nothing else is asked for.** The Composite asks the Exchange CM for consent tokens limited to these scopes, so each registry returns no other field.
* A scope ID is `<controller>.<name>` and must belong to the source's registry. It may not be listed twice, nor in both lists.
* A source with neither list has no scope check: its registry's consent token carries every scope the consent grants for that registry.
* A grant with no `data_scopes` (including a legacy consent with `data_controller` only) grants no scopes, so it fails a source with required scopes.
* The describe endpoint lists each source's scopes and, per registry, `consent_scopes: {required, optional}`: what to grant in the consent, and what each department's ceiling for the Composite must allow. A scope one source requires and another lists as optional is required.

### Query templates

A template is sandboxed Jinja that renders the query part of the DCI `search_criteria` as JSON. The Composite adds `version`, `reg_type`, `reg_record_type` and the consent token ([registry calls](README.md#registry-calls)).

* **Inline or a file:** `query_template` holds the template, or the plain name of a `.j2`, `.jinja` or `.jinja2` file next to the use case (no directories: a ConfigMap has none).
* **Output:** a JSON object with `query: {type, value}` and optionally `query_type` (default: `query.type`), `pagination` and `sort`; no other keys.
* **Context:** `subject` (`type`, `value`), `parameters` (every declared parameter), `sources` (the results of `depends_on`: `{id: {status, records}}`), `request_id`, `today` (ISO date) and `use_case` (`name@major`).
* Use `| tojson` for values. Keep a space between consecutive braces (`} }`) so literal JSON doesn't read as `{{ … }}`.
* **Checked at load:** each template is rendered for every subject ID type, with default and with all parameters (dependencies `ok` with no records), and must produce a valid query; otherwise the file does not load.
* A query whose expression has an empty `subject_id` (e.g. the farmer record carries no farmer ID) is not sent: the source is reported `error`.

## Response mapping and derived values

| Key | |
| --- | --- |
| `response.mapping` | `<output path>: <JSONPath>` |
| `response.derived` | `<output path>: <expression>` |
| `response.source_status` | Include the per-source statuses (`sources`) in the response. Default `true` |

* **Mapping:** each output path gets the value of a JSONPath (jsonpath-ng, extended syntax with filters) over `{subject, parameters, sources: {<id>: {status, records}}}`. A path with a wildcard, slice, filter or recursive descent gives the list of all matches; any other path gives its single value, or `null`.
* **Derived:** function calls over JSONPaths and numbers, parsed without `eval`: `sum`, `count`, `min`, `max`, `first`, `round`. Derived expressions also see the mapped output at `$.data`.
* **Name sources in dotted form:** `$.sources.<id>…` and `$.data.<path>`, so the Composite knows which sources a field uses. A `[...]`, `*` or `..` right after `$`, `$.sources` or `$.data` is refused at load.
* **Output paths** are dot-separated identifiers; each is defined once, and a path can't be both a value and the parent of another.
* A mapping or derived value that fails is logged and set to `null`; it never fails the request.

### Output

* **`message.data` is defined by the use case:** each output path becomes a nested object (`farmer.name` → `{"farmer": {"name": …}}`). The signed envelope around it is in [Composite API](api.md).
* **Failed sources give `null`:** a field built from a source that is `denied`, `unavailable` or `error` is `null`; `[]` and `0` mean the registry answered and has nothing.
* **Records keep the registries' shapes.** Where a mapping copies records (e.g. `land.parcels`, `crops.seasons`), they are the registries' DCI / SPDCI records, already clamped by each registry to the consented scopes.
* **Not an open standard.** The envelope follows DCI conventions; the `data` shape is Agri Stack's, per use case.
* **No machine-readable schema is published yet.** The describe endpoint lists the output field names only (`output_fields`); a JSON Schema per use case is a [TODO](../open-items/README.md#composite).

## Execution, limits and audit

| Key | |
| --- | --- |
| `execution.overall_timeout_ms` | 100–300000; default from the service setting `DEFAULT_OVERALL_TIMEOUT_MS` (10000). Must cover the slowest chain of `depends_on` |
| `execution.partial_response` | `allowed` (default): only a failing mandatory source fails the request. `denied`: any failing source does ([failure handling](README.md#failure-handling)) |
| `limits.rate_per_partner` | e.g. `60/min`; units `s`, `min`, `hour` (also `sec`, `second`, `m`, `minute`, `h`). Counted per pod and worker ([scaling](../deployment/composite.md#scaling-and-rate-limits)) |
| `audit.events` | Which audit events to send: `request`, `source_call`, `response` (default: all three) ([audit](../deployment/composite.md#audit)) |

## Accepted but not acted on

Keys from the [full design](README.md#example-configuration-full-design) that load but do nothing yet (each is logged once at load, except `response.mode` and `execution.fan_out`, which accept only their one built value):

* `owner`
* `consent.collection` (`cm-originated` or `partner-embedded`) and `consent.mode` (`single`): how consent is checked is a service setting ([consent mode](README.md#consent-mode))
* `response.schema`, `response.correlate_on`
* `limits.daily_quota_per_partner`
* `response.mode: merged` (data-blind is not built) and `execution.fan_out: parallel`

## The `loan-profile` use case

The sample use case, [`composite/use-cases/loan-profile.yaml`](https://github.com/openg2p/agri-stack/blob/develop/composite/use-cases/loan-profile.yaml) (the Helm chart's default `composite.useCases.loan-profile` is kept identical; a test checks it; the repository file also carries explanatory comments):

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

* **Sources:** `farmer` (mandatory) first; then `season_summaries` and `crop_seasons` (optional) in parallel. The Crop Sown Registry knows the farmer by farmer ID, so both crop sources depend on `farmer` and read `FARMER_ID` from its record (or use the subject itself when the partner sends a `FARMER_ID`). The request fails only when the Farmer Registry fails or denies; the crop data is best effort.
* **Timeouts:** each source `timeout_ms: 10000` with `retries: 0` (a slow registry search is not retried: a retry only doubles the wait); `overall_timeout_ms: 25000` covers the two levels.
* **Scopes:** one consent, with a grant per registry naming its [data scopes](../../products/registry/registry/design/data-scopes.md); the describe endpoint gives them per registry as `consent_scopes`. `farmer-registry.farmer_identifiers` is required, since the crop sources query by the farmer ID read from it. The partner test kit grants every listed scope:
  * `farmer-registry`: `farmer_identifiers`, `personal_details`, `land`, `main_crops` (required); `household_location`, `land_location` (optional);
  * `crop-sown-registry`: `farmer_reference`, `crop_season`, `measures` (required); `location` (optional).
