# Architecture

OpenG2P PBMS (Programme & Beneficiary Management System) is built from a set of loosely-coupled runtime components that share a common set of databases and commons services. Operators define programmes, rules and cycles in an Odoo application; the heavy list-generation, entitlement and disbursement processing runs asynchronously in a decoupled Celery engine; and two FastAPI portals expose read views to staff and beneficiaries. Actual money/goods movement is delegated to the external [G2P Bridge](https://docs.openg2p.org/g2p-bridge/) service.

This page describes the consolidated runtime architecture and how the components interact.

## Components

| Component | Technology | Responsibility |
| --- | --- | --- |
| PBMS Odoo app (`g2p_pbms`) | Odoo | Operator UI and system of record — define programmes, eligibility/priority/entitlement rules, enrolment and disbursement cycles, benefit codes, approvals; triggers background processing by writing work rows into the PBMS database. |
| Celery beat producers | Celery beat | Periodically scan the databases for pending work and enqueue tasks onto the broker. |
| Celery workers | Celery | Execute the processing pipeline — list generation, entitlement, summaries, envelope/batch creation and disbursement. |
| Staff Portal API | FastAPI | Read-oriented API for programme staff (beneficiary search, disbursement and summary views). |
| Beneficiary Portal API | FastAPI | Read-oriented API for beneficiaries (their benefit programmes). |
| G2P Bridge | External REST service | Executes disbursement envelopes and disbursements downstream. PBMS is the caller. |
| Social Registry | External (read-only) | Source of registrant data used for eligibility and entitlement computation. |

### Commons services

PBMS depends on the shared OpenG2P commons services:

| Service | Used for |
| --- | --- |
| PostgreSQL | Persistence — the `pbmsdb`, `bgtaskdb` and (read) `socialregistrydb` databases. |
| Keycloak | Authentication / identity for the portal APIs. |
| MinIO | Object storage (documents). |
| Keymanager | Digital signing of outbound G2P Bridge requests (see [Keymanager signing](#keymanager-signing)). |
| Redis | Celery broker and result backend. |

## High-level flow

```
                         ┌───────────────────────────┐
   Operators ──────────► │   PBMS Odoo app (g2p_pbms) │  define programmes, rules,
                         │   operator UI + records    │  cycles, approvals
                         └─────────────┬─────────────┘
                                       │ writes work rows
                                       ▼
        ┌──────────────────────────────────────────────────────────┐
        │                   Databases (PostgreSQL)                   │
        │        pbmsdb        bgtaskdb        socialregistrydb (r)  │
        └───────┬───────────────────┬──────────────────────┬────────┘
                │                   │                       │
   reads ▲      │        ┌──────────┴───────────┐           │ reads
         │      │        │  Celery beat producers│           │
   Staff Portal │        │  (Redis broker)       │           │
   Bene  Portal │        │          │            │           │
   (FastAPI)    │        │          ▼            │           │
                │        │     Celery workers ───┼───────────┘
                │        └──────────┬────────────┘
                │                   │ POST (JWT-signed via Keymanager)
                │                   ▼
                │        ┌──────────────────────┐
                │        │      G2P Bridge       │  envelope + disbursement
                │        │   (external REST)     │  execution
                │        └──────────────────────┘
```

The Odoo app and the portal APIs never call the workers directly. Coordination is entirely through database state: Odoo (and the workers themselves) mark rows as `pending`, the beat producers pick those rows up on a fixed schedule and enqueue tasks, and the workers advance each row's status field as they progress.

## The Celery engine

The background engine is split into two deployables that share the same task/queue naming but run separately:

- **`openg2p-bg-task-celery-beat-producers`** — a Celery beat scheduler. On each tick it runs one producer per stage, queries the databases for rows in the `pending` state for that stage, flips them to `processing`, and enqueues the matching worker task onto the broker queue.
- **`openg2p-bg-task-celery-workers`** — the Celery workers that consume the queue and perform the actual processing.

**Redis is the broker** (and result backend): `redis://…` via `celery_broker_url` / `celery_backend_url`.

The scheduling frequency is a single interval applied to every producer (`producer_frequency`, default `30` seconds), and each producer enqueues at most `no_of_tasks_to_process` rows per tick onto the `bg_task_worker_queue`.

### Pipeline stages

Each stage is a producer → worker pair. The stages run in the following order, with each stage's completion (a status field on the beneficiary list / batch) unlocking the next:

| # | Worker task name | Triggered when | Does |
| --- | --- | --- | --- |
| 1 | `beneficiary_list_worker` | `eligibility_process_status = pending` | Generates the beneficiary/eligibility list for a programme by reading the Social Registry and applying the programme's eligibility and priority rules. |
| 2 | `entitlement_worker` | `entitlement_process_status = pending` (per list detail) | Computes each beneficiary's entitlement by applying the programme's entitlement rules and benefit codes. |
| 3 | `entitlement_summary_worker` | list ready for summary | Aggregates entitlement statistics for the beneficiary list. |
| 4 | `disbursement_envelope_creation_worker` | `envelope_creation_status = pending` (approved list) | Builds a disbursement envelope for the cycle and creates it on the G2P Bridge (`POST /create_disbursement_envelopes`). |
| 5 | `disbursement_batch_creation_worker` | `disbursement_batch_creation_status = pending` | Splits the envelope's beneficiaries into disbursement batches (`batch_size`, default `2000`). |
| 6 | `disbursement_worker` | `disbursement_status = pending` (per batch) | Submits each batch of disbursements to the G2P Bridge (`POST /create_disbursements`). |

Workers read from `pbmsdb` (programme/list definitions), `bgtaskdb` (intermediate list details, envelopes, batches) and — for stages 1–3 — the Social Registry (`socialregistrydb`, read-only). Failed tasks are retried up to `worker_max_attempts` (default `5`).

## The disbursement / G2P Bridge contract

PBMS does not move funds itself. For the last stages of the pipeline it acts as the **caller** to the external G2P Bridge REST API, in two steps:

| Step | Worker | Endpoint |
| --- | --- | --- |
| Create envelope | `disbursement_envelope_creation_worker` | `POST {g2p_bridge_base_url}/create_disbursement_envelopes` |
| Create disbursements | `disbursement_worker` | `POST {g2p_bridge_base_url}/create_disbursements` |

Both requests wrap a standard OpenG2P request header + body, are serialized to JSON, and carry a JWT digital signature in the `Signature` HTTP header. The signing is described below. Responses are validated back into the `DisbursementEnvelopeResponse` / `DisbursementResponse` schemas, and the resulting identifiers/status are persisted.

The relevant configuration an operator sets on the workers (env prefix `BG_TASK_CELERY_WORKERS_`):

```
BG_TASK_CELERY_WORKERS_G2P_BRIDGE_BASE_URL      # base URL of the G2P Bridge service
BG_TASK_CELERY_WORKERS_KEYMANAGER_SIGN_APP_ID   # Keymanager application id used for signing
BG_TASK_CELERY_WORKERS_KEYMANAGER_SIGN_REF_ID   # Keymanager key reference id used for signing
BG_TASK_CELERY_WORKERS_CELERY_BROKER_URL        # Redis broker URL
```

The G2P Bridge itself organises the received envelopes and batched disbursements and drives downstream execution; see the [Post disbursement workflow](g2p-bridge-workflow.md) and the [G2P Bridge documentation](https://docs.openg2p.org/g2p-bridge/features/cash-goods-and-services).

## Keymanager signing

Outbound G2P Bridge requests are **digitally signed** so the Bridge can verify that a disbursement instruction genuinely originated from PBMS and was not tampered with in transit.

Before each POST, the worker asks Keymanager to produce a JWT over the request JSON (via `KeymanagerCryptoHelper.create_jwt_token`) using the configured signing identity (`keymanager_sign_app_id` / `keymanager_sign_ref_id`, also carried as the `sender_app_mnemonic` in the request header). The resulting token is attached as the `Signature` header. This is a **signature only** — the payload is still sent as normal JSON; the JWT does not embed the payload, certificate or certificate hash.

Signing is **toggle-able**: it is gated by `keymanager_auth_enabled`. When Keymanager integration is disabled the signing step is skipped, which is useful for local development and test environments where the G2P Bridge does not enforce signature verification. In production it should be enabled and pointed at a valid signing key.

## Portal APIs

Two lightweight FastAPI services expose read views over the same databases; neither performs the pipeline processing.

| Portal | Env prefix | Reads | Audience |
| --- | --- | --- | --- |
| Staff Portal API | `STAFF_PORTAL_API_` | `pbmsdb`, `socialregistrydb` | Programme staff — beneficiary search, disbursement and summary views. |
| Beneficiary Portal API | `PBMS_BENE_PORTAL_API_` | `pbmsdb`, `bgtaskdb` | Beneficiaries — their benefit programmes. |

Both authenticate against the commons Keycloak/auth stack and serve data that the Odoo app and Celery engine have already produced.
