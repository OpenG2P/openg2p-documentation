---
description: >-
  Agri Stack components, the layers they belong to, and who talks to whom
  when a partner asks for farmer data.
---

# Architecture & Concepts

## Components and who talks to whom

<figure><img src="../../.gitbook/assets/open-agri-stack-components.svg" alt="Agri Stack across departments: each department runs its own cluster behind its own ingress; the Agriculture Department hosts the exchange services and the Farmer Registry as separate installs, each with its own Partner Management and Consent Manager; the Crops Department hosts the Crop Sown Registry. Paths: A, a partner uses one registry directly; B, a use case across registries via the composite; C, registry to registry"><figcaption><p>Components of Agri Stack, across departments</p></figcaption></figure>

| Colour | Layer |
| --- | --- |
| Blue | Layer 1: functional registries (system of record) |
| Ochre | Layer 2: catalogues (reference data; MDS for now) |
| Teal | Layer 3: shared DPI |
| Green | Layer 4: use-case service |

**Departments and installs.** Each department runs its own Kubernetes cluster, behind its own ingress (Nginx, Istio): the public entry point for everything in that cluster. Inside it, each registry is its own install with its own Partner Management, Consent Manager and catalogue, and works on its own. The **exchange services** (partner portal, Consent Manager, Partner Management, eSignet, the use-case composite) are one more install, hosted by one department. Here the Agriculture Department, which holds the Farmer Registry, hosts them; other arrangements are possible.

**A — a partner uses one registry directly (no composite).** The partner is onboarded in that registry's Partner Management and bound in its Consent Manager, and calls the registry's partner API (DCI) with a consent for it. The registry checks the signature at its own Partner Management and the consent at its own Consent Manager, and releases only the effective scopes. Every registry shares data this way, composite or not.

**B — a use case across registries, through the composite** (the OAN layer). The partner onboards once, in the exchange, and uses one consent for several registries:

1. **Consent request.** (How consent is collected, in person with a form, in person digitally, or self-service: [consent scenarios](consent-scenarios.md).) The partner's staff raise a consent request in the partner portal, with the farmer's national ID and Farmer ID, and upload the form the farmer signed.
2. **National-ID login.** The farmer proves who they are through eSignet against the national ID system. Consent Manager staff verify the form and check the Farmer ID in the Farmer Registry; the consent becomes active ([consent collection](../../consent-management/design/consent-collection.md)).
3. **Query.** The partner's system sends a signed query to the composite with the consent (its ID, or a consent the partner signed).
4. **Consent tokens.** The composite asks the exchange's Consent Manager for one signed consent token per registry, with only the scopes the use case needs.
5. **Search.** The composite searches each registry with its consent token: the Farmer Registry in the same cluster, the Crop Sown Registry in the Crops Department's.
6. **Check.** Each registry checks its consent token at its **own** Consent Manager, which trusts the exchange's consent tokens (its public keys) and applies its standing policy for the composite.

**C — registry to registry (not in use today).** A registry that needs another's data is simply one of its partners: onboarded in its Partner Management, with a policy in its Consent Manager, no composite involved. The reference design is crop activity from the Crop Sown Registry kept in the Farmer Registry, through the registries' outgestion and ingestion and a small relay (not built): [registry data sync](../design/registry-data-sync.md) and the [setup guide](../guides/registry-to-registry-sync.md). Sharing of this kind usually rests on a mandate rather than each farmer's consent; the Consent Manager's rule for that (a standing permission for a purpose) is an [open item](../open-items/README.md).

* The ingress (dashed grey: OpenG2P deployment infrastructure, not an Agri Stack service) routes requests but never reads data. The composite runs only approved use cases and keeps nothing after it responds.
* Beckn appears only at the OAN network layer, for discovering service providers and consumers. It isn't used to exchange registry data.

