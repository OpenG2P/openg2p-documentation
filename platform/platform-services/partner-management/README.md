---
description: >-
  OpenG2P's central registry of partners, their public keys and their access
  policies, read by other modules over an internal API.
---

# Partner Management

The **Partner Management** service is OpenG2P's central registry of **partners**,
their **public keys** and their **access policies** (what each partner may ask
for). Every OpenG2P module that needs to verify a partner's signature
(g2p-bridge, consent-manager, …) fetches that partner's public key from this
service, and modules that enforce access (the Consent Manager, an Exchange's
Composite) fetch its policies, instead of maintaining their own partner tables.

## Why it exists

Before Partner Management, partner keys lived in two disconnected places:

* **g2p-bridge / openg2p-fastapi-common** kept a local `partner_keys` table
  seeded from Helm config, with no runtime admin API.
* **consent-manager** kept its own richer `Partner` + key model with an approval
  flow and a JWKS endpoint.

Partner Management consolidates these into one system of record. Modules stop
managing partners locally and simply **read keys and policies from a shared
API**. Access policies, formerly kept in the Consent Manager, are also held and
approved here.

{% hint style="info" %}
Partner Management is installed **as part of `openg2p-commons-services`** (the
shared platform-services layer), deployed as `commons-services-pm-*`. See
[Deployment](deployment.md).
{% endhint %}

## What it does (v1)

* **Onboarding** — an admin registers a partner (`partner_id`, name, free-text
  description) and its initial public key(s). Keys may be pasted (PEM, X.509
  certificate, or JWK) or imported once from the partner's `jwks_url`.
* **Approval** — a partner moves through `created` → `active` → `disabled`. Keys
  are served only while the partner is `active`.
* **Key rotation** — a partner (via the admin, in v1) files an *update* request
  that adds new keys and/or revokes old ones. New and old keys can be active at
  once for zero-downtime rotation.
* **Access policies** — per partner, a scope policy for each registry (data
  controller) and/or a use-case policy for an Exchange, versioned and changed
  through approved onboarding or policy requests. See
  [Access policies](functional-specifications.md#access-policies).
* **Key and policy fetch** — unauthenticated internal APIs return a partner's
  active public keys by `partner_id` (and optionally `kid`), plus a per-partner
  JWKS view, and its active access policies.

## Scope of the first version

* The portal is **admin-run**, not partner self-service. The admin both files
  requests and approves them.
* Approval is a **simple built-in step** (`created` → approved/`active`); there
  is no Approval Workflow Engine (AWE) integration yet. The data model reserves
  an `awe_request_id` for a later AWE integration.
* The key- and policy-fetch APIs require **no caller signature** — they return
  only non-secret material and are exposed on the cluster-internal gateway.

## Built on

The two backend services are built on **[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common)** (with `openg2p-fastapi-auth` for staff-realm JWT validation), tracked at the `develop` ref. See [Technical Architecture → Framework](technical-architecture.md#framework).

## Pages

* [Versions](versions.md)
* [Functional Specifications](functional-specifications.md)
* [Creating and Changing Policies](creating-and-changing-policies.md)
* [API Reference](api-reference.md)
* [Technical Architecture](technical-architecture.md)
* [Integration — consuming partner keys and policies](integration.md)
* [Deployment](deployment.md)
* [Testing](testing.md)
