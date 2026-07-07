# Staff portal APIs (for Odoo)

The Staff Portal API is the FastAPI service that backs the PBMS staff experience rendered in the Odoo UI. It serves the read-side data for the staff views: the eligibility **summary** of a beneficiary list, the **disbursement envelope** and **disbursement batch** views, and **beneficiary search** against a target registry. These endpoints are consumed by the Odoo staff portal rather than by end beneficiaries.

* **Base image:** `openg2p/openg2p-pbms-staff-portal-api`
* **Python module:** `openg2p_pbms_staff_portal_api`
* **In-cluster service name:** `<release-name>-staff-portal-api` (Kubernetes `Service`, HTTP)
* **Container port:** `8000` (Gunicorn + Uvicorn workers)
* **Startup:** on start the container runs `python3 -m openg2p_pbms_staff_portal_api.main migrate` to migrate the database (beneficiary-list details, disbursement batch/envelope, and registry-adapter models), then launches `gunicorn openg2p_pbms_staff_portal_api.main:app` with `uvicorn.workers.UvicornWorker`.
* **Databases used:** the background-task database (`bg_taskdb`) and the social-registry database (`socialregistrydb`), together with pluggable registry adapters selected per request via the `target_registry` field.

The interactive Swagger UI (`/docs`) and OpenAPI JSON (`/openapi.json`) served by the running app are the authoritative, always-current specification. This page documents the main endpoints.

## Authentication

The staff portal endpoints themselves do not attach the `AuthFactory` dependency in code; they are expected to be reached from the Odoo staff portal within the trusted cluster / gateway boundary. The underlying `openg2p-fastapi-auth` framework does support a staff Keycloak strategy (`user_type: "staff"`) for deployments that choose to enforce authentication at the gateway.

## Common request / response envelope

All endpoints accept `POST` requests using the shared G2P envelope (`openg2p_fastapi_common.schemas`), the same structure used across PBMS:

```json
{
  "request_header": {
    "sender_app_mnemonic": "PBMS_STAFF_PORTAL",
    "sender_app_url": "https://odoo.example.org",
    "request_id": "unique-request-id",
    "request_timestamp": "2026-07-07T10:00:00Z"
  },
  "request_body": {
    "pagination_request": { "current_page": 1, "page_size": 20 },
    "request_payload": { "beneficiary_list_id": "abc-123", "target_registry": "social_registry" }
  }
}
```

Successful responses carry `response_header.response_status = "SUCCESS"`; handled `BGTaskException` errors are returned as HTTP 200 with `response_status = "ERROR"` and a populated `response_error_code`.

## Endpoint reference

| Method | Path | Purpose | Response model |
| --- | --- | --- | --- |
| `POST` | `/summary` | Eligibility / list summary for a beneficiary list. | `SummaryResponse` |
| `POST` | `/disbursement_envelope` | Disbursement envelopes for a beneficiary list. | `DisbursementEnvelopeResponse` |
| `POST` | `/disbursement_batch` | Disbursement batches for a beneficiary list. | `DisbursementBatchResponse` |
| `POST` | `/search_beneficiaries` | Search beneficiaries of a list in a target registry. | `BeneficiarySearchResponse` |

## `POST /summary`

Returns the summary for a beneficiary list (used by the staff eligibility / summary view in Odoo).

* **Request payload (`request_body.request_payload`):**

```json
{ "beneficiary_list_id": "abc-123", "target_registry": "social_registry" }
```

* **Response payload (`response_body.response_payload`):**

```json
{ "beneficiary_list_id": "abc-123", "summary": { /* summary object */ } }
```

## `POST /disbursement_envelope`

Returns the disbursement envelopes associated with a beneficiary list (staff disbursement envelope view).

* **Request payload:**

```json
{ "beneficiary_list_id": "abc-123" }
```

* **Response payload:**

```json
{ "beneficiary_list_id": "abc-123", "disbursement_envelopes": [ { /* envelope */ } ] }
```

## `POST /disbursement_batch`

Returns the disbursement batches associated with a beneficiary list (staff disbursement batch view).

* **Request payload:**

```json
{ "beneficiary_list_id": "abc-123" }
```

* **Response payload:**

```json
{ "beneficiary_list_id": "abc-123", "disbursement_batches": [ { /* batch */ } ] }
```

## `POST /search_beneficiaries`

Searches the beneficiaries of a list against a target registry, using the registry adapter selected by `target_registry`. Supports text search and pagination via the standard `pagination_request` (`search_text`, `current_page`, `page_size`).

* **Request payload (`request_body.request_payload`):**

```json
{ "beneficiary_list_id": "abc-123", "target_registry": "social_registry" }
```

* **Optional `request_body.pagination_request`:** `current_page`, `page_size`, `search_text`.
* **Response payload (`response_body.response_payload`):**

```json
{ "beneficiary_count": 42, "beneficiaries": [ { /* registrant record */ } ] }
```

`response_body.pagination_response` reports `number_of_items` (total matched count) and `number_of_pages`.
