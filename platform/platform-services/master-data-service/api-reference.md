---
description: Geo, Attribute and Partner lookup APIs served by the Master Data Service
---

# API Reference

The Master Data Service exposes three groups of **read-only lookup** APIs, plus a
health check:

| Group | Prefix | What it serves |
|---|---|---|
| Geo | `/geo` | The administrative hierarchy and its units (P-codes, boundary URLs) |
| Attributes | `/attributes` | The country's code lists and their values |
| Partner | `/partner` | Partner organisations — mnemonics, key-manager reference IDs, status |
| Health | `/ping` | Liveness |

{% hint style="info" %}
**Everything is `POST`, including the reads.** These follow the OpenG2P common
request/response envelope, which carries a request header alongside the payload,
so the arguments travel in a body rather than the query string. `/ping` is the
only `GET`.
{% endhint %}

## The request envelope

Every request is `{ request_header, request_body }`, and every response is
`{ response_header, response_body }`. The header carries `sender_app_mnemonic`,
`sender_app_url`, `request_id`, `request_timestamp` and `instance_id`; the actual
arguments sit in `request_body.request_payload`.

```json
{
  "request_header": {
    "sender_app_mnemonic": "my-service",
    "request_id": "6f4634d6-a4bd-4a95-b05b-3bf80a6c06b2",
    "request_timestamp": "2026-08-04T10:00:00Z"
  },
  "request_body": {
    "request_payload": { "level_id": "l1" }
  }
}
```

Errors are returned inside the envelope with a status in the response header,
rather than as bare HTTP error bodies.

## Notes on specific endpoints

* **`/geo/get_g2p_geo_levels`** takes an optional `parent_level_id` and returns the
  levels beneath it; **`/geo/get_all_g2p_geo_levels`** returns the whole hierarchy
  in one call.
* **`/geo/get_g2p_geo_level_values`** returns the units at a level, optionally
  filtered by `parent_level_value_id` — this is what drives cascading geo
  dropdowns. It is **permission-checked**, so callers need an authenticated
  identity; the two level endpoints are not.
* Geo responses include `pcode`, `boundary_uri` and `boundary_simplified_uri`. See
  [Country Data Architecture](../../country-data-architecture.md) for what those
  mean and where the boundary files actually live.

{% hint style="warning" %}
**Sample individuals and households are not exposed over the API.** Master Data
stores them, but registries load them database-to-database during seeding, not
through these endpoints.
{% endhint %}

## Endpoints

{% openapi-operation spec="master-data-api" path="/geo/get_g2p_geo_levels" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/geo/get_all_g2p_geo_levels" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/geo/get_g2p_geo_level_values" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/partner/get_all_partners" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/partner/get_partner" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/attributes/get_all_attributes" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/attributes/get_attribute_values" method="post" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-operation spec="master-data-api" path="/ping" method="get" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-operation %}

{% openapi-schemas spec="master-data-api" schemas="AttributeData,AttributeValueData,ErrorListResponse,ErrorResponse,G2PPaginationRequest,G2PPaginationResponse,G2PPartnerData,G2PPartnerResponse,G2PPartnerResponseBody,G2PPartnersResponse,G2PPartnersResponseBody,G2PRequestHeader,G2PResponseHeader,G2PResponseStatus,GeoLevelData,GeoLevelValueData,GetAllGeoLevelsRequest,GetAllGeoLevelsRequestBody,GetAllGeoLevelsRequestPayload,GetAllGeoLevelsResponse,GetAllGeoLevelsResponseBody,GetAllPartnersRequest,GetAllPartnersRequestBody,GetAllPartnersRequestPayload,GetAttributeValuesRequest,GetAttributeValuesRequestBody,GetAttributeValuesRequestPayload,GetAttributeValuesResponse,GetAttributeValuesResponseBody,GetAttributeValuesResponsePayload,GetAttributesRequest,GetAttributesRequestBody,GetAttributesRequestPayload,GetAttributesResponse,GetAttributesResponseBody,GetAttributesResponsePayload,GetGeoLevelValuesRequest,GetGeoLevelValuesRequestBody,GetGeoLevelValuesRequestPayload,GetGeoLevelValuesResponse,GetGeoLevelValuesResponseBody,GetGeoLevelsRequest,GetGeoLevelsRequestBody,GetGeoLevelsRequestPayload,GetGeoLevelsResponse,GetGeoLevelsResponseBody,GetPartnerRequest,GetPartnerRequestBody,GetPartnerRequestPayload,HTTPValidationError,ValidationError" grouped="true" %}
[OpenAPI master-data-api](https://raw.githubusercontent.com/openg2p/openg2p-documentation/latest/platform/platform-services/master-data-service/openapi/master-data.json)
{% endopenapi-schemas %}
