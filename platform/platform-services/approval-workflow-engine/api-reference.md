---
description: >-
  REST API reference for the Approval Workflow Engine — rendered directly from
  the live OpenAPI 3.1 spec committed to the repo.
---

# API Reference

Base path: `/v1/awe/`. The spec below is rendered from the live [`docs/openapi.json`](https://github.com/OpenG2P/awe/blob/develop/docs/openapi.json). CI regenerates it from the FastAPI app on every `src/`-touching push, so endpoint signatures, response shapes, status-code descriptions, and the error-code catalog stay in lockstep with the code. This page does **not** duplicate any of that in prose.

A running instance also exposes the live spec at `/v1/awe/openapi.json` and interactive UIs at `/v1/awe/docs` (Swagger) and `/v1/awe/redoc`.

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

{% openapi-schemas spec="awe-specification" schemas="ApproverRuleIn,ApproverRuleOut,CancelRequest,CreateRequestIn,CreateRequestOut,DecisionIn,DecisionOut,ErrorDetail,EventOut,HTTPValidationError,HealthPayload,HealthResponse,PolicyCreate,PolicyOut,PolicyVersionOut,RequestOut,SimulateRequest,SimulateResponse,SimulateStageOut,StageIn,StageOut,TaskOut,ValidationError,VersionPayload,VersionResponse" grouped="true" %}
[OpenAPI awe-specification](https://raw.githubusercontent.com/OpenG2P/awe/develop/docs/openapi.json)
{% endopenapi-schemas %}
