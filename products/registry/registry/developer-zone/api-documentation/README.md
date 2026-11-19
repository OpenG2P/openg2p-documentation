---
description: API reference for OpenG2P Registry.
---

# API Documentation

{% hint style="info" %}
**New home: GitLab.** **`registry-platform`** is now developed at [github.com/OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform).
{% endhint %}

OpenG2P Registry exposes three API surfaces. All the pages below are **generated from the OpenAPI specs published by [`registry-platform`](https://github.com/OpenG2P/registry-platform/tree/develop/apis/docs/openapi)** and render live from them, so the request/response schemas are always the spec's own.

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

## Agent Portal API

REST APIs used by the Agent Portal UI at a service counter: issue a verifiable credential to a beneficiary, as a printed card or into their mobile wallet, and verify a credential's QR. See [Verifiable Credentials](../../../../../platform/platform-services/vc-issuance/README.md) for how issuance works.

* **Who calls it.** Agents signed in to the Keycloak `agent` realm. Issuance endpoints need the `register:issue_credential` permission and `verify_vc` needs `register:verify_credential`.
* **What gets mounted.** Each feature is switched on separately in the Helm chart: `agentPortalApi.vcIssuance`, `agentPortalApi.walletIssuance` (for `create_wallet_offer`) and `agentPortalApi.vcVerification` (for `verify_vc`). A route whose feature is off is not served. This reference lists every route.
* **Order of calls.** A credential is issued only after the beneficiary authenticates: `get_vc_types` → `lookup_beneficiary` → `start_authentication` → `get_authentication_status` → `issue_vc` or `create_wallet_offer`.

{% content-ref url="agent-portal-api.md" %}
[agent-portal-api.md](agent-portal-api.md)
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