{% hint style="info" %}
How the departments are installed and set up: [distributed deployment architecture](../design/distributed-deployment-architecture.md) and [deploying on a cluster](../guides/deployment.md#three-namespace-setup-exchange-and-departments).
{% endhint %}

## Who does what

* **Partner Management (one per install).** Each registry's own, and the exchange's: the trust root for whoever calls that install. Partners of a use case onboard in the exchange's; a registry's lists its direct partners, the composite and other registries. In the target design it also holds the data-share policies; today they are in the Consent Manager.
* **Consent Manager (one per install).** A registry's own checks the consents (and the exchange's consent tokens) for that registry. The exchange's holds the farmers' consents collected in the partner portal (national-ID login, signed form, staff verification) and issues a signed consent token per registry.
* **Registries (one per install).** Each one is sovereign and works on its own: it checks the caller, checks the consent at its own Consent Manager, and releases only the effective scopes. All of them are keyed to the same national-ID-based identifier; the Farmer Registry holds the link between the national ID and the Farmer ID.
* **Ingress and composites.** The OpenG2P deployment's ingress is the single public entry point (see [below](#entry-point-the-openg2p-deployment-not-a-separate-api-gateway)). Data from several registries is merged only in narrow composite services built for one purpose each, such as `loan-profile`. There is no general query engine across registries. Each use case is a configuration file loaded by one generic composite service (see [use-case composite](../design/use-case-composite.md)).
* **eSignet and the national ID system.** The farmer's login with their national ID when consent is collected in person.
* **AWE.** Approval of policy changes, where a department switches it on.
* **Audit Manager.** Receives audit events from every hop, linked by the request ID.

## Entry point: the OpenG2P deployment, not a separate API gateway

Agri Stack has **no API gateway product**. Partners reach it through the ingress of the [OpenG2P deployment](../../deployment/openg2p-deployment-model.md) (Nginx and Istio on Kubernetes), as for every OpenG2P service, and the jobs usually given to an API gateway are covered by that deployment and by the composite:

| Gateway job | Handled by |
| --- | --- |
| One public entry point, TLS, routing | Nginx and the Istio ingress gateway, with an Istio VirtualService per service |
| Partner authentication | The composite and each registry verify the partner's signature against [Partner Management](../../platform/platform-services/partner-management/README.md). A gateway could not do this natively anyway: the signature covers the request body |
| Who may call what | The composite's `allowed_partners` today, PM policies later. Istio `AuthorizationPolicy` can restrict the registries' partner APIs to the composite (to do) |
| Rate limits | Per pod in the composite today; across pods, with shared counters in Redis (to do). Istio global rate limiting is an alternative, but needs the partner ID in a header, since Istio cannot read the signed body |
| Daily quotas, usage reports | The composite knows the partner on every request and sends audit events, so quotas and usage reports come from there (to do) |
| mTLS between services, timeouts, retries, circuit breaking | Istio |
| Developer portal, API keys, analytics, billing | Not needed now: the [partner guide](../guides/partner-guide.md) and the composite's describe endpoints cover discovery |

A gateway product becomes worth adding only if Agri Stack grows many partner-facing APIs from different teams that need a common portal, keys, analytics or billing, or if a national API gateway is mandated. It would then sit in front of the composite, unchanged.

## In this part

| Page | Covers |
| --- | --- |
| [Request flow](request-flow.md) | One request, end to end |
| [Policy and consent](policy-and-consent.md) | What gets released; policy vs use case vs consent |
| [Consent model](consent-model.md) | One consent for the partner, one grant per registry |
| [Consent scenarios](consent-scenarios.md) | How a farmer gives a bank consent: in person with a form (built), in person digitally, self-service |
| [Registry model](registry-model.md) | Register, table and activity-register kinds; projections; the Layer 2 split |
| [Register vs activity register](register-vs-activity-register.md) | How the two kinds differ, as built |
| [Terms](terms.md) | Validation, change, correction, void, approval of changes, verification, dispute |
