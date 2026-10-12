---
description: >-
  Agri Stack components, the layers they belong to, and who talks to whom
  when a partner asks for farmer data.
---

# Architecture & Concepts

## Components and who talks to whom

<figure><img src="../../.gitbook/assets/open-agri-stack-components.svg" alt="Agri Stack across departments: the Agriculture Department runs the exchange (partner portal, Consent Manager, eSignet, use-case composite) and the Farmer Registry; the Crops Department runs the Crop Sown Registry with its own Partner Management and Consent Manager, which trusts the Agriculture Consent Manager's receipts"><figcaption><p>Components of Agri Stack, across departments</p></figcaption></figure>

| Colour | Layer |
| --- | --- |
| Blue | Layer 1: functional registries (system of record) |
| Ochre | Layer 2: catalogues (reference data; MDS for now) |
| Teal | Layer 3: shared DPI |
| Green | Layer 4: use-case service |

Each department is its own install with its own Partner Management, Consent Manager and catalogue, and decides at its own boundary. The **Agriculture Department** also runs the exchange: the partner portal, the use-case composite and the Consent Manager that farmers consent at. The **Crops Department** (and any other, e.g. Livestock) runs only its registry and its own services. Calls between departments go over their public hostnames.

1. **Consent request.** A partner's staff (e.g. at a bank) raise a consent request for the farmer in the Consent Manager's partner portal, with the farmer's national ID and Farmer ID, and upload the form the farmer signed.
2. **National-ID login.** The farmer proves who they are through eSignet against the national ID system (OTP or biometrics). Consent Manager staff verify the form and check the Farmer ID in the Farmer Registry; the consent becomes active ([consent collection](../../consent-management/design/consent-collection.md)).
3. **Query.** The partner's system sends a signed query to the use-case composite through the ingress, with the consent: its ID, or a consent the partner signed itself.
4. **Receipts.** The composite asks the Agriculture Consent Manager to validate the consent and gets one signed receipt per registry, with only the scopes the use case needs.
5. **Search.** The composite searches each registry (DCI) with that registry's receipt: the Farmer Registry in its own department, the Crop Sown Registry in the Crops Department.
6. **Check.** Each registry checks its receipt at its **own** department's Consent Manager, which trusts the Agriculture Consent Manager's receipts (its public keys) and applies its standing policy for the composite. Each registry releases only its own slice.

* Every signed call (partner → composite, composite → registry) is checked against Partner Management in the receiving department.
* The ingress (dashed grey: OpenG2P deployment infrastructure, not an Agri Stack service) routes requests but never reads data. The composite runs only approved use cases and keeps nothing after it responds.
* Beckn appears only at the OAN network layer, for discovering service providers and consumers. It isn't used to exchange registry data.

{% hint style="info" %}
How the departments are installed and set up: [distributed deployment architecture](../design/distributed-deployment-architecture.md) and [deploying on a cluster](../guides/deployment.md#three-namespace-setup-exchange-and-departments).
{% endhint %}

## Who does what

* **Partner Management (one per department).** The trust root for the participants that call into that department: partners (in the Agriculture Department, where they onboard) and services such as the composite (in every department whose registry it calls). In the target design it also holds the data-share policies; today they are in the Consent Manager.
* **Consent Manager (one per department).** In the Agriculture Department, it holds the farmer's consents (collected in the partner portal, with the national-ID login, signed form and staff verification) and issues a signed receipt per registry. In every department, it checks the receipts its registry receives against the department's standing policy for the composite.
* **Registries (one per department).** Each one is sovereign: it checks the caller, checks the consent at its own Consent Manager, and releases only the effective scopes. All of them are keyed to the same national-ID-based identifier; the Farmer Registry holds the link between the national ID and the Farmer ID.
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
| [Registry model](registry-model.md) | Register, table and activity-register kinds; projections; the Layer 2 split |
| [Register vs activity register](register-vs-activity-register.md) | How the two kinds differ, as built |
| [Terms](terms.md) | Validation, change, correction, void, approval of changes, verification, dispute |
