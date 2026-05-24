---
description: >-
  Citizen login is phone-number + OTP via Logto. Why Logto (not Keycloak) for
  the citizen IdP, and what changes if eSignet is present (essentially nothing).
---

# Identity & IdP

## Citizen login: phone number + OTP

For OpenG2P deployments **eSignet is not assumed to be present**, so the **citizen** logs into
the Beneficiary/department portal with their **phone number + OTP**. The login provider is also
the **OIDC authorization server** for the whole issuance flow (Mimoto's `authorization_code`
download and Certify's token validation both use it).

The citizen is identified by **phone number**, which is the key the Certify Registry connector
uses to resolve the Registry record (see [Technical Architecture](technical-architecture.md)).

## Why Logto for the citizen IdP (and Keycloak for staff)

We use **Logto** as the **citizen** IdP, and keep **Keycloak** for **staff/admin** (where it is
already used). They are complementary OIDC providers, both self-hostable and free.

* **Phone-OTP is first-class in Logto.** Logto OSS provides **phone-number signup + OTP login
  out of the box**, with an easy custom SMS-connector for a local gateway. In Keycloak,
  phone-OTP passwordless is **not built-in** — it needs plugins / custom SPI / custom flows
  (a known friction point). For a citizen-facing, phone-first audience, Logto removes that work.
* **Footprint & DX.** Logto is lightweight (Node/TS) with a modern admin UI and config-driven
  connectors; Keycloak is a heavier JVM platform whose theming/extensions are Java + FreeMarker.
* **Keycloak's strengths are staff-side.** Keycloak excels at SAML, LDAP/AD federation,
  identity brokering and fine-grained authz — what staff/admin IAM needs, and where it's already
  deployed. We keep it there.
* **Licensing.** Self-hosted **Logto OSS is MPL-2.0 (free)** — same codebase as their cloud; you
  pay only for your own infrastructure. The Logto Cloud price tiers are for their managed SaaS,
  not self-hosting. Keycloak is Apache-2.0 (free). So both are free to self-host.

| Dimension | Keycloak (staff/admin) | Logto (citizen) |
|---|---|---|
| Phone-OTP passwordless | Not built-in (plugins/SPI) | **Built-in, turnkey** |
| Protocols | OIDC + SAML + more | OIDC / OAuth 2.1 (SAML limited) |
| Enterprise federation | Strong (LDAP/AD, Kerberos, brokering) | Lighter (social/enterprise connectors) |
| Footprint / DX | Heavy JVM; Java+FreeMarker theming | Lightweight Node/TS; modern admin UI |
| Cost (self-hosted) | Free (Apache-2.0) | Free (MPL-2.0) |

**Essence:** Keycloak = heavyweight enterprise IAM (max protocol/federation breadth) — but
phone-OTP is DIY. Logto = modern citizen-oriented OIDC where phone signup + OTP login is a
first-class feature. They federate cleanly (both OIDC), so staff stay on Keycloak and citizens
use Logto.

## The IdP's role in the flow

Whatever the citizen IdP is, it must be an **OIDC authorization server** that:

* supports **`authorization_code` + PKCE**,
* exposes OIDC **discovery + JWKS** (so Certify validates tokens via `authn.issuer-uri` /
  `jwk-set-uri`),
* can be registered as the issuer's auth server in **Mimoto** (`mimoto-issuers-config.json`),
* releases the **phone number** claim (so Certify's connector can resolve the Registry record).

Logto satisfies all of these. Configuration only — no code.

## Optional: eSignet

eSignet is **not required** and **not assumed** for OpenG2P deployments. If a deployment **does**
have eSignet, the architecture is unchanged — eSignet is simply another OIDC authorization
server. The changes are configuration-only:

* **If eSignet is the citizen IdP:** point Certify's `authn.issuer-uri`/`jwk-set-uri` and
  Mimoto's issuer config at **eSignet** instead of Logto. **No code changes.**
* **If eSignet fronts another provider:** eSignet can sit in front of an OIDC backend (e.g.
  Keycloak); from the issuance flow's perspective it is still just the OIDC AS.
* **National-ID reconciliation becomes possible:** when citizens authenticate via eSignet with a
  **National ID**, the Certify connector can resolve the Registry record by national ID (with
  consent) in addition to phone number. The connector simply reads whichever identifier claim is
  present — a small connector configuration, not a redesign.

In short: **nothing structural changes if eSignet appears** — it slots into the same "OIDC AS"
role, and the only adjustment is which identifier claim the Registry connector keys on.
