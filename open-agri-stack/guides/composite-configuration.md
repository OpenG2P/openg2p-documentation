---
description: >-
  Configuring the use-case composite: its API, which registry APIs it calls and
  where that is configured, the use-case file format, failure handling, output
  format, environment settings, Helm values and scaling.
---

# Composite Configuration

How to configure the [use-case composite](../design/use-case-composite.md) as built. The code, Helm chart and scripts are in [agri-stack/composite](https://github.com/openg2p/agri-stack/tree/develop/composite); what is built and what is not is on [composite as built](../implementation/composite.md). Partners calling it should read the [partner guide](partner-guide.md).

## API reference

| Method | Path | Auth | |
| --- | --- | --- | --- |
| `GET` | `/composite/v1/use-cases` | none | Published use cases: input, parameters, sources, output fields, the consent grants needed |
| `GET` | `/composite/v1/use-cases/{use_case}` | none | One use case (`name` or `name@major`; or the `X-Use-Case-Major` header) |
| `POST` | `/composite/v1/use-cases/{use_case}/query` | signed envelope | Run a query. `use_case` is `name` or `name@major`; the major version can also be sent in the `X-Use-Case-Major` header. Without a major, the highest published major is used. |
| `GET` | `/ping` | none | Health check |
| `GET` | `/docs` | none | OpenAPI UI |

Request (a detached JWS over `{header, message}`, as in DCI; `sender_id` is the partner's ID):

```json
{"signature": "<header>..<signature>",
 "header": {"version": "1.0.0", "message_id": "…", "message_ts": "2026-10-01T10:00:00Z",
            "action": "query", "sender_id": "bank-a", "receiver_id": "agri-composite"},
 "message": {"subject": {"type": "FAYDA_FAN", "value": "123456789012"},
             "parameters": {"crop_year": 2019, "season": "SEASON_MEHER"},
             "consent_jws": "<partner-signed consent with a grant per registry>"}}
```

Response: signed by the composite, `header.status` `succ`/`rjct`. The message is `{use_case, version, request_id, subject, sources: {id: {status, detail?}}, data}`. On failure, `data` is replaced by `error: {code, message}`, and the HTTP status is one of:

| Status | Meaning |
| --- | --- |
| 400 | Invalid envelope, input or stale timestamp |
| 401 | Bad signature or unknown partner |
| 403 | Partner not allowed, or a consent problem (`consent_*`), or a mandatory source denied |
| 404 | Unknown use case |
| 429 | Rate limit reached |
| 502 / 503 / 504 | A mandatory source failed (error / unavailable / timed out) |

The error codes, response envelope and signature verification are detailed in the [partner guide](partner-guide.md#step-10-read-the-response).

## Which registry APIs the composite calls

**Every source is one DCI synchronous search** on a registry's **partner API**: `POST /dci/registry/sync/search`. The composite calls nothing else on a registry, and nothing about a registry is hard-coded: the endpoints come from the service's settings, and what is asked from each comes from the use-case file.

**For `loan-profile`, per request:**

1. **One call to the Farmer Registry** (`farmer`, `reg_type: Farmer`), by `foundational_id` (FAN) or `functional_record_id` (farmer ID).
2. Then **two parallel calls to the Crop Sown Registry**: `season_summaries` (`reg_record_type: spdci-extensions-agri:ActivityAggregate`) and `crop_seasons` (`spdci-extensions-agri:CropSeason`), both by the farmer ID read from the farmer record.

Retries can add calls (one retry per source in `loan-profile`, on network errors and 5xx only).

**What each call looks like.** The composite renders the source's query template, adds the rest, signs the envelope with its own key and posts it:

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
                                                     "authorize": {"consent_jws": "<the partner's consent, unchanged>"}}}]}}
```

* `sender_id` is the composite's PM ID; the registry verifies the composite's signature against `PARTNER_AGRI_COMPOSITE`.
* `receiver_id` is the source's controller ID unless the registry's `receiver_id` is set.
* `header.meta.on_behalf_of` names the partner. The registry logs it; it never grants access.
* The consent travels at `search_criteria.authorize.consent_jws`, as for a partner calling the registry directly ([Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md)).

**Where it is configured:**

| What | Where | Example |
| --- | --- | --- |
| The registry's URL, per controller | Helm `composite.registries.<controller>.url` → env `AGRI_COMPOSITE_REGISTRIES` | `farmer-registry: http://fr-partner-api/dci/registry/sync/search` |
| Verify the registry's response signature (optional) | `composite.registries.<controller>.partnerId`: the registry's PM partner ID; its responses are verified against `PARTNER_<ID>` | empty (off) by default |
| The `receiver_id` sent (optional) | `composite.registries.<controller>.receiverId` | defaults to the controller ID |
| Which registry a source calls | use case `sources[].controller` | `farmer-registry` |
| What it asks for | use case `sources[].dci.reg_type`, `dci.reg_record_type`, `dci.query_template` | `Farmer`, `spdci-extensions-dci:Farmer` |

