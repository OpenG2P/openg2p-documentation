---
description: Geo, Attribute and Partner lookup APIs served by the Master Data Service
---

# API Reference

The Master Data Service exposes three groups of **read-only lookup** APIs, plus a
health check.

| Group | Prefix | What it serves |
|---|---|---|
| [Geo](#geo-apis) | `/geo` | The administrative hierarchy and its units |
| [Attributes](#attribute-apis) | `/attributes` | The country's code lists and their values |
| [Partner](#partner-apis) | `/partner` | Partner organisations, for inter-service trust and routing |
| [Health](#health) | `/ping` | Liveness |

{% hint style="info" %}
**Every lookup is a `POST`, including the reads.** These follow the OpenG2P common
request/response envelope, which carries a request header alongside the payload, so
arguments travel in a body rather than the query string. `/ping` is the only `GET`.
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

### `POST /geo/get_g2p_geo_levels`

Returns the levels directly beneath a given level — the hierarchy one step at a
time. Omit `parent_level_id` to get the top level.

**Request payload**

| Field | Type | Required | Description |
|---|---|---|---|
| `parent_level_id` | string | no | Return the levels below this one. Omitted → the root level. |

**Response payload** — a list of level objects:

| Field | Description |
|---|---|
| `level_id` | Level identifier, e.g. `l0`, `l1` |
| `level_mnemonic` | The country's name for the level, e.g. `region`, `woreda` |
| `parent_level_id` | Parent level, `null` at the root |
| `display_name`, `display_name_i18n` | Optional labels |
| `version`, `valid_from`, `valid_to` | Pack version and validity window |

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
      {
        "level_id": "l0",
        "level_mnemonic": "country",
        "parent_level_id": null,
        "display_name": null,
        "display_name_i18n": null,
        "version": null,
        "valid_from": null,
        "valid_to": null
      }
    ]
  }
}
```
{% endcode %}

### `POST /geo/get_all_g2p_geo_levels`

Returns the **entire** level hierarchy in one call — the same objects as above, for
every level. Takes an empty payload. Use this when you need the shape of the
hierarchy up front, for example to build a set of cascading dropdowns.

### `POST /geo/get_g2p_geo_level_values`

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
| `level_value_id` | The unit's identifier — **this is its P-code** |
| `level_id` | Which level it belongs to |
| `level_value_mnemonic` | Short name |
| `parent_level_value_id` | Parent unit |
| `pcode`, `pcode_source` | The P-code and where it came from, e.g. `OCHA COD-AB` |
| `boundary_uri`, `boundary_simplified_uri` | Where the unit's map shape can be fetched |
| `display_name`, `display_name_i18n` | Labels |
| `version`, `valid_from`, `valid_to` | Pack version and validity window |

{% hint style="danger" %}
**This endpoint requires authentication.** It is permission-checked, so an
unauthenticated call returns `401`. The two level endpoints above are not.
{% endhint %}

See [Country Data Architecture](../../country-data-architecture.md) for what
P-codes are and where the boundary files actually live.

---

## Attribute APIs

These serve the country's code lists — the vocabularies a registry validates
against.

### `POST /attributes/get_all_attributes`

Returns the list of attributes (the code lists themselves, not their values).

**Request payload**

| Field | Type | Required | Description |
|---|---|---|---|
| `domain` | string | no | Only attributes in this domain, e.g. `agriculture` |
| `include_domains` | boolean | no | Include domain-specific attributes alongside the core ones |

**Response payload** — `{ "attributes": [...], "total": n }`, each attribute
carrying `attribute_id`, `attribute_code`, `attribute_display`, `is_hierarchical`,
`display_name_i18n`, `country` and `version`.

### `POST /attributes/get_attribute_values`

Returns the values within one or more code lists.

**Request payload**

| Field | Type | Required | Description |
|---|---|---|---|
| `attribute_id` | string | no | Restrict to one code list, e.g. `GENDER` |
| `domain` | string | no | Restrict to a domain |
| `include_domains` | boolean | no | Include domain-specific values |
| `page_size` | integer | no | Page size |
| `page_number` | integer | no | Page number |

**Response payload** — `{ "attribute_values": [...], "total": n }`:

| Field | Description |
|---|---|
| `attribute_id`, `value_id` | Which list, and the value's identifier |
| `value_code`, `value_display` | Code and human-readable label |
| `parent_value_id` | Set for hierarchical lists |
| `sort_order` | Display order |
| `roles` | Semantic role tags — see below |
| `domain`, `country`, `version` | Provenance |
| `valid_from`, `valid_to` | Validity window |

{% hint style="info" %}
**`roles` is what makes reporting portable across countries.** Rather than
hardcoding a literal like `"SELF"`, platform logic asks which value carries the role
`head_of_household`. The vocabulary is fixed; which value holds a role is the
country's decision.
{% endhint %}

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
    "request_payload": { "attribute_id": "GENDER", "page_size": 3 }
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
      "sort_order": 1,
      "display_name_i18n": {},
      "roles": ["female"],
      "domain": null,
      "country": "ETH",
      "version": "2026-04-17T09:59:45.523963",
      "valid_from": null,
      "valid_to": null
    }
  ],
  "total": 2
}
```
{% endcode %}

{% hint style="info" %}
Attribute ids are **upper-case**: `GENDER`, `COOKING_FUEL_TYPE`,
`DISABILITY_SEVERITY`. Call `get_all_attributes` to list what a deployment actually
holds — it varies with the country pack loaded.
{% endhint %}

---

## Partner APIs

### `POST /partner/get_all_partners`

Returns every registered partner organisation. Empty payload.

### `POST /partner/get_partner`

Returns one partner.

**Request payload**

| Field | Type | Required |
|---|---|---|
| `partner_id` | string | yes |

**Response payload** — a partner object:

| Field | Description |
|---|---|
| `partner_id` | Identifier |
| `partner_mnemonic` | Short name used across services |
| `keymanager_reference_id` | Key-manager reference used for inter-service trust |
| `is_active` | Whether the partner is currently active |

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

Boundary geometry is likewise not served by this API. The geo endpoints return a
**URL** to each unit's map shape; the file itself lives in object storage. See
[Country Data Architecture](../../country-data-architecture.md).
