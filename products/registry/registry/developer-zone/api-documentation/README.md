---
description: API reference for OpenG2P Registry.
---

# API Documentation

OpenG2P Registry exposes two primary API surfaces. Both pages below are **generated from the OpenAPI specs published by [`registry-platform`](https://github.com/OpenG2P/registry-platform/tree/develop/apis/docs/openapi)** and render live from them, so the request/response schemas are always the spec's own.

## Staff Portal API

REST APIs consumed by the Registry Staff Portal UI for registry configuration, record management, change requests, intake forms, and search.

{% content-ref url="staff-portal-api.md" %}
[staff-portal-api.md](staff-portal-api.md)
{% endcontent-ref %}

## Partner API

REST APIs for external system integration, including data ingestion and DCI-compliant search. The partner API is the policy-enforcement point for consent-aware data sharing — see [Partner APIs](../../design/partner-apis.md).

{% content-ref url="partner-api.md" %}
[partner-api.md](partner-api.md)
{% endcontent-ref %}

## How these pages are maintained

Each endpoint needs one GitBook `openapi-operation` block. Hand-typing them is how the reference silently fell to 96 of 174 endpoints, so the block list is now generated:

```bash
bash tools/gen-openapi-pages.sh
```

Run that after adding or removing routes; it re-emits every operation from the spec, so the page cannot be short.

{% hint style="info" %}
**There is one version of this reference, tracking `develop`.** Per-release snapshots were removed because they were not snapshots: the committed OpenAPI spec is currently byte-identical at `develop`, `1.1.0` and `v1.0.0`, so all three rendered the same 174 endpoints.

Frozen per-release references become meaningful once `apis/scripts/generate_openapi.py` runs in CI so the spec is regenerated with each release. At that point a snapshot is one line in the generator script.
{% endhint %}
