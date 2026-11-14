---
description: Ingress, gateway functions, networking.
---

# Networking and Gateway

**Status: decided; built except where marked "to do".**

The functions of an API gateway are fulfilled by the ingress of the [OpenG2P deployment](../../deployment/openg2p-deployment-model.md) (Nginx, Istio), through which partners reach Agri Stack as every OpenG2P service, and by the services themselves:

| API gateway feature | In the OpenG2P deployment |
| --- | --- |
| Single public entry point, TLS, routing | Nginx and the Istio ingress gateway, a VirtualService per service |
| Partner authentication | Each service verifies the partner's signature over the request body against [Partner Management](../../platform/platform-services/partner-management/README.md) |
| Access control | Each partner's use-case policies (one per use case) in the Exchange's Partner Management, checked by the Composite on every call; Istio `AuthorizationPolicy` to limit registries' partner APIs to the Composite (to do) |
| Rate limits and quotas | A per-partner, per-use-case limit in the Composite, set in each use case and counted across pods in Redis; optionally an edge limit on the Composite's route at the Istio ingress gateway (off by default); daily quotas to do ([rate limiting](../composite/rate-limiting.md)) |
| Usage reports | Audit events from every hop, in the Audit Manager |
| mTLS between services, timeouts, retries, circuit breaking | Istio |
| Developer portal | The [Partner Guide: Fetching Farmer Data](../partner-integration-guide.md) and the Composite's describe endpoints |

{% hint style="info" %}
A gateway product is worth adding only if many partner-facing APIs from different teams need a common portal, keys, analytics or billing, or if a national API gateway is mandated. It would then sit in front of the Composite, unchanged.
{% endhint %}

## Networking between installs

Each install's partner-facing APIs (the registries' partner APIs; at the Exchange, the Composite, the Consent Manager's partner API and the partner portal) are on public hostnames on its own ingress. Staff portals and admin APIs can stay on an internal gateway reached over WireGuard. The Composite's internal API (`/composite/v1/internal`, the consent templates the Exchange CM reads) is never on its public host ([chart settings](../deployment/composite-chart-settings.md#hostnames-and-ingress)). Calls between installs use those public hostnames, protected by signed requests with keys in Partner Management, not shared Keycloak tokens: each install is a partner of the services it calls, and no secrets are exchanged. A gateway between departments with mutual TLS is an [Roadmap](../roadmap/README.md).
