---
description: >-
  REST API reference for the Audit Manager — rendered directly from the live
  OpenAPI 3.1 spec committed to the repo.
---

# API Reference

Base path: `/v1/auditmanager/`. The spec below is rendered from the live
[`docs/openapi.json`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/docs/openapi.json).
CI regenerates it from the FastAPI app on every `src/`-touching push, so
endpoint signatures, response shapes, status-code descriptions, and the
error-code catalog stay in lockstep with the code. This page does **not**
duplicate any of that in prose.

A running instance also exposes the live spec at
`/v1/auditmanager/openapi.json` and interactive UIs at
`/v1/auditmanager/docs` (Swagger) and `/v1/auditmanager/redoc`.

{% openapi-operation spec="audit-manager-api" path="/v1/auditmanager/events" method="post" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="audit-manager-api" path="/v1/auditmanager/events/batch" method="post" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="audit-manager-api" path="/v1/auditmanager/health" method="get" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="audit-manager-api" path="/v1/auditmanager/version" method="get" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-operation spec="audit-manager-api" path="/v1/auditmanager/config" method="get" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-operation %}

{% openapi-schemas spec="audit-manager-api" schemas="AcceptedResponse,BatchAcceptedResponse,HealthResponse,VersionResponse,ConfigResponse,ErrorResponse,CloudEvent,EventBatch,Actor,AuditData,Resource" grouped="true" %}
[OpenAPI audit-manager-api](https://raw.githubusercontent.com/OpenG2P/audit-manager/develop/docs/openapi.json)
{% endopenapi-schemas %}
