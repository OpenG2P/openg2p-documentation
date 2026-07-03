# Partner Management

The **Partner Management** service is OpenG2P's central registry of **partners**
and their **public keys**. Every OpenG2P module that needs to verify a partner's
signature (g2p-bridge, consent-manager, …) fetches that partner's public key
from this service instead of maintaining its own partner table.

## Why it exists

Before Partner Management, partner keys lived in two disconnected places:

* **g2p-bridge / openg2p-fastapi-common** kept a local `partner_keys` table
  seeded from Helm config, with no runtime admin API.
* **consent-manager** kept its own richer `Partner` + key model with an approval
  flow and a JWKS endpoint.

Partner Management consolidates these into one system of record. Modules stop
managing partners locally and simply **read keys from a shared API**.

## What it does (v1)

* **Onboarding** — an admin registers a partner (`partner_id`, name, free-text
  description) and its initial public key(s). Keys may be pasted (PEM, X.509
  certificate, or JWK) or imported once from the partner's `jwks_url`.
* **Approval** — a partner moves through `created` → `active` → `disabled`. Keys
  are served only while the partner is `active`.
* **Key rotation** — a partner (via the admin, in v1) files an *update* request
  that adds new keys and/or revokes old ones. New and old keys can be active at
  once for zero-downtime rotation.
* **Key fetch** — unauthenticated APIs return a partner's active public keys by
  `partner_id` (and optionally `kid`), plus a per-partner JWKS view.

## Scope of the first version

* The portal is **admin-run**, not partner self-service. The admin both files
  requests and approves them.
* Approval is a **simple built-in step** (`created` → approved/`active`); there
  is no Approval Workflow Engine (AWE) integration yet. The data model reserves
  an `awe_request_id` for a later AWE integration.
* The key-fetch APIs require **no caller signature** — they return only
  non-secret public material and are exposed on the cluster-internal gateway.

## Built on

The two backend services are built on **[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common)** (with `openg2p-fastapi-auth` for staff-realm JWT validation), tracked at the `develop` ref. See [Technical Architecture → Framework](technical-architecture.md#framework).

## Pages

* [Versions](versions.md)
* [Functional Specifications](functional-specifications.md)
* [API Reference](api-reference.md)
* [Technical Architecture](technical-architecture.md)
* [Deployment](deployment.md)
* [Testing](testing.md)