`AGRI_COMPOSITE_REGISTRIES` is JSON: `{"<controller>": {"url": "…", "partner_id": "…", "receiver_id": "…"}}`. The chart builds it from `composite.registries`. A use-case file whose sources name a controller with no configured endpoint **fails to load** (it is logged and skipped). Partner Management has no registry endpoints yet, so they are set here ([open items](../open-items/README.md#composite)). To add a registry, see [adding a data source](adding-a-data-source.md).

## Use-case file format

One YAML file per use case, validated strictly when loaded (**unknown keys are errors**). Pods check the directory every 30 s and reload changed files without a restart. A file that fails validation is logged and skipped; if an earlier version of it loaded, that version keeps serving. Only `status: published` is served; if two files publish the same name and major, the higher version is served.

| Key | |
| --- | --- |
| `use_case` | Lower-case slug (letters, digits, `-`) |
| `version` | Semver `MAJOR.MINOR.PATCH`. Partners call `use_case@<major>`; without a major, they get the highest published major |
| `status` | `draft`, `validated`, `published`, `deprecated` or `retired`; only `published` is served |
| `title`, `description` | Shown by the describe endpoints |
| `policy`, `purpose` | Informational until PM has policies |
| `consent.required` | Default `true`: requires `message.consent_jws` and checks it (signature, subject, validity, grants for mandatory sources) |
| `allowed_partners` | Partner IDs allowed to call (`"*"` = any verified partner). This **stands in for the PM policy association**, which PM does not have yet. |
| `input.subject.id_types` | Allowed `message.subject.type` values, e.g. `[FAYDA_FAN, FARMER_ID]` (see [subject ID types](#subject-id-types)) |
| `input.parameters.<name>` | `{type: integer\|number\|string\|boolean, description, required, default, min, max, enum}`. For strings, `min`/`max` bound the length. Unknown parameters are rejected. |
| `input.batch.max_subjects` | Must be 1 |
| `sources[]` | `{id, controller, requirement: mandatory\|optional, depends_on: [], dci: {reg_type, reg_record_type, query_template}, timeout_ms, retries}`. `id` matches `^[a-z][a-z0-9_]*$`; `timeout_ms` 50–120000; `retries` 0–5 (default 0); `requirement` defaults to `mandatory`. `depends_on` may not form a cycle. |
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
* **Consent Manager:** each partner policy's `allowed_subject_id_types` must include the type, or CM refuses the consent.


Also accepted from the design but **not acted on yet** (logged once at load): `owner`, `consent.collection`, `consent.mode`, `sources[].request_scopes`, `response.schema`, `response.correlate_on`, `response.mode: merged`, `execution.fan_out: parallel`, and `limits.daily_quota_per_partner`.

Output paths (`mapping` and `derived` keys) are dot-separated identifiers; each may be defined once, and a path can't be both a value and the parent of another.

## Query templates

A template is sandboxed Jinja, given inline or as the name of a `.j2` (`.jinja`, `.jinja2`) file next to the use case (a plain file name: a ConfigMap has no subdirectories). It renders the query part of the DCI `search_criteria`, as `{"query_type", "query": {"type", "value"}, "pagination"?, "sort"?}`. The composite adds `version`, `reg_type`, `reg_record_type` and the consent.

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

**`loan-profile`'s settings:** `farmer` mandatory; `season_summaries` and `crop_seasons` optional and `depends_on: [farmer]`; each `timeout_ms: 3000`, `retries: 1`; `overall_timeout_ms: 8000`; `partial_response: allowed`. So the request fails only when the Farmer Registry fails (or denies), and the crop data is best effort.

## Output format

* **The envelope** is DCI-style: `{signature, header, message}`, signed by the composite (detached JWS over `{header, message}`), `header.action: on-query`, `header.status: succ | rjct`.
* **`message.data` is defined per use case** by its `mapping` and `derived` keys: each output path becomes a nested object (`farmer.name` → `{"farmer": {"name": …}}`).
* **Records keep the registries' shapes.** Where a mapping copies records (e.g. `land.parcels`, `crops.seasons`), they are the registries' DCI / SPDCI records (e.g. the Farmer Registry's `farm_details`, the Crop Sown Registry's `…:CropSeason` records with `crop_season`, `measures`, `location`, `farmer_reference`), already clamped by each registry to the consented scopes.
* **This is not an open standard.** The envelope follows DCI conventions; the `data` shape is Open Agri Stack's, per use case.
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

# Interim stand-in for the PM policy association (PM has no policies yet).
allowed_partners: [bank-a]

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
    dci:
      reg_type: Farmer
      reg_record_type: spdci-extensions-dci:Farmer
      query_template: |
        {%- set field = 'foundational_id' if subject.type == 'FAYDA_FAN' else 'functional_record_id' -%}
        {"query_type": "expression",
         "query": {"type": "expression",
                   "value": {"expression": {"query": {"{{ field }}": {"$eq": {{ subject.value | tojson }} } } } } },
         "pagination": {"page_size": 1, "page_number": 1} }
    timeout_ms: 3000
    retries: 1

  - id: season_summaries
    controller: crop-sown-registry
    requirement: optional
    depends_on: [farmer]
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
    timeout_ms: 3000
    retries: 1

  - id: crop_seasons
    controller: crop-sown-registry
    requirement: optional
    depends_on: [farmer]
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
    timeout_ms: 3000
    retries: 1

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
  overall_timeout_ms: 8000
  partial_response: allowed   # a failing mandatory source (farmer) fails the request

limits:
  rate_per_partner: 60/min
```

* The Crop Sown Registry knows the farmer by farmer ID, so both crop sources depend on the farmer source and read `FARMER_ID` from its record (or use the subject itself when the partner sends a `FARMER_ID`).
* **Consent** (one consent, a grant per registry). The farmer record must include `farmer_personal_details`, since that is where the farmer ID is read from:
  * `farmer-registry`: `farmer_personal_details`, `family_details`, `farm_details`, `main_crops`;
  * `crop-sown-registry`: `farmer_reference`, `crop_season`, `measures`, `location`.

## Configuration (environment, prefix `AGRI_COMPOSITE_`)

| Variable | Default | |
| --- | --- | --- |
| `USE_CASES_DIR` | `use-cases` (`/app/config/use-cases` in the chart) | Use-case directory |
| `USE_CASES_RELOAD_SECONDS` | `30` | `0` = no reload |
| `REGISTRIES` | `{}` | JSON `{controller: {url, partner_id?, receiver_id?}}`. `url` is the registry's DCI sync search URL. If `partner_id` (its DCI ID, e.g. `farmer-registry`) is set, the registry's response signature is verified against `PARTNER_<ID>` in PM. |
| `COMPOSITE_PARTNER_ID` | `agri-composite` | The composite's ID. It is the `sender_id` towards registries, and partners use it as `receiver_id`. |
| `SIGNING_P12_PATH`, `SIGNING_P12_PASSWORD`, `SIGNING_KID`, `SIGNING_ALGORITHM` | –, –, thumbprint, `auto` | The composite's key. If the kid is set, it must match the kid registered in PM. `auto` picks the algorithm from the key type (EC → ES256, Ed25519 → EdDSA, RSA → RS256). Without a key every query fails with `signing_unavailable`; the describe endpoints still work. |
| `PARTNER_MGMT_API_URL` | `http://commons-services-pm-partner-api` | Partner keys are fetched by `PARTNER_<SENDER_ID>` and cached |
| `PARTNER_KEY_CACHE_TTL_SECONDS`, `PARTNER_KEY_HARD_TTL_SECONDS`, `PARTNER_KEY_NEGATIVE_TTL_SECONDS`, `PARTNER_KEY_REFRESH_COOLDOWN_SECONDS`, `PARTNER_KEY_FETCH_TIMEOUT_SECONDS` | `300`, `21600`, `30`, `10`, `3.0` | Partner key cache: soft TTL, last-known-good during a PM outage, cache of "unknown", refresh cooldown on an unknown `kid`, fetch timeout |
| `CRYPTO_ALLOWED_ALGORITHMS` | `EdDSA,ES256,RS256` | |
| `REQUEST_MAX_SKEW_SECONDS` | `300` | How far `header.message_ts` may be from now (`0` disables) |
| `DEFAULT_SOURCE_TIMEOUT_MS`, `DEFAULT_OVERALL_TIMEOUT_MS` | `5000`, `10000` | Used when the use case doesn't set them |
| `HTTP_MAX_CONNECTIONS`, `HTTP_MAX_KEEPALIVE_CONNECTIONS`, `HTTP_KEEPALIVE_EXPIRY_SECONDS` | `200`, `50`, `30` | One pooled client per worker |
| `AUDIT_MANAGER_URL` | empty (off) | e.g. `http://commons-services-auditmanager:80` |
| `AUDIT_TIMEOUT_SECONDS`, `AUDIT_SOURCE` | `2.0`, `/openg2p/agri-composite` | |
| `NO_OF_WORKERS` | `2` | gunicorn workers per pod |
| `LOGGING_LEVEL` | `INFO` (chart) | |

## Helm values

The chart is `openg2p-agri-composite` (Rancher catalog: **"Agri Stack Composite"**). Its [values](https://github.com/openg2p/agri-stack/blob/develop/composite/deployment/charts/openg2p-agri-composite/values.yaml) and [Rancher questions](https://github.com/openg2p/agri-stack/blob/develop/composite/deployment/charts/openg2p-agri-composite/questions.yaml):

| Value | Default | Rancher form |
| --- | --- | --- |
| `global.compositeHostname` | `agri-composite.<namespace>.openg2p.org` | General: Composite Hostname (Istio `internal` gateway) |
| `composite.image.tag` | `develop` | General: Image Tag |
| `composite.existingUseCasesConfigMap` | empty | General: your own ConfigMap of use cases (keys `<name>.yaml`) instead of `composite.useCases` |
| `composite.useCasesReloadSeconds` | `30` | General: Use-Case Reload Interval |
| `global.compositePartnerId` | `agri-composite` | Integration: Composite Partner ID (its key must be in PM) |
| `global.partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | Integration |
| `global.auditManagerUrl` | `http://commons-services-auditmanager:80` | Integration (empty disables auditing) |
| `composite.registries.farmer-registry.url` | `http://fr-partner-api/dci/registry/sync/search` | Integration: Farmer Registry Search URL |
| `composite.registries.crop-sown-registry.url` | `http://csr-partner-api/dci/registry/sync/search` | Integration: Crop Sown Registry Search URL |
| `composite.registries.<controller>.partnerId`, `.receiverId` | empty | values only |
| `composite.signingKey.secretName` | `agri-composite-signing` | Signing key: the Secret with `composite.p12`, `password`, and optionally `kid` and `algorithm` |
| `composite.autoscaling.enabled`, `minReplicas`, `maxReplicas` | `true`, `1`, `5` (70% CPU) | Scaling |
| `composite.replicaCount` | `1` | Scaling (when autoscaling is off) |
| `composite.workers` | `2` | Scaling: Workers per Pod |
| `composite.useCases` | `loan-profile` | **Not in the form**: edit in **Edit YAML** |
| `sanity.enabled`, `sanity.failOnError` | `true`, `true` | values only: the post-install hook pings the API and lists the use cases |

The registry URLs default to the partner-API services of registry releases named `fr` and `csr`; check them against your release names.

**Use cases in Helm.** `composite.useCases` is a map of name → YAML text, one use case per entry. Edit it in Rancher's **Edit YAML** view of the values. The chart renders it into the ConfigMap `<release>-use-cases`, mounted at `/app/config/use-cases`; running pods pick up changes within the reload interval (about a minute after the ConfigMap updates), without a restart. To manage use cases elsewhere (e.g. GitOps), set `composite.existingUseCasesConfigMap` to your own ConfigMap with keys `<name>.yaml` (and any `.j2` template files).

Registry settings (`composite.registries`) are environment variables, so changing them rolls the pods.

## Scaling notes

* Pods are stateless; scale on CPU (memory autoscaling is off on purpose).
* Each worker keeps its own connection pool and partner-key cache.
* Rate limits are per pod and worker (up to pods × workers × the configured rate in total); limits across pods and daily quotas are to do (shared counters in the composite).
* Startup never calls a registry; a registry being down only affects requests.
