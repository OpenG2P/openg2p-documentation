---
description: >-
  REST API reference for the Approval Workflow Engine — rendered directly from
  the live OpenAPI 3.1 spec committed to the repo.
layout:
  feedback:
    visible: false
---

# API Reference

Base path: `/v1/awe/`. The spec below is rendered from the live [`docs/openapi.json`](https://gitlab.com/openg2p/awe/-/blob/develop/docs/openapi.json). CI regenerates it from the FastAPI app on every `src/`-touching push, so endpoint signatures, response shapes, status-code descriptions, and the error-code catalog stay in lockstep with the code. This page does **not** duplicate any of that in prose.

A running instance also exposes the live spec at `/v1/awe/openapi.json` and interactive UIs at `/v1/awe/docs` (Swagger) and `/v1/awe/redoc`.

## Caller API surface — what an integrator actually uses

The full reference below covers every endpoint, including the admin
surface that powers AWE's own portal (policy CRUD, simulate, delegations,
audit log, delivery retry). **Caller services do not call any of those.**

A Caller integration touches only the five endpoints below, plus implements
one inbound webhook handler.

### Outbound — Caller → AWE

| API | When the Caller calls it |
|--|--|
| `POST /v1/awe/requests` | A Caller-owned artifact has been created and needs approval. Pass `policy_key`, `artifact_type`, `artifact_id`, `context`, `callback_url`, `requester`. |
| `POST /v1/awe/requests/{id}/cancel` | The underlying artifact was withdrawn, or the Caller wants to abort an in-flight flow. |
| `GET /v1/awe/tasks?assignee=me` *(forwarding the approver's JWT)* | When an approver opens the Caller's UI — returns every open AWE task assigned to the user whose JWT is on the request, across all requests and policies. `me` expands to the token's `sub` claim. The Caller joins this list with its own artifact rows (by `awe_request_id`) to build the per-Caller inbox. |
| `POST /v1/awe/tasks/{task_id}/decision` *(forwarding the approver's JWT)* | Records the approver's `approve` / `reject` / `abstain`. |
| `GET /v1/awe/requests/{id}` *(optional)* | Per-request lookup — full state of one approval flow by id (current stage, resolved approvers, history, context snapshot). Used when a user opens an artifact detail page in the Caller's UI and the Caller wants to render an "approval state" panel inline. **Not** an admin list view; takes a single id, returns one request. Skip it if you'd rather rely solely on the webhook to drive UI state. The Caller decides which users see this panel — AWE itself does not restrict reads. |

### Inbound — AWE → Caller (implemented by the Caller, not called)

| Endpoint | What the Caller does |
|--|--|
| `POST {callback_url}` | Receives signed AWE webhooks. On `request_approved` apply the artifact-side effect; on `request_rejected` / `request_cancelled` close out the artifact accordingly. Validate the `X-Approval-Signature` HMAC, dedup on `X-Approval-Event-Id`, return 2xx within the configured timeout. |

Everything else in the reference below is admin / operator surface served
from AWE's bundled portal.

### Error responses

Every non-2xx response returns AWE's standard error envelope with an
`AWE-NNN` code in `errors[0].errorCode`. See the
[Error codes](error-codes.md) page for the full catalog — what each
code means, the HTTP status it ships with, and whether to retry.

---

{% openapi-operation spec="awe-specification" path="/v1/awe/health" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/version" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/config" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}/versions" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}/versions/{version}" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}/versions/{version}" method="patch" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}/versions/{version}/activate" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}" method="put" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/requests" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/policies/{policy_key}/versions/{version}/simulate" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/requests" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/requests/{request_id}" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/requests/{request_id}/cancel" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/requests/{request_id}/events" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/tasks" method="get" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/tasks/{task_id}/claim" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="awe-specification" path="/v1/awe/tasks/{task_id}/decision" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-operation %}

## Webhook (outbound from AWE → Caller)

AWE POSTs to whatever `callback_url` was set on the request whenever a
status-changing event occurs. The contract — body schema and the three
signed headers — is declared in the OpenAPI spec under the top-level
`webhooks:` field (OpenAPI 3.1 feature) so it's discoverable from the
same artifact as the rest of the API.

{% openapi-webhook spec="awe-specification" name="approval-event" method="post" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-webhook %}

{% openapi-schemas spec="awe-specification" schemas="ApproverRuleIn,ApproverRuleOut,CancelRequest,CreateRequestIn,CreateRequestOut,DecisionIn,DecisionOut,ErrorDetail,EventOut,HTTPValidationError,HealthPayload,HealthResponse,PolicyCreate,PolicyOut,PolicyVersionOut,RequestOut,SimulateRequest,SimulateResponse,SimulateStageOut,StageIn,StageOut,TaskOut,ValidationError,VersionPayload,VersionResponse,WebhookEvent" grouped="true" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-schemas %}
