---
description: >-
  One consent for the partner, one grant per registry inside it: why, how it
  works, what is built in the Consent Manager, and what is still open.
---

# Consent Model

{% hint style="info" %}
**Status: mostly built (October 2026).**

{% hint style="info" %}
**Consent object, artefact, receipt, token:** four different things; see [key terms](../../consent-management/design/README.md#key-terms). In Agri Stack the bank holds a consent (stored in the exchange's Consent Manager as a consent artefact, with a consent receipt in its consent record), and each registry gets a **consent token** per query.
{% endhint %}

* **Built:** a partner-signed consent can carry one **grant per registry** (`grants: [{data_controller, data_scopes}]`), and each registry validates its own grant (it sends its `data_controller` to CM `/validate`). A partner can be bound to several registries in CM, each with its own policy. Replay is per consent and registry, and each registry gets its own receipt. See [Consent Manager changes](../implementation/consent-manager.md).
* **Built since:** a consent collected through the Consent Manager, in person in the partner portal (the farmer's national-ID login, signed form, staff verification, Farmer ID checked in the Farmer Registry), presented by its ID (`message.consent_id`) and turned into a consent token per registry in the exchange. How a farmer gives consent, in person with a form, in person digitally, or self-service: [consent collection](../../consent-management/design/consent-collection.md).
* **Still to do:** consent in person digitally (no form, no staff step) and self-service, and policies held in Partner Management.
{% endhint %}

## The problem

A partner asks for consent to all the fields it needs. It doesn't know or care which registries hold them. The earlier CM model, however, allowed only **one `data_controller` per consent object**, which would make partners collect a separate consent per registry.

## Proposal

**What the partner sees:** it asks once, for the fields it needs, and gets back **one consent**. It never deals with sources.

**Inside CM:** that one consent holds a **grant per registry** (data controller). Each registry validates only its own grant.

India's Account Aggregator works the same way: one consent artefact lists several data providers, and each provider checks only the accounts that belong to it.

## How it works (target)

**1. Consent request (partner → CM).** The partner states what it needs in business terms. It doesn't name any registries.

```jsonc
POST /consent-requests
{ "subject": {"type":"FAYDA_FAN","value":"…"},
  "purpose": "credit-assessment",
  "scopes": ["farmer:profile","farmer:land","crop:season","livestock:herd"],
  "validity": "P90D", "fetch_type": "oneshot" }
```

**2. CM works out which registries are involved.** Each scope belongs to one registry (`<registry>.<name>`), so the scopes map to registries. CM also checks that the requested scopes fall within the partner's data-share policy. Today the policies are in CM, one per partner binding and registry; in the target design they are held in PM.

**3. The farmer confirms.**

* **Built, in person ([scenario 1](consent-scenarios.md)):** the bank's staff raise the request in the CM partner portal, the farmer logs in with the national ID (eSignet) and signs a form, and CM staff verify it and check the Farmer ID in the Farmer Registry before the consent becomes active.
* **Planned, self-service ([scenario 3](consent-scenarios.md)):** the farmer sees one screen grouped by source (for example "Farmer Registry: profile, land. Crop Sown Registry: crop seasons."), which tells them _who_ holds the data, and, if allowed, can decline individual items.

**4. CM issues one consent artefact, signed by CM.**

```jsonc
{ "consent_id": "…", "subject": "…", "aud": "bank-a", "purpose": "credit-assessment",
  "valid_until": "…", "fetch_type": "oneshot",
  "grants": [
    { "controller": "farmer-registry",    "scopes": ["farmer:profile"] },   // land declined
    { "controller": "crop-sown-registry", "scopes": ["crop:season"] },
    { "controller": "livestock-registry", "scopes": ["livestock:herd"] }
  ] }
```

* It's stored as one consent record, with a child row per grant.
* The farmer gets **one receipt** listing all the controllers. Kantara consent receipts and ISO/IEC 27560 both allow several controllers on one receipt.
* Each department can still see every consent that touches its data.

**5. Using the consent.**

* The partner, or the composite acting for it, sends the consent ID or artefact with the request.
* Each registry calls its own CM's `/validate(consent, controller = itself)`.
* CM returns **that registry's grant ∩ that registry's policy**.
* Through the composite in exchange mode, the exchange CM first turns the consent into one signed consent token per registry, and each registry presents its consent token instead (see [request flow](request-flow.md)).
* Usage is counted **per consent and per controller**, so one-shot and periodic limits apply to each registry separately.

**6. Revocation.** The farmer can revoke the whole consent, or only one source (for example, "stop sharing my livestock data"). The partner is notified either way.

{% hint style="info" %}
**As built,** a consent reaches the composite in one of two forms: collected in CM ([scenario 1](consent-scenarios.md)) and presented by its ID (`message.consent_id`, exchange mode only), or signed by the partner itself (the partner-embedded flow: a compact JWS with a `grants` claim). In exchange mode the exchange CM turns either into a consent token per registry; in passthrough mode the composite forwards the partner's consent unchanged. A partner-signed consent can also be presented directly to a registry. The claims, signing and reason codes are in the Consent Manager's [Partner Integration Guide](../../consent-management/partner-integration-guide.md); the Agri Stack specifics are in the [partner guide](../guides/partner-guide.md).
{% endhint %}

## Changes in CM

What is built, per change, is in [Consent Manager changes](../implementation/consent-manager.md).

| Area | Change | Status |
| --- | --- | --- |
| Consent model | One consent with several grants, replacing the single `data_controller` field | Built for partner-signed consents (`grants` claim; the single-controller form still works) |
| `/validate` | Takes the calling registry as a parameter; returns only that registry's grant ∩ its policy | Built with policies in CM: `data_controller` on `/validate`, bindings per (partner, controller). Policies in PM: target |
| Replay guard | It was keyed on the consent object's ID (`jti`), which would reject the second and third registries presented with the same consent. Move replay protection to a **per-request nonce** (the DCI envelope already carries message IDs and timestamps), and count usage per consent and controller. | Built as replay per (`jti`, controller); the per-request nonce is open |
| Consent collection | The farmer confirms a consent CM holds | Built in person ([scenario 1](consent-scenarios.md)): partner portal, national-ID login (eSignet), signed form, staff verification, Farmer ID as a required identifier checked in the Farmer Registry, consent record download for the partner. In person digitally and self-service (grouped by source, per-item decline): planned |
| Exchange consent tokens | Turn one consent into a signed consent token per registry | Built: exchange CM `/validate` with `issue_receipts` (by `consent_jws` or `consent_id`; consent tokens are called *receipts* in the API and settings); a department CM accepts consent tokens from trusted issuers (`trustedReceiptIssuers`) and checks their status at the issuer |
| Intermediary presentation | Accept a consent presented by the composite on the partner's behalf | Exchange mode: only callers in the exchange CM's `receiptPresenters` (`agri-composite`) get consent tokens, and a department CM checks the token's presenter is its caller. Passthrough mode: the composite forwards the partner's consent unchanged and names the partner in `header.meta.on_behalf_of`; there is no presenter check |

## Open questions

1. **Should consent that spans registries always be collected by CM?**
   * CM supports two ways: the partner collects consent in its own app and signs it ("embedded"), or CM collects it ("originated"): today in person through the partner portal, with a national-ID login and staff verification ([scenario 1](consent-scenarios.md)); in person digitally (no form, no staff step) or self-service later.
   * **Recommendation:** make CM collection the default when consent spans departments. Departments are more likely to trust a consent CM witnessed than one the bank vouches for, and the farmer sees the same screen whichever partner is asking.
   * A consent collected in CM is used through the composite in exchange mode (`message.consent_id`). Presenting it directly at a registry (path A) is open ([open items](../open-items/README.md)).
2. **Should the farmer be able to decline individual items?**
   * It's better for the farmer, but the partner may get less than its use case needs.
   * The composite response already reports a status per source (`ok`, `no_record`, `denied`, `unavailable`, `error`). An optional source whose scopes the consent does not grant is not called and is reported `denied`; a mandatory one fails the request.
   * Alternatively, a policy could mark some scopes as mandatory, meaning the farmer must accept all of them or none.

## Related

* [Consent Management](../../consent-management/README.md): the service, its design and APIs
* [Verification & enforcement](../../consent-management/design/verification-and-enforcement.md): the `/validate` pipeline, replay per (`jti`, controller)
* [Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md): what a registry does with the decision
