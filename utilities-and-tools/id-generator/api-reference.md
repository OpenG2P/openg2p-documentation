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

`POST /v1/idgenerator/{id_type}/id`

Issues a single AVAILABLE ID from the specified ID type pool and marks it as TAKEN. No request body required.

{% hint style="info" %}
**Why POST?** Issuing an ID is a state-changing operation (AVAILABLE → TAKEN). Per HTTP/REST semantics, `GET` must be safe and idempotent. `POST` correctly signals that this operation modifies server state.
{% endhint %}

**Success response (200 OK):**

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-27T10:00:00.000Z",
  "response": {
    "id": "5738201964"
  },
  "errors": []
}
```

**Error responses:**

| Condition                                   | HTTP Status             | Error Code |
| ------------------------------------------- | ----------------------- | ---------- |
| Pool temporarily empty                      | 503 Service Unavailable | IDG-001    |
| ID space permanently exhausted              | 410 Gone                | IDG-002    |
| Unknown ID type                             | 404 Not Found           | IDG-003    |

### Validate ID

`GET /v1/idgenerator/{id_type}/id/validate/{id}`

Validates whether a given ID is **structurally valid** — checks the Verhoeff checksum and all 10 filter rules. Does **not** check whether the ID exists in the database.

{% hint style="info" %}
**Use case**: A downstream system receives an ID (e.g., typed in by a user) and wants to quickly verify it is not a typo or fabricated number — without needing a database lookup.
{% endhint %}

**Response (200 OK):**

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-27T10:00:00.000Z",
  "response": {
    "id": "5738201964",
    "valid": true
  },
  "errors": []
}
```

Both valid and invalid IDs return HTTP 200 — the result is in the `valid` field.

| Condition                                   | HTTP Status             | Error Code |
| ------------------------------------------- | ----------------------- | ---------- |
| Unknown ID type                             | 404 Not Found           | IDG-003    |

### Health Check

`GET /v1/idgenerator/health`

Returns service health (DB connectivity ping). Used as Kubernetes readiness/liveness probe.

| Condition                   | HTTP Status             | Error Code |
| --------------------------- | ----------------------- | ---------- |
| Healthy                     | 200 OK                  | —          |
| Startup not complete        | 503 Service Unavailable | IDG-005    |
| DB health check failed      | 503 Service Unavailable | IDG-006    |

### Version

`GET /v1/idgenerator/version`

Returns the service version and build metadata.

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-28T10:00:00.000Z",
  "response": {
    "service_version": "0.1.0",
    "build_time": "2026-03-28T08:30:00.000Z",
    "git_commit": "a1b2c3d"
  },
  "errors": []
}
```

| Field              | Description                                    |
| ------------------ | ---------------------------------------------- |
| `service_version`  | Semantic version from `pyproject.toml`          |
| `build_time`       | Timestamp when the Docker image was built       |
| `git_commit`       | Short git commit hash                           |

### Config

`GET /v1/idgenerator/config`

Returns the active service configuration — configured ID types, ID lengths, and filter rules.

```json
{
  "id": "openg2p.idgenerator",
  "version": "1.0",
  "responsetime": "2026-03-28T10:00:00.000Z",
  "response": {
    "id_types": {
      "farmer_id": { "id_length": 12 },
      "household_id": { "id_length": 10 }
    },
    "filter_rules": {
      "sequence_limit": 3,
      "repeating_limit": 2,
      "repeating_block_limit": 2,
      "conjugative_even_digits_limit": 3,
      "digits_group_limit": 5,
      "reverse_digits_group_limit": 5,
      "not_start_with": ["0", "1"],
      "restricted_numbers": []
    }
  },
  "errors": []
}
```

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
