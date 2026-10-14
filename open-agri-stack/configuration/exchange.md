---
description: >-
  What the Agri Stack exchange install (agrix) is configured with: the Consent
  Manager in the exchange role, the partner portal with national-ID login,
  Partner Management, and the partners with their bindings and policies.
---

# Exchange

The **exchange** is the install where partners (banks, MFIs, agritechs) onboard once and farmers give consent once, for data held in several departments' registries. It holds no registry. In the three-namespace setup it is the namespace `agrix`.

| Part | Product | Role in the exchange |
| --- | --- | --- |
| Partner Management (PM) | [Partner Management](../../platform/platform-services/partner-management/README.md) | The partners' and the composite's identities and public keys |
| Consent Manager (CM) | [Consent Manager](../../consent-management/README.md) | Holds the farmers' consents and the partners' policies; issues a consent token per registry to the composite |
| Partner portal | Part of the Consent Manager | Partner staff record a consent given in person |
| eSignet, mock identity system | Commons services | The farmer's national-ID login in the partner portal; the mock identity system stands in for the national ID system (Fayda) in testing |
| Use-case composite | [agri-stack](https://github.com/openg2p/agri-stack) | The partners' entry point; see [Composite](composite.md) |
| Audit Manager | [Audit Manager](../../platform/platform-services/audit-manager/README.md) | The composite's audit events |

How to install it, form field by form field: [What to install in `agrix`](../guides/deployment.md#what-to-install-in-agrix). The one-time setup after install: [exchange setup](../guides/exchange-setup.md). Why the exchange and the departments are split this way: [distributed deployment architecture](../design/distributed-deployment-architecture.md).

## Consent Manager: exchange role

In the commons-services form, **Exchange Role** is `exchange`. That alone gives these values:

| Setting | Value | Meaning |
| --- | --- | --- |
| Token issuer | `agri-stack-exchange-cm` | Stamped as `iss` on every consent token. The department CMs trust this ID |
| Token presenters | `agri-composite` | Only the composite may ask for consent tokens (`/validate` with `issue_receipts: true`) |
| Token lifetime | 900 seconds, capped by the consent's expiry | A consent token is used for one query |
| Signing key | The CM's signing key (same `kid`, same public JWKS) | The demo key for a demo; your own `.p12` (Secret `agrix-cm-signing`) for production. The department CMs fetch the public key from `https://consent-manager-partner.agrix.<parent domain>/api/consent-manager-partner/.well-known/jwks.json` |
| AWE approval of policies | Off | Policies take effect when the CM administrator saves them |

A consent token carries only the scopes in the consent's grant for that registry ∩ the partner's policy for that registry ∩ the scopes the use case asks for. Each department CM then applies its own standing policy for the composite on top ([Farmer Registry](farmer-registry.md#standing-policy-for-the-composite), [Crop Sown Registry](crop-sown-registry.md#the-composite-as-a-partner)). The token format, its status check and the department side are in [exchange consent tokens](../../consent-management/design/exchange-receipts.md); every setting is in [CM deployment](../../consent-management/deployment/README.md#exchange-optional).

## Partner portal

**Partner Portal?** is on. With the exchange role, the portal is set up for Agri Stack without further fields:

| Setting | Value with the exchange role | Meaning |
| --- | --- | --- |
| National-ID login | Always on | The farmer logs in with their national ID through eSignet before a request can be submitted. Only subject ID types `FAYDA_FAN`, `NATIONAL_ID`, `national_id` can log in |
| Required subject identifiers | `[FARMER_ID]` | Every request carries the farmer's Farmer ID besides the FAN. CM staff check it in the [Farmer Registry](farmer-registry.md#farmer-id-and-national-id) before approving the consent |
| Composite URL | `https://agri-composite.<this domain>` | The portal lists the composite's published use cases and fills a request's grants from them. The composite allows the portal's origin by default (`composite.corsAllowOrigins`) |
| Evidence storage | Garage, bucket `consent-evidence` | The form the farmer signed |

Partner users log in to the portal through the CM's `partner` realm in Keycloak. They are created with `setup-partner-realm.sh` from the consent-manager repository; a user's `partner_id` must be the partner's ID as bound in the CM (e.g. `bank-a`). How a consent is collected, verified and handed to the partner: [consent collection](../../consent-management/design/consent-collection.md) and [consent scenarios](../architecture/consent-scenarios.md).

## Partner Management

| Entry | Who adds it |
| --- | --- |
| `PARTNER_AGRI_COMPOSITE`, with the composite's public key and `kid` | [Exchange setup](../guides/exchange-setup.md) |
| `PARTNER_<ID>` for each partner (e.g. `PARTNER_BANK_A`), with its public key | A PM administrator ([partner guide, step 2](../guides/partner-guide.md#step-2-get-onboarded-in-partner-management)) |

The composite verifies every partner request against the partner's key here. The departments' PMs hold only the composite's key: a partner of the exchange is never onboarded in a department.

## Partners and policies

For each partner, the exchange CM holds one **binding** per registry the partner reads, all with the partner's ID as audience, each with its own **policy**:

| Policy field | Example for `bank-a` |
| --- | --- |
| Controller | `farmer-registry`, and a second binding for `crop-sown-registry` |
| Allowed data scopes | At least the scopes the use case requires from that registry ([Farmer Registry](farmer-registry.md#what-agri-stack-reads), [Crop Sown Registry](crop-sown-registry.md#what-agri-stack-reads)) |
| Allowed purposes | The use case's purpose, e.g. `credit-assessment` |
| Allowed subject ID types | `FAYDA_FAN`, `FARMER_ID` |

The CM administrator creates these ([partner guide, step 3](../guides/partner-guide.md#step-3-get-a-binding-and-policy-for-each-registry)); the [partner test](../guides/partner-test.md) creates them for a test partner. A partner must also be in the use case's `allowed_partners` (see [Composite](composite.md#use-cases)).

## What the exchange does not hold

* **No registry and no farmer data.** The composite keeps nothing after it responds.
* **No department policy.** Each department decides at its own CM what it releases to the composite.
* **No partner key in the departments.** The departments trust the composite and the exchange CM's consent tokens, not each partner.

## Not built yet

* Consent given in person digitally (no form, no staff step) and self-service consent by the farmer ([consent scenarios](../architecture/consent-scenarios.md)).
* Policies held in Partner Management rather than in the Consent Manager.
* A consent collected in the exchange CM presented directly at a registry, without the composite.

See [TODOs and open items](../open-items/README.md).
