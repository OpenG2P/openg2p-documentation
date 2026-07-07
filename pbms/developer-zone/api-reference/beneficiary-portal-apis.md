# Beneficiary portal APIs

The Beneficiary Portal API is the FastAPI service that powers the PBMS beneficiary-facing self-service portal. It lets an authenticated beneficiary discover the benefit programs they are enrolled in, browse all available programs, and view the details of a single program (including its benefit codes and the beneficiary's own enrolment status).

* **Base image:** `openg2p/openg2p-pbms-bene-portal-api`
* **Python module:** `openg2p_pbms_bene_portal_api`
* **In-cluster service name:** `<release-name>-bene-portal-api` (Kubernetes `Service`, HTTP)
* **Container port:** `8000` (Gunicorn + Uvicorn workers)
* **Startup:** on start the container runs `python3 -m openg2p_pbms_bene_portal_api.main migrate` to migrate the database, then launches `gunicorn openg2p_pbms_bene_portal_api.main:app` with `uvicorn.workers.UvicornWorker`.
* **Databases used:** the PBMS database (`pbmsdb`) for program/benefit-code definitions and the background-task database (`bg_taskdb`) for beneficiary-list membership.

The interactive Swagger UI (`/docs`) and OpenAPI JSON (`/openapi.json`) served by the running app are the authoritative, always-current specification. This page documents the main endpoints.

## Authentication

Every endpoint is protected by the `AuthFactory` dependency from `openg2p-fastapi-auth`. A verified OIDC / JWT access token must be supplied, either as an `Authorization: Bearer <token>` header or as an `X-Access-Token` cookie (an `X-ID-Token` cookie may additionally be supplied for ID-token claims). The token signature is verified against the configured OIDC issuers and their JWKS URLs (`auth_default_issuers` / `auth_default_jwks_urls`, or the configured login providers). For the beneficiary portal the token must carry `user_type: "beneficiary"` (validated via the eSignet strategy). The authenticated subject claim (`sub`) is used as the beneficiary ID that scopes every query.

## Common request / response envelope

All endpoints accept `POST` requests using the shared G2P envelope (`openg2p_fastapi_common.schemas`).

Request:

```json
{
  "request_header": {
    "sender_app_mnemonic": "PBMS_BENE_PORTAL",
    "sender_app_url": "https://portal.example.org",
    "request_id": "unique-request-id",
    "request_timestamp": "2026-07-07T10:00:00Z",
    "instance_id": null
  },
  "request_body": {
    "pagination_request": { "current_page": 1, "page_size": 10 },
    "request_payload": { "program_id": "12" }
  }
}
```

Response:

```json
{
  "response_header": {
    "request_id": "unique-request-id",
    "response_status": "SUCCESS",
    "response_error_code": null,
    "response_error_message": null,
    "response_timestamp": "2026-07-07T10:00:01Z"
  },
  "response_body": {
    "pagination_response": { "number_of_items": 3, "number_of_pages": 1 },
    "response_payload": [ /* list of benefit programs */ ]
  }
}
```

On a handled `PBMSException`, the service still returns HTTP 200 with `response_status: "ERROR"` and a populated `response_error_code` / `response_error_message` (for example `AUTH001` when credentials are missing, or `PROGRAM_NOT_FOUND`).

A `benefit_program` object in a payload has the shape:

```json
{
  "id": 12,
  "program_name": "Food Assistance",
  "program_mnemonic": "FOOD_ASSIST",
  "program_description": "Food Assistance",
  "am_i_enrolled": true,
  "enrolment_date": "2026-01-15",
  "benefit_codes": [
    {
      "id": 5,
      "benefit_code_mnemonic": "RICE",
      "benefit_type": "in_kind",
      "benefit_code_description": "Rice ration",
      "benefit_code_max_quantity": 25.0,
      "measurement_unit": "kg"
    }
  ]
}
```

## Endpoint reference

All routes are under the `/benefit_program` prefix and use the `POST` method.

| Method | Path | Purpose | Response model |
| --- | --- | --- | --- |
| `POST` | `/benefit_program/get_my_programs` | List the programs the authenticated beneficiary is enrolled in. | `BenefitProgramResponse` |
| `POST` | `/benefit_program/get_all_programs` | List all programs, each flagged with the beneficiary's own enrolment status. | `BenefitProgramResponse` |
| `POST` | `/benefit_program/get_program` | Get the details of a single program by `program_id`. | `BenefitProgramDetailResponse` |

## `POST /benefit_program/get_my_programs`

Returns the list of benefit programs the authenticated beneficiary is enrolled in. For each program the service finds the latest approved beneficiary list and checks whether the beneficiary's `sub` appears among its registrant details; only enrolled programs are returned, each with its benefit codes.

* **Auth:** required (`user_type: "beneficiary"`).
* **Request body:** `pagination_request` is optional; defaults are `page_size = 10`, `current_page = 1`. `request_payload` may be omitted.
* **Response payload:** a list of `benefit_program` objects (all with `am_i_enrolled: true`). Pagination is applied after filtering, so `pagination_response.number_of_items` is the number of enrolled programs.

## `POST /benefit_program/get_all_programs`

Returns a paginated list of all benefit programs defined in PBMS. Each program is annotated with `am_i_enrolled` and `enrolment_date` for the calling beneficiary, so the portal can show both enrolled and not-yet-enrolled programs.

* **Auth:** required (`user_type: "beneficiary"`).
* **Request body:** `pagination_request` is optional; defaults are `page_size = 30`, `current_page = 1`.
* **Response payload:** a list of `benefit_program` objects with per-beneficiary enrolment flags. `pagination_response` reflects the total program count and page count. Returns error code `PROGRAM_NOT_FOUND` if no programs exist for the requested page.

## `POST /benefit_program/get_program`

Returns the details of a single benefit program, including its benefit codes and the calling beneficiary's enrolment status for that program.

* **Auth:** required (`user_type: "beneficiary"`).
* **Request body:** `request_payload.program_id` is **required**.

```json
{
  "request_header": { "...": "..." },
  "request_body": { "request_payload": { "program_id": "12" } }
}
```

* **Response model:** `BenefitProgramDetailResponse` — `response_body.response_payload` is a single `benefit_program` object (not a list).
* **Errors:** returns `INVALID_REQUEST` if `program_id` is missing, or `PROGRAM_NOT_FOUND` if no program matches the given id.
