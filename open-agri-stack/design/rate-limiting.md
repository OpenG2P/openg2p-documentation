---
description: >-
  How Agri Stack limits request rates: an edge limit at the Istio ingress
  gateway and a per-partner, per-use-case limit in the Composite, shared in
  Redis. What is built and what is later.
---

# Rate Limiting

**Status: built** (edge limit and per-partner limit); partner-aware edge limits and quotas are later.

## Three layers

Good practice limits requests in up to three places. Each catches what the others cannot.

| Layer | Where | Keyed on | What it is for |
| --- | --- | --- | --- |
| **Edge** | The ingress gateway (Istio, Envoy) | Route, client IP, or everything | Cheap. Stops floods before they reach a service; knows nothing about partners |
| **Identity-aware edge** | The ingress gateway | The caller, read from something the gateway can trust: a JWT claim or an mTLS client certificate | Per-caller limits without touching the service |
| **Application** | The service | Business identity: partner and use case | Business rules (rate per partner per use case, quotas). Counters in shared storage so every pod counts together |

The identity-aware edge layer is **not possible today**: partners sign inside the request body (a detached JWS over the envelope, `header.sender_id`), which the gateway cannot verify. Only the Composite, which checks the signature against [Partner Management](../../platform/platform-services/partner-management/README.md), knows who is calling.

## What Agri Stack does

1. **Edge limit at the ingress gateway.** The Composite chart adds a local rate limit (Envoy token bucket) on the Composite's use-case route (`/composite/v1/use-cases`) at the shared Istio ingress gateway. It counts all partners together, per gateway pod. Over the limit the gateway answers `429` with the header `x-local-rate-limit: true` (plain text, not a signed envelope). Default 600 requests per minute.
2. **Per partner, per use case, in the Composite.** Each use case sets `limits.rate_per_partner` (e.g. `60/min`). The Composite applies it after the signature and use-case policy checks: a token bucket per (partner, use case) in Redis (the commons Redis), so every pod and worker draws from the same bucket. Over the limit: `429 rate_limited`.

If Redis is unreachable, each worker process falls back to its own in-memory bucket and logs a warning. This is deliberate: **availability over exactness**. A Redis outage never fails a partner call; the limit only loosens (up to pods × workers × the rate) until Redis answers again.

Settings: [Composite deployment](../deployment/composite.md#scaling-and-rate-limits).

## Later

* **Per-partner limits at the edge**, if partner identity moves to mTLS client certificates or a JWT the gateway can read.
* **Daily quotas** per partner per use case (`limits.daily_quota_per_partner`), counted in the same Redis.
* **Per-farmer fetch frequency**: the policy's `max_fetch_frequency` (how often a partner may fetch the same farmer's data).

The policy's `data_life` is a retention term for the partner (how long it may keep the data), not a rate. It is recorded only.
