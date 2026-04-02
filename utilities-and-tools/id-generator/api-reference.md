---
description: >-
  API reference for the ID Generator service — endpoints, response envelope,
  error codes, and HTTP status codes.
---

# API Reference

The ID Generator exposes an **OpenAPI 3.1 compliant** REST API. A running instance provides interactive documentation at:

* **Swagger UI**: `GET /docs`
* **ReDoc**: `GET /redoc`
* **OpenAPI JSON spec**: `GET /openapi.json`

## Endpoints

### Issue ID

{% openapi-operation spec="openg2p-id-generator" path="/v1/idgenerator/{id_type}/id" method="post" %}
[OpenAPI openg2p-id-generator](https://raw.githubusercontent.com/OpenG2P/id-generator/main/docs/openapi.json)
{% endopenapi-operation %}

{% hint style="info" %}
**Why POST?** Issuing an ID is a state-changing operation (AVAILABLE → TAKEN). Per HTTP/REST semantics, `GET` must be safe and idempotent. `POST` correctly signals that this operation modifies server state.
{% endhint %}

### Validate ID

{% openapi-operation spec="openg2p-id-generator" path="/v1/idgenerator/{id_type}/id/validate/{id_value}" method="get" %}
[OpenAPI openg2p-id-generator](https://raw.githubusercontent.com/OpenG2P/id-generator/main/docs/openapi.json)
{% endopenapi-operation %}

{% hint style="info" %}
**Use case**: A downstream system receives an ID (e.g., typed in by a user) and wants to quickly verify it is not a typo or fabricated number — without needing a database lookup.
{% endhint %}

### Health Check

{% openapi-operation spec="openg2p-id-generator" path="/v1/idgenerator/health" method="get" %}
[OpenAPI openg2p-id-generator](https://raw.githubusercontent.com/OpenG2P/id-generator/main/docs/openapi.json)
{% endopenapi-operation %}

### Version

{% openapi-operation spec="openg2p-id-generator" path="/v1/idgenerator/version" method="get" %}
[OpenAPI openg2p-id-generator](https://raw.githubusercontent.com/OpenG2P/id-generator/main/docs/openapi.json)
{% endopenapi-operation %}

### Config

{% openapi-operation spec="openg2p-id-generator" path="/v1/idgenerator/config" method="get" %}
[OpenAPI openg2p-id-generator](https://raw.githubusercontent.com/OpenG2P/id-generator/main/docs/openapi.json)
{% endopenapi-operation %}

## Response envelope

All endpoints return a consistent JSON envelope.

**Success response:**

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-27T10:00:00.000Z",
  "response": { ... },
  "errors": []
}
```

**Error response** (`response` is `null`, `errors` is populated):

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-27T10:00:00.000Z",
  "response": null,
  "errors": [
    { "errorCode": "IDG-001", "message": "No IDs available for ID type 'farmer_id'" }
  ]
}
```

## Path parameter constraints

| Parameter    | Type   | Pattern                       | Description                                          |
| ------------ | ------ | ----------------------------- | ---------------------------------------------------- |
| `{id_type}`  | string | `^[a-z][a-z0-9_]{1,63}$`     | Lowercase alphanumeric + underscore, starts with letter |
| `{id}`       | string | `^\d{1,32}$`                  | Digits only, 1–32 characters                         |

Invalid path parameters return HTTP `422 Unprocessable Entity`.

## HTTP status codes

| Status                  | Meaning                       | When used                                                |
| ----------------------- | ----------------------------- | -------------------------------------------------------- |
| 200 OK                  | Request succeeded              | Successful issue, validate, health, version, config      |
| 404 Not Found           | Resource not found             | Unknown ID type (IDG-003)                                |
| 410 Gone                | Resource permanently gone      | ID space exhausted (IDG-002)                             |
| 422 Unprocessable Entity| Validation error               | Invalid path parameter format                            |
| 503 Service Unavailable | Temporarily unavailable        | Pool empty (IDG-001), health check failing (IDG-005/006) |

## Error codes

| Code    | HTTP Status | Description                                                          |
| ------- | ----------- | -------------------------------------------------------------------- |
| IDG-001 | 503         | No IDs available in pool (temporary — replenishment in progress)     |
| IDG-002 | 410         | ID space exhausted for ID type (permanent — no more IDs possible)    |
| IDG-003 | 404         | Unknown ID type                                                      |
| IDG-004 | —           | Invalid ID (returned in validate response body, not as HTTP error)   |
| IDG-005 | 503         | Service not ready — startup not complete                             |
| IDG-006 | 503         | Database health check failed                                         |
