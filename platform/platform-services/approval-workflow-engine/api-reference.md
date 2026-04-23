---
description: >-
  REST API reference for the Approval Workflow Engine — summary tables plus
  live OpenAPI 3.1 blocks rendered from the spec committed to the repo.
---

# API Reference

Base path: `/v1/awe/`. The live OpenAPI 3.1 spec is committed at
[`docs/openapi.json`](https://github.com/OpenG2P/awe/blob/develop/docs/openapi.json)
and regenerated from the FastAPI app whenever the service changes, so the
blocks below stay in lockstep with the code.

A running instance also exposes:

* Spec JSON — `/v1/awe/openapi.json`
* Swagger UI — `/v1/awe/docs`
* ReDoc — `/v1/awe/redoc`

## Authentication

Every endpoint under `/v1/awe/` (except `/health`, `/version`, `/config`)
requires a **Keycloak JWT bearer token** in the `Authorization` header:

```
Authorization: Bearer <token>
```

Authorization model:

| Operation                                                    | Required              |
| ------------------------------------------------------------ | --------------------- |
| Policy CRUD, request cancellation                            | `awe-admin` realm role |
| Create approval request, read requests, list/decide on tasks | Any valid token       |
| Task decision                                                | Token's `sub` must match task's `assignee` (or `awe-admin` override) |

Dev mode (`awe.keycloak.issuer=""`) skips signature verification — for
local development only; never reachable from the shipped Helm chart.

## Error envelope

Every non-2xx response has the same shape:

```json
{
  "id": "openg2p.awe",
  "version": "1.0",
  "responsetime": "2026-04-23T10:00:00.000Z",
  "response": null,
  "errors": [
    { "errorCode": "AWE-NNN", "message": "..." }
  ]
}
```

Error code catalog:

| Code      | Meaning                                                |
| --------- | ------------------------------------------------------ |
| `AWE-001` | Policy not found                                       |
| `AWE-002` | Policy conflict / version clash                        |
| `AWE-003` | Request not found                                      |
| `AWE-004` | Task not found                                         |
| `AWE-005` | Service not ready (startup incomplete)                 |
| `AWE-006` | Database health check failed                           |
| `AWE-007` | Invalid state transition                               |
| `AWE-008` | Unauthorized / forbidden                               |
| `AWE-009` | Idempotency key conflict (same key, different payload) |
| `AWE-010` | Validation — bad policy definition                     |

## Endpoint summary

### Policy configuration

| Method  | Path                                                           | Summary                                                     | Auth          |
| ------- | -------------------------------------------------------------- | ----------------------------------------------------------- | ------------- |
| `POST`  | `/v1/awe/policies`                                             | Create first draft of a new policy                          | `awe-admin`   |
| `GET`   | `/v1/awe/policies`                                             | List policies (newest version of each `policy_key`)         | `awe-admin`   |
| `GET`   | `/v1/awe/policies/{policy_key}/versions`                       | List all versions of a `policy_key`                         | `awe-admin`   |
| `GET`   | `/v1/awe/policies/{policy_key}/versions/{version}`             | Fetch a specific version with stages and rules              | `awe-admin`   |
| `PUT`   | `/v1/awe/policies/{policy_key}`                                | Add a new draft version under an existing `policy_key`      | `awe-admin`   |
| `PATCH` | `/v1/awe/policies/{policy_key}/versions/{version}`             | Edit a draft version in place (drafts only — 409 on active) | `awe-admin`   |
| `POST`  | `/v1/awe/policies/{policy_key}/versions/{version}/activate`    | Activate a version (archives the previously active one)     | `awe-admin`   |
| `POST`  | `/v1/awe/policies/{policy_key}/versions/{version}/simulate`    | Resolve approvers for a sample context — no DB writes       | `awe-admin`   |

### Requests (runtime, service-to-service)

| Method | Path                                    | Summary                                                         | Auth          |
| ------ | --------------------------------------- | --------------------------------------------------------------- | ------------- |
| `POST` | `/v1/awe/requests`                      | Create an approval request (`Idempotency-Key` header supported) | Service token |
| `GET`  | `/v1/awe/requests`                      | Search by `artifact_type` / `artifact_id` / `status`            | Any valid     |
| `GET`  | `/v1/awe/requests/{request_id}`         | Fetch a request by id                                           | Any valid     |
| `POST` | `/v1/awe/requests/{request_id}/cancel`  | Cancel an in-flight request                                     | `awe-admin`   |
| `GET`  | `/v1/awe/requests/{request_id}/events`  | Timeline of every event (audit log)                             | Any valid     |

### Tasks (approver-facing, proxied by the caller)

| Method | Path                                 | Summary                                                 | Auth                         |
| ------ | ------------------------------------ | ------------------------------------------------------- | ---------------------------- |
| `GET`  | `/v1/awe/tasks`                      | List the caller's open tasks (`assignee=me` by default) | Any valid                    |
| `POST` | `/v1/awe/tasks/{task_id}/claim`      | Claim a task (intent-to-act marker)                     | Task assignee or `awe-admin` |
| `POST` | `/v1/awe/tasks/{task_id}/decision`   | Record a decision (`approve` / `reject` / `abstain`)    | Task assignee or `awe-admin` |

### Service endpoints (unauthenticated)

| Method | Path              | Summary                                |
| ------ | ----------------- | -------------------------------------- |
| `GET`  | `/v1/awe/health`  | Health / readiness probe               |
| `GET`  | `/v1/awe/version` | Service version + build metadata       |
| `GET`  | `/v1/awe/config`  | Effective non-sensitive configuration  |

## Live OpenAPI blocks

The blocks below render from a GitBook-registered OpenAPI source named
`awe-api`. If the blocks appear empty in a specific viewer, confirm the
source is registered in your GitBook project pointing to
`https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json`,
or view the same information in the Swagger UI at `/v1/awe/docs` on a
running instance.

### Policy configuration

{% openapi-operation spec="awe-api" path="/v1/awe/policies" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}/versions" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}/versions/{version}" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}" method="put" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}/versions/{version}" method="patch" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}/versions/{version}/activate" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/policies/{policy_key}/versions/{version}/simulate" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

### Requests

{% openapi-operation spec="awe-api" path="/v1/awe/requests" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/requests/{request_id}" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/requests" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/requests/{request_id}/cancel" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/requests/{request_id}/events" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

### Tasks

{% openapi-operation spec="awe-api" path="/v1/awe/tasks" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/tasks/{task_id}/claim" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/tasks/{task_id}/decision" method="post" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

### Service endpoints

{% openapi-operation spec="awe-api" path="/v1/awe/health" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/version" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-api" path="/v1/awe/config" method="get" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

### Schemas

{% openapi-schemas spec="awe-api" schemas="PolicyCreate,PolicyOut,PolicyVersionOut,StageIn,StageOut,ApproverRuleIn,ApproverRuleOut,SimulateRequest,SimulateResponse,CreateRequestIn,CreateRequestOut,RequestOut,TaskOut,DecisionIn,DecisionOut,EventOut,CancelRequest,WebhookEvent,HealthResponse,VersionResponse,ErrorResponse" grouped="true" %}
[OpenAPI awe-api](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-schemas %}
