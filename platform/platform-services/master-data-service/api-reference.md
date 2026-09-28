---
description: Geo and Attribute APIs served by the Master Data Service
---

# API Reference

The Master Data Service exposes two groups of APIs — **reads**, used by registries
and other services, and **writes**, used to maintain the data (the Master Data admin
UI) — plus a health check.

| Group | Prefix | What it serves |
|---|---|---|
| [Geo](#geo-apis) | `/geo` | The administrative hierarchy and its units |
| [Attributes](#attribute-apis) | `/attributes` | The country's code lists and their values |
| [Health](#health) | `/ping` | Liveness |

{% hint style="info" %}
**MDS holds no partners.** Partner organisations and their keys are served by
[Partner Management](../partner-management/README.md); the `/partner` APIs this
service once had are gone.
{% endhint %}

{% hint style="info" %}
**Every lookup is a `POST`, including the reads.** These follow the OpenG2P common
request/response envelope, which carries a request header alongside the payload, so
arguments travel in a body rather than the query string. `/ping` is the only `GET`.
{% endhint %}

{% hint style="warning" %}
**Every endpoint except `/ping` needs a bearer token** from the deployment's
Keycloak. Reads need authentication only (geo units and attribute values are
additionally filtered by the caller's data policy); writes need a permission — `geo:create`, `geo:edit`,
`geo:delete`, `referenceData:create`, `referenceData:edit` or
`referenceData:delete` — held under the `master-data-ui` client.
{% endhint %}

A machine-readable OpenAPI document is available at
[`master-data.json`](openapi/master-data.json), and any running instance serves its
own at `/openapi.json` with interactive docs at `/docs`.

## The envelope

Every request is `{ request_header, request_body }` and every response is
`{ response_header, response_body }`. Arguments go in
`request_body.request_payload`; results come back in
`response_body.response_payload`.

**Request header**

| Field | Type | Required |
|---|---|---|
| `sender_app_mnemonic` | string | yes |
| `sender_app_url` | string | yes |
| `request_id` | string | yes |
| `request_timestamp` | string (ISO 8601) | yes |
| `instance_id` | string | no |

**Response header**

| Field | Type | Notes |
|---|---|---|
| `request_id` | string | Echoed back from the request |
| `response_status` | string | `SUCCESS` or an error status |
| `response_error_code` | string | Empty on success |
| `response_error_message` | string | Empty on success |
| `response_timestamp` | string | |

{% hint style="warning" %}
**Errors come back inside the envelope, not as HTTP error bodies.** A failed lookup
can still return `200` with `response_status` set to an error and the detail in
`response_error_code` / `response_error_message`. Check the status field rather than
relying on the HTTP code alone.
{% endhint %}

---

## Geo APIs

### `POST /geo/get_all_geo_levels`

Returns the **entire** level hierarchy in one call. Takes an empty payload. Use it
to learn the shape of the hierarchy up front — how many levels, and what the
country calls them — for example to build a set of cascading dropdowns. A level's
children are the levels whose `parent_level_id` is its `level_id`.

**Response payload** — a list of level objects:

| Field | Description |
|---|---|
| `level_id` | Level identifier, e.g. `l0`, `l1` |
| `level_mnemonic` | The country's name for the level, e.g. `region`, `woreda` — unique under its parent |
| `parent_level_id` | Parent level, `null` at the root |

**Example**

{% code title="Request" %}
```json
{
  "request_header": {
    "sender_app_mnemonic": "my-service",
    "sender_app_url": "http://my-service",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "request_timestamp": "2026-08-04T10:00:00Z"
  },
  "request_body": { "request_payload": {} }
}
```
{% endcode %}

{% code title="Response" %}
```json
{
  "response_header": {
    "request_id": "11111111-1111-1111-1111-111111111111",
    "response_status": "SUCCESS",
    "response_error_code": "",
    "response_error_message": "",
    "response_timestamp": "2026-08-06T02:33:33.177919"
  },
  "response_body": {
    "pagination_response": null,
    "response_payload": [
      { "level_id": "l0", "level_mnemonic": "country", "parent_level_id": null },
      { "level_id": "l1", "level_mnemonic": "region",  "parent_level_id": "l0" }
    ]
  }
}
```
{% endcode %}

### `POST /geo/get_geo_level_values`

Returns the administrative **units** at a level, optionally only those under a given
parent. This is the call that drives cascading address dropdowns: ask for level `l1`
to fill the first dropdown, then for `l2` with the chosen unit as
`parent_level_value_id` to fill the second.

**Request payload**

| Field | Type | Required | Description |
|---|---|---|---|
| `level_id` | string | yes | Which level's units to return |
| `parent_level_value_id` | string | no | Restrict to children of this unit |

**Response payload** — a list of unit objects:

| Field | Description |
|---|---|
| `level_value_id` | The unit's identifier — for a unit loaded from a country pack, **this is its P-code** |
| `level_id` | Which level it belongs to |
| `level_value_mnemonic` | Short name — unique under its parent at that level |
| `parent_level_value_id` | Parent unit |

The results are filtered by the caller's **data policy**, so two callers can see
different subsets of the same level.

See [Country Data Architecture](../../country-data-architecture.md) for what
P-codes are.

### Geo writes

For maintaining the hierarchy. Each returns the object it created or changed, or —
for a delete — its id.

| Endpoint | Permission | Request payload |
|---|---|---|
| `POST /geo/add_geo_level` | `geo:create` | `level_mnemonic`, `parent_level_id`? |
| `POST /geo/update_geo_level` | `geo:edit` | `level_id`, `level_mnemonic`?, `parent_level_id`? |
| `POST /geo/delete_geo_level` | `geo:delete` | `level_id` |
| `POST /geo/add_geo_level_value` | `geo:create` | `level_id`, `level_value_mnemonic`, `parent_level_value_id`? |
| `POST /geo/update_geo_level_value` | `geo:edit` | `level_value_id`, `level_id`?, `level_value_mnemonic`?, `parent_level_value_id`? |
| `POST /geo/delete_geo_level_value` | `geo:delete` | `level_value_id`, `cascade` (default `false`) |

`?` marks an optional field.

---

## Attribute APIs

These serve the country's code lists — the vocabularies registry dropdowns read
their options from, and that a registry's coded-value check validates against.

### `POST /attributes/get_all_attributes`

Returns the list of attributes (the code lists themselves, not their values). Takes
an empty payload.

**Response payload** — `{ "attributes": [...] }`, each attribute carrying
`attribute_id`, `attribute_code`, `attribute_display` and `is_hierarchical`.

### `POST /attributes/get_attribute_values`

Returns the values of one code list — or, with no `attribute_id`, of every list.

**Request payload**

| Field | Type | Required | Description |
|---|---|---|---|
| `attribute_id` | string | no | The code list, e.g. `GENDER`. Omitted → every value of every list |

Paging is not part of the payload: it goes in the envelope, as
`request_body.pagination_request` (`current_page`, `page_size`).

**Response payload** — `{ "attribute_values": [...], "total": n }`:

| Field | Description |
|---|---|
| `attribute_id`, `value_id` | Which list, and the value's identifier — the code a registry stores |
| `value_code`, `value_display` | Code and human-readable label |
| `parent_value_id` | Set for hierarchical lists |
| `sort_order` | Display order |

As with geo units, the values are filtered by the caller's **data policy**.

**Example**

{% code title="Request" %}
```json
{
  "request_header": {
    "sender_app_mnemonic": "my-service",
    "sender_app_url": "http://my-service",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "request_timestamp": "2026-08-04T10:00:00Z"
  },
  "request_body": {
    "request_payload": { "attribute_id": "GENDER" },
    "pagination_request": { "current_page": 1, "page_size": 3 }
  }
}
```
{% endcode %}

{% code title="Response (payload only)" %}
```json
{
  "attribute_values": [
    {
      "attribute_id": "GENDER",
      "value_id": "FEMALE",
      "value_code": "FEMALE",
      "value_display": "Female",
      "parent_value_id": null,
      "sort_order": 1
    }
  ],
  "total": 4
}
```
{% endcode %}

{% hint style="info" %}
Attribute ids are **upper-case**: `GENDER`, `COOKING_FUEL_TYPE`,
`DISABILITY_SEVERITY`. Call `get_all_attributes` to list what a deployment actually
holds — it varies with the country pack loaded, and a pack's **domain** lists (such
as `agriculture`) are there only if the deployment asked for that domain
(`geoSeed.domains`).
{% endhint %}

{% hint style="warning" %}
**Only the codes and labels are stored.** A pack's values may also declare semantic
`roles`, a domain and provenance, but MDS does not keep them and these APIs do not
return them. See
[Country Data Architecture → Semantic roles](../../country-data-architecture.md#semantic-roles).
{% endhint %}

### Attribute writes

| Endpoint | Permission | Request payload |
|---|---|---|
| `POST /attributes/add_attribute` | `referenceData:create` | `attribute_code`, `attribute_display`, `is_hierarchical`? |
| `POST /attributes/update_attribute` | `referenceData:edit` | `attribute_id`, `attribute_code`?, `attribute_display`?, `is_hierarchical`? |
| `POST /attributes/delete_attribute` | `referenceData:delete` | `attribute_id`, `cascade` (default `false`) |
| `POST /attributes/add_attribute_value` | `referenceData:create` | `attribute_id`, `value_code`, `value_display`, `parent_value_id`?, `sort_order`? |
| `POST /attributes/update_attribute_value` | `referenceData:edit` | `value_id`, `attribute_id`?, `value_code`?, `value_display`?, `parent_value_id`?, `sort_order`? |
| `POST /attributes/delete_attribute_value` | `referenceData:delete` | `value_id`, `attribute_id`? |

{% hint style="danger" %}
**A registry stores these codes.** Changing a `value_code` or deleting a value that
records already hold leaves those records with a code no dropdown can show — and,
with the registry's coded-value check on, a record that cannot be saved until the
field is re-picked. Add new values freely; change or remove existing ones only with
the registries' data in mind.
{% endhint %}

---

## Health

### `GET /ping`

Liveness probe. The only `GET`, and the only endpoint without the envelope.

---

## What is *not* exposed

{% hint style="warning" %}
**Sample individuals and households have no API.** Master Data stores the country
pack's sample people, but registries load them **database-to-database** during
seeding rather than over HTTP. There is no endpoint for them.
{% endhint %}

Boundary geometry is likewise not served by this API, and the geo endpoints carry
no link to it: a unit's map shape is not part of its record. See
[Country Data Architecture](../../country-data-architecture.md).
